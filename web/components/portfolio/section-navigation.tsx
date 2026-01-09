"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { PortfolioSection } from "@/lib/portfolio-content";

interface SectionNavigationProps {
    sections: PortfolioSection[];
}

/**
 * Navigation component for Portfolio Info page.
 * Shows a sticky sidebar on desktop and horizontal tabs on mobile.
 */
export function SectionNavigation({ sections }: SectionNavigationProps) {
    const [activeSection, setActiveSection] = useState<string>("");

    useEffect(() => {
        if (sections.length === 0) return;

        // Set first section as active by default if none set
        if (!activeSection) {
            setActiveSection(sections[0].id);
        }

        const sectionIds = sections.map((s) => s.id);

        const observerOptions = {
            root: null,
            rootMargin: "-20% 0px -70% 0px",
            threshold: 0,
        };

        const observerCallback = (entries: IntersectionObserverEntry[]) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    setActiveSection(entry.target.id);
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, observerOptions);

        sectionIds.forEach((id) => {
            const el = document.getElementById(id);
            if (el) observer.observe(el);
        });

        return () => observer.disconnect();
    }, [sections, activeSection]);

    const scrollToSection = (id: string) => {
        const el = document.getElementById(id);
        if (el) {
            // Offset calculation for sticky header + mobile nav
            const headerOffset = 85;
            const elementPosition = el.getBoundingClientRect().top + window.scrollY;
            const offsetPosition = elementPosition - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: "smooth",
            });
        }
    };

    return (
        <>
            {/* Mobile Tabs - Sticky below header */}
            <div className="md:hidden sticky top-[57px] z-40 bg-background/95 backdrop-blur-md border-b border-border/50 overflow-x-auto scrollbar-hide">
                <div className="flex px-4 whitespace-nowrap">
                    {sections.map((section) => (
                        <button
                            key={section.id}
                            onClick={() => scrollToSection(section.id)}
                            className={cn(
                                "px-4 py-4 text-[10px] font-bold uppercase tracking-widest transition-colors relative",
                                activeSection === section.id
                                    ? "text-primary"
                                    : "text-muted-foreground"
                            )}
                        >
                            {section.title}
                            {activeSection === section.id && (
                                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Desktop Sidebar - Sticky Index */}
            <nav className="hidden md:block sticky top-28 space-y-1">
                <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] mb-8 px-4 opacity-50">
                    Document Index
                </div>
                {sections.map((section) => (
                    <button
                        key={section.id}
                        onClick={() => scrollToSection(section.id)}
                        className={cn(
                            "w-full text-left px-4 py-4 rounded-r-lg border-l-2 transition-all duration-300 group flex items-start gap-4",
                            activeSection === section.id
                                ? "bg-zinc-900 border-primary text-foreground"
                                : "border-transparent text-muted-foreground hover:bg-zinc-900/40 hover:text-foreground"
                        )}
                    >
                        <span className="text-sm font-semibold tracking-tight transition-colors duration-300">
                            {section.title}
                        </span>
                    </button>
                ))}
            </nav>
        </>
    );
}
