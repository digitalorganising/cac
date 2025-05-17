import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import NextTopLoader from "nextjs-toploader";

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
        <NextTopLoader shadow={false} height={2} color="hsl(222.2 84% 4.9%)" />
        {children}
      </body>
    </html>
  );
}
