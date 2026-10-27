import React from 'react';
import { Database, RefreshCw, Menu, X, Wifi, WifiOff } from 'lucide-react';

interface HeaderProps {
  backendConnected: boolean;
  refreshing: boolean;
  onRefresh: () => void;
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  backendConnected,
  refreshing,
  onRefresh,
  mobileMenuOpen,
  setMobileMenuOpen,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-4 sm:px-6 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Logo & Brand */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Database size={20} className="text-white" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                RetailIQ <span className="text-indigo-400 font-semibold">Lakehouse</span>
              </h1>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Medallion Architecture (Bronze • Silver • Gold) & Multi-Agent Analytics
            </p>
          </div>
        </div>

        {/* Right Status Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Connection Status Pill */}
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
              backendConnected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}
          >
            {backendConnected ? (
              <>
                <Wifi size={13} className="text-emerald-400" />
                <span className="hidden sm:inline">Render API Connected</span>
                <span className="sm:hidden">Live</span>
              </>
            ) : (
              <>
                <WifiOff size={13} className="text-amber-400" />
                <span className="hidden sm:inline">Offline Demo Mode</span>
                <span className="sm:hidden">Demo</span>
              </>
            )}
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-medium transition disabled:opacity-50"
            title="Refresh lakehouse data"
          >
            <RefreshCw size={13} className={refreshing ? 'animate-spin text-indigo-400' : ''} />
            <span className="hidden sm:inline">Sync Data</span>
          </button>
        </div>
      </div>
    </header>
  );
};
