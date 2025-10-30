import bundleAnalyzer from "@next/bundle-analyzer";
import createMDX from "@next/mdx";

/** @type {import('next').NextConfig} */
const nextConfig = {
  cacheComponents: true,
  pageExtensions: ["ts", "tsx", "mdx"],
  images: {
    localPatterns: [{ pathname: "/assets/**", search: "" }],
  },
};

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const withMDX = createMDX({
  options: {
    rehypePlugins: ["rehype-mermaid"],
  },
});

export default withBundleAnalyzer(withMDX(nextConfig));
