"""Sales Forecasting Engine for RetailIQ Lakehouse."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


@dataclass
class ForecastMetrics:
    mae: float
    rmse: float
    mape: float
    test_days: int
    train_days: int


@dataclass
class ForecastPoint:
    date: str
    forecast_value: float
    lower_bound: float
    upper_bound: float


@dataclass
class ForecastResult:
    metrics: ForecastMetrics
    forecast_points: list[ForecastPoint]
    model_name: str
    disclaimer: str = (
        "Forecasts are statistical projections derived strictly from historical data. "
        "They do not guarantee future performance or account for unmodeled exogenous factors."
    )


class SalesForecaster:
    """Trains autoregressive models on daily sales and evaluates with chronological split."""

    def __init__(self, lag_days: list[int] | None = None) -> None:
        self.lag_days = lag_days or [1, 2, 3, 7]

    def _create_features(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        data = df.sort_values("date_key").copy()
        for lag in self.lag_days:
            data[f"lag_{lag}"] = data[target_col].shift(lag)
        # Day of week seasonality feature
        dates = pd.to_datetime(data["date_key"])
        data["day_of_week"] = dates.dt.dayofweek
        return data.dropna()

    def forecast_daily_sales(
        self,
        daily_df: pd.DataFrame,
        horizon_days: int = 14,
        target_column: str = "gross_revenue",
        test_ratio: float = 0.2,
    ) -> ForecastResult:
        """Execute chronological train/test split, train model, and project out-of-sample."""
        if len(daily_df) < 15:
            raise ValueError(f"Insufficient historical data ({len(daily_df)} days); minimum 15 days required.")

        feature_df = self._create_features(daily_df, target_column)
        feature_cols = [f"lag_{lag}" for lag in self.lag_days] + ["day_of_week"]

        # Chronological Split (strictly ordered, no shuffling)
        n = len(feature_df)
        split_idx = int(n * (1 - test_ratio))

        train_data = feature_df.iloc[:split_idx]
        test_data = feature_df.iloc[split_idx:]

        X_train = train_data[feature_cols]
        y_train = train_data[target_column]

        X_test = test_data[feature_cols]
        y_test = test_data[target_column]

        # Fit model on values to avoid feature name mismatch during recursive step projection
        model = Ridge(alpha=1.0)
        model.fit(X_train.values, y_train.values)

        # Evaluate on test partition
        y_pred = model.predict(X_test.values)
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mape = float(np.mean(np.abs((y_test - y_pred) / (y_test + 1e-5))) * 100)

        # Generate out-of-sample forecast
        last_date = pd.to_datetime(daily_df["date_key"].max())
        history = list(daily_df.sort_values("date_key")[target_column].values)

        forecast_points: list[ForecastPoint] = []
        for step in range(1, horizon_days + 1):
            next_date = last_date + timedelta(days=step)
            features: list[float] = []
            for lag in self.lag_days:
                features.append(history[-lag] if lag <= len(history) else history[-1])
            features.append(next_date.dayofweek)

            pred = float(model.predict([features])[0])
            pred = max(0.0, pred)  # Revenue cannot be negative
            history.append(pred)

            # Uncertainty interval based on test RMSE
            low = max(0.0, pred - (1.96 * rmse))
            high = pred + (1.96 * rmse)

            forecast_points.append(
                ForecastPoint(
                    date=next_date.strftime("%Y-%m-%d"),
                    forecast_value=round(pred, 2),
                    lower_bound=round(low, 2),
                    upper_bound=round(high, 2),
                )
            )

        return ForecastResult(
            metrics=ForecastMetrics(
                mae=round(mae, 2),
                rmse=round(rmse, 2),
                mape=round(mape, 2),
                test_days=len(test_data),
                train_days=len(train_data),
            ),
            forecast_points=forecast_points,
            model_name="Autoregressive Ridge (Lags 1, 2, 3, 7 + DayOfWeek)",
        )
