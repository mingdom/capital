import { getPortfolioSections } from "@/lib/portfolio-content";
import PortfolioInfoContent from "./portfolio-info-content";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Portfolio Info | Mingdom Capital",
    description: "Investment philosophy, fund strategy, and institutional mandates.",
};

/**
 * Portfolio Info page - Server Component
 * Fetches markdown content at build/request time and renders interactive content.
 */
export default async function PortfolioInfoPage() {
    const sections = await getPortfolioSections();

    return <PortfolioInfoContent sections={sections} />;
}
