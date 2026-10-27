"""Quarantine manager for invalid or malformed retail records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from retailiq.config import settings


@dataclass
class QuarantinedRecord:
    batch_id: str
    row_idx: int
    rejection_reason: str
    raw_payload: dict[str, Any]
    quarantined_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class QuarantineManager:
    """Manages rejected records, ensuring full auditability and preventing silent data loss."""

    def __init__(self, quarantine_dir: Path | None = None) -> None:
        self.quarantine_dir = quarantine_dir or settings.storage.quarantine_dir
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def save_quarantined_dataframe(
        self,
        batch_id: str,
        quarantine_df: pd.DataFrame,
    ) -> Path | None:
        """Persist rejected records into an immutable quarantine Parquet file."""
        if quarantine_df.empty:
            return None

        out_path = self.quarantine_dir / f"quarantine_{batch_id}.parquet"
        table = pa.Table.from_pandas(quarantine_df)
        pq.write_table(table, out_path, compression="snappy")
        return out_path
