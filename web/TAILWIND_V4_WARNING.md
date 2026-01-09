# Tailwind CSS Version Lock

**DO NOT UPGRADE TO TAILWIND V4** until the following issue is resolved:

## Issue
Tailwind v4's new `@tailwindcss/postcss` plugin does NOT generate responsive media queries correctly in Next.js 16 with static export mode. This causes all `md:`, `sm:`, `lg:` breakpoint classes to be ignored, breaking mobile responsiveness.

## Symptoms
- Mobile devices show desktop layout regardless of viewport width
- No `@media (min-width: 768px)` rules in generated CSS
- Classes like `hidden md:block` and `md:hidden` don't work

## Root Cause
The v4 engine requires explicit `@source` directives to scan component files, and the CSS-first configuration model is incompatible with our current setup.

## Resolution
Stay on Tailwind v3 until:
1. Tailwind v4 reaches stable release
2. Next.js 16 has full compatibility documentation
3. The responsive breakpoint generation issue is confirmed fixed

## Date
January 8, 2026
