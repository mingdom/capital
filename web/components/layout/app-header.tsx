"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ExternalLink, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { getPortfolioMeta } from "@/lib/portfolio-meta";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { loadPortfolioData } from "@/lib/data";
import { PortfolioData } from "@/lib/types";
import { MobileNav } from "./mobile-nav";

export function AppHeader() {
    const pathname = usePathname();
    const meta = getPortfolioMeta("Mingdom");
    const [data, setData] = useState<PortfolioData | null>(null);

    useEffect(() => {
        loadPortfolioData().then(setData).catch(console.error);
    }, []);

    const navItems = [
        { name: "Performance", href: "/" },
        { name: "About", href: "/portfolio-info" },
    ];

    return (
        <header className="border-b border-border/50 bg-card/60 backdrop-blur-md sticky top-0 z-50">
            <div className="container mx-auto px-4 py-3">
                <div className="flex flex-row items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="flex flex-col">
                            <h1 className="text-xl font-bold tracking-tight">
                                Mingdom Capital
                            </h1>
                        </Link>

                        {/* Desktop Navigation */}
                        <nav className="hidden md:flex items-center gap-6">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "text-sm font-medium transition-colors hover:text-primary relative py-1",
                                        pathname === item.href
                                            ? "text-primary"
                                            : "text-muted-foreground"
                                    )}
                                >
                                    {item.name}
                                    {pathname === item.href && (
                                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                                    )}
                                </Link>
                            ))}
                        </nav>
                    </div>

                    <div className="flex items-center gap-3 md:gap-4">
                        {meta.url && (
                            <a
                                href={meta.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-primary hover:text-primary/80 border border-primary/20 hover:border-primary/40 rounded-md transition-colors"
                            >
                                <ExternalLink className="h-3.5 w-3.5" />
                                <span>Follow Live Trades</span>
                            </a>
                        )}

                        {data && data.warnings.length > 0 && (
                            <Badge variant="destructive" className="gap-1 scale-90 md:scale-100">
                                <AlertTriangle className="h-3 w-3" />
                                <span className="hidden sm:inline">{data.warnings.length} warning{data.warnings.length > 1 ? "s" : ""}</span>
                                <span className="sm:hidden">{data.warnings.length}</span>
                            </Badge>
                        )}

                        {/* Mobile Nav Toggle */}
                        <MobileNav items={navItems} meta={meta} />
                    </div>
                </div>
            </div>
        </header>
    );
}
