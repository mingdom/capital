"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPercent, formatNumber, getValueColor } from "@/lib/data";
import { PerformanceMetrics } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info } from "lucide-react";

interface MetricCardProps {
    title: string;
    value: number | null;
    format?: "percent" | "number";
    decimals?: number;
    description?: string;
    subtitle?: string;
    colorize?: boolean;
    className?: string;
}

export function MetricCard({
    title,
    value,
    format = "percent",
    decimals = 1,
    description,
    subtitle,
    colorize = true,
    className,
}: MetricCardProps) {
    const formattedValue =
        format === "percent"
            ? formatPercent(value, decimals)
            : formatNumber(value, decimals);

    const valueColorClass = colorize ? getValueColor(value) : "text-foreground";

    return (
        <Card className={cn("relative", className)}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    {title}
                </CardTitle>
                {description && (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger>
                                <Info className="h-4 w-4 text-muted-foreground/50" />
                            </TooltipTrigger>
                            <TooltipContent className="max-w-xs">
                                <p className="text-sm">{description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )}
            </CardHeader>
            <CardContent>
                <div className={cn("text-2xl font-bold tracking-tight", valueColorClass)}>
                    {formattedValue}
                </div>
                {subtitle && (
                    <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
                )}
            </CardContent>
        </Card>
    );
}

interface PerformanceMetricsGridProps {
    metrics: PerformanceMetrics;
    name: string;
}

export function PerformanceMetricsGrid({ metrics, name }: PerformanceMetricsGridProps) {
    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
            <MetricCard
                title="CAGR"
                value={metrics.cagr}
                description="Compound Annual Growth Rate - annualized return since inception"
            />
            <MetricCard
                title="1Y"
                value={metrics.one_year}
                description="Trailing 12-month compounded return"
            />
            <MetricCard
                title="YTD"
                value={metrics.ytd}
                description="Year-to-date return"
            />
            <MetricCard
                title="3M"
                value={metrics.three_month}
                description="Trailing 3-month compounded return"
            />
            <MetricCard
                title="Sharpe"
                value={metrics.sharpe}
                format="number"
                decimals={2}
                colorize={false}
                description="Risk-adjusted return vs risk-free rate (higher is better)"
            />
            <MetricCard
                title="Sortino"
                value={metrics.sortino}
                format="number"
                decimals={2}
                colorize={false}
                description="Risk-adjusted return considering only downside volatility (higher is better)"
            />
            <MetricCard
                title="Max Drawdown"
                value={metrics.max_drawdown}
                description="Largest peak-to-trough decline (monthly basis)"
            />
        </div>
    );
}
