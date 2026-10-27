"""Statistical Anomaly Detection Engine for RetailIQ Lakehouse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class AnomalyDetectionResult:
    """Detected volume or revenue anomaly."""

    date: str
    metric_name: str
    actual_value: float
    expected_lower_bound: float
    expected_upper_bound: float
    deviation_score: float
    severity: str  # LOW, MEDIUM, HIGH
    anomaly_type: str  # SPIKE, DROP
    note: str


class AnomalyDetector:
    """Identifies statistical deviations in time-series sales without altering historical data."""

    def __init__(self, window_size: int = 7, threshold_sigma: float = 2.5) -> None:
        self.window_size = window_size
        self.threshold_sigma = threshold_sigma

    def detect_daily_anomalies(
        self,
        daily_df: pd.DataFrame,
        metric_column: str = "gross_revenue",
    ) -> list[AnomalyDetectionResult]:
        """Detect statistical outliers using rolling mean and deviation bands."""
        if len(daily_df) < self.window_size + 2:
            return []

        df = daily_df.sort_values("date_key").copy()
        series = df[metric_column].astype(float)

        # Compute rolling baseline on prior observations (shift by 1 to prevent self-contamination)
        prior_series = series.shift(1)
        rolling_mean = prior_series.rolling(window=self.window_size, min_periods=3).mean().bfill()
        rolling_std = prior_series.rolling(window=self.window_size, min_periods=3).std().fillna(1.0).bfill()
        rolling_std = rolling_std.replace(0.0, 1.0)

        upper_bound = rolling_mean + (self.threshold_sigma * rolling_std)
        lower_bound = (rolling_mean - (self.threshold_sigma * rolling_std)).clip(lower=0.0)

        anomalies: list[AnomalyDetectionResult] = []

        for idx, (val, mean, std, up, low, dt) in enumerate(
            zip(series, rolling_mean, rolling_std, upper_bound, lower_bound, df["date_key"])
        ):
            if idx < self.window_size:
                continue

            if val > up or val < low:
                dev = abs(val - mean) / (std if std > 0 else 1.0)
                anomaly_type = "SPIKE" if val > up else "DROP"
                severity = "HIGH" if dev > 3.5 else "MEDIUM"

                anomalies.append(
                    AnomalyDetectionResult(
                        date=str(dt),
                        metric_name=metric_column,
                        actual_value=round(float(val), 2),
                        expected_lower_bound=round(float(low), 2),
                        expected_upper_bound=round(float(up), 2),
                        deviation_score=round(float(dev), 2),
                        severity=severity,
                        anomaly_type=anomaly_type,
                        note=f"Observed statistical {anomaly_type.lower()} ({dev:.1f}σ from {self.window_size}-day rolling mean).",
                    )
                )

        return anomalies
