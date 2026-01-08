"use client";

import { motion } from "framer-motion";
import { PeriodPerformance } from "@/lib/types";
import { formatPercent } from "@/lib/data";

interface ConvictionHeatStripProps {
    performance: PeriodPerformance;
}

export function ConvictionHeatStrip({ performance }: ConvictionHeatStripProps) {
    const { summary, holdings } = performance;

    if (holdings.length === 0) return null;

    // Calculate the range for the Heat Strip
    // We want to map the worst performer to 0% and best to 100%
    const returns = holdings.map(h => h.period_return);
    const minReturn = Math.min(...returns);
    const maxReturn = Math.max(...returns);
    const range = maxReturn - minReturn;

    // Position of the net return marker
    const markerPos = range !== 0
        ? ((summary.net_return - minReturn) / range) * 100
        : 50;

    return (
        <div className="py-2 space-y-6">
            <div className="relative">
                {/* The Strip */}
                <div className="relative h-3 w-full rounded-full bg-gradient-to-r from-red-500/40 via-zinc-700 to-emerald-500/40 border border-white/10 overflow-visible shadow-inner">
                    {/* Net Return Marker */}
                    <motion.div
                        className="absolute top-1/2 -translate-y-1/2 w-0.5 h-7 bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)] z-10"
                        initial={{ left: "50%" }}
                        animate={{ left: `${Math.min(Math.max(markerPos, 0), 100)}%` }}
                        transition={{ type: "spring", stiffness: 60, damping: 15 }}
                    />

                    {/* Tick for center (0%) if possible, or just the labels below */}
                </div>

                {/* Extremes Labels - Positioned below the bar for zero overlap */}
                <div className="flex justify-between items-center mt-3 text-[10px] uppercase tracking-widest font-bold">
                    <div className="flex flex-col items-start">
                        <span className="text-muted-foreground/80">Worst</span>
                        <span className="text-red-400">{formatPercent(minReturn, 1)}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-muted-foreground/80">Best</span>
                        <span className="text-emerald-400">{formatPercent(maxReturn, 1)}</span>
                    </div>
                </div>
            </div>

            <div className="flex justify-center border-t border-white/[0.03] pt-4">
                <div className="text-center">
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground/60 mb-1">Weighted Net Return</div>
                    <div className={`text-2xl font-heading font-bold ${summary.net_return >= 0 ? "text-emerald-500" : "text-red-500"}`}>
                        {summary.net_return >= 0 ? "+" : ""}{formatPercent(summary.net_return)}
                    </div>
                </div>
            </div>
        </div>
    );
}
