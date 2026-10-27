"""End-to-End RetailIQ Lakehouse Pipeline Runner."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from retailiq.analytics.gold_builder import GoldLayerBuilder
from retailiq.config import settings
from retailiq.database.connection import get_session, init_db
from retailiq.database.models import PipelineRunRecord
from retailiq.database.repositories import LakehouseRepository
from retailiq.ingestion.download import download_dataset
from retailiq.ingestion.loader import BronzeLoader
from retailiq.pipeline.quality import DataQualityChecker, QualityCheckResult
from retailiq.transformations.cleaning import SilverCleaner


@dataclass
class PipelineSummary:
    """Consolidated summary of end-to-end pipeline execution."""

    run_id: str
    status: str
    started_at: str
    completed_at: str
    duration_seconds: float
    bronze_records: int
    silver_records: int
    quarantined_records: int
    gold_sales_count: int
    quality_checks_passed: int
    quality_checks_failed: int
    output_files: list[str] = field(default_factory=list)
    quality_details: list[dict[str, Any]] = field(default_factory=list)


class PipelineRunner:
    """Executes the complete Bronze -> Silver -> Gold lakehouse pipeline deterministically."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(settings.storage.data_dir)
        self.runs_log = self.data_dir / "processed" / "pipeline_runs.json"
        self.runs_log.parent.mkdir(parents=True, exist_ok=True)

    def run_all(
        self,
        source_path: Path | None = None,
        limit: int | None = None,
        force_ingest: bool = False,
    ) -> PipelineSummary:
        """Run complete lakehouse pipeline from raw ingestion to Gold marts and QA."""
        start_time = datetime.now(UTC)
        run_id = f"RUN_{start_time.strftime('%Y%m%d_%H%M%S')}"
        output_files: list[str] = []

        print(f"==================================================")
        print(f"[*] RetailIQ Lakehouse Pipeline Execution: {run_id}")
        print(f"==================================================")

        # Step 1: Ensure dataset exists or download
        src = source_path or settings.dataset.raw_file_path
        if not src.exists():
            print(f"[*] Downloading source dataset...")
            download_dataset(target_path=src)

        # Step 2: Bronze Ingestion
        print(f"[*] Step 1/4: Ingesting into Bronze Parquet layer...")
        loader = BronzeLoader()
        ingest_res = loader.load_dataset(file_path=src, force_reingest=force_ingest, nrows=limit)
        output_files.extend(ingest_res.output_files)

        # Read bronze output
        bronze_parquet = settings.storage.bronze_parquet_dir / "bronze_transactions_raw.parquet"
        import pyarrow.parquet as pq

        bronze_df = pq.read_table(bronze_parquet).to_pandas()
        if limit and len(bronze_df) > limit:
            bronze_df = bronze_df.head(limit)

        # Step 3: Silver Cleaning & Quarantine
        print(f"[*] Step 2/4: Cleaning & routing invalid records to quarantine...")
        cleaner = SilverCleaner()
        valid_df, quarantine_df, clean_summary = cleaner.clean_dataframe(bronze_df, batch_id=run_id)
        output_files.append(clean_summary.silver_output_file)
        if clean_summary.quarantine_output_file:
            output_files.append(clean_summary.quarantine_output_file)

        # Persist to database
        init_db()
        repo = LakehouseRepository()
        repo.load_silver_dataframe(valid_df)
        if not quarantine_df.empty:
            repo.load_quarantine_dataframe(quarantine_df)

        # Step 4: Gold Analytics Layer
        print(f"[*] Step 3/4: Building Gold dimensions, facts, and analytical marts...")
        gold_builder = GoldLayerBuilder()
        gold_summary = gold_builder.build_gold_layer(valid_df, persist_to_db=True)
        output_files.extend(gold_summary.output_files)

        # Step 5: Data Quality Verification
        print(f"[*] Step 4/4: Executing automated data quality checks...")
        checker = DataQualityChecker()
        quality_results = checker.run_all_checks(valid_df, quarantine_df, persist_to_db=True)

        passed_checks = sum(1 for q in quality_results if q.status == "PASS")
        failed_checks = sum(1 for q in quality_results if q.status == "FAIL")

        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()
        status = "SUCCESS" if failed_checks == 0 else "COMPLETED_WITH_WARNINGS"

        summary = PipelineSummary(
            run_id=run_id,
            status=status,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            duration_seconds=duration,
            bronze_records=len(bronze_df),
            silver_records=len(valid_df),
            quarantined_records=len(quarantine_df),
            gold_sales_count=gold_summary.fact_sales_count,
            quality_checks_passed=passed_checks,
            quality_checks_failed=failed_checks,
            output_files=output_files,
            quality_details=[q.__dict__ for q in quality_results],
        )

        # Persist pipeline run record
        self._record_pipeline_run(summary)

        print(f"==================================================")
        print(f"[+] Pipeline {run_id} completed successfully in {duration:.2f}s!")
        print(f"    - Bronze records:     {summary.bronze_records:,}")
        print(f"    - Clean Silver:       {summary.silver_records:,}")
        print(f"    - Quarantined:        {summary.quarantined_records:,}")
        print(f"    - Gold Sales Facts:   {summary.gold_sales_count:,}")
        print(f"    - QA Checks:          {passed_checks} Passed, {failed_checks} Failed")
        print(f"==================================================")
        return summary

    def _record_pipeline_run(self, summary: PipelineSummary) -> None:
        """Record run in database and json log."""
        try:
            with get_session() as session:
                record = PipelineRunRecord(
                    run_id=summary.run_id,
                    pipeline_name="retailiq_lakehouse_end_to_end",
                    status=summary.status,
                    started_at=datetime.fromisoformat(summary.started_at),
                    completed_at=datetime.fromisoformat(summary.completed_at),
                    duration_seconds=summary.duration_seconds,
                    summary_json=json.dumps(summary.__dict__, default=str),
                )
                session.add(record)
        except Exception:
            pass

        # Also write to local runs log
        try:
            runs_data = []
            if self.runs_log.exists():
                runs_data = json.loads(self.runs_log.read_text(encoding="utf-8"))
            runs_data.append(summary.__dict__)
            self.runs_log.write_text(json.dumps(runs_data, indent=2, default=str), encoding="utf-8")
        except Exception:
            pass
