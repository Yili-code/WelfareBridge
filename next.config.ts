import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  output: "standalone",
  async rewrites() {
    return { fallback: [{
      source: "/api/:path*",
      destination: `${process.env.BENEFIT_API_URL || "http://127.0.0.1:8000"}/api/:path*`,
    }] };
  },
};

export default nextConfig;
