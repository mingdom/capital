import { PortfolioData, TimeSeriesPoint, WealthPoint } from "./types";

/**
 * Load portfolio data from the static JSON file.
 */
export async function loadPortfolioData(): Promise<PortfolioData> {
    const response = await fetch("/data/portfolio.json");
    if (!response.ok) {
        throw new Error(`Failed to load portfolio data: ${response.status}`);
    }
    return response.json();
}

/**
 * Parse period string (e.g., "2024-01") into a Date.
 */
export function periodToDate(period: string): Date {
    const [year, month] = period.split("-").map(Number);
    // Use the last day of the month for proper ordering
    return new Date(year, month, 0);
}

/**
 * Convert monthly returns to time series data for charts.
 */
export function toTimeSeries(
    monthlyReturns: Record<string, Record<string, number>>,
    sources: string[]
): TimeSeriesPoint[] {
    // Get all unique periods across all sources
    const allPeriods = new Set<string>();
    for (const source of sources) {
        const data = monthlyReturns[source];
        if (data) {
            Object.keys(data).forEach((p) => allPeriods.add(p));
        }
    }

    // Sort periods chronologically
    const sortedPeriods = Array.from(allPeriods).sort();

    return sortedPeriods.map((period) => {
        const point: TimeSeriesPoint = {
            period,
            date: periodToDate(period),
        };
        for (const source of sources) {
            const value = monthlyReturns[source]?.[period];
            // Convert to percentage for display
            point[source] = value !== undefined ? value * 100 : NaN;
        }
        return point;
    });
}

/**
 * Convert monthly returns to cumulative wealth index for comparison.
 * Starts at 100,000 for all series.
 */
export function toCumulativeWealth(
    monthlyReturns: Record<string, Record<string, number>>,
    sources: string[]
): WealthPoint[] {
    const timeSeries = toTimeSeries(monthlyReturns, sources);

    // Initialize wealth at 100,000 for each source
    const wealth: Record<string, number> = {};
    for (const source of sources) {
        wealth[source] = 100000;
    }

    return timeSeries.map((point) => {
        const wealthPoint: WealthPoint = {
            period: point.period,
            date: point.date,
        };
        for (const source of sources) {
            const monthlyReturn = point[source];
            if (typeof monthlyReturn === "number" && !isNaN(monthlyReturn)) {
                // Convert from percentage back to decimal for calculation
                wealth[source] = wealth[source] * (1 + monthlyReturn / 100);
            }
            wealthPoint[source] = wealth[source];
        }
        return wealthPoint;
    });
}

/**
 * Format a number as percentage.
 */
export function formatPercent(value: number | null, decimals: number = 1): string {
    if (value === null || value === undefined || isNaN(value)) {
        return "—";
    }
    return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a number with specified decimals.
 */
export function formatNumber(value: number | null, decimals: number = 2): string {
    if (value === null || value === undefined || isNaN(value)) {
        return "—";
    }
    return value.toFixed(decimals);
}

/**
 * Get color class for a metric value (positive = green, negative = red).
 */
export function getValueColor(value: number | null): string {
    if (value === null || value === undefined || isNaN(value)) {
        return "text-muted-foreground";
    }
    if (value > 0) {
        return "text-emerald-500";
    }
    if (value < 0) {
        return "text-red-500";
    }
    return "text-muted-foreground";
}

/**
 * Chart color palette for different series.
 * High-contrast colors for easy differentiation.
 */
export const CHART_COLORS: Record<string, string> = {
    // Portfolios - bold, saturated colors
    Mingdom: "#3b82f6",   // Bright blue
    Fidelity: "#8b5cf6",  // Vivid purple

    // Benchmarks - distinct, high-contrast colors
    SPY: "#10b981",       // Emerald green
    QQQ: "#f59e0b",       // Amber/orange
    ARKK: "#ef4444",      // Red
};

/**
 * Get chart color for a series name.
 */
export function getChartColor(name: string): string {
    return CHART_COLORS[name] || "#6b7280";
}
