"use client";

import { motion } from "framer-motion";
import { PortfolioSection as SectionType } from "@/lib/portfolio-content";
import { PortfolioSection } from "@/components/portfolio/portfolio-section";
import { SectionNavigation } from "@/components/portfolio/section-navigation";
import { Linkedin, Twitter } from "lucide-react";

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

            {/* Mobile Sticky Social Bar */}
            <div className="md:hidden fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
                <div className="bg-card/80 backdrop-blur-md border border-border/50 rounded-full px-6 py-3 shadow-xl flex items-center gap-6">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mr-2">
                        Connect
                    </span>
                    <a
                        href="https://linkedin.com/in/dongming"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                    >
                        <Linkedin className="h-5 w-5" />
                    </a>
                    <a
                        href="https://x.com/dming"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                    >
                        <Twitter className="h-5 w-5" />
                    </a>
                </div>
            </div>
        </main>
    );
}
