"use client";

import Sidebar from "@/components/Sidebar";
import { usePathname } from "next/navigation";

export default function RootLayout({ children }) {
  const pathname = usePathname();

  // Login page pe sidebar hide
  const hideSidebar = pathname === "/login" || pathname === "/register";

  return (
    <html lang="en">
      <body className="bg-[#0f172a] text-white">
        <div className="flex min-h-screen">
          {!hideSidebar && <Sidebar />}
          <main className="flex-1 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}