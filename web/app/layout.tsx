import type { Metadata } from "next";
import { Bricolage_Grotesque, Geist_Mono, Geist } from "next/font/google";
import "./globals.css";
import { AppHeader } from "@/components/layout/app-header";
import { IOSViewportFix } from "@/components/ios-viewport-fix";

const bricolage = Bricolage_Grotesque({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
});

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Mingdom Capital | Portfolio Performance",
  description: "Institutional-grade portfolio performance analytics and risk management",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  viewportFit: "cover",
  themeColor: "#09090b",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        {/* Explicit viewport meta for iOS Safari - sometimes the Next.js viewport export isn't enough */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover" />
      </head>
      <body className={`${bricolage.variable} ${geistSans.variable} ${geistMono.variable} font-sans antialiased`} suppressHydrationWarning>
        <IOSViewportFix />
        <AppHeader />
        {children}
      </body>
    </html>
  );
}
