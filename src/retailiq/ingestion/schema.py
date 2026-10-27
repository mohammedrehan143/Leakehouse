"""Schema definitions and row validation for raw Bronze ingestion."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


EXPECTED_RAW_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


class RawTransactionRecord(BaseModel):
    """Pydantic model representing an uncleaned raw transaction record."""

    model_config = ConfigDict(extra="ignore")

    invoice_no: str = Field(..., description="Invoice number")
    stock_code: str = Field(..., description="Product stock code")
    description: str | None = Field(default=None, description="Product description")
    quantity: int = Field(..., description="Quantity ordered or cancelled")
    invoice_date: datetime = Field(..., description="Date and time of invoice")
    unit_price: float = Field(..., description="Unit price in GBP")
    customer_id: str | None = Field(default=None, description="Customer ID")
    country: str = Field(..., description="Country of customer")


def compute_row_hash(
    invoice_no: Any,
    stock_code: Any,
    invoice_date: Any,
    quantity: Any,
    unit_price: Any,
    row_idx: int,
) -> str:
    """Compute a deterministic SHA-256 hash representing a unique raw record ingestion key."""
    raw_str = f"{invoice_no}|{stock_code}|{invoice_date}|{quantity}|{unit_price}|{row_idx}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def validate_raw_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate that the incoming DataFrame possesses all required source columns."""
    missing = [col for col in EXPECTED_RAW_COLUMNS if col not in df.columns]
    if missing:
        return False, [f"Missing expected columns: {missing}"]
    return True, []
