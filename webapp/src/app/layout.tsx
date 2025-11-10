import { BarChartIcon } from "@radix-ui/react-icons";
import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Form from "next/form";
import Link from "next/link";
import NextTopLoader from "nextjs-toploader";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import GithubCorner from "@/components/GithubCorner";
import SearchInputs from "@/components/SearchInputs";
import Navbar from "@/components/ui/navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "CAC Outcomes",
    template: "%s | CAC Outcomes",
  },
  description: "Search and explore statutory union recognition outcomes",
  metadataBase: new URL("https://cac.digitalganis.ing"),
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1.0,
};

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans">
        <NuqsAdapter>
          <NextTopLoader
            shadow={false}
            height={2}
            color="hsl(222.2 84% 4.9%)"
            showSpinner={false}
          />
          <Navbar
            navigationLinks={[
              { href: "/", label: "Home" },
              { href: "/docs", label: "Documentation" },
              {
                href: "/dashboard",
                label: (
                  <span className="flex items-center gap-2">
                    Dashboard <BarChartIcon />
                  </span>
                ),
              },
            ]}
          />
          <GithubCorner href="https://github.com/digitalorganising/cac" />
          <main className="container max-w-(--breakpoint-xl) px-4 xs:px-5 sm:px-6 pb-6">
            <h1 className="text-5xl font-extrabold text-center">
              <Link href="/">CAC Outcomes</Link>
            </h1>
            <Form
              action="/"
              className="mt-8 xs:mt-12 max-w-2xl mx-auto"
              id="outcomes-search-form"
            >
              <div className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 ">
                <SearchInputs />
              </div>
            </Form>
            {children}
          </main>
        </NuqsAdapter>
      </body>
    </html>
  );
}
