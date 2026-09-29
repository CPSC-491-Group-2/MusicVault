import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Proxies API calls to Flask; resolved at build time.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://127.0.0.1:5000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
