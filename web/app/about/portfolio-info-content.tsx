"use client";

import { motion } from "framer-motion";
import { PortfolioSection as SectionType } from "@/lib/portfolio-content";
import { PortfolioSection } from "@/components/portfolio/portfolio-section";
import { SectionNavigation } from "@/components/portfolio/section-navigation";

interface PortfolioInfoContentProps {
    sections: SectionType[];
}

export default function PortfolioInfoContent({ sections }: PortfolioInfoContentProps) {
    return (
        <main className="min-h-screen bg-background pb-32">
            <div className="container mx-auto px-4">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-12 relative">
                    {/* Section Navigation */}
                    <div className="lg:col-span-1">
                        <SectionNavigation sections={sections} />
                    </div>

                    {/* Content Area */}
                    <div className="lg:col-span-3">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.5 }}
                            className="space-y-12"
                        >
                            {sections.map((section) => (
                                <PortfolioSection
                                    key={section.id}
                                    id={section.id}
                                    title={section.title}
                                    order={section.order}
                                    contentHtml={section.contentHtml}
                                    accent={section.accent}
                                />
                            ))}
                        </motion.div>
                    </div>
                </div>
            </div>
        </main>
    );
}
