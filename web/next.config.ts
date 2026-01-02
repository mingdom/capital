import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use Turbopack by default (Next.js 16+)
  // The suppressHydrationWarning in layout.tsx handles browser extension issues
};

export default nextConfig;
