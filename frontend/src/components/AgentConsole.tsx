import React, { useState } from 'react';
import {
  Bot,
  Play,
  CheckCircle2,
  ListOrdered,
  FileText,
  Lightbulb,
  Cpu,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import { AgentTaskState } from '../types';
import { submitAgentTask } from '../api';

interface AgentConsoleProps {
  initialAgentState: AgentTaskState | null;
}

export const AgentConsole: React.FC<AgentConsoleProps> = ({ initialAgentState }) => {
  const [query, setQuery] = useState(
    'What are our top revenue-generating products and total sales volume?'
  );
  const [loading, setLoading] = useState(false);
  const [state, setState] = useState<AgentTaskState | null>(initialAgentState);

  const samplePrompts = [
    'What are our top revenue-generating products and total sales volume?',
    'Analyze return and cancellation rates across Q4 giftware orders.',
    'Are there any quarantined records or non-positive price anomalies?',
    'How do repeat customer purchase rates compare with single-order buyers?',
  ];

  const handleExecute = async (queryText: string) => {
    setLoading(true);
    setQuery(queryText);
    try {
      const res = await submitAgentTask(queryText);
      setState(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          AI Multi-Agent Investigation Console
          <span className="text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-medium">
            LangGraph Router
          </span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-400">
          Autonomous orchestration routing natural language investigations to domain specialists.
        </p>
      </div>

      {/* Query Submission Box */}
      <div className="glass-card p-5 rounded-2xl space-y-4">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && handleExecute(query)}
            placeholder="Ask an analytical or data quality question..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition pr-28"
          />

          <button
            onClick={() => handleExecute(query)}
            disabled={loading || !query.trim()}
            className="absolute right-2 top-2 bottom-2 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw size={13} className="animate-spin" />
                <span>Thinking...</span>
              </>
            ) : (
              <>
                <Play size={13} fill="currentColor" />
                <span>Investigate</span>
              </>
            )}
          </button>
        </div>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Sample Inquiries:
          </span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleExecute(p)}
              disabled={loading}
              className="text-[11px] bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-slate-300 hover:text-white px-2.5 py-1 rounded-lg transition text-left"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Execution Results View */}
      {state && (
        <div className="space-y-6">
          {/* Status Header Bar */}
          <div className="glass-card p-4 rounded-xl flex flex-wrap items-center justify-between gap-3 border-indigo-500/30">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Bot size={18} />
              </div>
              <div>
                <span className="text-xs text-slate-400">Assigned Specialist:</span>
                <p className="text-sm font-bold text-white flex items-center gap-2">
                  {state.assigned_specialist}
                  <span className="text-[10px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full">
                    {state.status.toUpperCase()}
                  </span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
              <span>Task ID:</span>
              <span className="text-indigo-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                {state.task_id}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Multi-Step Execution Plan Timeline */}
            <div className="glass-card p-5 rounded-2xl">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
                <ListOrdered size={16} className="text-indigo-400" />
                Decomposed Investigation Plan
              </h3>

              <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                {state.plan.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-3 relative z-10">
                    <div className="w-6 h-6 rounded-full bg-slate-900 border border-indigo-500/50 text-indigo-400 flex items-center justify-center text-[10px] font-bold shrink-0">
                      {idx + 1}
                    </div>
                    <p className="text-xs text-slate-300 pt-0.5 leading-relaxed">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Empirical Findings & Recommendations */}
            <div className="lg:col-span-2 space-y-6">
              {/* Findings */}
              <div className="glass-card p-5 rounded-2xl">
                <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
                  <FileText size={16} className="text-emerald-400" />
                  Empirical Findings (Lakehouse Evidence)
                </h3>
                <div className="space-y-2.5">
                  {state.findings.map((finding, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-200 flex items-start gap-2.5"
                    >
                      <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                      <span className="leading-relaxed">{finding}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div className="glass-card p-5 rounded-2xl border-amber-500/20">
                <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
                  <Lightbulb size={16} className="text-amber-400" />
                  Actionable Business Recommendations
                </h3>
                <div className="space-y-2.5">
                  {state.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-200 flex items-start gap-2.5"
                    >
                      <Sparkles size={14} className="text-amber-400 shrink-0 mt-0.5" />
                      <span className="leading-relaxed">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Tool Execution History */}
          <div className="glass-card p-4 rounded-xl flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <Cpu size={15} className="text-indigo-400" />
              <span>Controlled Tool Invocation History:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {state.tool_history.map((th, idx) => (
                <span
                  key={idx}
                  className="font-mono text-[11px] bg-slate-900 border border-slate-800 text-indigo-300 px-2.5 py-0.5 rounded-lg"
                >
                  {th.tool_name} ({th.duration_ms.toFixed(1)}ms)
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
