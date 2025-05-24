import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import NextTopLoader from "nextjs-toploader";
import SearchForm from "@/components/SearchForm";

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
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans">
        <NextTopLoader
          shadow={false}
          height={2}
          color="hsl(222.2 84% 4.9%)"
          showSpinner={false}
        />
        <main className="container max-w-(--breakpoint-xl) px-4 xs:px-5 sm:px-6 pb-6">
          <h1 className="text-5xl font-extrabold text-center mt-8 xs:mt-10 sm:mt-12">
            CAC Outcomes
          </h1>
          <SearchForm />
          {children}
        </main>
      </body>
    </html>
  );
}
