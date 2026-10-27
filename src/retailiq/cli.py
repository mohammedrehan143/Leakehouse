"""RetailIQ Command Line Interface.

Provides CLI execution of the data lakehouse pipeline.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from retailiq.config import settings
from retailiq.ingestion.batch_manager import BatchManager
from retailiq.ingestion.download import download_dataset
from retailiq.ingestion.loader import BronzeLoader


def cmd_download(args: argparse.Namespace) -> None:
    """Download the UCI Online Retail dataset."""
    print("=== RetailIQ Dataset Acquisition ===")
    target = Path(args.target) if args.target else settings.dataset.raw_file_path
    path = download_dataset(target_path=target, force=args.force)
    print(f"Dataset ready at: {path}")


def cmd_ingest(args: argparse.Namespace) -> None:
    """Ingest raw data into the Bronze Lakehouse layer."""
    print("=== RetailIQ Bronze Lakehouse Ingestion ===")
    source = Path(args.source) if args.source else settings.dataset.raw_file_path

    if not source.exists():
        print(f"Source file not found at {source}. Attempting automatic download...")
        download_dataset(target_path=source)

    loader = BronzeLoader()
    result = loader.load_dataset(
        file_path=source,
        force_reingest=args.force,
        nrows=args.limit,
    )
    print(f"Batch ID: {result.batch_id}")
    print(f"Status: {result.status}")
    print(f"Total Records: {result.total_records:,}")
    print(f"Bronze Records: {result.bronze_records:,}")
    print(f"Execution Time: {result.execution_time_seconds:.2f}s")
    for out in result.output_files:
        print(f"  - Output: {out}")


def cmd_transform(args: argparse.Namespace) -> None:
    """Clean Bronze records and produce Silver Lakehouse layer."""
    print("=== RetailIQ Silver Layer Transformation ===")
    import pyarrow.parquet as pq
    from retailiq.database.connection import init_db
    from retailiq.database.repositories import LakehouseRepository
    from retailiq.transformations.cleaning import SilverCleaner

    bronze_file = settings.storage.bronze_parquet_dir / "bronze_transactions_raw.parquet"
    if not bronze_file.exists():
        print("Bronze parquet file not found. Running ingestion first...")
        loader = BronzeLoader()
        loader.load_dataset(nrows=args.limit)

    table = pq.read_table(bronze_file)
    bronze_df = table.to_pandas()
    if args.limit:
        bronze_df = bronze_df.head(args.limit)

    cleaner = SilverCleaner()
    valid_df, quarantine_df, summary = cleaner.clean_dataframe(bronze_df, batch_id="BATCH_SILVER_TRANSFORM")

    print(f"Total Bronze Records: {summary.total_bronze_records:,}")
    print(f"Valid Silver Records: {summary.valid_silver_records:,}")
    print(f"Quarantined Records:  {summary.quarantined_records:,}")
    print(f"Cancellations:        {summary.cancellations_count:,}")
    print(f"Guest Checkouts:      {summary.guest_checkouts_count:,}")
    print(f"Silver Parquet:       {summary.silver_output_file}")

    if args.load_db:
        print("[*] Initializing database and persisting Silver records...")
        init_db()
        repo = LakehouseRepository()
        inserted = repo.load_silver_dataframe(valid_df)
        if not quarantine_df.empty:
            repo.load_quarantine_dataframe(quarantine_df)
        stats = repo.get_silver_stats()
        print(f"[+] Loaded {inserted:,} records into database. Current stats: {stats}")


def cmd_status(args: argparse.Namespace) -> None:
    """Display lakehouse batch and ingestion history."""
    print("=== RetailIQ Ingestion Status ===")
    manager = BatchManager()
    if not manager.batches:
        print("No ingestion batches found.")
        return

    print(f"Total Batches Recorded: {len(manager.batches)}")
    for batch in manager.batches.values():
        print(f"[{batch.status}] {batch.batch_id} | Records: {batch.bronze_records:,} | File: {Path(batch.source_file).name}")
        if batch.completed_at:
            print(f"    Completed: {batch.completed_at}")
        if batch.error_message:
            print(f"    Error: {batch.error_message}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RetailIQ CLI: E-commerce Data Lakehouse & Pipeline Engine"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # download
    p_dl = subparsers.add_parser("download", help="Download raw UCI Online Retail dataset")
    p_dl.add_argument("--target", type=str, default=None, help="Target download path")
    p_dl.add_argument("--force", action="store_true", help="Force re-download even if file exists")
    p_dl.set_defaults(func=cmd_download)

    # ingest
    p_ing = subparsers.add_parser("ingest", help="Ingest raw records into Bronze Parquet layer")
    p_ing.add_argument("--source", type=str, default=None, help="Source Excel or CSV path")
    p_ing.add_argument("--limit", type=int, default=None, help="Optional row limit for quick testing")
    p_ing.add_argument("--force", action="store_true", help="Force re-ingestion ignoring checksums")
    p_ing.set_defaults(func=cmd_ingest)

    # transform
    p_tf = subparsers.add_parser("transform", help="Clean Bronze records and produce Silver Lakehouse layer")
    p_tf.add_argument("--limit", type=int, default=None, help="Optional row limit for testing")
    p_tf.add_argument("--load-db", action="store_true", help="Persist cleaned Silver records to relational database")
    p_tf.set_defaults(func=cmd_transform)

    # status
    p_stat = subparsers.add_parser("status", help="Inspect ingestion batches and status")
    p_stat.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
