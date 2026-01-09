"use client";

import { cn } from "@/lib/utils";
import React from "react";

interface MarkdownContentProps {
    contentHtml: string;
    className?: string;
    accentColor?: string;
}

/**
 * Renders raw HTML from parsed markdown with custom prose styling.
 */
export function MarkdownContent({
    contentHtml,
    className,
    accentColor,
}: MarkdownContentProps) {
    return (
        <div
            className={cn("portfolio-prose max-w-none shadow-none", className)}
            style={{ "--section-accent": accentColor } as React.CSSProperties}
            dangerouslySetInnerHTML={{ __html: contentHtml }}
        />
    );
}
