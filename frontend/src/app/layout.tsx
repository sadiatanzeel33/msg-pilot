import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Msg-Pilot — WhatsApp Automation",
  description: "Bulk WhatsApp messaging platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
