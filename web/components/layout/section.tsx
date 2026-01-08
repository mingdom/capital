"use client";

import { ReactNode, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";

interface SectionProps {
    title: string;
    children: ReactNode;
    className?: string;
    collapsible?: boolean;
    defaultExpanded?: boolean;
}

/**
 * Dashboard section with consistent header styling.
 * Creates visual separation between content areas.
 */
export function Section({
    title,
    children,
    className = "",
    collapsible = false,
    defaultExpanded = true
}: SectionProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <section className={className}>
            <div className="flex items-center gap-3 mb-4 group">
                <h2 className="text-lg font-heading font-bold text-foreground tracking-tight">{title}</h2>
                <div className="flex-1 h-px bg-border/40" />
                {collapsible && (
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-foreground hover:bg-white/5"
                        onClick={() => setIsExpanded(!isExpanded)}
                    >
                        {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </Button>
                )}
            </div>

            <AnimatePresence initial={false}>
                {(!collapsible || isExpanded) && (
                    <motion.div
                        initial={collapsible ? { height: 0, opacity: 0 } : false}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
                        className="overflow-hidden"
                    >
                        {children}
                    </motion.div>
                )}
            </AnimatePresence>
        </section>
    );
}
