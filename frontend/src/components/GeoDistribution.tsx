import React from 'react';
import { MapPin } from 'lucide-react';
import { CountryPerformance } from '../types';

interface GeoDistributionProps {
  countries: CountryPerformance[];
}

export const GeoDistribution: React.FC<GeoDistributionProps> = ({ countries }) => {
  const totalGeoRevenue = countries.reduce((acc, c) => acc + c.total_revenue, 0);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          Global Market Footprint
        </h2>
        <p className="text-xs sm:text-sm text-slate-400">
          Geographic revenue dispersion and international wholesale concentration across 38 territories.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dominant Domestic Market Card */}
        <div className="glass-card p-6 rounded-2xl border-indigo-500/30">
          <div className="flex items-center gap-2 text-indigo-400 mb-2">
            <MapPin size={18} />
            <span className="text-xs font-bold uppercase tracking-wider">Domestic Core</span>
          </div>
          <h3 className="text-3xl font-extrabold text-white">United Kingdom</h3>
          <p className="text-2xl font-bold text-indigo-400 mt-2">£8.19M</p>
          <p className="text-xs text-slate-400 mt-1">
            Accounts for <span className="font-bold text-white">88.5%</span> of all gross revenue and 3,950 registered wholesale buyers.
          </p>

          <div className="mt-6 pt-4 border-t border-slate-800 text-xs text-slate-400 leading-relaxed">
            The platform’s fulfillment hub operates in the UK, with high regional concentration among Midlands gift shops and regional department chains.
          </div>
        </div>

        {/* International Markets Ranking Table */}
        <div className="lg:col-span-2 glass-card rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-base font-bold text-white">Top International Markets</h3>
            <p className="text-xs text-slate-400">
              Cross-border export volumes ranked by gross invoiced amount
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Country</th>
                  <th className="py-3 px-4">Gross Revenue</th>
                  <th className="py-3 px-4">Market Share</th>
                  <th className="py-3 px-4">Total Orders</th>
                  <th className="py-3 px-4 text-right">Buyers</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {countries.map((c) => {
                  const sharePct = totalGeoRevenue > 0 ? (c.total_revenue / totalGeoRevenue) * 100 : 0;
                  return (
                    <tr key={c.country} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-4 font-semibold text-white flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                        {c.country}
                      </td>
                      <td className="py-3 px-4 font-bold text-indigo-300">
                        £{c.total_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 px-4 w-40">
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div
                              className="bg-indigo-500 h-full rounded-full"
                              style={{ width: `${Math.min(100, Math.max(4, sharePct))}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-slate-400 w-10 text-right">{sharePct.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-300">{c.total_orders.toLocaleString()}</td>
                      <td className="py-3 px-4 text-right text-slate-400 font-medium">{c.unique_customers}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
