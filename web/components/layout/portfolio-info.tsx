"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Info } from "lucide-react";
import { getPortfolioMeta } from "@/lib/portfolio-meta";

interface PortfolioInfoProps {
    portfolio: string;
    className?: string;
}

/**
 * Portfolio info card showing description, investment style, and external link.
 * Provides context about the portfolio being viewed.
 */
export function PortfolioInfo({ portfolio, className = "" }: PortfolioInfoProps) {
    const meta = getPortfolioMeta(portfolio);

    // Skip if no meaningful metadata
    if (!meta.description && !meta.style && !meta.url) {
        return null;
    }

    return (
        <Card className={`bg-card/50 border-border/50 ${className}`}>
            <CardContent className="py-4 px-5">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="flex items-start gap-3">
                        <Info className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                        <div className="space-y-1">
                            {meta.description && (
                                <p className="text-sm text-foreground">{meta.description}</p>
                            )}
                            {meta.style && (
                                <div className="flex flex-wrap gap-2">
                                    {meta.style.split("•").map((tag, i) => (
                                        <Badge key={i} variant="secondary" className="text-xs font-normal">
                                            {tag.trim()}
                                        </Badge>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {meta.url && (
                        <a
                            href={meta.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline shrink-0"
                        >
                            {meta.urlLabel || "View portfolio"}
                            <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
