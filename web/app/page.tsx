"use client";

import { useEffect, useState, useMemo } from "react";
import { PortfolioData } from "@/lib/types";
import { loadPortfolioData, toCumulativeWealth, toTimeSeries } from "@/lib/data";
import { TimePeriod, filterMonthlyReturnsByPeriod, getPeriodLabel, hasSufficientData } from "@/lib/periods";
import { MetricCard } from "@/components/metrics/metric-card";
import { ComparisonTable } from "@/components/metrics/comparison-table";
import { RiskMetricsCard } from "@/components/metrics/risk-metrics-card";
import { PerformanceChart } from "@/components/charts/performance-chart";
import { MonthlyReturnsChart } from "@/components/charts/monthly-returns-chart";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { TrendingUp, Activity, AlertTriangle } from "lucide-react";

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
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const ampm = hours >= 12 ? "PM" : "AM";
    const hour12 = hours % 12 || 12;
    return `${month} ${day}, ${year} ${hour12}:${minutes} ${ampm}`;
  };

  const generatedDate = mounted ? formatDate(data.generated_at) : "Loading...";

  return (
    <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Mingdom Capital
            </h1>
            <p className="text-sm text-muted-foreground">
              Portfolio Performance Dashboard
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Last updated</p>
              <p className="text-sm font-medium">{generatedDate}</p>
            </div>
            {data.warnings.length > 0 && (
              <Badge variant="destructive" className="gap-1">
                <AlertTriangle className="h-3 w-3" />
                {data.warnings.length} warning{data.warnings.length > 1 ? "s" : ""}
              </Badge>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

function HeroMetrics({ data, portfolio }: { data: PortfolioData; portfolio: string }) {
  const metrics = data.performance[portfolio];

  if (!metrics) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card className="relative overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <TrendingUp className="h-4 w-4" />
            Annual Return
          </div>
          <div className={`text-3xl font-bold ${metrics.cagr && metrics.cagr > 0 ? "text-emerald-500" : "text-red-500"}`}>
            {metrics.cagr ? `${(metrics.cagr * 100).toFixed(1)}%` : "—"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">CAGR since inception</p>
        </CardContent>
        <div className={`absolute inset-0 opacity-5 ${metrics.cagr && metrics.cagr > 0 ? "bg-emerald-500" : "bg-red-500"}`} />
      </Card>

      <Card className="relative overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Activity className="h-4 w-4" />
            1 Year
          </div>
          <div className={`text-3xl font-bold ${metrics.one_year && metrics.one_year > 0 ? "text-emerald-500" : "text-red-500"}`}>
            {metrics.one_year ? `${(metrics.one_year * 100).toFixed(1)}%` : "—"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">Trailing 12 months</p>
        </CardContent>
        <div className={`absolute inset-0 opacity-5 ${metrics.one_year && metrics.one_year > 0 ? "bg-emerald-500" : "bg-red-500"}`} />
      </Card>

      <Card className="relative overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Activity className="h-4 w-4" />
            Year to Date
          </div>
          <div className={`text-3xl font-bold ${metrics.ytd && metrics.ytd > 0 ? "text-emerald-500" : "text-red-500"}`}>
            {metrics.ytd ? `${(metrics.ytd * 100).toFixed(1)}%` : "—"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">{data.current_year} performance</p>
        </CardContent>
        <div className={`absolute inset-0 opacity-5 ${metrics.ytd && metrics.ytd > 0 ? "bg-emerald-500" : "bg-red-500"}`} />
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="text-sm text-muted-foreground mb-2">Sortino Ratio</div>
          <div className="text-3xl font-bold">
            {metrics.sortino ? metrics.sortino.toFixed(2) : "—"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">Monthly, annualized</p>
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
  const [timePeriod, setTimePeriod] = useState<TimePeriod>("all");

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

  // Filter data by selected time period
  const filteredMonthlyReturns = useMemo(() => {
    if (!data) return {};
    return filterMonthlyReturnsByPeriod(data.monthly_returns, timePeriod, data.current_year);
  }, [data, timePeriod]);

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
  const wealthData = toCumulativeWealth(filteredMonthlyReturns, chartSeries);
  const timeSeriesData = toTimeSeries(filteredMonthlyReturns, [selectedPortfolio]);
  const metrics = data.performance[selectedPortfolio];
  const riskMetrics = data.risk[selectedPortfolio];

  return (
    <div className="min-h-screen bg-background">
      <Header data={data} />

      <main className="container mx-auto px-4 py-8 space-y-8">
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
        )}\n\n        {/* Time Period Selector */}\n        <div className="flex items-center gap-4">\n          <span className="text-sm font-medium text-muted-foreground">Period:</span>\n          <Tabs value={timePeriod} onValueChange={(v) => setTimePeriod(v as TimePeriod)}>\n            <TabsList>\n              <TabsTrigger value="ytd">YTD</TabsTrigger>\n              <TabsTrigger value="1y">1Y</TabsTrigger>\n              <TabsTrigger value="3y">3Y</TabsTrigger>\n              <TabsTrigger value="5y">5Y</TabsTrigger>\n              <TabsTrigger value="all">All</TabsTrigger>\n            </TabsList>\n          </Tabs>\n        </div>

        {/* Hero Metrics */}
        <HeroMetrics data={data} portfolio={selectedPortfolio} />

        {/* Benchmark Selector */}
        <BenchmarkSelector
          benchmarks={data.benchmarks}
          selected={selectedBenchmarks}
          onChange={setSelectedBenchmarks}
        />

        {/* Main Chart */}
        <PerformanceChart
          data={wealthData}
          series={chartSeries}
          title={`${selectedPortfolio} Growth - ${getPeriodLabel(timePeriod)} (Growth of $100)`}
        />

        {/* Analysis Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MonthlyReturnsChart
            data={timeSeriesData}
            series={selectedPortfolio}
            title={`${selectedPortfolio} Monthly Returns`}
          />
          {riskMetrics && (
            <RiskMetricsCard
              metrics={riskMetrics}
              name={selectedPortfolio}
              benchmarkMetrics={data.risk}
              benchmarks={data.benchmarks}
            />
          )}
        </div>

        {/* Comparison Table */}
        <ComparisonTable
          performance={data.performance}
          portfolios={data.portfolios}
          benchmarks={data.benchmarks}
        />

        {/* Footer */}
        <footer className="border-t border-border/50 pt-8 mt-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <p>
              Data as of {data.last_period || "—"} • Risk-free rate: {(data.annual_rf * 100).toFixed(1)}%
            </p>
            <p>
              Powered by{" "}
              <a
                href="https://github.com/mingdom/capital"
                className="underline underline-offset-4 hover:text-foreground"
                target="_blank"
                rel="noopener noreferrer"
              >
                Mingdom Capital Analytics
              </a>
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
