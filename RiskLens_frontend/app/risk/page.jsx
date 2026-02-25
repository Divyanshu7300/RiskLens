"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function RiskPage() {
  const router = useRouter();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔐 Login check
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  useEffect(() => {
    async function fetchRisk() {
      try {
        const res = await api.get("/risk");
        setData(res.data);
      } catch (err) {
        console.error("Risk fetch error:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchRisk();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        Loading risk analysis...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-500">
        Failed to load risk data.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Risk Analysis</h1>

      {/* ───────────── Overview Cards ───────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-10">
        <Card title="Total Violations" value={data.overview.total_violations} />
        <Card title="Total Risk Score" value={data.overview.total_risk_score} />
        <Card title="Average Risk" value={data.overview.average_risk} />
        <Card title="Max Risk" value={data.overview.max_risk} />
        <Card title="Min Risk" value={data.overview.min_risk} />
      </div>

      {/* ───────────── System Status ───────────── */}
      <div className="mb-10">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        <div className={`px-6 py-4 rounded-xl text-lg font-bold ${getStatusColor(data.system_status)}`}>
          {data.system_status}
        </div>
      </div>

      {/* ───────────── High Risk Percentage ───────────── */}
      <div className="mb-10">
        <h2 className="text-xl font-semibold mb-4">High Risk Percentage</h2>
        <div className="bg-[#1e293b] p-6 rounded-xl">
          <div className="w-full bg-gray-700 rounded-full h-4">
            <div
              className="bg-red-500 h-4 rounded-full"
              style={{ width: `${data.high_risk_percentage}%` }}
            />
          </div>
          <p className="mt-2 text-sm text-gray-400">
            {data.high_risk_percentage}% of violations are high risk
          </p>
        </div>
      </div>

      {/* ───────────── Risk Distribution ───────────── */}
      <div className="mb-10">
        <h2 className="text-xl font-semibold mb-4">Risk Distribution</h2>
        <div className="bg-[#1e293b] p-6 rounded-xl space-y-3">
          {Object.entries(data.distribution).map(([risk, count]) => (
            <div key={risk} className="flex justify-between">
              <span>Risk {risk}</span>
              <span className="font-semibold">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ───────────── Top Risky Rules ───────────── */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Top 5 Risky Rules</h2>
        <div className="bg-[#1e293b] rounded-xl overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-[#334155] text-gray-300 text-sm">
              <tr>
                <th className="px-6 py-4">Rule ID</th>
                <th className="px-6 py-4">Total Risk</th>
              </tr>
            </thead>
            <tbody>
              {data.top_risky_rules.map((rule) => (
                <tr
                  key={rule.rule_id}
                  className="border-b border-gray-700 hover:bg-[#273449] transition"
                >
                  <td className="px-6 py-4">{rule.rule_id}</td>
                  <td className="px-6 py-4 font-semibold">{rule.total_risk}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
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

/* 🎨 Status Color */
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