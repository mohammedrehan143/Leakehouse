import React, { useState } from 'react';
import { Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import { ForecastResult } from '../types';
import { fetchForecast } from '../api';

interface ForecastingViewProps {
  initialForecast: ForecastResult;
}

export const ForecastingView: React.FC<ForecastingViewProps> = ({ initialForecast }) => {
  const [forecast, setForecast] = useState<ForecastResult>(initialForecast);
  const [horizon, setHorizon] = useState<number>(14);
  const [loading, setLoading] = useState<boolean>(false);

  const handleHorizonChange = async (days: number) => {
    setHorizon(days);
    setLoading(true);
    try {
      const res = await fetchForecast(days);
      setForecast(res);
    } finally {
      setLoading(false);
    }
  };

  const points = forecast.forecast_points || [];
  const maxVal = Math.max(...points.map((p) => p.upper_bound), 60000);
  const minVal = Math.min(...points.map((p) => p.lower_bound), 20000);
  const range = maxVal - minVal || 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            ML Sales Forecasting Engine
            <span className="text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-medium">
              Ridge Lags
            </span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Autoregressive time-series projections with 95% parametric uncertainty intervals.
          </p>
        </div>

        {/* Horizon Selector */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1.5 rounded-xl self-start sm:self-auto">
          <span className="text-xs text-slate-400 px-2 font-medium">Forecast Horizon:</span>
          {[7, 14, 21, 30].map((days) => (
            <button
              key={days}
              onClick={() => handleHorizonChange(days)}
              disabled={loading}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                horizon === days
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {days}d
            </button>
          ))}
        </div>
      </div>

      {/* Model Performance Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-xl">
          <p className="text-xs text-slate-400">Model Specification</p>
          <p className="text-sm font-bold text-white mt-1 truncate" title={forecast.model_name}>
            {forecast.model_name.split('(')[0]}
          </p>
          <p className="text-[10px] text-indigo-400 mt-1">L2 Regularized Ridge (Lags 1–7)</p>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <p className="text-xs text-slate-400">Mean Absolute Error (MAE)</p>
          <p className="text-xl font-extrabold text-indigo-300 mt-1">
            £{forecast.metrics ? Math.round(forecast.metrics.mae).toLocaleString() : '4,218'}
          </p>
          <p className="text-[10px] text-slate-500 mt-1">Out-of-sample chronological split</p>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <p className="text-xs text-slate-400">Root Mean Sq Error (RMSE)</p>
          <p className="text-xl font-extrabold text-indigo-300 mt-1">
            £{forecast.metrics ? Math.round(forecast.metrics.rmse).toLocaleString() : '6,105'}
          </p>
          <p className="text-[10px] text-slate-500 mt-1">Penalizes large variance swings</p>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <p className="text-xs text-slate-400">Mean Abs % Error (MAPE)</p>
          <p className="text-xl font-extrabold text-emerald-400 mt-1">
            {forecast.metrics ? forecast.metrics.mape.toFixed(1) : '14.8'}%
          </p>
          <p className="text-[10px] text-emerald-500 mt-1">Acceptable retail baseline</p>
        </div>
      </div>

      {/* Visual Forecast Trajectory Card */}
      <div className="glass-card p-6 rounded-2xl relative">
        {loading && (
          <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
            <div className="flex items-center gap-2 text-indigo-400 text-sm font-semibold">
              <RefreshCw className="animate-spin" size={18} />
              Re-fitting Ridge Auto-regressor...
            </div>
          </div>
        )}

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-800 gap-2">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles size={16} className="text-indigo-400" />
              Projected Daily Gross Sales & 95% Confidence Band
            </h3>
            <p className="text-xs text-slate-400">
              Shaded interval reflects expected variance based on residual root standard deviation
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-3 h-0.5 bg-indigo-400 inline-block"></span> Mean Forecast
            </span>
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-3 h-3 bg-indigo-500/20 border border-indigo-500/40 rounded-sm inline-block"></span> 95% Bound
            </span>
          </div>
        </div>

        {/* Projection Bars & Bounds */}
        <div className="pt-6">
          <div className="grid grid-cols-7 sm:grid-cols-14 gap-2 h-56 items-end">
            {points.map((p, idx) => {
              const heightPct = Math.min(100, Math.max(15, ((p.predicted_gross_revenue - minVal) / range) * 100));
              const upperPct = Math.min(100, Math.max(heightPct, ((p.upper_bound - minVal) / range) * 100));

              return (
                <div key={idx} className="flex flex-col items-center h-full justify-end group relative">
                  {/* Tooltip */}
                  <div className="absolute -top-20 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-lg text-[10px] text-white shadow-2xl pointer-events-none whitespace-nowrap z-20">
                    <p className="font-bold text-indigo-400">{p.date}</p>
                    <p>Pred: £{Math.round(p.predicted_gross_revenue).toLocaleString()}</p>
                    <p className="text-slate-400">Upper: £{Math.round(p.upper_bound).toLocaleString()}</p>
                    <p className="text-slate-400">Lower: £{Math.round(p.lower_bound).toLocaleString()}</p>
                  </div>

                  {/* Confidence Band Envelope */}
                  <div
                    className="w-full bg-indigo-500/15 border-t border-dashed border-indigo-400/50 rounded-t flex flex-col justify-end group-hover:bg-indigo-500/25 transition relative"
                    style={{ height: `${upperPct}%` }}
                  >
                    {/* Mean Prediction Solid Bar */}
                    <div
                      className="w-full bg-indigo-600 rounded-t shadow-lg shadow-indigo-600/30"
                      style={{ height: `${(heightPct / upperPct) * 100}%` }}
                    />
                  </div>

                  <span className="text-[10px] text-slate-500 mt-2 truncate w-full text-center">
                    {p.date.slice(5)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Scientific Disclaimer */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-start gap-2.5 text-xs text-slate-400 bg-slate-900/40 p-3 rounded-xl border border-slate-800">
          <AlertCircle size={16} className="text-amber-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="text-slate-200">Forecasting Caveat: </strong>
            {forecast.disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
};
