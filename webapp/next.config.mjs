/** @type {import('next').NextConfig} */
import bundleAnalyzer from "@next/bundle-analyzer";

const nextConfig = {
  cacheComponents: true,
};

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

export default withBundleAnalyzer(nextConfig);
