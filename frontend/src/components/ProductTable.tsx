import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { ProductItem } from '../types';

interface ProductTableProps {
  products: ProductItem[];
}

export const ProductTable: React.FC<ProductTableProps> = ({ products }) => {
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'revenue' | 'units' | 'orders'>('revenue');

  const filtered = products
    .filter(
      (p) =>
        p.description.toLowerCase().includes(search.toLowerCase()) ||
        p.stock_code.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'revenue') return b.total_revenue - a.total_revenue;
      if (sortBy === 'units') return b.total_units_sold - a.total_units_sold;
      return b.order_count - a.order_count;
    });

  const maxRevenue = Math.max(...products.map((p) => p.total_revenue), 1);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            Product Catalog Intelligence
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Gold mart analysis ranking top revenue drivers and volume velocities.
          </p>
        </div>

        {/* Search & Sort Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search SKU or description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-4 py-2 bg-slate-900 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-full sm:w-64 transition"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-xl">
            <button
              onClick={() => setSortBy('revenue')}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                sortBy === 'revenue' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Revenue
            </button>
            <button
              onClick={() => setSortBy('units')}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                sortBy === 'units' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Units
            </button>
            <button
              onClick={() => setSortBy('orders')}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                sortBy === 'orders' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Orders
            </button>
          </div>
        </div>
      </div>

      {/* Catalog Table */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Stock Code</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">Total Revenue</th>
                <th className="py-3 px-4">Revenue Share</th>
                <th className="py-3 px-4">Units Sold</th>
                <th className="py-3 px-4 text-right">Orders</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {filtered.map((item) => {
                const sharePct = (item.total_revenue / maxRevenue) * 100;
                return (
                  <tr key={item.stock_code} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-mono font-bold text-indigo-400">
                      {item.stock_code}
                    </td>
                    <td className="py-3 px-4 font-medium max-w-xs truncate" title={item.description}>
                      {item.description}
                    </td>
                    <td className="py-3 px-4 font-bold text-white">
                      £{item.total_revenue.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 w-40">
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-indigo-500 to-indigo-400 h-full rounded-full"
                          style={{ width: `${Math.min(100, Math.max(5, sharePct))}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-300">
                      {item.total_units_sold.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-400">
                      {item.order_count.toLocaleString()}
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No products matching "{search}"
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
