import React from 'react';
import {
  DollarSign,
  TrendingDown,
  ShoppingBag,
  Package,
  Calendar,
  Layers,
  ArrowUpRight,
  ShieldAlert,
} from 'lucide-react';
import { SalesOverview, CustomerOverview, SalesTrendsData } from '../types';

interface ExecutiveOverviewProps {
  sales: SalesOverview;
  customers: CustomerOverview;
  trends: SalesTrendsData;
}

export const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({
  sales,
  customers,
  trends,
}) => {
  const avgOrderValue = sales.total_orders > 0 ? sales.gross_revenue / sales.total_orders : 0;
  const returnRatePct = sales.gross_revenue > 0 ? (sales.returns_revenue / sales.gross_revenue) * 100 : 0;

  // Monthly revenue breakdown max for SVG bar sizing
  const maxMonthlyRevenue = Math.max(
    ...trends.monthly.map((m) => m.gross_revenue),
    1000000
  );

  return (
    <div className="space-y-6">
      {/* Top Welcome & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Executive Summary
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Certified Gold Lakehouse metrics aggregated over {sales.days_recorded} operational days.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60 self-start sm:self-auto">
          <Calendar size={14} className="text-indigo-400" />
          <span>Period: 01 Dec 2010 – 09 Dec 2011</span>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Gross Revenue */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-indigo-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Gross Sales Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <DollarSign size={16} />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-white tracking-tight">
              £{sales.gross_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h3>
            <div className="flex items-center gap-1.5 mt-1.5 text-xs text-emerald-400 font-medium">
              <ArrowUpRight size={14} />
              <span>541,909 raw records verified</span>
            </div>
          </div>
        </div>

        {/* Net Revenue */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Net Retained Sales</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <DollarSign size={16} />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-emerald-300 tracking-tight">
              £{sales.net_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h3>
            <p className="text-xs text-slate-400 mt-1.5">
              Net of cancellations and credit returns
            </p>
          </div>
        </div>

        {/* Returns & Cancellations */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-rose-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Returns & Cancellations</span>
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-400">
              <TrendingDown size={16} />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-rose-300 tracking-tight">
              £{sales.returns_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h3>
            <p className="text-xs text-slate-400 mt-1.5">
              Return Rate: <span className="font-semibold text-rose-400">{returnRatePct.toFixed(2)}%</span> of gross
            </p>
          </div>
        </div>

        {/* Total Orders & Volume */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-purple-500/40 transition">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Orders Fulfilled</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <ShoppingBag size={16} />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-white tracking-tight">
              {sales.total_orders.toLocaleString()}
            </h3>
            <p className="text-xs text-slate-400 mt-1.5">
              Avg Order Value: <span className="font-semibold text-purple-300">£{avgOrderValue.toFixed(2)}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Secondary Metrics & Lakehouse Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3.5">
          <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
            <Package size={20} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Total Units Sold</p>
            <p className="text-lg font-bold text-white">{sales.units_sold.toLocaleString()} items</p>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3.5">
          <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
            <Layers size={20} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Customer Base & Repeat Rate</p>
            <p className="text-lg font-bold text-white">
              {customers.total_registered_customers.toLocaleString()} ({customers.repeat_purchase_rate_pct}% repeat)
            </p>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center gap-3.5">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <ShieldAlert size={20} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Quarantined Anomalies</p>
            <p className="text-lg font-bold text-emerald-400">2,517 isolated (0.46%)</p>
          </div>
        </div>
      </div>

      {/* Monthly Sales Revenue Chart */}
      <div className="glass-card p-6 rounded-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-800 gap-2">
          <div>
            <h3 className="text-base font-bold text-white">
              Monthly Lakehouse Sales Trajectory
            </h3>
            <p className="text-xs text-slate-400">
              Aggregated monthly gross sales revenue vs returns across 13 months
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-indigo-500 inline-block"></span>
              <span className="text-slate-300">Gross Sales</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-rose-500 inline-block"></span>
              <span className="text-slate-300">Returns</span>
            </div>
          </div>
        </div>

        {/* Visual Bar Chart */}
        <div className="pt-6">
          <div className="grid grid-cols-13 gap-1.5 sm:gap-2.5 h-48 items-end">
            {trends.monthly.map((m) => {
              const heightPct = Math.min(100, Math.max(10, (m.gross_revenue / maxMonthlyRevenue) * 100));
              const returnHeightPct = Math.min(heightPct, Math.max(4, (m.returns_revenue / maxMonthlyRevenue) * 100));

              return (
                <div key={m.month} className="flex flex-col items-center h-full justify-end group relative">
                  {/* Tooltip */}
                  <div className="absolute -top-16 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 border border-slate-700 px-2.5 py-1.5 rounded-lg text-[10px] text-white shadow-xl pointer-events-none whitespace-nowrap z-20">
                    <p className="font-bold">{m.month}</p>
                    <p className="text-indigo-400">Gross: £{Math.round(m.gross_revenue).toLocaleString()}</p>
                    <p className="text-rose-400">Returns: £{Math.round(m.returns_revenue).toLocaleString()}</p>
                  </div>

                  {/* Main Stacked Bar */}
                  <div
                    className="w-full rounded-t bg-indigo-500/80 group-hover:bg-indigo-400 transition-all relative overflow-hidden flex flex-col justify-end"
                    style={{ height: `${heightPct}%` }}
                  >
                    <div
                      className="w-full bg-rose-500/90"
                      style={{ height: `${(returnHeightPct / heightPct) * 100}%` }}
                    />
                  </div>
                  <span className="text-[9px] text-slate-500 mt-2 truncate w-full text-center">
                    {m.month.split('-')[1]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
