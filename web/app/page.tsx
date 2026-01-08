"use client";

import { useEffect, useState } from "react";
import { PortfolioData } from "@/lib/types";
import { loadPortfolioData, toCumulativeWealth, toTimeSeries } from "@/lib/data";
import { getPortfolioMeta } from "@/lib/portfolio-meta";
import { MetricCard } from "@/components/metrics/metric-card";
import { ComparisonTable } from "@/components/metrics/comparison-table";
import { RiskMetricsCard } from "@/components/metrics/risk-metrics-card";
import { QuickStatsCard } from "@/components/metrics/quick-stats-card";
import { PerformanceChart } from "@/components/charts/performance-chart";
import { MonthlyReturnsChart } from "@/components/charts/monthly-returns-chart";
import { Section } from "@/components/layout/section";
import { InfoTooltip, METRIC_INFO } from "@/components/ui/info-tooltip";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { TrendingUp, Activity, AlertTriangle, ExternalLink } from "lucide-react";
import { StockPerformanceSection } from "@/components/holdings/stock-performance-section";
import { motion } from "framer-motion";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 }
};

function LoadingSkeleton() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <Skeleton className="h-[450px]" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Skeleton className="h-[400px]" />
        <Skeleton className="h-[400px]" />
      </div>
    </div>
  );
}

