"""Database repositories for RetailIQ Lakehouse entities."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from retailiq.database.connection import get_session
from retailiq.database.models import (
    BronzeTransaction,
    MartDataQuality,
    PipelineRunRecord,
    QuarantineTransaction,
    SilverTransaction,
)


class LakehouseRepository:
    """Manages persistence and queries for Bronze, Silver, and Quarantine records."""

    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def load_silver_dataframe(self, df: pd.DataFrame, batch_size: int = 5000) -> int:
        """Insert or append cleaned Silver transactions into the database."""
        if df.empty:
            return 0

        records = []
        for row in df.itertuples(index=False):
            record = SilverTransaction(
                transaction_id=str(row.transaction_id),
                batch_id=str(row.batch_id),
                invoice_no=str(row.invoice_no),
                stock_code=str(row.stock_code),
                description=str(row.description),
                quantity=int(row.quantity),
                invoice_date=row.invoice_date.to_pydatetime() if hasattr(row.invoice_date, "to_pydatetime") else row.invoice_date,
                unit_price=float(row.unit_price),
                customer_id=str(row.customer_id),
                country=str(row.country),
                is_cancellation=bool(row.is_cancellation),
                is_guest_checkout=bool(row.is_guest_checkout),
                line_total=float(row.line_total),
            )
            records.append(record)

        with get_session() as session:
            session.bulk_save_objects(records)
        return len(records)

    def load_quarantine_dataframe(self, df: pd.DataFrame) -> int:
        """Persist rejected records into quarantine table."""
        if df.empty:
            return 0

        records = []
        for idx, row in enumerate(df.itertuples(index=False)):
            payload = {c: getattr(row, c) for c in df.columns if hasattr(row, c)}
            # Convert non-serializable objects (like datetime) to string
            serializable_payload = {
                k: (v.isoformat() if isinstance(v, (datetime, pd.Timestamp)) else str(v) if pd.isna(v) else v)
                for k, v in payload.items()
            }
            record = QuarantineTransaction(
                batch_id=str(row.batch_id),
                source_row_idx=idx,
                rejection_reason=str(row.rejection_reason),
                raw_payload_json=json.dumps(serializable_payload),
            )
            records.append(record)

        with get_session() as session:
            session.bulk_save_objects(records)
        return len(records)

    def get_silver_stats(self) -> dict[str, Any]:
        """Compute basic summary statistics from the Silver layer."""
        with get_session() as session:
            total_records = session.query(func.count(SilverTransaction.id)).scalar() or 0
            total_revenue = (
                session.query(func.sum(SilverTransaction.line_total))
                .filter(SilverTransaction.is_cancellation.is_(False))
                .scalar()
                or 0.0
            )
            cancellations = (
                session.query(func.count(SilverTransaction.id))
                .filter(SilverTransaction.is_cancellation.is_(True))
                .scalar()
                or 0
            )
            unique_customers = (
                session.query(func.count(func.distinct(SilverTransaction.customer_id)))
                .filter(SilverTransaction.customer_id != "guest_checkout")
                .scalar()
                or 0
            )

        return {
            "total_records": total_records,
            "gross_revenue": round(total_revenue, 2),
            "cancellations_count": cancellations,
            "unique_registered_customers": unique_customers,
        }
