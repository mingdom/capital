"use client";

import { useState, useEffect } from "react";
import { HoldingsPerformanceData, StockPerformance } from "@/lib/types";
import { loadHoldingsPerformanceData, formatPercent, formatNumber, getValueColor } from "@/lib/data";
import { ConvictionHeatStrip } from "./conviction-heat-strip";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion, AnimatePresence } from "framer-motion";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";

export function StockPerformanceSection() {
    const [data, setData] = useState<HoldingsPerformanceData | null>(null);
    const [activePeriod, setActivePeriod] = useState<string>("3mo");
    const [loading, setLoading] = useState(true);
    const [sortConfig, setSortConfig] = useState<{ key: keyof StockPerformance | 'none', direction: 'asc' | 'desc' }>({
        key: 'period_return',
        direction: 'desc'
    });
    const [isTableExpanded, setIsTableExpanded] = useState(false);

    useEffect(() => {
        loadHoldingsPerformanceData()
            .then(setData)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="space-y-4">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-96 w-full" />
            </div>
        );
    }

    if (!data) return null;

    const currentPeriodData = data.periods[activePeriod];
    if (!currentPeriodData) return null;

    // Sorting logic
    const sortedHoldings = [...currentPeriodData.holdings].sort((a, b) => {
        if (sortConfig.key === 'none') return 0;

        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];

        if (typeof aValue === 'string' && typeof bValue === 'string') {
            return sortConfig.direction === 'asc'
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }

        if (typeof aValue === 'number' && typeof bValue === 'number') {
            return sortConfig.direction === 'asc'
                ? aValue - bValue
                : bValue - aValue;
        }

        return 0;
    });

    const handleSort = (key: keyof StockPerformance) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
        }));
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr + "T12:00:00");
        return new Intl.DateTimeFormat("en-US", {
            month: "short",
            day: "2-digit",
            year: "numeric",
        }).format(date);
    };

    const SortIcon = ({ column }: { column: keyof StockPerformance }) => {
        if (sortConfig.key !== column) return <div className="w-3 h-3 ml-1 opacity-20 group-hover:opacity-50">↕</div>;
        return <div className="w-3 h-3 ml-1 text-primary">{sortConfig.direction === 'desc' ? '↓' : '↑'}</div>;
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-end">
                <Tabs value={activePeriod} onValueChange={setActivePeriod}>
                    <TabsList className="bg-zinc-900/50 border border-white/5 h-8">
                        <TabsTrigger value="3mo" className="text-xs px-3">3MO</TabsTrigger>
                        <TabsTrigger value="ytd" className="text-xs px-3">YTD</TabsTrigger>
                        <TabsTrigger value="1y" className="text-xs px-3">1Y</TabsTrigger>
                    </TabsList>
                </Tabs>
            </div>

            <ConvictionHeatStrip performance={currentPeriodData} />

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center pt-2 border-t border-white/5">
                <p className="text-xs text-muted-foreground italic">
                    Price change of holdings, excluding transaction timing and cash flows.
                </p>
                <div className="flex items-center gap-2 mt-1 md:mt-0">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-zinc-500">Analysis Period:</span>
                    <span className="text-xs font-mono text-zinc-300">
                        {formatDate(currentPeriodData.start_date)} — {formatDate(currentPeriodData.end_date)}
                    </span>
                </div>
            </div>

            <div className="flex justify-center mt-2">
                <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-2 group"
                    onClick={() => setIsTableExpanded(!isTableExpanded)}
                >
                    {isTableExpanded ? (
                        <>
                            <ChevronUp className="h-3 w-3 transition-transform group-hover:-translate-y-0.5" />
                            Hide All Holdings
                        </>
                    ) : (
                        <>
                            <ChevronDown className="h-3 w-3 transition-transform group-hover:translate-y-0.5" />
                            View All Holdings ({sortedHoldings.length})
                        </>
                    )}
                </Button>
            </div>

            <AnimatePresence>
                {isTableExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
                        className="overflow-hidden"
                    >
                        <Card className="bg-zinc-950/40 border-white/5 overflow-hidden">
                            <CardContent className="p-0">
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead className="text-[10px] uppercase tracking-widest text-muted-foreground border-b border-white/5 bg-zinc-900/50">
                                            <tr>
                                                <th className="px-6 py-4 text-left font-bold group cursor-pointer hover:text-foreground transition-colors" onClick={() => handleSort('symbol')}>
                                                    <div className="flex items-center">Symbol <SortIcon column="symbol" /></div>
                                                </th>
                                                <th className="px-6 py-4 text-right font-bold group cursor-pointer hover:text-foreground transition-colors" onClick={() => handleSort('period_return')}>
                                                    <div className="flex items-center justify-end">Period Return <SortIcon column="period_return" /></div>
                                                </th>
                                                <th className="px-6 py-4 text-right font-bold group cursor-pointer hover:text-foreground transition-colors" onClick={() => handleSort('current_price')}>
                                                    <div className="flex items-center justify-end">Current Price <SortIcon column="current_price" /></div>
                                                </th>
                                                <th className="px-6 py-4 text-right font-bold group cursor-pointer hover:text-foreground transition-colors" onClick={() => handleSort('allocation')}>
                                                    <div className="flex items-center justify-end">Allocation <SortIcon column="allocation" /></div>
                                                </th>
                                                <th className="px-6 py-4 text-right font-bold group cursor-pointer hover:text-foreground transition-colors" onClick={() => handleSort('total_return_pct')}>
                                                    <div className="flex items-center justify-end">Total Return <SortIcon column="total_return_pct" /></div>
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {sortedHoldings.map((h) => (
                                                <tr key={h.symbol} className="hover:bg-white/[0.03] transition-colors group">
                                                    <td className="px-6 py-4">
                                                        <div className="font-bold font-mono text-sm tracking-tight group-hover:text-primary transition-colors">
                                                            {h.symbol}
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 text-right">
                                                        <div className={`font-mono font-bold text-sm ${getValueColor(h.period_return)}`}>
                                                            {h.period_return >= 0 ? "+" : ""}{formatPercent(h.period_return)}
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 text-right font-mono text-muted-foreground">
                                                        ${formatNumber(h.current_price)}
                                                    </td>
                                                    <td className="px-6 py-4 text-right font-mono text-muted-foreground">
                                                        {formatPercent(h.allocation)}
                                                    </td>
                                                    <td className={`px-6 py-4 text-right font-mono font-medium ${getValueColor(h.total_return_pct)}`}>
                                                        {h.total_return_pct >= 0 ? "+" : ""}{formatPercent(h.total_return_pct)}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

