"use client";

import { ReactNode } from "react";

interface SectionProps {
    title: string;
    children: ReactNode;
    className?: string;
}

/**
 * Dashboard section with consistent header styling.
 * Creates visual separation between content areas.
 */
export function Section({ title, children, className = "" }: SectionProps) {
    return (
        <section className={className}>
            <div className="flex items-center gap-3 mb-4">
                <h2 className="text-lg font-semibold text-foreground">{title}</h2>
                <div className="flex-1 h-px bg-border/50" />
            </div>
            {children}
        </section>
    );
}
