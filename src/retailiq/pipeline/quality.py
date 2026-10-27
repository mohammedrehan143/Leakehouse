"""Deterministic Data Quality Engine for RetailIQ Lakehouse."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from retailiq.database.connection import get_session, init_db
from retailiq.database.models import MartDataQuality


@dataclass
class QualityCheckResult:
    """Outcome of an individual data quality check."""

    check_name: str
    status: str  # PASS, WARNING, FAIL
    records_examined: int
    records_failed: int
    severity: str  # INFO, WARNING, ERROR
    details: str
    checked_at: str = ""


class DataQualityChecker:
    """Executes deterministic data validation checks on Silver and Gold data."""

    def __init__(self) -> None:
        pass

    def run_all_checks(
        self,
        silver_df: pd.DataFrame,
        quarantine_df: pd.DataFrame | None = None,
        persist_to_db: bool = True,
    ) -> list[QualityCheckResult]:
        """Execute comprehensive quality test suite and record results."""
        results: list[QualityCheckResult] = []
        n_silver = len(silver_df)
        n_quarantine = len(quarantine_df) if quarantine_df is not None else 0
        total_records = n_silver + n_quarantine
        now_str = datetime.now(UTC).isoformat()

        # Check 1: Missing invoice numbers in Silver
        missing_inv = int(silver_df["invoice_no"].isna().sum()) if n_silver > 0 else 0
        results.append(
            QualityCheckResult(
                check_name="missing_invoice_numbers",
                status="PASS" if missing_inv == 0 else "FAIL",
                records_examined=n_silver,
                records_failed=missing_inv,
                severity="ERROR",
                details="Confirmed zero missing invoice numbers in Silver layer." if missing_inv == 0 else f"{missing_inv} records missing invoice number.",
                checked_at=now_str,
            )
        )

        # Check 2: Missing stock codes in Silver
        missing_stock = int(silver_df["stock_code"].isna().sum()) if n_silver > 0 else 0
        results.append(
            QualityCheckResult(
                check_name="missing_stock_codes",
                status="PASS" if missing_stock == 0 else "FAIL",
                records_examined=n_silver,
                records_failed=missing_stock,
                severity="ERROR",
                details="All Silver records contain a valid product stock code." if missing_stock == 0 else f"{missing_stock} records missing stock code.",
                checked_at=now_str,
            )
        )

        # Check 3: Non-positive unit prices in Silver
        bad_prices = int((silver_df["unit_price"] <= 0).sum()) if n_silver > 0 else 0
        results.append(
            QualityCheckResult(
                check_name="non_positive_unit_prices",
                status="PASS" if bad_prices == 0 else "FAIL",
                records_examined=n_silver,
                records_failed=bad_prices,
                severity="ERROR",
                details="Zero non-positive unit prices in Silver layer." if bad_prices == 0 else f"{bad_prices} records have unit price <= 0.",
                checked_at=now_str,
            )
        )

        # Check 4: Cancellation integrity
        if n_silver > 0:
            cancellation_mismatches = int(
                ((silver_df["quantity"] < 0) & (~silver_df["is_cancellation"])).sum()
            )
        else:
            cancellation_mismatches = 0
        results.append(
            QualityCheckResult(
                check_name="cancellation_classification_integrity",
                status="PASS" if cancellation_mismatches == 0 else "FAIL",
                records_examined=n_silver,
                records_failed=cancellation_mismatches,
                severity="ERROR",
                details="All negative quantity records correctly flagged as cancellations." if cancellation_mismatches == 0 else f"{cancellation_mismatches} cancellations unflagged.",
                checked_at=now_str,
            )
        )

        # Check 5: Quarantine anomaly threshold (< 5% of total records)
        quarantine_pct = (n_quarantine / total_records * 100) if total_records > 0 else 0.0
        q_status = "PASS" if quarantine_pct < 5.0 else "WARNING"
        results.append(
            QualityCheckResult(
                check_name="quarantine_anomaly_threshold",
                status=q_status,
                records_examined=total_records,
                records_failed=n_quarantine,
                severity="WARNING",
                details=f"Quarantine rate is {quarantine_pct:.2f}% (healthy threshold: < 5.0%).",
                checked_at=now_str,
            )
        )

        # Persist to database
        if persist_to_db:
            init_db()
            with get_session() as session:
                session.bulk_save_objects([
                    MartDataQuality(
                        check_name=res.check_name,
                        checked_at=datetime.utcnow(),
                        records_examined=res.records_examined,
                        records_failed=res.records_failed,
                        severity=res.severity,
                        status=res.status,
                        details=res.details,
                    )
                    for res in results
                ])

        return results
