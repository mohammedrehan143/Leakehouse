"""RetailIQ Central Configuration Manager.

Loads configuration from YAML and environment variables, validates directory paths,
and provides strongly typed configuration settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectConfig(BaseModel):
    name: str = "RetailIQ"
    version: str = "0.1.0"
    description: str = "AI-Powered E-commerce Data Lakehouse & Multi-Agent Engineering Platform"


class StorageConfig(BaseModel):
    data_dir: Path = Path("data")
    raw_dir: Path = Path("data/raw")
    bronze_parquet_dir: Path = Path("data/raw/bronze")
    processed_dir: Path = Path("data/processed")
    silver_dir: Path = Path("data/processed/silver")
    quarantine_dir: Path = Path("data/quarantine")
    batch_metadata_file: Path = Path("data/processed/batches.json")


class DatasetConfig(BaseModel):
    source_name: str = "UCI Online Retail Dataset"
    download_url: str = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
    archive_inner_file: str = "Online Retail.xlsx"
    raw_file_path: Path = Path("data/raw/Online Retail.xlsx")
    expected_columns: list[str] = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
    ]


class IngestionConfig(BaseModel):
    batch_size: int = 50000
    enable_parquet_preservation: bool = True
    compression: str = "snappy"


class Settings(BaseSettings):
    """Global system settings combining environment variables and YAML configurations."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)

    # Database
    database_url: str = "sqlite:///data/processed/retailiq_dev.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "retailiq_db"
    postgres_user: str = "retailiq"
    postgres_password: str = "retailiq_secret"

    # Logging
    log_level: str = "INFO"

    # AI Agent Configuration
    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-120b"
    llm_api_key: str | None = None
    agent_max_retries: int = 3
    agent_timeout_seconds: int = 60

    # API & Dashboard
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    dashboard_port: int = 8501

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> Settings:
        """Load settings from optional YAML configuration file with env overrides."""
        cfg_file = Path(config_path or "configs/settings.yaml")
        yaml_data: dict[str, Any] = {}

        if cfg_file.exists():
            with cfg_file.open("r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}

        # Allow environment variable overrides
        env_data = {}
        if "DATABASE_URL" in os.environ:
            env_data["database_url"] = os.environ["DATABASE_URL"]
        if "DATASET_PATH" in os.environ:
            yaml_data.setdefault("dataset", {})["raw_file_path"] = Path(os.environ["DATASET_PATH"])
        if "LOG_LEVEL" in os.environ:
            env_data["log_level"] = os.environ["LOG_LEVEL"]

        combined = {**yaml_data, **env_data}
        settings = cls(**combined)

        # Ensure essential storage directories exist
        settings.storage.raw_dir.mkdir(parents=True, exist_ok=True)
        settings.storage.bronze_parquet_dir.mkdir(parents=True, exist_ok=True)
        settings.storage.processed_dir.mkdir(parents=True, exist_ok=True)
        settings.storage.silver_dir.mkdir(parents=True, exist_ok=True)
        settings.storage.quarantine_dir.mkdir(parents=True, exist_ok=True)

        return settings


# Default global settings singleton instance
settings = Settings.load()
