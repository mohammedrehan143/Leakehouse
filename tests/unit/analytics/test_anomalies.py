"""Unit tests for statistical anomaly detection."""

import pandas as pd
from retailiq.analytics.anomalies import AnomalyDetector


def test_anomaly_detector():
    dates = pd.date_range("2026-01-01", periods=20, freq="D")
    revenues = [1000.0] * 20
    # Inject spike on day 15
    revenues[15] = 8500.0

    df = pd.DataFrame({"date_key": dates.strftime("%Y-%m-%d"), "gross_revenue": revenues})

    detector = AnomalyDetector(window_size=5, threshold_sigma=2.0)
    anomalies = detector.detect_daily_anomalies(df, metric_column="gross_revenue")

    assert len(anomalies) >= 1
    spike = [a for a in anomalies if a.anomaly_type == "SPIKE"][0]
    assert spike.date == dates[15].strftime("%Y-%m-%d")
    assert spike.actual_value == 8500.0
