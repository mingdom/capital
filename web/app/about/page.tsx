import { getPortfolioSections } from "@/lib/portfolio-content";
import PortfolioInfoContent from "./portfolio-info-content";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "About | Mingdom Capital",
    description: "Investment philosophy, strategy, and background.",
};

/**
 * About page - Server Component
 * Fetches markdown content at build/request time and renders interactive content.
 */
export default async function AboutPage() {
    const sections = await getPortfolioSections();

    return <PortfolioInfoContent sections={sections} />;
}
