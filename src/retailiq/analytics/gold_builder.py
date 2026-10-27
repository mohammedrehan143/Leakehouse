"""Gold Layer Analytics Builder.

Constructs dimensional entities (customers, products, dates), fact tables (sales, returns),
and analytical marts (daily sales, monthly sales, customer metrics, product performance)
from cleaned Silver data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from retailiq.config import settings
from retailiq.database.connection import get_session, init_db
from retailiq.database.models import (
    DimCustomer,
    DimDate,
    DimProduct,
    FactReturns,
    FactSales,
    MartCountryPerformance,
    MartCustomerMetrics,
    MartDailySales,
    MartMonthlySales,
    MartProductPerformance,
)


@dataclass
class GoldBuildSummary:
    """Execution summary of Gold model building."""

    fact_sales_count: int
    fact_returns_count: int
    dim_customers_count: int
    dim_products_count: int
    dim_dates_count: int
    mart_daily_rows: int
    mart_monthly_rows: int
    execution_time_seconds: float
    output_files: list[str]


class GoldLayerBuilder:
    """Builds Gold layer facts, dimensions, and analytical marts."""

    def __init__(self, gold_dir: Path | None = None) -> None:
        self.gold_dir = gold_dir or Path(settings.storage.processed_dir) / "gold"
        self.gold_dir.mkdir(parents=True, exist_ok=True)

    def build_gold_layer(
        self,
        silver_df: pd.DataFrame,
        persist_to_db: bool = True,
    ) -> GoldBuildSummary:
        """Transform Silver dataframe into all Gold models and marts."""
        start_time = datetime.now(UTC)
        output_files: list[str] = []

        if silver_df.empty:
            return GoldBuildSummary(
                fact_sales_count=0,
                fact_returns_count=0,
                dim_customers_count=0,
                dim_products_count=0,
                dim_dates_count=0,
                mart_daily_rows=0,
                mart_monthly_rows=0,
                execution_time_seconds=0.0,
                output_files=[],
            )

        df = silver_df.copy()
        df["invoice_date"] = pd.to_datetime(df["invoice_date"])
        df["date_key"] = df["invoice_date"].dt.strftime("%Y-%m-%d")
        df["year_month"] = df["invoice_date"].dt.strftime("%Y-%m")

        # ---------------------------------------------------------------------
        # 1. Fact Tables: fct_sales and fct_returns
        # ---------------------------------------------------------------------
        sales_mask = (~df["is_cancellation"]) & (df["quantity"] > 0) & (df["unit_price"] > 0)
        fct_sales = df[sales_mask].copy()
        fct_sales["gross_revenue"] = fct_sales["line_total"]

        returns_mask = df["is_cancellation"] | (df["quantity"] < 0)
        fct_returns = df[returns_mask].copy()
        fct_returns["return_quantity"] = fct_returns["quantity"].abs()
        fct_returns["return_amount"] = fct_returns["line_total"].abs()

        # ---------------------------------------------------------------------
        # 2. Dimension Tables
        # ---------------------------------------------------------------------
        # dim_customers
        reg_customers = df[df["customer_id"] != "guest_checkout"]
        dim_cust = (
            reg_customers.groupby("customer_id")
            .agg(
                country=("country", "last"),
                first_purchase_date=("invoice_date", "min"),
                last_purchase_date=("invoice_date", "max"),
                total_orders=("invoice_no", "nunique"),
                total_spend=("line_total", lambda x: round(float(x[x > 0].sum()), 2)),
            )
            .reset_index()
        )
        dim_cust["is_repeat_customer"] = dim_cust["total_orders"] > 1

        # dim_products
        dim_prod = (
            df.groupby("stock_code")
            .agg(
                description=("description", "last"),
                typical_unit_price=("unit_price", lambda x: round(float(x.mean()), 2)),
                total_units_sold=("quantity", lambda x: int(x[x > 0].sum())),
                total_revenue=("line_total", lambda x: round(float(x[x > 0].sum()), 2)),
            )
            .reset_index()
        )

        # dim_dates
        unique_dates = pd.date_range(
            start=df["invoice_date"].min().floor("D"),
            end=df["invoice_date"].max().ceil("D"),
            freq="D",
        )
        dim_dates = pd.DataFrame({
            "date_key": unique_dates.strftime("%Y-%m-%d"),
            "full_date": unique_dates,
            "day_of_week": unique_dates.dayofweek,
            "day_name": unique_dates.day_name(),
            "month": unique_dates.month,
            "month_name": unique_dates.month_name(),
            "year": unique_dates.year,
            "is_weekend": unique_dates.dayofweek.isin([5, 6]),
        })

        # ---------------------------------------------------------------------
        # 3. Analytical Marts
        # ---------------------------------------------------------------------
        # mart_daily_sales
        daily_sales = (
            fct_sales.groupby("date_key")
            .agg(
                order_count=("invoice_no", "nunique"),
                units_sold=("quantity", "sum"),
                gross_revenue=("gross_revenue", lambda x: round(float(x.sum()), 2)),
                active_customers=("customer_id", "nunique"),
            )
            .reset_index()
        )
        daily_returns = (
            fct_returns.groupby("date_key")
            .agg(returns_revenue=("return_amount", lambda x: round(float(x.sum()), 2)))
            .reset_index()
        )
        mart_daily = pd.merge(daily_sales, daily_returns, on="date_key", how="left").fillna(0.0)
        mart_daily["net_revenue"] = (mart_daily["gross_revenue"] - mart_daily["returns_revenue"]).round(2)
        mart_daily.sort_values("date_key", inplace=True)

        # mart_monthly_sales
        monthly_sales = (
            fct_sales.groupby("year_month")
            .agg(
                order_count=("invoice_no", "nunique"),
                units_sold=("quantity", "sum"),
                gross_revenue=("gross_revenue", lambda x: round(float(x.sum()), 2)),
                unique_customers=("customer_id", "nunique"),
            )
            .reset_index()
        )
        monthly_returns = (
            fct_returns.groupby("year_month")
            .agg(returns_revenue=("return_amount", lambda x: round(float(x.sum()), 2)))
            .reset_index()
        )
        mart_monthly = pd.merge(monthly_sales, monthly_returns, on="year_month", how="left").fillna(0.0)
        mart_monthly["net_revenue"] = (mart_monthly["gross_revenue"] - mart_monthly["returns_revenue"]).round(2)
        mart_monthly.sort_values("year_month", inplace=True)

        # mart_product_performance
        mart_prod = (
            fct_sales.groupby(["stock_code", "description"])
            .agg(
                total_units_sold=("quantity", "sum"),
                total_revenue=("gross_revenue", lambda x: round(float(x.sum()), 2)),
                order_count=("invoice_no", "nunique"),
            )
            .reset_index()
        )
        mart_prod_ret = (
            fct_returns.groupby("stock_code")
            .agg(return_count=("quantity", lambda x: int(x.count())))
            .reset_index()
        )
        mart_product = pd.merge(mart_prod, mart_prod_ret, on="stock_code", how="left").fillna(0)
        mart_product.sort_values("total_revenue", ascending=False, inplace=True)

        # mart_country_performance
        mart_country = (
            fct_sales.groupby("country")
            .agg(
                order_count=("invoice_no", "nunique"),
                total_revenue=("gross_revenue", lambda x: round(float(x.sum()), 2)),
                unique_customers=("customer_id", "nunique"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )

        # mart_customer_metrics
        latest_date = df["invoice_date"].max()
        mart_cust = (
            reg_customers.groupby(["customer_id", "country"])
            .agg(
                total_orders=("invoice_no", "nunique"),
                total_spend=("line_total", lambda x: round(float(x[x > 0].sum()), 2)),
                last_purchase=("invoice_date", "max"),
            )
            .reset_index()
        )
        mart_cust["avg_order_value"] = (mart_cust["total_spend"] / mart_cust["total_orders"]).round(2)
        mart_cust["is_repeat_purchaser"] = mart_cust["total_orders"] > 1
        mart_cust["recency_days"] = (latest_date - mart_cust["last_purchase"]).dt.days

        # ---------------------------------------------------------------------
        # Persist Gold Parquet Files
        # ---------------------------------------------------------------------
        tables_map = {
            "fct_sales.parquet": fct_sales,
            "fct_returns.parquet": fct_returns,
            "dim_customers.parquet": dim_cust,
            "dim_products.parquet": dim_prod,
            "dim_dates.parquet": dim_dates,
            "mart_daily_sales.parquet": mart_daily,
            "mart_monthly_sales.parquet": mart_monthly,
            "mart_product_performance.parquet": mart_product,
            "mart_country_performance.parquet": mart_country,
            "mart_customer_metrics.parquet": mart_cust,
        }

        for fname, table_df in tables_map.items():
            fpath = self.gold_dir / fname
            pq.write_table(pa.Table.from_pandas(table_df), fpath, compression="snappy")
            output_files.append(str(fpath))

        # ---------------------------------------------------------------------
        # Persist to Relational Database
        # ---------------------------------------------------------------------
        if persist_to_db:
            init_db()
            with get_session() as session:
                # Clear and insert into daily sales
                session.query(MartDailySales).delete()
                session.bulk_save_objects([
                    MartDailySales(
                        date_key=row.date_key,
                        order_count=int(row.order_count),
                        units_sold=int(row.units_sold),
                        gross_revenue=float(row.gross_revenue),
                        returns_revenue=float(row.returns_revenue),
                        net_revenue=float(row.net_revenue),
                        active_customers=int(row.active_customers),
                    )
                    for row in mart_daily.itertuples(index=False)
                ])

                # Monthly sales
                session.query(MartMonthlySales).delete()
                session.bulk_save_objects([
                    MartMonthlySales(
                        year_month=row.year_month,
                        order_count=int(row.order_count),
                        units_sold=int(row.units_sold),
                        gross_revenue=float(row.gross_revenue),
                        returns_revenue=float(row.returns_revenue),
                        net_revenue=float(row.net_revenue),
                        unique_customers=int(row.unique_customers),
                    )
                    for row in mart_monthly.itertuples(index=False)
                ])

                # Country performance
                session.query(MartCountryPerformance).delete()
                session.bulk_save_objects([
                    MartCountryPerformance(
                        country=row.country,
                        order_count=int(row.order_count),
                        total_revenue=float(row.total_revenue),
                        unique_customers=int(row.unique_customers),
                    )
                    for row in mart_country.itertuples(index=False)
                ])

        duration = (datetime.now(UTC) - start_time).total_seconds()

        return GoldBuildSummary(
            fact_sales_count=len(fct_sales),
            fact_returns_count=len(fct_returns),
            dim_customers_count=len(dim_cust),
            dim_products_count=len(dim_prod),
            dim_dates_count=len(dim_dates),
            mart_daily_rows=len(mart_daily),
            mart_monthly_rows=len(mart_monthly),
            execution_time_seconds=duration,
            output_files=output_files,
        )
