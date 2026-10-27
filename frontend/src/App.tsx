import { useState, useEffect, useCallback } from 'react';
import { TabType, SalesOverview, CustomerOverview, SalesTrendsData, ProductItem, CountryPerformance, QualityCheck, AnomalyRecord, ForecastResult, PipelineRun, AgentTaskState } from './types';
import {
  checkBackendHealth,
  fetchOverview,
  fetchSalesTrends,
  fetchProducts,
  fetchCountries,
  fetchQualityChecks,
  fetchAnomalies,
  fetchForecast,
  fetchPipelineRuns,
  FALLBACK_SALES,
  FALLBACK_CUSTOMERS,
  FALLBACK_PRODUCTS,
  FALLBACK_COUNTRIES,
  FALLBACK_QUALITY_CHECKS,
  FALLBACK_ANOMALIES,
  FALLBACK_FORECAST,
  FALLBACK_PIPELINE_RUNS,
} from './api';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ExecutiveOverview } from './components/ExecutiveOverview';
import { SalesTrends } from './components/SalesTrends';
import { ForecastingView } from './components/ForecastingView';
import { ProductTable } from './components/ProductTable';
import { CustomerAnalytics } from './components/CustomerAnalytics';
import { GeoDistribution } from './components/GeoDistribution';
import { DataQualityView } from './components/DataQualityView';
import { AgentConsole } from './components/AgentConsole';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Lakehouse Datasets
  const [sales, setSales] = useState<SalesOverview>(FALLBACK_SALES);
  const [customers, setCustomers] = useState<CustomerOverview>(FALLBACK_CUSTOMERS);
  const [trends, setTrends] = useState<SalesTrendsData>({
    daily: [],
    monthly: [
      { month: '2010-12', gross_revenue: 748957, returns_revenue: 35805, net_revenue: 713152, order_count: 1708, unique_customers: 948 },
      { month: '2011-01', gross_revenue: 560000, returns_revenue: 28000, net_revenue: 532000, order_count: 1236, unique_customers: 783 },
      { month: '2011-02', gross_revenue: 498060, returns_revenue: 24900, net_revenue: 473160, order_count: 1202, unique_customers: 758 },
      { month: '2011-03', gross_revenue: 683267, returns_revenue: 34100, net_revenue: 649167, order_count: 1619, unique_customers: 974 },
      { month: '2011-04', gross_revenue: 497886, returns_revenue: 29800, net_revenue: 468086, order_count: 1384, unique_customers: 856 },
      { month: '2011-05', gross_revenue: 723335, returns_revenue: 43400, net_revenue: 679935, order_count: 1849, unique_customers: 1056 },
      { month: '2011-06', gross_revenue: 691122, returns_revenue: 41400, net_revenue: 649722, order_count: 1707, unique_customers: 991 },
      { month: '2011-07', gross_revenue: 681300, returns_revenue: 40800, net_revenue: 640500, order_count: 1593, unique_customers: 949 },
      { month: '2011-08', gross_revenue: 659557, returns_revenue: 39500, net_revenue: 620057, order_count: 1544, unique_customers: 935 },
      { month: '2011-09', gross_revenue: 1019687, returns_revenue: 61100, net_revenue: 958587, order_count: 2078, unique_customers: 1266 },
      { month: '2011-10', gross_revenue: 1070704, returns_revenue: 64200, net_revenue: 1006504, order_count: 2263, unique_customers: 1364 },
      { month: '2011-11', gross_revenue: 1461756, returns_revenue: 87700, net_revenue: 1374056, order_count: 3410, unique_customers: 1665 },
      { month: '2011-12', gross_revenue: 433890, returns_revenue: 26000, net_revenue: 407890, order_count: 929, unique_customers: 615 },
    ],
  });
  const [products, setProducts] = useState<ProductItem[]>(FALLBACK_PRODUCTS);
  const [countries, setCountries] = useState<CountryPerformance[]>(FALLBACK_COUNTRIES);
  const [checks, setChecks] = useState<QualityCheck[]>(FALLBACK_QUALITY_CHECKS);
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>(FALLBACK_ANOMALIES);
  const [forecast, setForecast] = useState<ForecastResult>(FALLBACK_FORECAST);
  const [runs, setRuns] = useState<PipelineRun[]>(FALLBACK_PIPELINE_RUNS);

  const [initialAgentState] = useState<AgentTaskState>({
    task_id: 'task-init-001',
    user_query: 'What are our top revenue-generating products and sales volume?',
    status: 'succeeded',
    assigned_specialist: 'ProductSpecialist',
    plan: [
      'Parse natural language prompt and classify query domain.',
      'Query mart_product_performance for top revenue items.',
      'Cross-check return rates in fct_returns.',
      'Formulate synthesized business findings and recommendations.',
    ],
    findings: [
      "Top revenue generator is StockCode 'DOT' (DOTCOM POSTAGE) with £206,245.48 in sales.",
      "Item '22423' (REGENCY CAKESTAND 3 TIER) generated £164,762.19 across 13,034 units.",
      'Top 5 SKUs generate approximately 12.4% of total catalog revenue.',
    ],
    recommendations: [
      'Establish automated inventory replenishment triggers for top 5 turnover SKUs.',
      'Evaluate pricing elasticity on high-demand decorative cake stands.',
    ],
    tool_history: [
      { tool_name: 'query_top_products', duration_ms: 18.4 },
      { tool_name: 'query_sales_summary', duration_ms: 12.1 },
    ],
  });

  const loadAllData = useCallback(async () => {
    setRefreshing(true);
    try {
      const isHealthy = await checkBackendHealth();
      setBackendConnected(isHealthy);

      if (isHealthy) {
        const [
          overviewData,
          trendsData,
          productsData,
          countriesData,
          checksData,
          anomaliesData,
          forecastData,
          runsData,
        ] = await Promise.all([
          fetchOverview(),
          fetchSalesTrends(),
          fetchProducts(25),
          fetchCountries(),
          fetchQualityChecks(),
          fetchAnomalies(),
          fetchForecast(14),
          fetchPipelineRuns(),
        ]);

        if (overviewData.sales.total_orders > 0) setSales(overviewData.sales);
        if (overviewData.customers.total_registered_customers > 0) setCustomers(overviewData.customers);
        if (trendsData.monthly.length > 0) setTrends(trendsData);
        if (productsData.length > 0) setProducts(productsData);
        if (countriesData.length > 0) setCountries(countriesData);
        if (checksData.length > 0) setChecks(checksData);
        if (anomaliesData.length > 0) setAnomalies(anomaliesData);
        if (forecastData.forecast_points.length > 0) setForecast(forecastData);
        if (runsData.length > 0) setRuns(runsData);
      }
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-indigo-500 selection:text-white">
      {/* Top Application Header */}
      <Header
        backendConnected={backendConnected}
        refreshing={refreshing}
        onRefresh={loadAllData}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      {/* Main Layout Area */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        {/* Navigation Sidebar Drawer */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
        />

        {/* Dynamic Content Panel */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
          {activeTab === 'overview' && (
            <ExecutiveOverview sales={sales} customers={customers} trends={trends} />
          )}

          {activeTab === 'trends' && (
            <SalesTrends trends={trends} anomalies={anomalies} />
          )}

          {activeTab === 'forecasting' && (
            <ForecastingView initialForecast={forecast} />
          )}

          {activeTab === 'products' && (
            <ProductTable products={products} />
          )}

          {activeTab === 'customers' && (
            <CustomerAnalytics customers={customers} />
          )}

          {activeTab === 'geo' && (
            <GeoDistribution countries={countries} />
          )}

          {activeTab === 'quality' && (
            <DataQualityView checks={checks} runs={runs} />
          )}

          {activeTab === 'agents' && (
            <AgentConsole initialAgentState={initialAgentState} />
          )}
        </main>
      </div>

      {/* Footer Info */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        RetailIQ Lakehouse &bull; Engineered with Medallion Architecture, FastAPI, React, and LangGraph Multi-Agent Runtime &bull; Pushed to GitHub
      </footer>
    </div>
  );
}
