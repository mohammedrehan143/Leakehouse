"""Batch lifecycle and ingestion metadata manager."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from retailiq.config import settings


class BatchStatus(StrEnum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchRecord(BaseModel):
    """Metadata record for an ingestion batch execution."""

    batch_id: str
    source_file: str
    file_sha256: str
    total_records: int = 0
    bronze_records: int = 0
    quarantined_records: int = 0
    status: BatchStatus = BatchStatus.STARTED
    started_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    output_files: list[str] = Field(default_factory=list)
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchManager:
    """Manages persistent batch metadata and execution history."""

    def __init__(self, metadata_path: Path | None = None) -> None:
        self.metadata_path = metadata_path or settings.storage.batch_metadata_file
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self.batches: dict[str, BatchRecord] = {}
        self._load()

    def _load(self) -> None:
        if self.metadata_path.exists():
            try:
                data = json.loads(self.metadata_path.read_text(encoding="utf-8"))
                for b_id, b_data in data.items():
                    self.batches[b_id] = BatchRecord(**b_data)
            except Exception:
                self.batches = {}

    def _save(self) -> None:
        serialized = {k: v.model_dump() for k, v in self.batches.items()}
        self.metadata_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA-256 checksum of source file for audit and idempotency."""
        sha = hashlib.sha256()
        with file_path.open("rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def start_batch(self, source_file: Path) -> BatchRecord:
        """Create and register a new ingestion batch."""
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        batch_id = f"BATCH_{timestamp_str}"
        file_hash = self.calculate_file_hash(source_file)

        record = BatchRecord(
            batch_id=batch_id,
            source_file=str(source_file),
            file_sha256=file_hash,
            status=BatchStatus.STARTED,
        )
        self.batches[batch_id] = record
        self._save()
        return record

    def complete_batch(
        self,
        batch_id: str,
        total_records: int,
        bronze_records: int,
        output_files: list[str],
        quarantined_records: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> BatchRecord:
        """Mark an ingestion batch as successfully completed."""
        record = self.batches.get(batch_id)
        if not record:
            raise KeyError(f"Batch '{batch_id}' not found.")

        record.total_records = total_records
        record.bronze_records = bronze_records
        record.quarantined_records = quarantined_records
        record.output_files = output_files
        record.status = BatchStatus.COMPLETED
        record.completed_at = datetime.now(UTC).isoformat()
        if metadata:
            record.metadata.update(metadata)
        self._save()
        return record

    def fail_batch(self, batch_id: str, error_message: str) -> BatchRecord:
        """Mark an ingestion batch as failed with error details."""
        record = self.batches.get(batch_id)
        if not record:
            raise KeyError(f"Batch '{batch_id}' not found.")

        record.status = BatchStatus.FAILED
        record.error_message = error_message
        record.completed_at = datetime.now(UTC).isoformat()
        self._save()
        return record

    def find_completed_batch_by_hash(self, file_hash: str) -> BatchRecord | None:
        """Check if an identical file checksum has already been ingested successfully."""
        for batch in self.batches.values():
            if batch.file_sha256 == file_hash and batch.status == BatchStatus.COMPLETED:
                return batch
        return None
