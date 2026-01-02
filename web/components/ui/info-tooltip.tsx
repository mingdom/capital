"use client";

import { Info } from "lucide-react";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

interface InfoTooltipProps {
    content: string;
    className?: string;
}

/**
 * Small info icon that shows explanatory text on hover.
 * Use next to metric names to explain what they mean.
 */
export function InfoTooltip({ content, className = "" }: InfoTooltipProps) {
    return (
        <TooltipProvider delayDuration={300}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <Info className={`h-3.5 w-3.5 text-muted-foreground hover:text-foreground cursor-help ${className}`} />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs text-sm">
                    <p>{content}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}

/**
 * Metric explanations for all dashboard stats.
 * Use these with InfoTooltip for consistent descriptions.
 */
export const METRIC_INFO = {
    // Performance metrics
    cagr: "Compound Annual Growth Rate. The average annualized return if gains were reinvested. >15% is strong for long-term investing.",
    ytd: "Year-to-Date return. Total return from January 1st to the latest data point.",
    one_year: "Trailing 12-month return. Performance over the last year, regardless of calendar year.",
    three_month: "Trailing 3-month return. Recent short-term momentum.",
    sharpe: "Risk-adjusted return using total volatility. Above 1.0 is good, above 2.0 is excellent. Higher is better.",
    sortino: "Risk-adjusted return using only downside volatility. Higher than Sharpe suggests good downside protection.",
    max_drawdown: "Worst peak-to-trough decline. Smaller is better. Shows the maximum loss you would have experienced.",

    // Risk metrics
    volatility: "Annualized standard deviation of returns. Measures total price swings, both up and down.",
    downside_dev: "Annualized downside deviation. Like volatility but only counts negative returns. Used in Sortino ratio.",
    var_95: "Value at Risk (95%). In 95% of months, losses won't exceed this amount. Monthly figure, not annualized.",
    cvar_95: "Conditional VaR (95%). Average loss in the worst 5% of months. Shows tail risk severity.",
    beta_spy: "Market sensitivity vs S&P 500. Beta of 1.0 means moves with the market. <1 is defensive, >1 is aggressive.",
    corr_spy: "Correlation with S&P 500. 1.0 = moves perfectly together; 0 = no relationship; -1 = moves opposite.",

    // Quick stats
    hit_rate: "Percentage of months with positive returns. >50% means more winning months than losing.",
    avg_up: "Average return in positive months. Shows typical gain size when you win.",
    avg_down: "Average return in negative months. Shows typical loss size when you lose.",
    up_capture: "Performance vs SPY in up markets. 120% means you capture 120% of SPY's gains when SPY is up. Higher is better.",
    down_capture: "Performance vs SPY in down markets. 80% means you only lose 80% of what SPY loses. Lower is better.",
    best_month: "Best single month return in the period.",
    worst_month: "Worst single month return in the period.",
    drawdown_duration: "Maximum number of consecutive months in drawdown. Shows how long recoveries take.",
};
