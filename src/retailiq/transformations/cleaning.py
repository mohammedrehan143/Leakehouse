"""Silver Layer Data Cleaning and Validation Pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from retailiq.config import settings
from retailiq.transformations.quarantine import QuarantineManager


@dataclass
class CleaningSummary:
    """Detailed summary of cleaning and validation operations."""

    batch_id: str
    total_bronze_records: int
    valid_silver_records: int
    quarantined_records: int
    cancellations_count: int
    guest_checkouts_count: int
    silver_output_file: str
    quarantine_output_file: str | None = None
    execution_time_seconds: float = 0.0
    quarantine_breakdown: dict[str, int] = field(default_factory=dict)


class SilverCleaner:
    """Transforms raw Bronze transaction records into validated Silver records."""

    def __init__(
        self,
        silver_dir: Path | None = None,
        quarantine_manager: QuarantineManager | None = None,
    ) -> None:
        self.silver_dir = silver_dir or settings.storage.silver_dir
        self.silver_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_manager = quarantine_manager or QuarantineManager()

    def clean_dataframe(
        self,
        bronze_df: pd.DataFrame,
        batch_id: str = "BATCH_MANUAL",
    ) -> tuple[pd.DataFrame, pd.DataFrame, CleaningSummary]:
        """Execute cleaning rules and partition into (valid_silver_df, quarantine_df, summary)."""
        start_time = datetime.now(UTC)
        total_records = len(bronze_df)

        if total_records == 0:
            empty_df = pd.DataFrame()
            return empty_df, empty_df, CleaningSummary(
                batch_id=batch_id,
                total_bronze_records=0,
                valid_silver_records=0,
                quarantined_records=0,
                cancellations_count=0,
                guest_checkouts_count=0,
                silver_output_file="",
            )

        df = bronze_df.copy()

        # Normalize column mapping
        rename_map = {
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
        }
        df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

        # Standardize string fields
        df["invoice_no"] = df["invoice_no"].astype(str).str.strip()
        df["stock_code"] = df["stock_code"].astype(str).str.strip()
        df["description"] = df["description"].fillna("UNKNOWN ITEM").astype(str).str.strip()
        df["country"] = df["country"].fillna("Unspecified").astype(str).str.strip()

        # Parse numeric columns safely
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0).astype(float)
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

        # ---------------------------------------------------------------------
        # Quarantine Rule Evaluations
        # ---------------------------------------------------------------------
        rejection_reasons = pd.Series(index=df.index, dtype=object)

        # Rule 1: Missing or blank invoice number
        mask_bad_invoice = df["invoice_no"].isna() | (df["invoice_no"] == "") | (df["invoice_no"] == "nan")
        rejection_reasons[mask_bad_invoice] = "MISSING_INVOICE_NUMBER"

        # Rule 2: Missing or blank stock code
        mask_bad_stock = df["stock_code"].isna() | (df["stock_code"] == "") | (df["stock_code"] == "nan")
        rejection_reasons[mask_bad_stock & rejection_reasons.isna()] = "MISSING_STOCK_CODE"

        # Rule 3: Invalid or unparseable invoice date
        mask_bad_date = df["invoice_date"].isna()
        rejection_reasons[mask_bad_date & rejection_reasons.isna()] = "INVALID_INVOICE_DATE"

        # Rule 4: Non-positive unit price (zero or negative price without commercial justification)
        # Note: In UCI retail, UnitPrice <= 0 denotes bad debts, manual test adjustments, or gifts
        mask_bad_price = df["unit_price"] <= 0.0
        rejection_reasons[mask_bad_price & rejection_reasons.isna()] = "INVALID_UNIT_PRICE_NON_POSITIVE"

        # Separate quarantined rows
        is_quarantined = rejection_reasons.notna()
        quarantine_df = df[is_quarantined].copy()
        valid_df = df[~is_quarantined].copy()

        quarantine_breakdown: dict[str, int] = {}
        if not quarantine_df.empty:
            quarantine_df["rejection_reason"] = rejection_reasons[is_quarantined]
            quarantine_df["batch_id"] = batch_id
            quarantine_df["quarantined_at"] = datetime.now(UTC).isoformat()
            quarantine_breakdown = quarantine_df["rejection_reason"].value_counts().to_dict()

        # ---------------------------------------------------------------------
        # Silver Business Logic & Feature Enrichment
        # ---------------------------------------------------------------------
        if not valid_df.empty:
            # Handle Customer ID: guest checkouts flagged, not dropped
            valid_df["is_guest_checkout"] = (
                valid_df["customer_id"].isna()
                | (valid_df["customer_id"] == "")
                | (valid_df["customer_id"] == "nan")
            )
            valid_df["customer_id"] = valid_df["customer_id"].apply(
                lambda x: "guest_checkout" if pd.isna(x) or str(x).strip() in ("", "nan") else str(x).strip()
            )

            # Detect cancellations: 'C' prefix in invoice or negative quantity
            valid_df["is_cancellation"] = (
                valid_df["invoice_no"].str.upper().str.startswith("C")
                | (valid_df["quantity"] < 0)
            )

            # Compute line total (quantity * unit_price)
            valid_df["line_total"] = (valid_df["quantity"] * valid_df["unit_price"]).round(4)

            # Generate unique surrogate key for Silver transaction
            valid_df["transaction_id"] = [
                f"TX_{batch_id}_{i}" for i in range(len(valid_df))
            ]
            valid_df["batch_id"] = batch_id
            valid_df["cleaned_at"] = datetime.now(UTC).isoformat()

        # Save outputs
        silver_file = self.silver_dir / f"silver_{batch_id}.parquet"
        standard_silver = self.silver_dir / "silver_transactions_cleaned.parquet"
        if not valid_df.empty:
            tbl = pa.Table.from_pandas(valid_df)
            pq.write_table(tbl, silver_file, compression="snappy")
            pq.write_table(tbl, standard_silver, compression="snappy")

        quarantine_file: str | None = None
        if not quarantine_df.empty:
            q_path = self.quarantine_manager.save_quarantined_dataframe(batch_id, quarantine_df)
            quarantine_file = str(q_path) if q_path else None

        duration = (datetime.now(UTC) - start_time).total_seconds()

        summary = CleaningSummary(
            batch_id=batch_id,
            total_bronze_records=total_records,
            valid_silver_records=len(valid_df),
            quarantined_records=len(quarantine_df),
            cancellations_count=int(valid_df["is_cancellation"].sum()) if not valid_df.empty else 0,
            guest_checkouts_count=int(valid_df["is_guest_checkout"].sum()) if not valid_df.empty else 0,
            silver_output_file=str(silver_file),
            quarantine_output_file=quarantine_file,
            execution_time_seconds=duration,
            quarantine_breakdown=quarantine_breakdown,
        )
        return valid_df, quarantine_df, summary
