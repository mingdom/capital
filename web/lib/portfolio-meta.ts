/**
 * PORTFOLIO METADATA CONFIGURATION
 * =================================
 *
 * This file defines metadata for portfolios displayed in the dashboard.
 * Edit this file to customize how your portfolios appear in the UI.
 *
 * HOW TO ADD/EDIT A PORTFOLIO:
 * 1. Find the PORTFOLIO_META object below
 * 2. Add a new entry with a key matching your portfolio name (e.g., "MyPortfolio")
 * 3. Fill in the optional fields as desired
 *
 * AVAILABLE FIELDS:
 * - name: Display name (required)
 * - description: Brief description shown in the info card
 * - style: Investment style tags, separated by " • " (shown as badges)
 * - url: External link to the portfolio (e.g., SavvyTrader, broker page)
 * - urlLabel: Text for the external link button
 *
 * EXAMPLE:
 * ```
 * MyNewPortfolio: {
 *   name: "My Growth Portfolio",
 *   description: "Aggressive tech-focused growth strategy.",
 *   style: "Tech focus • High conviction • Long-term holds",
 *   url: "https://example.com/my-portfolio",
 *   urlLabel: "View Details",
 * },
 * ```
 */

export interface PortfolioMeta {
    /** Display name for the portfolio */
    name: string;
    /** Brief description of the portfolio strategy */
    description?: string;
    /** Investment style/constraints, separated by " • " (shown as badges) */
    style?: string;
    /** External URL to view more details about the portfolio */
    url?: string;
    /** Button text for the external link (default: "View portfolio") */
    urlLabel?: string;
}

/**
 * Portfolio metadata definitions.
 *
 * The key must match the portfolio name in your data exactly (case-sensitive).
 * For example, if your data has "Mingdom", use "Mingdom" as the key.
 */
export const PORTFOLIO_META: Record<string, PortfolioMeta> = {
    // ─────────────────────────────────────────────────────────────────────
    // MINGDOM CAPITAL - Public portfolio on SavvyTrader
    // ─────────────────────────────────────────────────────────────────────
    Mingdom: {
        name: "Mingdom Capital",
        description: "Public portfolio focused on long-term growth with active risk management.",
        style: "Stocks only • No leverage • No options",
        url: "https://savvytrader.com/mingdom/mingdom-capital",
        urlLabel: "View on SavvyTrader",
    },

    // ─────────────────────────────────────────────────────────────────────
    // FIDELITY - Managed advisory account
    // ─────────────────────────────────────────────────────────────────────
    Fidelity: {
        name: "Fidelity Portfolio",
        description: "Managed advisory account.",
        style: "Diversified allocation",
        // No URL - this is a private account
    },

    // ─────────────────────────────────────────────────────────────────────
    // ADD YOUR PORTFOLIOS BELOW
    // ─────────────────────────────────────────────────────────────────────
    // Example:
    // MyPortfolio: {
    //   name: "My Portfolio Name",
    //   description: "Description of your investment strategy.",
    //   style: "Tag 1 • Tag 2 • Tag 3",
    //   url: "https://your-portfolio-link.com",
    //   urlLabel: "View Details",
    // },
};

/**
 * Get metadata for a portfolio by name.
 * Returns a default object with just the name if not found.
 */
export function getPortfolioMeta(name: string): PortfolioMeta {
    return PORTFOLIO_META[name] || { name };
}
