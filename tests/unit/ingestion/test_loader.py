"""Unit tests for BronzeLoader ingestion engine."""

from pathlib import Path
import pyarrow.parquet as pq
from retailiq.ingestion.batch_manager import BatchManager, BatchStatus
from retailiq.ingestion.loader import BronzeLoader
from tests.fixtures.sample_dataset import write_sample_excel


def test_bronze_loader_execution(tmp_path: Path):
    excel_path = write_sample_excel(tmp_path / "raw.xlsx")
    meta_path = tmp_path / "batches.json"
    bronze_dir = tmp_path / "bronze"

    manager = BatchManager(metadata_path=meta_path)
    loader = BronzeLoader(batch_manager=manager, bronze_dir=bronze_dir)

    result = loader.load_dataset(file_path=excel_path)

    assert result.status == BatchStatus.COMPLETED
    assert result.total_records == 5
    assert result.bronze_records == 5
    assert len(result.output_files) == 2

    # Verify Parquet file contents and schema
    parquet_path = Path(result.output_files[0])
    assert parquet_path.exists()

    table = pq.read_table(parquet_path)
    assert table.num_rows == 5

    # Check Bronze audit columns
    columns = table.column_names
    assert "_ingestion_id" in columns
    assert "_batch_id" in columns
    assert "_source_file" in columns
    assert "_ingestion_timestamp" in columns
    assert "InvoiceNo" in columns
    assert "StockCode" in columns


def test_bronze_loader_idempotency(tmp_path: Path):
    excel_path = write_sample_excel(tmp_path / "raw.xlsx")
    meta_path = tmp_path / "batches.json"
    bronze_dir = tmp_path / "bronze"

    manager = BatchManager(metadata_path=meta_path)
    loader = BronzeLoader(batch_manager=manager, bronze_dir=bronze_dir)

    # First ingestion
    res1 = loader.load_dataset(file_path=excel_path)
    assert res1.status == BatchStatus.COMPLETED

    # Second ingestion without force should skip idempotently
    res2 = loader.load_dataset(file_path=excel_path, force_reingest=False)
    assert res2.status == "SKIPPED_ALREADY_INGESTED"
    assert res2.batch_id == res1.batch_id
