"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function ScanPage() {
  const router = useRouter();

  const [policyFile, setPolicyFile] = useState(null);
  const [dataFile, setDataFile] = useState(null);
  const [dbUri, setDbUri] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // 🔐 Login Check
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  const handleScan = async (e) => {
    e.preventDefault();

    if (!policyFile) {
      alert("Policy file is required");
      return;
    }

    if (!dbUri && !dataFile) {
      alert("Provide either DB URI or dataset file");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("policy_file", policyFile);

    if (dataFile) {
      formData.append("data_file", dataFile);
    }

    if (dbUri) {
      formData.append("db_uri", dbUri);
    }

    try {
      const res = await api.post("/scan", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResult(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Run Compliance Scan</h1>

      <form
        onSubmit={handleScan}
        className="bg-[#1e293b] p-8 rounded-xl max-w-2xl shadow-lg space-y-6"
      >
        {/* Policy Upload */}
        <div>
          <label className="block mb-2 text-gray-400">
            Upload Policy (PDF)
          </label>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setPolicyFile(e.target.files[0])}
            className="w-full"
          />
        </div>

        {/* DB URI */}
        <div>
          <label className="block mb-2 text-gray-400">
            Database URI (Optional)
          </label>
          <input
            type="text"
            placeholder="postgresql://user:pass@localhost/dbname"
            value={dbUri}
            onChange={(e) => setDbUri(e.target.value)}
            className="w-full p-3 rounded bg-[#334155] text-white"
          />
        </div>

        <div className="text-center text-gray-400">OR</div>

        {/* Dataset Upload */}
        <div>
          <label className="block mb-2 text-gray-400">
            Upload Dataset (CSV / XLSX / JSON)
          </label>
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.json"
            onChange={(e) => setDataFile(e.target.files[0])}
            className="w-full"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 rounded font-semibold transition ${
            loading
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {loading ? "Scanning..." : "Start Scan"}
        </button>
      </form>

      {/* Result Section */}
      {result && (
        <div className="mt-10 bg-[#1e293b] p-6 rounded-xl max-w-2xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Scan Result</h2>

          <p>
            <strong>Status:</strong> {result.status}
          </p>
          <p>
            <strong>Scan ID:</strong> {result.scan_id}
          </p>
          <p>
            <strong>Total Rules:</strong> {result.total_rules}
          </p>
          <p>
            <strong>Violations Found:</strong>{" "}
            {result.violations_found}
          </p>
          <p>
            <strong>Scan Mode:</strong> {result.scan_mode}
          </p>
        </div>
      )}
    </div>
  );
}