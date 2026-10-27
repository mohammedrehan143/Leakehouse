"""Unit tests for deterministic DataQualityChecker."""

from retailiq.pipeline.quality import DataQualityChecker
from retailiq.transformations.cleaning import SilverCleaner
from tests.fixtures.sample_dataset import create_sample_dataframe


def test_quality_checker_pass(tmp_path):
    cleaner = SilverCleaner(silver_dir=tmp_path / "silver")
    df = create_sample_dataframe()
    valid_df, quarantine_df, _ = cleaner.clean_dataframe(df, batch_id="QA_TEST")

    checker = DataQualityChecker()
    results = checker.run_all_checks(valid_df, quarantine_df, persist_to_db=False)

    assert len(results) == 5
    # All checks should pass
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) == 0

    # Specific check names
    check_names = [r.check_name for r in results]
    assert "missing_invoice_numbers" in check_names
    assert "non_positive_unit_prices" in check_names
    assert "cancellation_classification_integrity" in check_names
