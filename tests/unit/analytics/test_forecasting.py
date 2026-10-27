"""Unit tests for sales forecasting engine."""

import pandas as pd
from retailiq.analytics.forecasting import SalesForecaster


def test_sales_forecaster():
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    # Linear upward trend with slight noise
    revenues = [1000.0 + (i * 50.0) for i in range(30)]

    df = pd.DataFrame({"date_key": dates.strftime("%Y-%m-%d"), "gross_revenue": revenues})

    forecaster = SalesForecaster(lag_days=[1, 2, 7])
    result = forecaster.forecast_daily_sales(df, horizon_days=7)

    assert result.metrics.train_days > 0
    assert result.metrics.test_days > 0
    assert result.metrics.mae >= 0.0
    assert len(result.forecast_points) == 7

    # Check forecast structure
    p1 = result.forecast_points[0]
    assert p1.forecast_value > 0
    assert p1.lower_bound <= p1.forecast_value <= p1.upper_bound
