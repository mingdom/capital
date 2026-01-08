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
    const [activePeriod, setActivePeriod] = useState<string>("ytd");
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(true);

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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Skeleton className="h-64" />
                    <Skeleton className="h-64" />
                </div>
            </div>
        );
    }

    if (!data) return null;

    const currentPeriodData = data.periods[activePeriod];
    if (!currentPeriodData) return null;

    const topPerformers = currentPeriodData.holdings.slice(0, 5);
    const bottomPerformers = [...currentPeriodData.holdings].reverse().slice(0, 5);
    const restOfHoldings = currentPeriodData.holdings.slice(5, -5);

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">
                        Price performance of current holdings over the selected period.
                        <span className="hidden md:inline"> This differs from portfolio time-weighted returns.</span>
                    </p>
                </div>
                <Tabs value={activePeriod} onValueChange={setActivePeriod}>
                    <TabsList className="bg-zinc-900/50 border border-white/5">
                        <TabsTrigger value="3mo">3M</TabsTrigger>
                        <TabsTrigger value="ytd">YTD</TabsTrigger>
                        <TabsTrigger value="1y">1Y</TabsTrigger>
                    </TabsList>
                </Tabs>
            </div>

            <ConvictionHeatStrip performance={currentPeriodData} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PerformanceSubTable
                    title="Top Performers"
                    holdings={topPerformers}
                    isTop={true}
                    totalCount={currentPeriodData.holdings.length}
                />
                <PerformanceSubTable
                    title="Bottom Performers"
                    holdings={bottomPerformers}
                    isTop={false}
                    totalCount={currentPeriodData.holdings.length}
                    startRank={currentPeriodData.holdings.length - 4}
                />
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                    >
                        <Card className="bg-zinc-950/30 border-white/5">
                            <CardContent className="p-0">
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead className="text-xs uppercase tracking-widest text-muted-foreground border-b border-white/5">
                                            <tr>
                                                <th className="px-6 py-3 text-left font-medium">Rank</th>
                                                <th className="px-6 py-3 text-left font-medium">Symbol</th>
                                                <th className="px-6 py-3 text-right font-medium">Return</th>
                                                <th className="px-6 py-3 text-right font-medium">Price</th>
                                                <th className="px-6 py-3 text-right font-medium">Allocation</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {restOfHoldings.map((h, i) => (
                                                <tr key={h.symbol} className="hover:bg-white/[0.02] transition-colors">
                                                    <td className="px-6 py-3 text-muted-foreground font-mono">{i + 6}</td>
                                                    <td className="px-6 py-3 font-bold font-mono">{h.symbol}</td>
                                                    <td className={`px-6 py-3 text-right font-mono font-bold ${getValueColor(h.period_return)}`}>
                                                        {h.period_return >= 0 ? "+" : ""}{formatPercent(h.period_return)}
                                                    </td>
                                                    <td className="px-6 py-3 text-right font-mono text-muted-foreground">${formatNumber(h.current_price)}</td>
                                                    <td className="px-6 py-3 text-right text-muted-foreground">{formatPercent(h.allocation)}</td>
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

            <div className="flex justify-center">
                <Button
                    variant="ghost"
                    size="sm"
                    className="text-muted-foreground hover:text-foreground gap-2"
                    onClick={() => setExpanded(!expanded)}
                >
                    {expanded ? (
                        <>Collapse<ChevronUp className="h-4 w-4" /></>
                    ) : (
                        <>Show all {currentPeriodData.holdings.length} holdings <ChevronDown className="h-4 w-4" /></>
                    )}
                </Button>
            </div>
        </div>
    );
}

function PerformanceSubTable({
    title,
    holdings,
    isTop,
    totalCount,
    startRank = 1
}: {
    title: string;
    holdings: StockPerformance[];
    isTop: boolean;
    totalCount: number;
    startRank?: number;
}) {
    return (
        <Card className="bg-zinc-900/40 border-white/5 overflow-hidden">
            <div className="px-5 py-3 border-b border-white/5 bg-zinc-900/80">
                <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                    {title}
                </h3>
            </div>
            <CardContent className="p-0">
                <div className="divide-y divide-white/5">
                    {holdings.map((h, i) => (
                        <motion.div
                            key={h.symbol}
                            initial={{ opacity: 0, x: isTop ? -10 : 10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.05 }}
                            className="flex items-center justify-between px-5 py-3 hover:bg-white/[0.02] transition-colors group"
                        >
                            <div className="flex items-center gap-4">
                                <span className="text-[10px] font-mono text-muted-foreground/50 w-4">
                                    {startRank + i}
                                </span>
                                <div>
                                    <div className="font-mono font-bold text-sm tracking-tight">{h.symbol}</div>
                                    <div className="text-[10px] text-muted-foreground/60">${formatNumber(h.current_price)}</div>
                                </div>
                            </div>

                            <div className="flex items-center gap-6">
                                <div className="hidden sm:block">
                                    <div className="h-1 w-20 bg-zinc-800 rounded-full overflow-hidden">
                                        <motion.div
                                            className={`h-full ${isTop ? "bg-emerald-500" : "bg-red-500"}`}
                                            initial={{ width: 0 }}
                                            animate={{ width: `${Math.min(Math.abs(h.period_return) * 100, 100)}%` }}
                                            transition={{ duration: 1, delay: 0.2 + i * 0.1 }}
                                        />
                                    </div>
                                </div>

                                <div className="text-right min-w-[70px]">
                                    <div className={`text-sm font-mono font-bold ${getValueColor(h.period_return)}`}>
                                        {h.period_return >= 0 ? "+" : ""}{formatPercent(h.period_return)}
                                    </div>
                                    <div className="text-[10px] text-muted-foreground/60">{formatPercent(h.allocation)} alloc</div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
