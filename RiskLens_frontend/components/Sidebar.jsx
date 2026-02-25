"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Scan", path: "/scan" },
  { name: "History", path: "/history" },
  { name: "Risk Analysis", path: "/risk" },
  { name: "Reports", path: "/reports" },
  { name: "System Settings", path: "/system" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#1e293b] p-6 border-r border-gray-700">
      <h2 className="text-2xl font-bold mb-10 text-green-400">
        PolicyGuard
      </h2>

      <nav className="space-y-4">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.path);

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`block px-4 py-2 rounded-lg transition ${
                active
                  ? "bg-green-600 text-white"
                  : "text-gray-400 hover:bg-gray-700 hover:text-white"
              }`}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="absolute bottom-10 left-6 right-6">
        <button
          onClick={() => {
            localStorage.removeItem("token");
            window.location.href = "/login";
          }}
          className="w-full bg-red-600 hover:bg-red-700 py-2 rounded-lg"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}