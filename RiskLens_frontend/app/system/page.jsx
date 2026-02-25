"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function SettingsPage() {
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [autoScan, setAutoScan] = useState(false);
  const [interval, setInterval] = useState(60);
  const [message, setMessage] = useState("");

  // 🔐 Login Check
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  // 📥 Fetch Current Config
  useEffect(() => {
    async function fetchConfig() {
      try {
        const res = await api.get("/system");
        setAutoScan(res.data.auto_scan_enabled);
        setInterval(res.data.scan_interval_minutes);
      } catch (err) {
        console.error("Failed to load system config", err);
      } finally {
        setLoading(false);
      }
    }

    fetchConfig();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");

    try {
      await api.patch("/system", {
        auto_scan_enabled: autoScan,
        scan_interval_minutes: interval,
      });

      setMessage("Settings updated successfully ✅");
    } catch (err) {
      setMessage(
        err.response?.data?.detail || "Failed to update settings ❌"
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        Loading settings...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8">
      <h1 className="text-3xl font-bold mb-8">System Settings</h1>

      <div className="bg-[#1e293b] p-8 rounded-xl max-w-xl shadow-lg">

        {/* Auto Scan Toggle */}
        <div className="flex items-center justify-between mb-6">
          <label className="text-lg font-medium">
            Enable Auto Scan
          </label>
          <input
            type="checkbox"
            checked={autoScan}
            onChange={(e) => setAutoScan(e.target.checked)}
            className="w-5 h-5"
          />
        </div>

        {/* Scan Interval */}
        <div className="mb-6">
          <label className="block mb-2 text-gray-400">
            Scan Interval (Minutes)
          </label>
          <input
            type="number"
            min="1"
            max="1440"
            value={interval}
            onChange={(e) => setInterval(Number(e.target.value))}
            className="w-full p-3 rounded bg-[#334155] text-white focus:outline-none"
          />
          <p className="text-sm text-gray-500 mt-1">
            Must be between 1 and 1440 minutes.
          </p>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className={`w-full py-3 rounded font-semibold transition ${
            saving
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {saving ? "Saving..." : "Save Settings"}
        </button>

        {/* Feedback Message */}
        {message && (
          <div className="mt-4 text-center text-sm">
            {message}
          </div>
        )}
      </div>
    </div>
  );
}