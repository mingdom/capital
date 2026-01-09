"use client";

import { motion } from "framer-motion";
import { MarkdownContent } from "./markdown-content";

interface PortfolioSectionProps {
    id: string;
    title: string;
    order: number;
    contentHtml: string;
    accent: string;
}

const ACCENT_COLORS: Record<string, string> = {
    purple: "#a855f7", // purple-500
    blue: "#3b82f6",   // blue-500
    emerald: "#10b981", // emerald-500
};

/**
 * Individual section of the Portfolio Info page with a side accent bar and section numbering.
 */
export function PortfolioSection({
    id,
    title,
    order,
    contentHtml,
    accent,
}: PortfolioSectionProps) {
    const accentColor = ACCENT_COLORS[accent] || ACCENT_COLORS.purple;

    return (
        <motion.section
            id={id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="relative pl-8 md:pl-12 py-16 first:pt-8"
        >
            {/* Side Accent Bar */}
            <div
                className="absolute left-0 top-0 bottom-0 w-1 md:w-1.5 opacity-80"
                style={{ backgroundColor: accentColor }}
            />


            {/* Markdown Content */}
            <MarkdownContent
                contentHtml={contentHtml}
                accentColor={accentColor}
            />
        </motion.section>
    );
}
