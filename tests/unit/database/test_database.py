"""Unit tests for database connection and repository persistence."""

import os
from pathlib import Path
from retailiq.database.connection import get_engine, init_db, reset_engine
from retailiq.database.repositories import LakehouseRepository
from retailiq.transformations.cleaning import SilverCleaner
from tests.fixtures.sample_dataset import create_sample_dataframe


def test_database_init_and_repository(tmp_path: Path):
    db_file = tmp_path / "test_retailiq.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    reset_engine()

    # Initialize tables
    init_db()
    assert db_file.exists()

    # Clean sample records
    cleaner = SilverCleaner(silver_dir=tmp_path / "silver")
    df = create_sample_dataframe()
    valid_df, _, _ = cleaner.clean_dataframe(df, batch_id="DB_TEST_BATCH")

    repo = LakehouseRepository()
    inserted = repo.load_silver_dataframe(valid_df)
    assert inserted == 5

    stats = repo.get_silver_stats()
    assert stats["total_records"] == 5
    assert stats["cancellations_count"] == 1
    assert stats["gross_revenue"] > 0
