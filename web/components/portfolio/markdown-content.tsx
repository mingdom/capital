"use client";

import { cn } from "@/lib/utils";
import { Linkedin, Twitter } from "lucide-react";
import React from "react";

interface MarkdownContentProps {
    contentHtml: string;
    className?: string;
    accentColor?: string;
}

/**
 * Renders raw HTML from parsed markdown with custom prose styling.
 * Post-processes to add icons to social media links.
 */
export function MarkdownContent({
    contentHtml,
    className,
    accentColor,
}: MarkdownContentProps) {
    const containerRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        if (!containerRef.current) return;

        // Find all links and add icons for social media
        const links = containerRef.current.querySelectorAll("a");
        links.forEach((link) => {
            const href = link.getAttribute("href") || "";
            const text = link.textContent || "";

            // Skip if already has an icon
            if (link.querySelector("svg")) return;

            let icon: React.ReactElement | null = null;

            if (href.includes("linkedin.com")) {
                icon = <Linkedin className="inline-block w-4 h-4 mr-1.5" />;
            } else if (href.includes("x.com") || href.includes("twitter.com")) {
                icon = <Twitter className="inline-block w-4 h-4 mr-1.5" />;
            }

            if (icon) {
                // Create a wrapper to hold both icon and text
                const wrapper = document.createElement("span");
                wrapper.className = "inline-flex items-center";

                // Render the icon
                const iconContainer = document.createElement("span");
                iconContainer.innerHTML = icon.type === Linkedin
                    ? '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block w-4 h-4 mr-1.5"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/></svg>'
                    : '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-block w-4 h-4 mr-1.5"><path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772"/></svg>';

                wrapper.appendChild(iconContainer);
                wrapper.appendChild(document.createTextNode(text));

                link.innerHTML = "";
                link.appendChild(wrapper);
            }
        });
    }, [contentHtml]);

    return (
        <div
            ref={containerRef}
            className={cn("portfolio-prose max-w-none shadow-none", className)}
            style={{ "--section-accent": accentColor } as React.CSSProperties}
            dangerouslySetInnerHTML={{ __html: contentHtml }}
        />
    );
}
