import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Enables a lean production image in later deployment phases.
  output: "standalone",
};

export default nextConfig;
