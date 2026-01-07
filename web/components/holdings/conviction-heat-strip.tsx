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
        <div className="space-y-4 py-4">
            <div className="relative h-2 w-full rounded-full bg-gradient-to-r from-red-900 via-zinc-700 to-emerald-900 border border-white/5 overflow-visible">
                {/* Net Return Marker */}
                <motion.div
                    className="absolute top-1/2 -translate-y-1/2 w-0.5 h-6 bg-white shadow-[0_0_8px_rgba(255,255,255,0.5)] z-10"
                    initial={{ left: "50%" }}
                    animate={{ left: `${Math.min(Math.max(markerPos, 0), 100)}%` }}
                    transition={{ type: "spring", stiffness: 50, damping: 15 }}
                />

                {/* Gainers/Losers density indicators (simplified for MVP) */}
                <div className="absolute inset-0 flex justify-between px-2 text-[10px] text-muted-foreground/50 -bottom-5">
                    <span>Worst ({formatPercent(minReturn, 0)})</span>
                    <span>Best ({formatPercent(maxReturn, 0)})</span>
                </div>
            </div>

            <div className="flex justify-center pt-2">
                <div className="text-center">
                    <div className="text-xs uppercase tracking-widest text-muted-foreground mb-0.5">Weighted Net Return</div>
                    <div className={`text-lg font-mono font-bold ${summary.net_return >= 0 ? "text-emerald-500" : "text-red-500"}`}>
                        {summary.net_return >= 0 ? "+" : ""}{formatPercent(summary.net_return)}
                    </div>
                </div>
            </div>
        </div>
    );
}
