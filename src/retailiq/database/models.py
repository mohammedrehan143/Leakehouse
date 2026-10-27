"""SQLAlchemy ORM models for the RetailIQ Lakehouse & Analytics Platform."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# -----------------------------------------------------------------------------
# Bronze & Silver Staging Tables
# -----------------------------------------------------------------------------


class BronzeTransaction(Base):
    """Raw transaction records preserved with source audit columns."""

    __tablename__ = "bronze_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingestion_id: Mapped[str] = mapped_column(String(64), index=True)
    batch_id: Mapped[str] = mapped_column(String(64), index=True)
    source_file: Mapped[str] = mapped_column(String(255))
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Raw payload columns
    raw_invoice_no: Mapped[str | None] = mapped_column(String(50))
    raw_stock_code: Mapped[str | None] = mapped_column(String(50))
    raw_description: Mapped[str | None] = mapped_column(Text)
    raw_quantity: Mapped[int | None] = mapped_column(Integer)
    raw_invoice_date: Mapped[datetime | None] = mapped_column(DateTime)
    raw_unit_price: Mapped[float | None] = mapped_column(Float)
    raw_customer_id: Mapped[str | None] = mapped_column(String(50))
    raw_country: Mapped[str | None] = mapped_column(String(100))


class SilverTransaction(Base):
    """Cleaned, validated, and normalized transaction records."""

    __tablename__ = "silver_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    batch_id: Mapped[str] = mapped_column(String(64), index=True)
    invoice_no: Mapped[str] = mapped_column(String(50), index=True)
    stock_code: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    invoice_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    unit_price: Mapped[float] = mapped_column(Float)
    customer_id: Mapped[str] = mapped_column(String(50), index=True, default="guest_checkout")
    country: Mapped[str] = mapped_column(String(100), index=True)

    # Derived business flags
    is_cancellation: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_guest_checkout: Mapped[bool] = mapped_column(Boolean, default=False)
    line_total: Mapped[float] = mapped_column(Float)
    cleaned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_silver_invoice_stock", "invoice_no", "stock_code"),
        Index("idx_silver_customer_date", "customer_id", "invoice_date"),
    )


class QuarantineTransaction(Base):
    """Invalid or malformed records routed out of the primary analytics pipeline."""

    __tablename__ = "quarantine_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String(64), index=True)
    source_row_idx: Mapped[int] = mapped_column(Integer)
    rejection_reason: Mapped[str] = mapped_column(String(255), index=True)
    raw_payload_json: Mapped[str] = mapped_column(Text)
    quarantined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# -----------------------------------------------------------------------------
# Gold Layer: Dimensional Models & Facts
# -----------------------------------------------------------------------------


class DimCustomer(Base):
    """Customer dimensional entity."""

    __tablename__ = "dim_customers"

    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country: Mapped[str] = mapped_column(String(100))
    first_purchase_date: Mapped[datetime | None] = mapped_column(DateTime)
    last_purchase_date: Mapped[datetime | None] = mapped_column(DateTime)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_spend: Mapped[float] = mapped_column(Float, default=0.0)
    is_repeat_customer: Mapped[bool] = mapped_column(Boolean, default=False)


class DimProduct(Base):
    """Product dimensional entity."""

    __tablename__ = "dim_products"

    stock_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    typical_unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    total_units_sold: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)


class DimDate(Base):
    """Calendar date dimension."""

    __tablename__ = "dim_dates"

    date_key: Mapped[str] = mapped_column(String(10), primary_key=True)  # YYYY-MM-DD
    full_date: Mapped[datetime] = mapped_column(Date)
    day_of_week: Mapped[int] = mapped_column(Integer)
    day_name: Mapped[str] = mapped_column(String(15))
    month: Mapped[int] = mapped_column(Integer)
    month_name: Mapped[str] = mapped_column(String(15))
    year: Mapped[int] = mapped_column(Integer)
    is_weekend: Mapped[bool] = mapped_column(Boolean)


class FactSales(Base):
    """Sales fact table at the grain of (InvoiceNo, StockCode, Line)."""

    __tablename__ = "fct_sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    invoice_no: Mapped[str] = mapped_column(String(50), index=True)
    stock_code: Mapped[str] = mapped_column(String(50), index=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True)
    date_key: Mapped[str] = mapped_column(String(10), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    gross_revenue: Mapped[float] = mapped_column(Float)
    country: Mapped[str] = mapped_column(String(100), index=True)


class FactReturns(Base):
    """Returns and cancellations fact table."""

    __tablename__ = "fct_returns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    invoice_no: Mapped[str] = mapped_column(String(50), index=True)
    stock_code: Mapped[str] = mapped_column(String(50), index=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True)
    date_key: Mapped[str] = mapped_column(String(10), index=True)
    return_quantity: Mapped[int] = mapped_column(Integer)  # Stored as positive quantity returned
    unit_price: Mapped[float] = mapped_column(Float)
    return_amount: Mapped[float] = mapped_column(Float)  # Dollar value of return
    country: Mapped[str] = mapped_column(String(100))


# -----------------------------------------------------------------------------
# Gold Analytical Marts
# -----------------------------------------------------------------------------


class MartDailySales(Base):
    """Aggregated daily sales mart."""

    __tablename__ = "mart_daily_sales"

    date_key: Mapped[str] = mapped_column(String(10), primary_key=True)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    units_sold: Mapped[int] = mapped_column(Integer, default=0)
    gross_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    returns_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    net_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    active_customers: Mapped[int] = mapped_column(Integer, default=0)


class MartMonthlySales(Base):
    """Aggregated monthly sales mart."""

    __tablename__ = "mart_monthly_sales"

    year_month: Mapped[str] = mapped_column(String(7), primary_key=True)  # YYYY-MM
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    units_sold: Mapped[int] = mapped_column(Integer, default=0)
    gross_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    returns_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    net_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    unique_customers: Mapped[int] = mapped_column(Integer, default=0)


class MartProductPerformance(Base):
    """Product performance rankings and revenue concentration."""

    __tablename__ = "mart_product_performance"

    stock_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    total_units_sold: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    return_count: Mapped[int] = mapped_column(Integer, default=0)


class MartCustomerMetrics(Base):
    """Customer analytics, repeat purchase rates, and spending."""

    __tablename__ = "mart_customer_metrics"

    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    country: Mapped[str] = mapped_column(String(100))
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_spend: Mapped[float] = mapped_column(Float, default=0.0)
    avg_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    is_repeat_purchaser: Mapped[bool] = mapped_column(Boolean, default=False)
    recency_days: Mapped[int | None] = mapped_column(Integer)


class MartCountryPerformance(Base):
    """Geographic revenue and order metrics by country."""

    __tablename__ = "mart_country_performance"

    country: Mapped[str] = mapped_column(String(100), primary_key=True)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    unique_customers: Mapped[int] = mapped_column(Integer, default=0)


class MartDataQuality(Base):
    """Audit records of automated data quality checks."""

    __tablename__ = "mart_data_quality"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    check_name: Mapped[str] = mapped_column(String(100), index=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    records_examined: Mapped[int] = mapped_column(Integer)
    records_failed: Mapped[int] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(20))  # INFO, WARNING, ERROR
    status: Mapped[str] = mapped_column(String(20))  # PASS, FAIL
    details: Mapped[str] = mapped_column(Text)


# -----------------------------------------------------------------------------
# Operations & Observability
# -----------------------------------------------------------------------------


class PipelineRunRecord(Base):
    """Execution logs for end-to-end data pipelines."""

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    pipeline_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    summary_json: Mapped[str | None] = mapped_column(Text)
