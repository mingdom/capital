/**
 * Portfolio metadata configuration.
 * Contains details about each portfolio that can be displayed in the UI.
 */

export interface PortfolioMeta {
    name: string;
    description?: string;
    url?: string;
    urlLabel?: string;
}

/**
 * Metadata for known portfolios.
 * Add new portfolios here with their details.
 */
export const PORTFOLIO_META: Record<string, PortfolioMeta> = {
    Mingdom: {
        name: "Mingdom Capital",
        description: "Public portfolio focused on long-term growth with active risk management.",
        url: "https://savvytrader.com/mingdom/mingdom-capital",
        urlLabel: "View on SavvyTrader",
    },
    Fidelity: {
        name: "Fidelity Portfolio",
        description: "Managed advisory account.",
    },
};

/**
 * Get metadata for a portfolio by name.
 * Returns default metadata if not found.
 */
export function getPortfolioMeta(name: string): PortfolioMeta {
    return PORTFOLIO_META[name] || { name };
}
