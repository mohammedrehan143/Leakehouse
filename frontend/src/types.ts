export interface SalesOverview {
  total_orders: number;
  units_sold: number;
  gross_revenue: number;
  returns_revenue: number;
  net_revenue: number;
  days_recorded: number;
}

export interface CustomerOverview {
  total_registered_customers: number;
  repeat_customers: number;
  repeat_purchase_rate_pct: number;
  average_customer_spend: number;
}

export interface DailySalesTrend {
  date: string;
  gross_revenue: number;
  returns_revenue: number;
  net_revenue: number;
  order_count: number;
  units_sold: number;
}

export interface MonthlySalesTrend {
  month: string;
  gross_revenue: number;
  returns_revenue: number;
  net_revenue: number;
  order_count: number;
  unique_customers: number;
}

export interface SalesTrendsData {
  daily: DailySalesTrend[];
  monthly: MonthlySalesTrend[];
}

export interface ProductItem {
  stock_code: string;
  description: string;
  total_revenue: number;
  total_units_sold: number;
  order_count: number;
}

export interface CountryPerformance {
  country: string;
  total_revenue: number;
  total_orders: number;
  unique_customers: number;
}

export interface QualityCheck {
  check_name: string;
  status: 'PASS' | 'WARN' | 'FAIL';
  severity: 'ERROR' | 'WARNING' | 'INFO';
  records_examined: number;
  records_failed: number;
  details: string;
}

export interface AnomalyRecord {
  date: string;
  metric_name: string;
  observed_value: number;
  expected_baseline: number;
  z_score: number;
  anomaly_type: 'SPIKE' | 'DROP';
  details: string;
}

export interface ForecastPoint {
  date: string;
  predicted_gross_revenue: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastResult {
  status: string;
  model_name: string;
  metrics?: {
    mae: number;
    rmse: number;
    mape: number;
  };
  forecast_points: ForecastPoint[];
  disclaimer: string;
}

export interface PipelineRun {
  run_id: string;
  pipeline_name: string;
  status: string;
  started_at: string;
  duration_seconds: number;
}

export interface AgentTaskState {
  task_id: string;
  user_query: string;
  status: string;
  assigned_specialist: string;
  plan: string[];
  findings: string[];
  recommendations: string[];
  tool_history: Array<{ tool_name: string; duration_ms: number }>;
}

export type TabType = 
  | 'overview' 
  | 'trends' 
  | 'forecasting' 
  | 'products' 
  | 'customers' 
  | 'geo' 
  | 'quality' 
  | 'agents';
