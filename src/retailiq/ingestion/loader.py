"""Bronze Layer Ingestion Loader.

Reads raw source records, validates columns, attaches audit metadata,
and preserves an immutable Bronze Parquet representation in the lakehouse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from retailiq.config import settings
from retailiq.ingestion.batch_manager import BatchManager, BatchRecord, BatchStatus
from retailiq.ingestion.schema import compute_row_hash, validate_raw_dataframe


@dataclass
class IngestionResult:
    """Summary of an ingestion execution."""

    batch_id: str
    status: str
    total_records: int
    bronze_records: int
    quarantined_records: int
    output_files: list[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BronzeLoader:
    """Handles raw data ingestion into the Bronze Lakehouse layer."""

    def __init__(
        self,
        batch_manager: BatchManager | None = None,
        bronze_dir: Path | None = None,
    ) -> None:
        self.batch_manager = batch_manager or BatchManager()
        self.bronze_dir = bronze_dir or settings.storage.bronze_parquet_dir
        self.bronze_dir.mkdir(parents=True, exist_ok=True)

    def load_dataset(
        self,
        file_path: Path | None = None,
        force_reingest: bool = False,
        nrows: int | None = None,
    ) -> IngestionResult:
        """Execute Bronze ingestion on source Excel or CSV dataset."""
        start_time = datetime.now(UTC)
        source_path = file_path or settings.dataset.raw_file_path

        if not source_path.exists():
            raise FileNotFoundError(f"Source dataset not found at: {source_path}")

        file_hash = self.batch_manager.calculate_file_hash(source_path)

        # Idempotency check: if not forcing rerun, check if already ingested
        if not force_reingest:
            existing = self.batch_manager.find_completed_batch_by_hash(file_hash)
            if existing and nrows is None:
                print(f"[*] Dataset with hash {file_hash[:8]} already ingested in {existing.batch_id}.")
                return IngestionResult(
                    batch_id=existing.batch_id,
                    status="SKIPPED_ALREADY_INGESTED",
                    total_records=existing.total_records,
                    bronze_records=existing.bronze_records,
                    quarantined_records=existing.quarantined_records,
                    output_files=existing.output_files,
                    metadata={"note": "Idempotent skip; rerun with force_reingest=True to override"},
                )

        # Start new batch
        batch = self.batch_manager.start_batch(source_path)

        try:
            print(f"[*] Reading source dataset: {source_path}...")
            # Read source file (Excel or CSV)
            if source_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(source_path, nrows=nrows)
            elif source_path.suffix.lower() == ".csv":
                df = pd.read_csv(source_path, nrows=nrows)
            else:
                raise ValueError(f"Unsupported file format: {source_path.suffix}")

            total_records = len(df)
            print(f"[*] Read {total_records:,} raw records. Validating schema...")

            # Validate expected columns
            is_valid, errors = validate_raw_dataframe(df)
            if not is_valid:
                error_msg = f"Schema validation failed: {'; '.join(errors)}"
                self.batch_manager.fail_batch(batch.batch_id, error_msg)
                return IngestionResult(
                    batch_id=batch.batch_id,
                    status=BatchStatus.FAILED,
                    total_records=total_records,
                    bronze_records=0,
                    quarantined_records=0,
                    error_message=error_msg,
                )

            # Normalize column data types for raw Bronze auditability
            # InvoiceNo contains both integers (e.g. 536365) and cancellations (e.g. C536379)
            df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
            df["StockCode"] = df["StockCode"].astype(str).str.strip()
            if "Description" in df.columns:
                df["Description"] = df["Description"].astype(str)
            if "CustomerID" in df.columns:
                # Keep as nullable string format: remove trailing .0 if present
                df["CustomerID"] = df["CustomerID"].apply(
                    lambda x: "" if pd.isna(x) else str(int(x)) if isinstance(x, (int, float)) and not pd.isna(x) and x == int(x) else str(x)
                )
            if "Country" in df.columns:
                df["Country"] = df["Country"].astype(str).str.strip()

            # Enrich with Bronze audit columns
            ingestion_time = datetime.now(UTC).isoformat()
            df["_batch_id"] = batch.batch_id
            df["_source_file"] = source_path.name
            df["_ingestion_timestamp"] = ingestion_time

            # Compute row hash identifier for each record
            df["_ingestion_id"] = [
                compute_row_hash(
                    row.InvoiceNo,
                    row.StockCode,
                    row.InvoiceDate,
                    row.Quantity,
                    row.UnitPrice,
                    idx,
                )
                for idx, row in enumerate(df.itertuples(index=False))
            ]

            # Reorder columns to place audit columns cleanly
            audit_cols = ["_ingestion_id", "_batch_id", "_source_file", "_ingestion_timestamp"]
            data_cols = [c for c in df.columns if c not in audit_cols]
            df = df[audit_cols + data_cols]

            # Save immutable Bronze Parquet representation
            parquet_filename = f"bronze_{batch.batch_id}.parquet"
            parquet_path = self.bronze_dir / parquet_filename

            # Convert to PyArrow Table and write with Snappy compression
            table = pa.Table.from_pandas(df)
            pq.write_table(
                table,
                parquet_path,
                compression=settings.ingestion.compression,
            )

            # Also maintain or symlink a standard bronze_transactions_raw.parquet
            standard_bronze_path = self.bronze_dir / "bronze_transactions_raw.parquet"
            pq.write_table(table, standard_bronze_path, compression=settings.ingestion.compression)

            output_files = [str(parquet_path), str(standard_bronze_path)]
            duration = (datetime.now(UTC) - start_time).total_seconds()

            self.batch_manager.complete_batch(
                batch_id=batch.batch_id,
                total_records=total_records,
                bronze_records=total_records,
                output_files=output_files,
                quarantined_records=0,
                metadata={"execution_time_seconds": duration},
            )

            print(f"[+] Bronze layer ingestion succeeded: {total_records:,} records written to {parquet_path}")

            return IngestionResult(
                batch_id=batch.batch_id,
                status=BatchStatus.COMPLETED,
                total_records=total_records,
                bronze_records=total_records,
                quarantined_records=0,
                output_files=output_files,
                execution_time_seconds=duration,
                metadata={"file_sha256": file_hash},
            )

        except Exception as e:
            self.batch_manager.fail_batch(batch.batch_id, str(e))
            raise
