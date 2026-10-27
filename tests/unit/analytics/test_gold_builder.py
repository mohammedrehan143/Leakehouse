"""Unit tests for Gold Layer facts, dimensions, and analytical marts."""

from pathlib import Path
import pyarrow.parquet as pq
from retailiq.analytics.gold_builder import GoldLayerBuilder
from retailiq.transformations.cleaning import SilverCleaner
from tests.fixtures.sample_dataset import create_sample_dataframe


def test_gold_layer_build(tmp_path: Path):
    cleaner = SilverCleaner(silver_dir=tmp_path / "silver")
    df = create_sample_dataframe()
    valid_df, _, _ = cleaner.clean_dataframe(df, batch_id="GOLD_TEST")

    gold_dir = tmp_path / "gold"
    builder = GoldLayerBuilder(gold_dir=gold_dir)
    summary = builder.build_gold_layer(valid_df, persist_to_db=False)

    # In our fixture: 4 sales, 1 cancellation
    assert summary.fact_sales_count == 4
    assert summary.fact_returns_count == 1
    assert summary.dim_customers_count == 3  # 17850, 12583, and 14527 (guest_checkout excluded from dim_customer)
    assert summary.mart_daily_rows > 0

    # Verify Parquet outputs
    sales_file = gold_dir / "fct_sales.parquet"
    assert sales_file.exists()
    sales_tbl = pq.read_table(sales_file)
    assert sales_tbl.num_rows == 4
    assert "gross_revenue" in sales_tbl.column_names

    returns_file = gold_dir / "fct_returns.parquet"
    assert returns_file.exists()
    returns_tbl = pq.read_table(returns_file)
    assert returns_tbl.num_rows == 1
    assert "return_amount" in returns_tbl.column_names
