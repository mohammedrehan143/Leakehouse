import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, Activity } from 'lucide-react';
import { QualityCheck, PipelineRun } from '../types';

interface DataQualityViewProps {
  checks: QualityCheck[];
  runs: PipelineRun[];
}

export const DataQualityView: React.FC<DataQualityViewProps> = ({ checks, runs }) => {
  const passingChecks = checks.filter((c) => c.status === 'PASS').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            Lakehouse Quality & Telemetry
            <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full font-semibold">
              {passingChecks}/{checks.length} Passing
            </span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Deterministic data invariants enforced at Bronze, Silver, and Gold transitions.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl self-start sm:self-auto">
          <Activity size={14} className="text-emerald-400" />
          <span>Audit Store: <code className="text-emerald-300">mart_data_quality</code></span>
        </div>
      </div>

      {/* Quality Checks Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {checks.map((chk) => {
          const isPass = chk.status === 'PASS';
          const isWarn = chk.status === 'WARN';

          return (
            <div
              key={chk.check_name}
              className="glass-card p-5 rounded-2xl border transition hover:border-slate-700"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-300 truncate max-w-[200px]" title={chk.check_name}>
                  {chk.check_name}
                </span>

                <span
                  className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    isPass
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : isWarn
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  {isPass ? <CheckCircle2 size={12} /> : isWarn ? <AlertTriangle size={12} /> : <XCircle size={12} />}
                  {chk.status}
                </span>
              </div>

              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                {chk.details}
              </p>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                <span>Examined: {chk.records_examined.toLocaleString()}</span>
                <span>Failed: {chk.records_failed.toLocaleString()}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pipeline Runs Telemetry Table */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Clock size={16} className="text-indigo-400" />
              Automated Pipeline Execution Telemetry
            </h3>
            <p className="text-xs text-slate-400">
              Recorded in <code className="text-indigo-300">lakehouse_pipeline_runs</code> ORM table
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Run Identifier</th>
                <th className="py-3 px-4">Pipeline Name</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Execution Timestamp</th>
                <th className="py-3 px-4 text-right">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {runs.map((r) => (
                <tr key={r.run_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-4 font-mono text-indigo-400 font-bold">{r.run_id}</td>
                  <td className="py-3 px-4 font-medium">{r.pipeline_name}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      <CheckCircle2 size={12} />
                      {r.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{r.started_at}</td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-white">{r.duration_seconds.toFixed(2)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
