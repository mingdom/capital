"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Target, Calendar, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { InfoTooltip, METRIC_INFO } from "@/components/ui/info-tooltip";

interface QuickStatsCardProps {
    metrics: {
        hit_rate: number | null;
        avg_up: number | null;
        avg_down: number | null;
        best_month: number | null;
        worst_month: number | null;
        up_capture: number | null;
        down_capture: number | null;
    };
    name: string;
    className?: string;
}

function formatPercent(value: number | null): string {
    if (value === null) return "—";
    const sign = value >= 0 ? "+" : "";
    return `${sign}${(value * 100).toFixed(1)}%`;
}

function formatCapturePercent(value: number | null): string {
    if (value === null) return "—";
    return `${(value * 100).toFixed(0)}%`;
}

function StatRow({
    icon: Icon,
    label,
    value,
    valueClass = "",
    info
}: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    value: string;
    valueClass?: string;
    info?: string;
}) {
    return (
        <div className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Icon className="h-4 w-4" />
                <span>{label}</span>
                {info && <InfoTooltip content={info} />}
            </div>
            <span className={`font-medium ${valueClass}`}>{value}</span>
        </div>
    );
}

export function QuickStatsCard({ metrics, name, className }: QuickStatsCardProps) {
    const hitRatePercent = metrics.hit_rate !== null
        ? `${(metrics.hit_rate * 100).toFixed(0)}%`
        : "—";

    // Up capture > 100% is good (capturing more upside)
    // Down capture < 100% is good (losing less in downturns)
    const upCaptureGood = metrics.up_capture !== null && metrics.up_capture >= 1;
    const downCaptureGood = metrics.down_capture !== null && metrics.down_capture < 1;

    return (
        <Card className={`${className} h-full flex flex-col`}>
            <CardContent className="p-4 flex-1 flex flex-col justify-between space-y-0 text-sm">
                <StatRow
                    icon={Target}
                    label="Hit Rate"
                    value={hitRatePercent}
                    valueClass={metrics.hit_rate !== null && metrics.hit_rate >= 0.5
                        ? "text-emerald-500"
                        : "text-red-500"}
                    info={METRIC_INFO.hit_rate}
                />

                <StatRow
                    icon={TrendingUp}
                    label="Avg Up Month"
                    value={formatPercent(metrics.avg_up)}
                    valueClass="text-emerald-500"
                    info={METRIC_INFO.avg_up}
                />

                <StatRow
                    icon={TrendingDown}
                    label="Avg Down Month"
                    value={formatPercent(metrics.avg_down)}
                    valueClass="text-red-500"
                    info={METRIC_INFO.avg_down}
                />

                <div className="border-t border-border/50 my-2" />

                <StatRow
                    icon={ArrowUpRight}
                    label="Up Capture"
                    value={formatCapturePercent(metrics.up_capture)}
                    valueClass={upCaptureGood ? "text-emerald-500" : "text-amber-500"}
                    info={METRIC_INFO.up_capture}
                />

                <StatRow
                    icon={ArrowDownRight}
                    label="Down Capture"
                    value={formatCapturePercent(metrics.down_capture)}
                    valueClass={downCaptureGood ? "text-emerald-500" : "text-red-500"}
                    info={METRIC_INFO.down_capture}
                />

                <div className="border-t border-border/50 my-2" />

                <StatRow
                    icon={Calendar}
                    label="Best Month"
                    value={formatPercent(metrics.best_month)}
                    valueClass="text-emerald-500"
                    info={METRIC_INFO.best_month}
                />

                <StatRow
                    icon={Calendar}
                    label="Worst Month"
                    value={formatPercent(metrics.worst_month)}
                    valueClass="text-red-500"
                    info={METRIC_INFO.worst_month}
                />
            </CardContent>
        </Card>
    );
}
