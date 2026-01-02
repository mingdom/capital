import { PortfolioData, MonthlyReturns } from "./types";

/**
 * Time period options for filtering data
 */
export type TimePeriod = "ytd" | "1y" | "3y" | "5y" | "all";

/**
 * Get the start date for a given time period
 */
export function getStartDateForPeriod(period: TimePeriod, currentYear: number): Date | null {
    const now = new Date();

    switch (period) {
        case "ytd":
            return new Date(currentYear, 0, 1); // Jan 1 of current year
        case "1y":
            return new Date(now.getFullYear() - 1, now.getMonth(), 1);
        case "3y":
            return new Date(now.getFullYear() - 3, now.getMonth(), 1);
        case "5y":
            return new Date(now.getFullYear() - 5, now.getMonth(), 1);
        case "all":
            return null; // No filtering
        default:
            return null;
    }
}

/**
 * Filter monthly returns by time period
 */
export function filterMonthlyReturnsByPeriod(
    monthlyReturns: MonthlyReturns,
    period: TimePeriod,
    currentYear: number
): MonthlyReturns {
    const startDate = getStartDateForPeriod(period, currentYear);

    if (!startDate) {
        return monthlyReturns; // Return all data
    }

    const filtered: MonthlyReturns = {};

    for (const [source, returns] of Object.entries(monthlyReturns)) {
        filtered[source] = {};

        for (const [periodStr, value] of Object.entries(returns)) {
            const [year, month] = periodStr.split("-").map(Number);
            const periodDate = new Date(year, month - 1, 1);

            if (periodDate >= startDate) {
                filtered[source][periodStr] = value;
            }
        }
    }

    return filtered;
}

/**
 * Get display label for time period
 */
export function getPeriodLabel(period: TimePeriod): string {
    switch (period) {
        case "ytd":
            return "YTD";
        case "1y":
            return "1 Year";
        case "3y":
            return "3 Years";
        case "5y":
            return "5 Years";
        case "all":
            return "All Time";
        default:
            return "All Time";
    }
}

/**
 * Check if a time period has enough data
 */
export function hasSufficientData(
    monthlyReturns: MonthlyReturns,
    period: TimePeriod,
    currentYear: number,
    minMonths: number = 1
): boolean {
    const filtered = filterMonthlyReturnsByPeriod(monthlyReturns, period, currentYear);

    // Check if any source has enough data
    for (const returns of Object.values(filtered)) {
        if (Object.keys(returns).length >= minMonths) {
            return true;
        }
    }

    return false;
}
