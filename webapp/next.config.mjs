import bundleAnalyzer from "@next/bundle-analyzer";
import createMDX from "@next/mdx";

/** @type {import('next').NextConfig} */
const nextConfig = {
  cacheComponents: true,
  pageExtensions: ["ts", "tsx", "mdx"],
};

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const withMDX = createMDX();

export default withBundleAnalyzer(withMDX(nextConfig));
