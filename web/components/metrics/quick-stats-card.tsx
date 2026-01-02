"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Target, Calendar } from "lucide-react";

interface QuickStatsCardProps {
    metrics: {
        hit_rate: number | null;
        avg_up: number | null;
        avg_down: number | null;
        best_month: number | null;
        worst_month: number | null;
    };
    name: string;
    className?: string;
}

function formatPercent(value: number | null): string {
    if (value === null) return "—";
    const sign = value >= 0 ? "+" : "";
    return `${sign}${(value * 100).toFixed(1)}%`;
}

function StatRow({
    icon: Icon,
    label,
    value,
    valueClass = ""
}: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    value: string;
    valueClass?: string;
}) {
    return (
        <div className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Icon className="h-4 w-4" />
                <span>{label}</span>
            </div>
            <span className={`font-medium ${valueClass}`}>{value}</span>
        </div>
    );
}

export function QuickStatsCard({ metrics, name, className }: QuickStatsCardProps) {
    const hitRatePercent = metrics.hit_rate !== null
        ? `${(metrics.hit_rate * 100).toFixed(0)}%`
        : "—";

    return (
        <Card className={className}>
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium">Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
                <StatRow
                    icon={Target}
                    label="Hit Rate"
                    value={hitRatePercent}
                    valueClass={metrics.hit_rate !== null && metrics.hit_rate >= 0.5
                        ? "text-emerald-500"
                        : "text-red-500"}
                />

                <StatRow
                    icon={TrendingUp}
                    label="Avg Up Month"
                    value={formatPercent(metrics.avg_up)}
                    valueClass="text-emerald-500"
                />

                <StatRow
                    icon={TrendingDown}
                    label="Avg Down Month"
                    value={formatPercent(metrics.avg_down)}
                    valueClass="text-red-500"
                />

                <div className="border-t border-border/50 my-2" />

                <StatRow
                    icon={Calendar}
                    label="Best Month"
                    value={formatPercent(metrics.best_month)}
                    valueClass="text-emerald-500"
                />

                <StatRow
                    icon={Calendar}
                    label="Worst Month"
                    value={formatPercent(metrics.worst_month)}
                    valueClass="text-red-500"
                />
            </CardContent>
        </Card>
    );
}
