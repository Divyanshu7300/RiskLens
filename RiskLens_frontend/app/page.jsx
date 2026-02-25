"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex flex-col justify-center items-center px-6">

      {/* Hero Section */}
      <div className="text-center max-w-3xl">
        <h1 className="text-5xl font-bold mb-6 leading-tight">
          AI-Powered <span className="text-green-400">Compliance Monitoring</span>
        </h1>

        <p className="text-gray-400 text-lg mb-8">
          Automatically extract rules from policy documents, scan enterprise data,
          detect violations, and generate intelligent risk reports — all in one system.
        </p>

        <div className="flex justify-center gap-6">
          <Link
            href="/login"
            className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold transition"
          >
            Login
          </Link>

          <Link
            href="/scan"
            className="border border-gray-500 hover:border-white px-6 py-3 rounded-lg font-semibold transition"
          >
            Start Scan
          </Link>
        </div>
      </div>

      {/* Feature Section */}
      <div className="grid md:grid-cols-3 gap-8 mt-20 max-w-6xl w-full">
        <FeatureCard
          title="Policy Intelligence"
          description="Upload PDFs and automatically convert unstructured policies into structured machine-readable rules."
        />
        <FeatureCard
          title="Automated Risk Detection"
          description="Scan live databases or datasets and instantly detect compliance violations."
        />
        <FeatureCard
          title="Analytics & Reports"
          description="Get risk distribution, top risky tables, and downloadable compliance reports."
        />
      </div>

      {/* Footer */}
      <div className="mt-20 text-gray-500 text-sm">
        © 2026 PolicyGuard. All rights reserved.
      </div>
    </div>
  );
}

function FeatureCard({ title, description }) {
  return (
    <div className="bg-[#1e293b] p-6 rounded-xl shadow-lg hover:scale-105 transition transform">
      <h3 className="text-xl font-semibold mb-3 text-green-400">
        {title}
      </h3>
      <p className="text-gray-400 text-sm">
        {description}
      </p>
    </div>
  );
}