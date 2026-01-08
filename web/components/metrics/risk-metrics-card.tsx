"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RiskMetrics as RiskMetricsType, PerformanceMetrics } from "@/lib/types";
import { formatPercent, formatNumber } from "@/lib/data";
import { Separator } from "@/components/ui/separator";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info, TrendingUp, TrendingDown } from "lucide-react";

interface RiskMetricsCardProps {
    metrics: RiskMetricsType;
    name: string;
    performanceMetrics?: PerformanceMetrics;
    benchmarkMetrics?: Record<string, RiskMetricsType>;
    benchmarkPerformance?: Record<string, PerformanceMetrics>;
    benchmarks?: string[];
    className?: string;
}

function MetricRow({
    label,
    value,
    compareValue,
    description,
    higherIsBetter = false,
}: {
    label: string;
    value: string;
    compareValue?: string;
    description?: string;
    higherIsBetter?: boolean;
}) {
    const showComparison = compareValue && compareValue !== "—" && value !== "—";

    // Determine if portfolio is better than benchmark
    let isBetter: boolean | null = null;
    if (showComparison) {
        const portfolioNum = parseFloat(value.replace(/[^0-9.-]/g, ''));
        const benchmarkNum = parseFloat(compareValue.replace(/[^0-9.-]/g, ''));
        if (!isNaN(portfolioNum) && !isNaN(benchmarkNum)) {
            isBetter = higherIsBetter
                ? portfolioNum > benchmarkNum
                : Math.abs(portfolioNum) < Math.abs(benchmarkNum);
        }
    }

    return (
        <div className="flex justify-between items-center py-2">
            <div className="flex items-center gap-1">
                <span className="text-sm text-muted-foreground">{label}</span>
                {description && (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger>
                                <Info className="h-3 w-3 text-muted-foreground/50" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-xs">
                                <p className="text-sm">{description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )}
            </div>
            <div className="flex items-center gap-3">
                <span className="text-sm font-mono font-medium">{value}</span>
                {showComparison && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <span className="font-mono">{compareValue}</span>
                        {isBetter !== null && (
                            isBetter ? (
                                <TrendingUp className="h-3 w-3 text-emerald-500" />
                            ) : (
                                <TrendingDown className="h-3 w-3 text-red-500" />
                            )
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export function RiskMetricsCard({
    metrics,
    name,
    performanceMetrics,
    benchmarkMetrics = {},
    benchmarkPerformance = {},
    benchmarks = [],
    className
}: RiskMetricsCardProps) {
    const [selectedBenchmark, setSelectedBenchmark] = useState<string>(
        benchmarks.includes("SPY") ? "SPY" : benchmarks[0] || ""
    );

    const compareMetrics = selectedBenchmark ? benchmarkMetrics[selectedBenchmark] : undefined;
    const comparePerformance = selectedBenchmark ? benchmarkPerformance[selectedBenchmark] : undefined;

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-medium">Risk Profile: {name}</CardTitle>
                    {benchmarks.length > 0 && (
                        <Select value={selectedBenchmark} onValueChange={setSelectedBenchmark}>
                            <SelectTrigger className="w-[140px] h-8">
                                <SelectValue placeholder="Compare with..." />
                            </SelectTrigger>
                            <SelectContent>
                                {benchmarks.map((benchmark) => (
                                    <SelectItem key={benchmark} value={benchmark}>
                                        vs {benchmark}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    )}
                </div>
            </CardHeader>
            <CardContent className="space-y-1">
                {/* Risk-Adjusted Ratios Section - Featured at top */}
                {performanceMetrics && (
                    <>
                        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                            Risk-Adjusted Returns
                        </div>
                        <MetricRow
                            label="Sharpe Ratio"
                            value={performanceMetrics.sharpe !== null ? performanceMetrics.sharpe.toFixed(2) : "—"}
                            compareValue={comparePerformance?.sharpe !== null && comparePerformance?.sharpe !== undefined
                                ? comparePerformance.sharpe.toFixed(2) : undefined}
                            description="Return per unit of total risk (volatility)"
                            higherIsBetter={true}
                        />
                        <MetricRow
                            label="Sortino Ratio"
                            value={performanceMetrics.sortino !== null ? performanceMetrics.sortino.toFixed(2) : "—"}
                            compareValue={comparePerformance?.sortino !== null && comparePerformance?.sortino !== undefined
                                ? comparePerformance.sortino.toFixed(2) : undefined}
                            description="Return per unit of downside risk only"
                            higherIsBetter={true}
                        />
                        <Separator className="my-4" />
                    </>
                )}

                {/* Market Relationship Section - Moved Up */}
                {(metrics.beta_spy !== null || metrics.corr_spy !== null) && (
                    <>
                        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                            Market Relationship
                        </div>
                        <MetricRow
                            label="Beta (SPY)"
                            value={formatNumber(metrics.beta_spy, 2)}
                            compareValue={compareMetrics ? formatNumber(compareMetrics.beta_spy, 2) : undefined}
                            description="Portfolio sensitivity to S&P 500 movements"
                        />
                        <MetricRow
                            label="Correlation (SPY)"
                            value={formatNumber(metrics.corr_spy, 2)}
                            compareValue={compareMetrics ? formatNumber(compareMetrics.corr_spy, 2) : undefined}
                            description="How closely returns move with S&P 500"
                        />
                        <Separator className="my-4" />
                    </>
                )}

                {/* Volatility Section */}
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                    Volatility
                </div>
                <MetricRow
                    label="Annualized Volatility"
                    value={formatPercent(metrics.volatility)}
                    compareValue={compareMetrics ? formatPercent(compareMetrics.volatility) : undefined}
                    description="Standard deviation of returns, annualized"
                    higherIsBetter={false}
                />
                <MetricRow
                    label="Downside Deviation"
                    value={formatPercent(metrics.downside_dev)}
                    compareValue={compareMetrics ? formatPercent(compareMetrics.downside_dev) : undefined}
                    description="Volatility of negative returns only"
                    higherIsBetter={false}
                />

                <Separator className="my-4" />

                {/* Drawdown Section */}
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                    Drawdown
                </div>
                <MetricRow
                    label="Max Drawdown"
                    value={formatPercent(metrics.max_drawdown)}
                    compareValue={compareMetrics ? formatPercent(compareMetrics.max_drawdown) : undefined}
                    description="Largest peak-to-trough decline"
                    higherIsBetter={false}
                />
                <MetricRow
                    label="Drawdown Duration"
                    value={metrics.drawdown_duration !== null ? `${metrics.drawdown_duration} mo` : "—"}
                    compareValue={compareMetrics && compareMetrics.drawdown_duration !== null ? `${compareMetrics.drawdown_duration} mo` : undefined}
                    description="Longest period below prior peak"
                    higherIsBetter={false}
                />

                <Separator className="my-4" />

                {/* VaR Section */}
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                    Value at Risk
                </div>
                <MetricRow
                    label="VaR (95%)"
                    value={formatPercent(metrics.var_95)}
                    compareValue={compareMetrics ? formatPercent(compareMetrics.var_95) : undefined}
                    description="Expected monthly loss exceeded 5% of the time"
                    higherIsBetter={false}
                />
                <MetricRow
                    label="CVaR (95%)"
                    value={formatPercent(metrics.cvar_95)}
                    compareValue={compareMetrics ? formatPercent(compareMetrics.cvar_95) : undefined}
                    description="Expected loss when VaR is exceeded"
                    higherIsBetter={false}
                />

                <Separator className="my-4" />

            </CardContent>
        </Card>
    );
}
