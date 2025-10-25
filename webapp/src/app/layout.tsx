import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Form from "next/form";
import Link from "next/link";
import NextTopLoader from "nextjs-toploader";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import GithubCorner from "@/components/GithubCorner";
import SearchInputs from "@/components/SearchInputs";
import "./globals.css";

export const metadata: Metadata = {
  title: "CAC Outcomes",
  description: "A dashboard for CAC statutory recognition outcomes",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1.0,
};

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export default function RootLayout({
  children,
  faceting,
}: Readonly<{
  children: React.ReactNode;
  faceting: React.ReactNode;
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
          <main className="container max-w-(--breakpoint-xl) px-4 xs:px-5 sm:px-6 pb-6">
            <h1 className="text-5xl font-extrabold text-center mt-8 xs:mt-10 sm:mt-12">
              <Link href="/">CAC Outcomes</Link>
            </h1>
            <GithubCorner href="https://github.com/digitalorganising/cac" />
            <Form
              action=""
              className="mt-8 xs:mt-12 max-w-2xl mx-auto"
              id="outcomes-search-form"
            >
              <div className="flex flex-col max-xs:space-y-2 xs:flex-row xs:space-x-2 ">
                <SearchInputs />
              </div>
            </Form>
            {faceting}
            {children}
          </main>
        </NuqsAdapter>
      </body>
    </html>
  );
}
