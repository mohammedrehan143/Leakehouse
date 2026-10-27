"""Unit tests for QuarantineManager."""

from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
from retailiq.transformations.quarantine import QuarantineManager


def test_quarantine_save(tmp_path: Path):
    manager = QuarantineManager(quarantine_dir=tmp_path / "quarantine")
    q_df = pd.DataFrame([
        {
            "invoice_no": "536399",
            "stock_code": "TEST",
            "rejection_reason": "INVALID_UNIT_PRICE",
            "quantity": 1,
            "unit_price": -5.0,
        }
    ])

    path = manager.save_quarantined_dataframe("BATCH_TEST_Q", q_df)
    assert path is not None
    assert path.exists()

    table = pq.read_table(path)
    assert table.num_rows == 1
    assert "rejection_reason" in table.column_names
