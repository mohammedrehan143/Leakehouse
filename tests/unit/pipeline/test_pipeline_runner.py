"""Unit tests for end-to-end PipelineRunner."""

import os
from pathlib import Path
from retailiq.pipeline.runner import PipelineRunner
from tests.fixtures.sample_dataset import write_sample_excel


def test_pipeline_runner_end_to_end(tmp_path: Path):
    excel_path = write_sample_excel(tmp_path / "raw.xlsx")
    db_path = tmp_path / "pipeline_test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    runner = PipelineRunner(data_dir=tmp_path)
    summary = runner.run_all(source_path=excel_path, force_ingest=True)

    assert summary.status == "SUCCESS"
    assert summary.bronze_records == 5
    assert summary.silver_records == 5
    assert summary.gold_sales_count == 4
    assert summary.quality_checks_passed == 5
    assert summary.quality_checks_failed == 0
