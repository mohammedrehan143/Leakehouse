"""Unit tests for schema validation and row hashing."""

from datetime import datetime
import pandas as pd
from retailiq.ingestion.schema import compute_row_hash, validate_raw_dataframe
from tests.fixtures.sample_dataset import create_sample_dataframe


def test_compute_row_hash_deterministic():
    h1 = compute_row_hash("536365", "85123A", datetime(2010, 12, 1, 8, 26), 6, 2.55, 0)
    h2 = compute_row_hash("536365", "85123A", datetime(2010, 12, 1, 8, 26), 6, 2.55, 0)
    assert h1 == h2
    assert len(h1) == 16


def test_compute_row_hash_distinguishes_index():
    h1 = compute_row_hash("536365", "85123A", datetime(2010, 12, 1, 8, 26), 6, 2.55, 0)
    h2 = compute_row_hash("536365", "85123A", datetime(2010, 12, 1, 8, 26), 6, 2.55, 1)
    assert h1 != h2


def test_validate_raw_dataframe_success():
    df = create_sample_dataframe()
    is_valid, errors = validate_raw_dataframe(df)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_raw_dataframe_missing_column():
    df = create_sample_dataframe().drop(columns=["StockCode"])
    is_valid, errors = validate_raw_dataframe(df)
    assert is_valid is False
    assert any("StockCode" in err for err in errors)
