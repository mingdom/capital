"use client";

import { useEffect } from "react";

/**
 * iOS Safari viewport fix
 * Forces the viewport to be set correctly on iOS devices
 * This runs client-side to override any caching issues
 */
export function IOSViewportFix() {
    useEffect(() => {
        // Only run on iOS
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        if (!isIOS) return;

        // Force viewport meta tag
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute(
                "content",
                "width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover"
            );
        }

        // Force a reflow to ensure iOS Safari picks up the change
        document.documentElement.style.display = "none";
        document.documentElement.offsetHeight; // Trigger reflow
        document.documentElement.style.display = "";
    }, []);

    return null;
}
