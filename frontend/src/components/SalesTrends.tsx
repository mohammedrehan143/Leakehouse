import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { SalesTrendsData, AnomalyRecord } from '../types';

interface SalesTrendsProps {
  trends: SalesTrendsData;
  anomalies: AnomalyRecord[];
}

export const SalesTrends: React.FC<SalesTrendsProps> = ({ trends, anomalies }) => {
  const [filterType, setFilterType] = useState<'all' | 'spikes' | 'drops'>('all');

  const filteredAnomalies = anomalies.filter((a) => {
    if (filterType === 'spikes') return a.anomaly_type === 'SPIKE';
    if (filterType === 'drops') return a.anomaly_type === 'DROP';
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            Sales Trends & Anomaly Detection
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Statistical deviations identified with 7-day prior un-contaminated rolling baselines.
          </p>
        </div>

        {/* Filter Chips */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-1 rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
              filterType === 'all'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All Events ({anomalies.length})
          </button>
          <button
            onClick={() => setFilterType('spikes')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
              filterType === 'spikes'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Spikes
          </button>
          <button
            onClick={() => setFilterType('drops')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
              filterType === 'drops'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Drops
          </button>
        </div>
      </div>

      {/* Anomaly Detection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {filteredAnomalies.map((anomaly, idx) => {
          const isSpike = anomaly.anomaly_type === 'SPIKE';
          return (
            <div
              key={idx}
              className={`p-5 rounded-2xl border transition hover:translate-y-[-2px] ${
                isSpike
                  ? 'bg-amber-950/20 border-amber-500/30 shadow-lg shadow-amber-950/30'
                  : 'bg-rose-950/20 border-rose-500/30 shadow-lg shadow-rose-950/30'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-slate-400"></span>
                  {anomaly.date}
                </span>

                <span
                  className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    isSpike
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  }`}
                >
                  {isSpike ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                  {anomaly.anomaly_type} (Z: {anomaly.z_score.toFixed(2)})
                </span>
              </div>

              <div className="mt-3">
                <p className="text-xs text-slate-400 capitalize">
                  Metric: <span className="font-semibold text-slate-200">{anomaly.metric_name.replace('_', ' ')}</span>
                </p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-xl font-extrabold text-white">
                    {anomaly.metric_name.includes('revenue') ? '£' : ''}
                    {Math.round(anomaly.observed_value).toLocaleString()}
                  </span>
                  <span className="text-xs text-slate-500">
                    vs baseline {anomaly.metric_name.includes('revenue') ? '£' : ''}
                    {Math.round(anomaly.expected_baseline).toLocaleString()}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 mt-3 pt-3 border-t border-slate-800/80 leading-relaxed">
                {anomaly.details}
              </p>
            </div>
          );
        })}
      </div>

      {/* Monthly Performance Table */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800">
          <h3 className="text-base font-bold text-white">Monthly Aggregate Ledger</h3>
          <p className="text-xs text-slate-400">
            Gold mart records detailing order count, unique buyers, and retained revenues.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Period</th>
                <th className="py-3 px-4">Gross Sales</th>
                <th className="py-3 px-4">Returns</th>
                <th className="py-3 px-4">Net Revenue</th>
                <th className="py-3 px-4">Orders</th>
                <th className="py-3 px-4">Unique Customers</th>
                <th className="py-3 px-4 text-right">Return Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {trends.monthly.map((row) => {
                const retRate = (row.returns_revenue / row.gross_revenue) * 100;
                return (
                  <tr key={row.month} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-semibold text-indigo-400">{row.month}</td>
                    <td className="py-3 px-4">£{row.gross_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2 })}</td>
                    <td className="py-3 px-4 text-rose-400">£{row.returns_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2 })}</td>
                    <td className="py-3 px-4 font-bold text-emerald-300">£{row.net_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2 })}</td>
                    <td className="py-3 px-4">{row.order_count.toLocaleString()}</td>
                    <td className="py-3 px-4">{row.unique_customers.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-medium">
                      <span className={retRate > 6 ? 'text-rose-400 font-bold' : 'text-slate-400'}>
                        {retRate.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
