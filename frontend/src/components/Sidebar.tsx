import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  LineChart,
  Package,
  Users,
  Globe2,
  ShieldCheck,
  Bot,
} from 'lucide-react';
import { TabType } from '../types';

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  mobileMenuOpen,
  setMobileMenuOpen,
}) => {
  const navItems: Array<{ id: TabType; label: string; icon: React.ReactNode; badge?: string }> = [
    { id: 'overview', label: 'Executive Overview', icon: <LayoutDashboard size={18} /> },
    { id: 'trends', label: 'Sales & Anomalies', icon: <TrendingUp size={18} />, badge: 'Live' },
    { id: 'forecasting', label: 'ML Forecaster', icon: <LineChart size={18} />, badge: 'Ridge' },
    { id: 'products', label: 'Product Catalog', icon: <Package size={18} /> },
    { id: 'customers', label: 'Customer Cohorts', icon: <Users size={18} /> },
    { id: 'geo', label: 'Global Markets', icon: <Globe2 size={18} /> },
    { id: 'quality', label: 'Data Quality & QA', icon: <ShieldCheck size={18} />, badge: '5/5' },
    { id: 'agents', label: 'AI Multi-Agent', icon: <Bot size={18} />, badge: 'MAS' },
  ];

  const handleSelect = (id: TabType) => {
    setActiveTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Navigation Drawer / Sidebar */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-800 p-4 flex flex-col justify-between transition-transform duration-300 ease-in-out md:translate-x-0 ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="space-y-6">
          <div className="px-3 pt-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
              Lakehouse Intelligence
            </span>
          </div>

          <nav className="space-y-1" aria-label="Main Navigation">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`transition-colors ${
                        isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-300'
                      }`}
                    >
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </div>

                  {item.badge && (
                    <span
                      className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                        isActive
                          ? 'bg-indigo-500/20 text-indigo-300'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer Meta */}
        <div className="pt-4 border-t border-slate-800 text-center px-2">
          <p className="text-[11px] text-slate-500">
            UCI Online Retail Dataset
          </p>
          <p className="text-[10px] text-slate-600 mt-0.5">
            541,909 Transactions Verified
          </p>
        </div>
      </aside>
    </>
  );
};
