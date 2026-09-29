import type { Metadata } from "next";
import Navbar from "../components/Navbar";

import "./globals.css";

export const metadata: Metadata = {
  title: "MusicVault",
  description: "Music discovery and library application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Navbar />

        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
