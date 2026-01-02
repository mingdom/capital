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
  return (
    <header className="border-b border-border/50 bg-card/60 backdrop-blur-md sticky top-0 z-50 transition-all duration-300">
      <div className="container mx-auto px-4 py-2.5 md:py-4">
        <div className="flex flex-row items-center justify-between">
          <div className="flex flex-col">
            <h1 className="text-lg md:text-2xl font-bold tracking-tight">
              Mingdom Capital
            </h1>
            <p className="hidden md:block text-sm text-muted-foreground">
              Portfolio Performance Dashboard
            </p>
          </div>

          <div className="flex items-center gap-4">
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
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const ampm = hours >= 12 ? "PM" : "AM";
    const hour12 = hours % 12 || 12;
    return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()} ${hour12}:${minutes} ${ampm}`;
  };

  const meta = getPortfolioMeta("Mingdom");

  return (
    <footer className="border-t border-border/50 py-10 md:py-16 mt-16 mb-8">
      <div className="flex flex-col gap-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
              Portfolio
            </h3>
            <div className="flex flex-col gap-2.5 text-sm text-muted-foreground">
              <p className="font-medium text-foreground">Mingdom Capital Dashboard</p>
              {meta.url && (
                <a
                  href={meta.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-primary hover:underline hover:text-primary/80 transition-colors"
                >
                  View on SavvyTrader
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              )}
              <p className="max-w-xs leading-relaxed">
                Automated performance tracking and risk analytics for managed capital.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
              System Status
            </h3>
            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <div className="flex justify-between md:justify-start md:gap-4">
                <span className="opacity-70">Analysis:</span>
                <span className="text-foreground">{mounted ? formatDate(data.generated_at) : "Loading..."}</span>
              </div>
              <div className="flex justify-between md:justify-start md:gap-4">
                <span className="opacity-70">Data to:</span>
                <span className="text-foreground">{data.last_period || "Latest"}</span>
              </div>
              <div className="flex justify-between md:justify-start md:gap-4">
                <span className="opacity-70">Risk-Free:</span>
                <span className="text-foreground">{(data.annual_rf * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-border/20 flex flex-col md:flex-row justify-between items-center gap-6 text-xs text-muted-foreground/60">
          <p>© {new Date().getFullYear()} Mingdom Capital. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/mingdom/capital"
              className="hover:text-muted-foreground transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <span className="hidden md:inline">•</span>
            <p>
              Powered by{" "}
              <span className="text-muted-foreground/80">Mingdom Capital Analytics</span>
            </p>
          </div>
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

      {/* Sortino Ratio */}
      <Card>
        <CardContent className="p-4 md:p-6">
          <div className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-1 md:mb-2 text-nowrap">
            Sortino Ratio
            <InfoTooltip content={METRIC_INFO.sortino} />
          </div>
          <div className="text-xl md:text-3xl font-bold">
            {metrics.sortino ? metrics.sortino.toFixed(2) : "—"}
          </div>
          <p className="text-[10px] md:text-xs text-muted-foreground mt-1 text-nowrap overflow-hidden text-ellipsis">Downside risk-adjusted</p>
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
  const wealthData = toCumulativeWealth(data.monthly_returns, chartSeries);
  const timeSeriesData = toTimeSeries(data.monthly_returns, [selectedPortfolio]);
  const metrics = data.performance[selectedPortfolio];
  const riskMetrics = data.risk[selectedPortfolio];

  return (
    <div className="min-h-screen bg-background">
      <Header data={data} />

      <main className="container mx-auto px-4 py-6 md:py-8 space-y-6 md:space-y-8">
        {/* Portfolio Selector - only show if multiple portfolios */}
        {data.portfolios.length > 1 && (
          <div className="flex items-center gap-4">
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
          </div>
        )}

        {/* Hero Metrics */}
        <HeroMetrics data={data} portfolio={selectedPortfolio} />

        {/* Benchmark Selector */}
        <BenchmarkSelector
          benchmarks={data.benchmarks}
          selected={selectedBenchmarks}
          onChange={setSelectedBenchmarks}
        />

        {/* Growth Section */}
        <Section title="Growth">
          <PerformanceChart
            data={wealthData}
            series={chartSeries}
            title={`${selectedPortfolio} Growth (Growth of $100)`}
          />
        </Section>

        {/* Returns Section */}
        <Section title="Returns">
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

        {/* Risk Section */}
        <Section title="Risk">
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

        {/* Comparison Section */}
        <Section title="Comparison">
          <ComparisonTable
            performance={data.performance}
            portfolios={data.portfolios}
            benchmarks={data.benchmarks}
          />
        </Section>

        {/* Footer */}
        <DashboardFooter data={data} />
      </main>
    </div>
  );
}
