import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClassBridge — Hệ thống Trợ giảng AI Song ngữ Thời gian thực",
  description: "ClassBridge v2.0: Hệ thống nhận diện tiếng nói và dịch thuật song ngữ Anh - Việt trực tiếp qua kiến trúc Dual-Specialist 2-Module chuyên biệt trên GPU.",
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="vi">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
