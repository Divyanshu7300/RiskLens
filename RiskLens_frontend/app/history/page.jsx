"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function HistoryPage() {
  const router = useRouter();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🔐 Login Check
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  // 📜 Fetch Scan History
  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await api.get("/history");
        setScans(res.data);
      } catch (err) {
        console.error("History fetch error:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        Loading history...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Scan History</h1>

      <div className="bg-[#1e293b] rounded-xl shadow-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-[#334155] text-gray-300 text-sm uppercase">
            <tr>
              <th className="px-6 py-4">Scan ID</th>
              <th className="px-6 py-4">Scanned At</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Total Violations</th>
              <th className="px-6 py-4">Total Risk</th>
            </tr>
          </thead>

          <tbody>
            {scans.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-6 text-center text-gray-400">
                  No scan history found.
                </td>
              </tr>
            ) : (
              scans.map((scan) => (
                <tr
                  key={scan.id}
                  className="border-b border-gray-700 hover:bg-[#273449] transition"
                >
                  <td className="px-6 py-4 font-semibold">{scan.id}</td>
                  <td className="px-6 py-4">
                    {new Date(scan.scanned_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={scan.status} />
                  </td>
                  <td className="px-6 py-4">{scan.total_violations}</td>
                  <td className="px-6 py-4">{scan.total_risk_score}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* 🎨 Status Badge */
function StatusBadge({ status }) {
  const colorMap = {
    COMPLETED: "bg-green-600",
    RUNNING: "bg-yellow-500 text-black",
    FAILED: "bg-red-600",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-semibold ${
        colorMap[status] || "bg-gray-600"
      }`}
    >
      {status}
    </span>
  );
}