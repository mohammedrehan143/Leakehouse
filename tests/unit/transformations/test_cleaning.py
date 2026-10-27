"""Unit tests for Silver cleaning rules, cancellations, and guest checkouts."""

from datetime import datetime
import pandas as pd
from retailiq.transformations.cleaning import SilverCleaner
from tests.fixtures.sample_dataset import create_sample_dataframe


def test_clean_dataframe_logic(tmp_path):
    cleaner = SilverCleaner(silver_dir=tmp_path / "silver")
    df = create_sample_dataframe()

    valid_df, quarantine_df, summary = cleaner.clean_dataframe(df, batch_id="TEST_B01")

    # In our fixture:
    # 4 normal purchases + 1 cancellation = 5 valid records
    assert summary.total_bronze_records == 5
    assert summary.valid_silver_records == 5
    assert summary.quarantined_records == 0
    assert summary.cancellations_count == 1  # C536379 has negative quantity and 'C' prefix
    assert summary.guest_checkouts_count == 1  # 536366 had NaN CustomerID

    # Verify line_total calculation
    first_row = valid_df[valid_df["invoice_no"] == "536365"].iloc[0]
    expected_total = round(6 * 2.55, 4)
    assert first_row["line_total"] == expected_total


def test_clean_dataframe_quarantine_bad_prices(tmp_path):
    cleaner = SilverCleaner(silver_dir=tmp_path / "silver")
    df = create_sample_dataframe()

    # Add invalid row with UnitPrice = 0.0
    bad_row = pd.DataFrame([{
        "InvoiceNo": "536399",
        "StockCode": "TEST99",
        "Description": "Damaged stock",
        "Quantity": 1,
        "InvoiceDate": datetime(2010, 12, 1, 10, 0),
        "UnitPrice": 0.0,
        "CustomerID": 12345.0,
        "Country": "United Kingdom",
    }])
    df = pd.concat([df, bad_row], ignore_index=True)

    valid_df, quarantine_df, summary = cleaner.clean_dataframe(df, batch_id="TEST_B02")

    assert summary.total_bronze_records == 6
    assert summary.valid_silver_records == 5
    assert summary.quarantined_records == 1
    assert "INVALID_UNIT_PRICE_NON_POSITIVE" in summary.quarantine_breakdown
