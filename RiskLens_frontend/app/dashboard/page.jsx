"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔐 Login Check
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  // 📊 Fetch Dashboard Data
  useEffect(() => {
    async function fetchDashboard() {
      try {
        const res = await api.get("/dashboard");
        setData(res.data);
      } catch (err) {
        console.error("Dashboard error:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        Loading dashboard...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-500">
        Failed to load dashboard.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Compliance Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        <Card title="Total Violations" value={data.total_violations} />

        <Card title="Rules Triggered" value={data.total_rules_triggered} />

        <Card title="Total Risk Score" value={data.total_risk_score} />

        <Card title="Average Risk" value={data.average_risk} />

      </div>

      {/* System Status */}
      <div className="mt-10">
        <h2 className="text-xl font-semibold mb-4">System Health</h2>
        <div className={`px-6 py-4 rounded-lg font-semibold text-lg 
          ${getStatusColor(data.system_status)}`}>
          {data.system_status}
        </div>
      </div>

      {/* Top Risky Table */}
      {data.top_risky_table && (
        <div className="mt-10">
          <h2 className="text-xl font-semibold mb-4">Top Risky Table</h2>
          <div className="bg-[#1e293b] p-6 rounded-xl shadow-lg">
            <p className="text-lg">
              <span className="font-semibold">Table:</span>{" "}
              {data.top_risky_table.table_name}
            </p>
            <p>
              <span className="font-semibold">Total Risk:</span>{" "}
              {data.top_risky_table.total_risk}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

/* 📦 Reusable Card */
function Card({ title, value }) {
  return (
    <div className="bg-[#1e293b] p-6 rounded-xl shadow-lg hover:scale-105 transition">
      <h3 className="text-gray-400 text-sm">{title}</h3>
      <p className="text-2xl font-bold mt-2">{value}</p>
    </div>
  );
}

/* 🎨 Status Color Logic */
function getStatusColor(status) {
  switch (status) {
    case "CRITICAL":
      return "bg-red-600";
    case "HIGH":
      return "bg-orange-500";
    case "MEDIUM":
      return "bg-yellow-500 text-black";
    default:
      return "bg-green-600";
  }
}