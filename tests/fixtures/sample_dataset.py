"""Deterministic test fixtures for RetailIQ ingestion tests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import pandas as pd


def create_sample_dataframe() -> pd.DataFrame:
    """Create a realistic sample DataFrame reflecting the UCI Online Retail schema."""
    data = [
        # Normal purchase 1 (2 items on same invoice 536365)
        {
            "InvoiceNo": "536365",
            "StockCode": "85123A",
            "Description": "WHITE HANGING HEART T-LIGHT HOLDER",
            "Quantity": 6,
            "InvoiceDate": datetime(2010, 12, 1, 8, 26, 0),
            "UnitPrice": 2.55,
            "CustomerID": 17850.0,
            "Country": "United Kingdom",
        },
        {
            "InvoiceNo": "536365",
            "StockCode": "71053",
            "Description": "WHITE METAL LANTERN",
            "Quantity": 6,
            "InvoiceDate": datetime(2010, 12, 1, 8, 26, 0),
            "UnitPrice": 3.39,
            "CustomerID": 17850.0,
            "Country": "United Kingdom",
        },
        # Guest checkout (missing CustomerID)
        {
            "InvoiceNo": "536366",
            "StockCode": "22633",
            "Description": "HAND WARMER UNION JACK",
            "Quantity": 12,
            "InvoiceDate": datetime(2010, 12, 1, 8, 28, 0),
            "UnitPrice": 1.85,
            "CustomerID": float("nan"),
            "Country": "United Kingdom",
        },
        # International purchase
        {
            "InvoiceNo": "536370",
            "StockCode": "22728",
            "Description": "ALARM CLOCK BAKELIKE PINK",
            "Quantity": 24,
            "InvoiceDate": datetime(2010, 12, 1, 8, 45, 0),
            "UnitPrice": 3.75,
            "CustomerID": 12583.0,
            "Country": "France",
        },
        # Cancellation record (Invoice starts with 'C', negative quantity)
        {
            "InvoiceNo": "C536379",
            "StockCode": "D",
            "Description": "Discount",
            "Quantity": -1,
            "InvoiceDate": datetime(2010, 12, 1, 9, 41, 0),
            "UnitPrice": 27.50,
            "CustomerID": 14527.0,
            "Country": "United Kingdom",
        },
    ]
    return pd.DataFrame(data)


def write_sample_excel(file_path: Path) -> Path:
    """Write sample dataframe to Excel format."""
    df = create_sample_dataframe()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(file_path, index=False)
    return file_path
