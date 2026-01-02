import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for production builds
  output: 'export',

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
