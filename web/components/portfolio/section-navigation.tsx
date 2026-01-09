"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { PortfolioSection } from "@/lib/portfolio-content";
import { Linkedin, Twitter } from "lucide-react";

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
                                "px-4 py-4 text-[10px] font-bold uppercase tracking-widest transition-colors relative flex items-center gap-1.5",
                                activeSection === section.id
                                    ? "text-primary"
                                    : "text-muted-foreground"
                            )}
                        >
                            <span className="opacity-40 font-mono text-[10px]">
                                {section.order.toString().padStart(2, "0")}
                            </span>
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
                            "w-full text-left px-4 py-4 rounded-r-lg border-l-2 transition-all duration-300 group flex items-start gap-3",
                            activeSection === section.id
                                ? "bg-zinc-900 border-primary text-foreground"
                                : "border-transparent text-muted-foreground hover:bg-zinc-900/40 hover:text-foreground"
                        )}
                    >
                        <span className={cn(
                            "font-mono text-[10px] mt-1 transition-colors duration-300",
                            activeSection === section.id ? "text-primary" : "text-zinc-600"
                        )}>
                            {section.order.toString().padStart(2, "0")}
                        </span>
                        <span className="text-sm font-semibold tracking-tight transition-colors duration-300">
                            {section.title}
                        </span>
                    </button>
                ))}

                {/* Social Links - Sticky in Sidebar */}
                <div className="pt-12 mt-12 border-t border-border/30">
                    <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em] mb-4 px-4 opacity-50">
                        Connect
                    </div>
                    <div className="space-y-2 px-1">
                        <a
                            href="https://linkedin.com/in/dongming"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-300 text-muted-foreground hover:bg-zinc-900 hover:text-foreground group"
                        >
                            <span className="p-1 px-1.5 rounded bg-zinc-900 border border-border/50 group-hover:border-primary/50 group-hover:text-primary transition-colors">
                                <Linkedin className="h-3.5 w-3.5" />
                            </span>
                            <span className="text-sm font-medium tracking-tight">LinkedIn</span>
                        </a>
                        <a
                            href="https://x.com/dming"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-300 text-muted-foreground hover:bg-zinc-900 hover:text-foreground group"
                        >
                            <span className="p-1 px-1.5 rounded bg-zinc-900 border border-border/50 group-hover:border-primary/50 group-hover:text-primary transition-colors">
                                <Twitter className="h-3.5 w-3.5" />
                            </span>
                            <span className="text-sm font-medium tracking-tight">X (Twitter)</span>
                        </a>
                    </div>
                </div>
            </nav>
        </>
    );
}
