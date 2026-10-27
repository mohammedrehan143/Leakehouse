"""RetailIQ Ingestion Package."""

from retailiq.ingestion.batch_manager import BatchManager, BatchRecord, BatchStatus
from retailiq.ingestion.download import download_dataset
from retailiq.ingestion.loader import BronzeLoader, IngestionResult
from retailiq.ingestion.schema import RawTransactionRecord, validate_raw_dataframe

__all__ = [
    "BatchManager",
    "BatchRecord",
    "BatchStatus",
    "BronzeLoader",
    "IngestionResult",
    "RawTransactionRecord",
    "download_dataset",
    "validate_raw_dataframe",
]
