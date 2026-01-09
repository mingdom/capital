"use client";

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PerformanceMetrics } from "@/lib/types";
import { formatPercent, formatNumber, getValueColor } from "@/lib/data";
import { cn } from "@/lib/utils";

interface ComparisonTableProps {
    performance: Record<string, PerformanceMetrics>;
    selectedPortfolio: string;
    benchmarks: string[];
    className?: string;
}

export function ComparisonTable({
    performance,
    selectedPortfolio,
    benchmarks,
    className,
}: ComparisonTableProps) {
    const allSeries = [selectedPortfolio, ...benchmarks];

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="text-lg font-medium">Performance Comparison</CardTitle>
            </CardHeader>
            <CardContent>
                {/* Desktop View: Table */}
                <div className="hidden md:block">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[140px]">Portfolio</TableHead>
                                <TableHead className="text-right">CAGR</TableHead>
                                <TableHead className="text-right">1Y</TableHead>
                                <TableHead className="text-right">YTD</TableHead>
                                <TableHead className="text-right">3M</TableHead>
                                <TableHead className="text-right">Max DD</TableHead>
                                <TableHead className="text-right">Sharpe</TableHead>
                                <TableHead className="text-right">Sortino</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {allSeries.map((name) => {
                                const metrics = performance[name];
                                if (!metrics) return null;

                                const isMainPortfolio = name === selectedPortfolio;

                                return (
                                    <TableRow
                                        key={name}
                                        className={cn(
                                            "transition-colors",
                                            isMainPortfolio ? "bg-primary/[0.03] hover:bg-primary/[0.05] border-l-2 border-l-primary font-bold" : "hover:bg-muted/10 text-muted-foreground/80"
                                        )}
                                    >
                                        <TableCell className="font-medium whitespace-nowrap">
                                            {name}
                                        </TableCell>
                                        <TableCell className={cn("text-right font-mono", getValueColor(metrics.cagr))}>
                                            {formatPercent(metrics.cagr)}
                                        </TableCell>
                                        <TableCell className={cn("text-right font-mono", getValueColor(metrics.one_year))}>
                                            {formatPercent(metrics.one_year)}
                                        </TableCell>
                                        <TableCell className={cn("text-right font-mono", getValueColor(metrics.ytd))}>
                                            {formatPercent(metrics.ytd)}
                                        </TableCell>
                                        <TableCell className={cn("text-right font-mono", getValueColor(metrics.three_month))}>
                                            {formatPercent(metrics.three_month)}
                                        </TableCell>
                                        <TableCell className={cn("text-right font-mono", getValueColor(metrics.max_drawdown))}>
                                            {formatPercent(metrics.max_drawdown)}
                                        </TableCell>
                                        <TableCell className="text-right font-mono text-muted-foreground">
                                            {formatNumber(metrics.sharpe, 2)}
                                        </TableCell>
                                        <TableCell className="text-right font-mono text-muted-foreground">
                                            {formatNumber(metrics.sortino, 2)}
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </div>

                {/* Mobile View: Card List */}
                <div className="md:hidden space-y-3">
                    {allSeries.map((name) => {
                        const metrics = performance[name];
                        if (!metrics) return null;

                        const isMainPortfolio = name === selectedPortfolio;

                        return (
                            <div
                                key={name}
                                className={cn(
                                    "p-4 rounded-lg border transition-all",
                                    isMainPortfolio
                                        ? "bg-primary/[0.03] border-primary/30 ring-1 ring-primary/20"
                                        : "bg-muted/5 border-border/50"
                                )}
                            >
                                <div className="flex justify-between items-center mb-3">
                                    <span className={cn("font-bold text-base", isMainPortfolio ? "text-primary" : "text-foreground")}>
                                        {name}
                                    </span>
                                    {isMainPortfolio && (
                                        <Badge variant="outline" className="text-[10px] uppercase tracking-wider py-0 px-1.5 h-5 border-primary/30 text-primary bg-primary/5">
                                            Active
                                        </Badge>
                                    )}
                                </div>

                                <div className="grid grid-cols-3 gap-2">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-muted-foreground uppercase font-semibold">CAGR</span>
                                        <span className={cn("text-sm font-mono font-bold", getValueColor(metrics.cagr))}>
                                            {formatPercent(metrics.cagr)}
                                        </span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-muted-foreground uppercase font-semibold">1Y</span>
                                        <span className={cn("text-sm font-mono font-bold", getValueColor(metrics.one_year))}>
                                            {formatPercent(metrics.one_year)}
                                        </span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-muted-foreground uppercase font-semibold">Max DD</span>
                                        <span className={cn("text-sm font-mono font-bold", getValueColor(metrics.max_drawdown))}>
                                            {formatPercent(metrics.max_drawdown)}
                                        </span>
                                    </div>
                                    <div className="flex flex-col pt-2 opacity-80">
                                        <span className="text-[10px] text-muted-foreground uppercase">YTD</span>
                                        <span className={cn("text-xs font-mono font-medium", getValueColor(metrics.ytd))}>
                                            {formatPercent(metrics.ytd)}
                                        </span>
                                    </div>
                                    <div className="flex flex-col pt-2 opacity-80">
                                        <span className="text-[10px] text-muted-foreground uppercase">Sharpe</span>
                                        <span className="text-xs font-mono text-foreground">
                                            {formatNumber(metrics.sharpe, 2)}
                                        </span>
                                    </div>
                                    <div className="flex flex-col pt-2 opacity-80">
                                        <span className="text-[10px] text-muted-foreground uppercase">Sortino</span>
                                        <span className="text-xs font-mono text-foreground">
                                            {formatNumber(metrics.sortino, 2)}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
