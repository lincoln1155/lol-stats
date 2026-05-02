import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LOL Stats — Match Tracker & AI Coach",
  description: "Track your League of Legends match history and get AI-powered coaching analysis. Search any player across BR, NA, EUW, and KR regions.",
  keywords: ["League of Legends", "match history", "AI coach", "LOL stats", "Riot API"],
  authors: [{ name: "Lincoln", url: "https://github.com/lincoln1155" }],
  openGraph: {
    title: "LOL Stats — Match Tracker & AI Coach",
    description: "Track your League of Legends match history and get AI-powered coaching analysis.",
    type: "website",
    url: "https://lolstats-64cbc4-lol-stats.guaracloud.com",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <div className="flex-1">
          {children}
        </div>
        <footer className="w-full py-6 text-center text-app-muted text-sm border-t border-app-border mt-auto">
          Made by <a href="https://github.com/lincoln1155" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline font-bold">Lincoln</a>
        </footer>
      </body>
    </html>
  );
}
