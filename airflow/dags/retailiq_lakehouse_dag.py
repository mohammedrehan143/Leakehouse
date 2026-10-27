"""RetailIQ Production Lakehouse Airflow DAG.

Orchestrates:
1. validate_configuration
2. download_or_locate_dataset
3. ingest_raw_data (Bronze Parquet)
4. clean_and_validate_data (Silver Cleaning & Quarantine)
5. build_gold_marts (Dimensional models & Fact tables)
6. run_quality_checks (Data Quality invariants)
7. publish_pipeline_summary
"""

from __future__ import annotations

from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False


def task_validate_config():
    from retailiq.config import settings
    print(f"Validated configuration for project: {settings.project.name}")
    return True


def task_ingest_bronze():
    from retailiq.ingestion.loader import BronzeLoader
    loader = BronzeLoader()
    res = loader.load_dataset()
    print(f"Bronze ingestion complete: {res.bronze_records} records.")
    return res.batch_id


def task_clean_silver():
    import pyarrow.parquet as pq
    from retailiq.config import settings
    from retailiq.transformations.cleaning import SilverCleaner

    bronze_path = settings.storage.bronze_parquet_dir / "bronze_transactions_raw.parquet"
    df = pq.read_table(bronze_path).to_pandas()
    cleaner = SilverCleaner()
    valid_df, _, summary = cleaner.clean_dataframe(df, batch_id="AIRFLOW_BATCH")
    print(f"Cleaned {len(valid_df)} Silver records.")
    return summary.valid_silver_records


def task_build_gold():
    import pyarrow.parquet as pq
    from retailiq.analytics.gold_builder import GoldLayerBuilder
    from retailiq.config import settings

    silver_path = settings.storage.silver_dir / "silver_transactions_cleaned.parquet"
    df = pq.read_table(silver_path).to_pandas()
    builder = GoldLayerBuilder()
    summary = builder.build_gold_layer(df, persist_to_db=True)
    print(f"Gold Layer marts generated: {summary.mart_daily_rows} daily entries.")
    return summary.fact_sales_count


def task_quality_checks():
    import pyarrow.parquet as pq
    from retailiq.config import settings
    from retailiq.pipeline.quality import DataQualityChecker

    silver_path = settings.storage.silver_dir / "silver_transactions_cleaned.parquet"
    df = pq.read_table(silver_path).to_pandas()
    checker = DataQualityChecker()
    results = checker.run_all_checks(df, persist_to_db=True)
    failed = sum(1 for r in results if r.status == "FAIL")
    if failed > 0:
        raise ValueError(f"{failed} Data Quality checks failed!")
    print("All Data Quality checks passed successfully.")
    return True


if AIRFLOW_AVAILABLE:
    default_args = {
        "owner": "retailiq_data_engineering",
        "depends_on_past": False,
        "start_date": datetime(2026, 1, 1),
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(hours=1),
    }

    dag = DAG(
        "retailiq_lakehouse_pipeline",
        default_args=default_args,
        description="Daily RetailIQ Bronze-Silver-Gold Lakehouse Ingestion & Marts Refresh",
        schedule_interval="0 2 * * *",  # Daily at 02:00 UTC
        catchup=False,
        max_active_runs=1,
    )

    t_validate = PythonOperator(task_id="validate_configuration", python_callable=task_validate_config, dag=dag)
    t_ingest = PythonOperator(task_id="ingest_raw_data", python_callable=task_ingest_bronze, dag=dag)
    t_clean = PythonOperator(task_id="clean_and_validate_data", python_callable=task_clean_silver, dag=dag)
    t_gold = PythonOperator(task_id="build_gold_marts", python_callable=task_build_gold, dag=dag)
    t_qa = PythonOperator(task_id="run_quality_checks", python_callable=task_quality_checks, dag=dag)

    t_validate >> t_ingest >> t_clean >> t_gold >> t_qa
