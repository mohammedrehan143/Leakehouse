"""Unit tests for configuration manager."""

from pathlib import Path
from retailiq.config import Settings


def test_settings_load_defaults():
    settings = Settings.load()
    assert settings.project.name == "RetailIQ"
    assert settings.ingestion.batch_size > 0
    assert "InvoiceNo" in settings.dataset.expected_columns
    assert "StockCode" in settings.dataset.expected_columns


def test_settings_storage_directories_exist():
    settings = Settings.load()
    assert settings.storage.raw_dir.exists()
    assert settings.storage.bronze_parquet_dir.exists()
    assert settings.storage.processed_dir.exists()