function Header({ data }: { data: PortfolioData }) {
  const meta = getPortfolioMeta("Mingdom");

  return (
    <header className="border-b border-border/50 bg-card/60 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex flex-row items-center justify-between">
          <div className="flex flex-col">
            <h1 className="text-xl font-bold tracking-tight">
              Mingdom Capital
            </h1>
          </div>

          <div className="flex items-center gap-3 md:gap-4">
            {meta.url && (
              <a
                href={meta.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-primary hover:text-primary/80 border border-primary/20 hover:border-primary/40 rounded-md transition-colors"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Follow Live Trades</span>
                <span className="sm:hidden">Follow</span>
              </a>
            )}
            {data.warnings.length > 0 && (
              <Badge variant="destructive" className="gap-1 scale-90 md:scale-100">
                <AlertTriangle className="h-3 w-3" />
                <span className="hidden sm:inline">{data.warnings.length} warning{data.warnings.length > 1 ? "s" : ""}</span>
                <span className="sm:hidden">{data.warnings.length}</span>
              </Badge>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

function DashboardFooter({ data }: { data: PortfolioData }) {
  const formatDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split("-").map(Number);
    return `${month}.${day}.${year}`;
  };

  const formatPeriodDate = (period: string) => {
    if (!period) return "latest available data";
    const [year, month] = period.split("-").map(Number);
    const date = new Date(year, month, 0); // Last day of month
    const monthNum = date.getMonth() + 1;
    const dayNum = date.getDate();
    return `${monthNum}.${dayNum}.${year}`;
  };

  // Use latest_date if available, otherwise fall back to last_period
  const displayDate = (data as any).latest_date
    ? formatDate((data as any).latest_date)
    : data.last_period ? formatPeriodDate(data.last_period) : "latest available data";

  return (
    <footer className="border-t border-border/40 py-8 mt-12 mb-8 text-xs text-muted-foreground/60">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <p>© {new Date().getFullYear()} Mingdom Capital. All rights reserved.</p>
          <p className="text-center">
            Data as of {displayDate}. Risk-adjusted metrics calculated using {(data.annual_rf * 100).toFixed(1)}% risk-free rate.
          </p>
        </div>
      </div>
    </footer>
  );
}

function HeroMetrics({ data, portfolio }: { data: PortfolioData; portfolio: string }) {
  const metrics = data.performance[portfolio];

  if (!metrics) return null;

  // Determine if YTD has meaningful data (show 1Y instead early in the year)
  // YTD is meaningful if: it exists and is not nearly zero, OR we're past Q1
  const currentMonth = new Date().getMonth(); // 0 = Jan, 1 = Feb, etc.
  const ytdMeaningful = currentMonth >= 2 || (metrics.ytd !== null && Math.abs(metrics.ytd) > 0.01);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
      {/* CAGR - Always show */}
      <Card className="relative overflow-hidden">
        <CardContent className="p-4 md:p-6">
          <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-1 md:mb-2 text-nowrap">
            <TrendingUp className="h-3 w-3 md:h-4 md:w-4" />
            Annual Return
            <InfoTooltip content={METRIC_INFO.cagr} />
          </div>
          <div className={`text-xl md:text-3xl font-bold ${metrics.cagr && metrics.cagr > 0 ? "text-emerald-500" : "text-red-500"}`}>
            {metrics.cagr ? `${(metrics.cagr * 100).toFixed(1)}%` : "—"}
          </div>
          <p className="text-[10px] md:text-xs text-muted-foreground mt-1">CAGR since inception</p>
        </CardContent>
        <div className={`absolute inset-0 opacity-5 ${metrics.cagr && metrics.cagr > 0 ? "bg-emerald-500" : "bg-red-500"}`} />
      </Card>

      {/* YTD or 1Y - Conditional based on time of year */}
      {ytdMeaningful ? (
        <Card className="relative overflow-hidden">
          <CardContent className="p-4 md:p-6">
            <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-1 md:mb-2 text-nowrap">
              <Activity className="h-3 w-3 md:h-4 md:w-4" />
              Year to Date
              <InfoTooltip content={METRIC_INFO.ytd} />
            </div>
            <div className={`text-xl md:text-3xl font-bold ${metrics.ytd && metrics.ytd > 0 ? "text-emerald-500" : "text-red-500"}`}>
              {metrics.ytd ? `${(metrics.ytd * 100).toFixed(1)}%` : "—"}
            </div>
            <p className="text-[10px] md:text-xs text-muted-foreground mt-1">{data.current_year} performance</p>
          </CardContent>
          <div className={`absolute inset-0 opacity-5 ${metrics.ytd && metrics.ytd > 0 ? "bg-emerald-500" : "bg-red-500"}`} />
        </Card>
      ) : (
        <Card className="relative overflow-hidden">
          <CardContent className="p-4 md:p-6">
            <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-1 md:mb-2 text-nowrap">
              <Activity className="h-3 w-3 md:h-4 md:w-4" />
              1 Year
              <InfoTooltip content={METRIC_INFO.one_year} />
            </div>
            <div className={`text-xl md:text-3xl font-bold ${metrics.one_year && metrics.one_year > 0 ? "text-emerald-500" : "text-red-500"}`}>
              {metrics.one_year ? `${(metrics.one_year * 100).toFixed(1)}%` : "—"}
            </div>
            <p className="text-[10px] md:text-xs text-muted-foreground mt-1">Trailing 12 months</p>
          </CardContent>
          <div className={`absolute inset-0 opacity-5 ${metrics.one_year && metrics.one_year > 0 ? "bg-emerald-500" : "bg-red-500"}`} />
        </Card>
      )}

      {/* Beta vs SPY */}
      <Card>
        <CardContent className="p-4 md:p-6">
          <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-1 md:mb-2 text-nowrap">
            Beta
            <InfoTooltip content={METRIC_INFO.beta_spy} />
          </div>
          <div className="text-xl md:text-3xl font-bold">
            {data.risk[portfolio]?.beta_spy ? data.risk[portfolio].beta_spy.toFixed(2) : "—"}
          </div>
          <p className="text-[10px] md:text-xs text-muted-foreground mt-1">vs S&P 500</p>
        </CardContent>
      </Card>

      {/* Sharpe Ratio */}
      <Card>
        <CardContent className="p-4 md:p-6">
          <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-1 md:mb-2 text-nowrap">
            Sharpe Ratio
            <InfoTooltip content={METRIC_INFO.sharpe} />
          </div>
          <div className="text-xl md:text-3xl font-bold">
            {metrics.sharpe ? metrics.sharpe.toFixed(2) : "—"}
          </div>
          <p className="text-[10px] md:text-xs text-muted-foreground mt-1">Risk-adjusted return</p>
        </CardContent>
      </Card>
    </div>
  );
}

function BenchmarkSelector({
  benchmarks,
  selected,
  onChange
}: {
  benchmarks: string[];
  selected: string[];
  onChange: (benchmarks: string[]) => void;
}) {
  const toggleBenchmark = (benchmark: string) => {
    if (selected.includes(benchmark)) {
      onChange(selected.filter(b => b !== benchmark));
    } else {
      onChange([...selected, benchmark]);
    }
  };

  return (
    <div className="flex flex-wrap gap-4 items-center">
      <span className="text-sm font-medium text-muted-foreground">Compare with:</span>
      {benchmarks.map((benchmark) => (
        <div key={benchmark} className="flex items-center space-x-2">
          <Checkbox
            id={`benchmark-${benchmark}`}
            checked={selected.includes(benchmark)}
            onCheckedChange={() => toggleBenchmark(benchmark)}
          />
          <Label
            htmlFor={`benchmark-${benchmark}`}
            className="text-sm font-medium cursor-pointer"
          >
            {benchmark}
          </Label>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedPortfolio, setSelectedPortfolio] = useState<string>("Mingdom");
  const [selectedBenchmarks, setSelectedBenchmarks] = useState<string[]>(["SPY"]);

  // GOD_MODE: if not set, only show Mingdom portfolio (public mode)
  // Set NEXT_PUBLIC_GOD_MODE=true in Vercel to show all portfolios
  const isGodMode = process.env.NEXT_PUBLIC_GOD_MODE === "true";

  useEffect(() => {
    loadPortfolioData()
      .then((d) => {
        // Filter portfolios based on GOD_MODE
        const filteredData = {
          ...d,
          portfolios: isGodMode ? d.portfolios : d.portfolios.filter(p => p === "Mingdom"),
        };

        setData(filteredData);
        if (filteredData.portfolios.length > 0) {
          setSelectedPortfolio(filteredData.portfolios[0]);
        }
      })
      .catch((err) => setError(err.message));
  }, [isGodMode]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h2 className="text-lg font-semibold mb-2">Failed to load data</h2>
            <p className="text-sm text-muted-foreground">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <LoadingSkeleton />
        </div>
      </div>
    );
  }

  const chartSeries = [selectedPortfolio, ...selectedBenchmarks];
  // Use weekly returns if available for more granular chart, otherwise fall back to monthly
  const returnsData = (data as any).weekly_returns && Object.keys((data as any).weekly_returns).length > 0
    ? (data as any).weekly_returns
    : data.monthly_returns;
  const wealthData = toCumulativeWealth(returnsData, chartSeries);
  const timeSeriesData = toTimeSeries(data.monthly_returns, [selectedPortfolio]);
  const metrics = data.performance[selectedPortfolio];
  const riskMetrics = data.risk[selectedPortfolio];

  return (
    <div className="min-h-screen bg-background">
      <Header data={data} />

      <main className="container mx-auto px-4 pt-4 md:pt-6 pb-6 md:pb-8 space-y-6 md:space-y-8">
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-6 md:space-y-8"
        >
          {/* Portfolio Selector - only show if multiple portfolios */}
          {data.portfolios.length > 1 && (
            <motion.div variants={item} className="flex items-center gap-4">
              <span className="text-sm font-medium text-muted-foreground">Portfolio:</span>
              <Tabs value={selectedPortfolio} onValueChange={setSelectedPortfolio}>
                <TabsList>
                  {data.portfolios.map((p) => (
                    <TabsTrigger key={p} value={p} className="min-w-[120px]">
                      {p}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </motion.div>
          )}

          {/* Hero Metrics */}
          <motion.div variants={item}>
            <HeroMetrics data={data} portfolio={selectedPortfolio} />
          </motion.div>



          {/* Performance Section */}
          <motion.div variants={item}>
            <Section title="Performance" collapsible>
              <div className="space-y-4">
                <BenchmarkSelector
                  benchmarks={data.benchmarks}
                  selected={selectedBenchmarks}
                  onChange={setSelectedBenchmarks}
                />
                <PerformanceChart
                  data={wealthData}
                  series={chartSeries}
                  title="Portfolio Growth"
                />
              </div>
            </Section>
          </motion.div>

          {/* Returns Section */}
          <motion.div variants={item}>
            <Section title="Returns" collapsible>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <MonthlyReturnsChart
                    data={timeSeriesData}
                    series={selectedPortfolio}
                    title={`${selectedPortfolio} Monthly Returns`}
                  />
                </div>
                {riskMetrics && (
                  <QuickStatsCard
                    metrics={riskMetrics}
                    name={selectedPortfolio}
                  />
                )}
              </div>
            </Section>
          </motion.div>


          {/* Risk Section */}
          <motion.div variants={item}>
            <Section title="Risk" collapsible>
              {riskMetrics && (
                <RiskMetricsCard
                  metrics={riskMetrics}
                  name={selectedPortfolio}
                  performanceMetrics={data.performance[selectedPortfolio]}
                  benchmarkMetrics={data.risk}
                  benchmarkPerformance={data.performance}
                  benchmarks={data.benchmarks}
                />
              )}
            </Section>
          </motion.div>

          {/* Holdings Performance Section - Mingdom only */}
          {selectedPortfolio === "Mingdom" && (
            <motion.div variants={item}>
              <Section title="Holdings" collapsible defaultExpanded={true}>
                <StockPerformanceSection />
              </Section>
            </motion.div>
          )}

          {/* Comparison Section */}
          <motion.div variants={item}>
            <Section title="Comparison" collapsible>
              <ComparisonTable
                performance={data.performance}
                selectedPortfolio={selectedPortfolio}
                benchmarks={data.benchmarks}
              />
            </Section>
          </motion.div>
        </motion.div>


        {/* Footer */}
        <DashboardFooter data={data} />
      </main>
    </div>
  );
}
