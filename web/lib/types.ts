/**
 * Type definitions for portfolio data exported from Python.
 */

export interface PortfolioData {
  generated_at: string;
  current_year: number;
  annual_rf: number;
  last_period: string | null;
  portfolios: string[];
  benchmarks: string[];
  monthly_returns: Record<string, Record<string, number>>;
  performance: Record<string, PerformanceMetrics>;
  risk: Record<string, RiskMetrics>;
  windows: Record<string, DataWindow>;
  freq_risk: Record<string, FrequencyRiskMetrics>;
  warnings: string[];
}

export interface PerformanceMetrics {
  cagr: number | null;
  one_year: number | null;
  three_month: number | null;
  ytd: number | null;
  sharpe: number | null;
  sortino: number | null;
  max_drawdown: number | null;
}

export interface RiskMetrics {
  volatility: number | null;
  downside_dev: number | null;
  max_drawdown: number | null;
  drawdown_duration: number | null;
  var_95: number | null;
  cvar_95: number | null;
  var_99: number | null;
  cvar_99: number | null;
  hit_rate: number | null;
  avg_up: number | null;
  avg_down: number | null;
  beta_spy: number | null;
  corr_spy: number | null;
  worst_month: number | null;
  best_month: number | null;
  up_capture: number | null;
  down_capture: number | null;
}

export interface DataWindow {
  start: string | null;
  end: string | null;
  count: number;
}

export interface PeriodRiskMetrics {
  volatility: number | null;
  sharpe: number | null;
  sortino: number | null;
  var_95: number | null;
  cvar_95: number | null;
}

export interface FrequencyRiskMetrics {
  daily: PeriodRiskMetrics;
  weekly: PeriodRiskMetrics;
  monthly: PeriodRiskMetrics;
}

/**
 * Processed time series data point for charts.
 */
export interface TimeSeriesPoint {
  period: string;
  date: Date;
  [key: string]: string | number | Date;
}

/**
 * Cumulative wealth index data point.
 */
export interface WealthPoint {
  period: string;
  date: Date;
  [key: string]: string | number | Date;
}
