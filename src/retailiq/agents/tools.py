"""Controlled execution tools for RetailIQ AI Agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import desc, func, select

from retailiq.config import settings
from retailiq.database.connection import get_session
from retailiq.database.models import (
    MartCountryPerformance,
    MartCustomerMetrics,
    MartDailySales,
    MartDataQuality,
    MartMonthlySales,
    MartProductPerformance,
    PipelineRunRecord,
)
from retailiq.database.repositories import LakehouseRepository
from retailiq.pipeline.quality import DataQualityChecker


def query_sales_summary() -> dict[str, Any]:
    """Retrieve high-level sales and revenue summary."""
    with get_session() as session:
        daily_records = session.query(MartDailySales).all()
        if not daily_records:
            return {"status": "NO_DATA", "message": "No sales data in Gold mart"}

        total_gross = sum(r.gross_revenue for r in daily_records)
        total_returns = sum(r.returns_revenue for r in daily_records)
        total_net = sum(r.net_revenue for r in daily_records)
        total_orders = sum(r.order_count for r in daily_records)
        total_units = sum(r.units_sold for r in daily_records)

        return {
            "status": "SUCCESS",
            "total_orders": total_orders,
            "units_sold": total_units,
            "gross_revenue": round(total_gross, 2),
            "returns_revenue": round(total_returns, 2),
            "net_revenue": round(total_net, 2),
            "days_recorded": len(daily_records),
        }


def query_top_products(limit: int = 5) -> list[dict[str, Any]]:
    """Retrieve top products by gross revenue."""
    with get_session() as session:
        records = (
            session.query(MartProductPerformance)
            .order_by(desc(MartProductPerformance.total_revenue))
            .limit(limit)
            .all()
        )
        return [
            {
                "stock_code": r.stock_code,
                "description": r.description,
                "total_revenue": r.total_revenue,
                "total_units_sold": r.total_units_sold,
                "order_count": r.order_count,
            }
            for r in records
        ]


def query_customer_overview() -> dict[str, Any]:
    """Retrieve customer statistics and repeat purchase metrics."""
    with get_session() as session:
        records = session.query(MartCustomerMetrics).all()
        if not records:
            return {"status": "NO_DATA"}

        total_customers = len(records)
        repeat_customers = sum(1 for r in records if r.is_repeat_purchaser)
        repeat_rate = round((repeat_customers / total_customers * 100), 2) if total_customers > 0 else 0.0
        avg_spend = round(sum(r.total_spend for r in records) / total_customers, 2) if total_customers > 0 else 0.0

        return {
            "status": "SUCCESS",
            "total_registered_customers": total_customers,
            "repeat_customers": repeat_customers,
            "repeat_purchase_rate_pct": repeat_rate,
            "average_customer_spend": avg_spend,
        }


def query_data_quality_report() -> list[dict[str, Any]]:
    """Retrieve latest data quality audit results."""
    with get_session() as session:
        records = session.query(MartDataQuality).order_by(desc(MartDataQuality.checked_at)).limit(10).all()
        return [
            {
                "check_name": r.check_name,
                "status": r.status,
                "severity": r.severity,
                "records_examined": r.records_examined,
                "records_failed": r.records_failed,
                "details": r.details,
            }
            for r in records
        ]
