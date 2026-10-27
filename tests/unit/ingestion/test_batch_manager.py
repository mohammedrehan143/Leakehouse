"""Unit tests for BatchManager lifecycle and idempotency."""

from pathlib import Path
from retailiq.ingestion.batch_manager import BatchManager, BatchStatus
from tests.fixtures.sample_dataset import write_sample_excel


def test_batch_lifecycle(tmp_path: Path):
    excel_path = write_sample_excel(tmp_path / "test_data.xlsx")
    meta_path = tmp_path / "batches.json"

    manager = BatchManager(metadata_path=meta_path)
    batch = manager.start_batch(excel_path)

    assert batch.status == BatchStatus.STARTED
    assert batch.batch_id.startswith("BATCH_")
    assert batch.file_sha256 != ""

    # Complete batch
    completed = manager.complete_batch(
        batch_id=batch.batch_id,
        total_records=5,
        bronze_records=5,
        output_files=["data/raw/bronze/test.parquet"],
    )
    assert completed.status == BatchStatus.COMPLETED
    assert completed.total_records == 5
    assert completed.completed_at is not None

    # Verify reloading from disk
    new_manager = BatchManager(metadata_path=meta_path)
    found = new_manager.find_completed_batch_by_hash(batch.file_sha256)
    assert found is not None
    assert found.batch_id == batch.batch_id


def test_batch_failure(tmp_path: Path):
    excel_path = write_sample_excel(tmp_path / "test_data.xlsx")
    meta_path = tmp_path / "batches.json"

    manager = BatchManager(metadata_path=meta_path)
    batch = manager.start_batch(excel_path)

    failed = manager.fail_batch(batch.batch_id, "Corrupted schema error")
    assert failed.status == BatchStatus.FAILED
    assert failed.error_message == "Corrupted schema error"
