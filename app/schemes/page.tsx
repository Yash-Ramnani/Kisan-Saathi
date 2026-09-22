"use client";

import { useEffect, useState } from "react";
import { ExternalLink, RefreshCw, Landmark, ShieldCheck, CircleAlert } from "lucide-react";
import Navbar from "../components/Navbar";
import { Card, Alert } from "../components/common";

type SchemeItem = {
  title: string;
  url: string;
  source: string;
};

type SchemeResponse = {
  fetched_at: string;
  total_schemes: number;
  sources_checked: Array<{ source: string; status: string }>;
  schemes: SchemeItem[];
};

export default function SchemesPage() {
  const [data, setData] = useState<SchemeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSchemes = async (refresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const url = `http://localhost:8000/api/schemes/current${refresh ? "?refresh=true" : ""}`;
      const res = await fetch(url);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Failed to fetch schemes");
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchemes(false);
  }, []);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#ecfeff_0%,_#f0fdf4_35%,_#f8fafc_100%)]">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8 md:py-10">
        <div className="mb-8 rounded-2xl bg-gradient-to-r from-emerald-700 via-teal-700 to-cyan-700 p-6 text-white shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-wider text-emerald-100">Government Benefits Hub</p>
              <h1 className="mt-1 text-3xl font-bold md:text-4xl">Live Farmer Schemes</h1>
              <p className="mt-2 max-w-2xl text-sm text-emerald-100 md:text-base">
                Real-time discoverable scheme links fetched from government websites for farmers.
              </p>
            </div>
            <Landmark className="h-10 w-10 shrink-0 text-emerald-100" />
          </div>
        </div>

        <div className="mb-6 flex flex-wrap items-center gap-3">
          <button
            onClick={() => loadSchemes(true)}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:bg-gray-400"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Refreshing..." : "Refresh Live Schemes"}
          </button>

          {data?.fetched_at && (
            <span className="rounded-lg bg-white px-3 py-2 text-xs text-gray-600 shadow-sm border">
              Last fetched: {new Date(data.fetched_at).toLocaleString()}
            </span>
          )}

          {data && (
            <span className="rounded-lg bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 border border-emerald-200">
              Total schemes found: {data.total_schemes}
            </span>
          )}
        </div>

        {error && <Alert type="danger" title="Unable to fetch schemes" message={error} />}

        <Card title="Available Schemes" className="border-0 shadow-xl">
          {!data && loading && <p className="text-sm text-gray-600">Loading schemes...</p>}

          {data && data.schemes.length === 0 && (
            <Alert
              type="info"
              title="No schemes found right now"
              message="Try refreshing in a few minutes. Source websites may be temporarily unavailable."
            />
          )}

          <div className="space-y-3">
            {data?.schemes.map((scheme, index) => (
              <a
                key={`${scheme.url}-${index}`}
                href={scheme.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 transition hover:border-emerald-400 hover:bg-emerald-50"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-gray-900">{scheme.title}</p>
                    <p className="mt-1 text-xs text-gray-500">Source: {scheme.source}</p>
                    <p className="mt-2 text-xs text-emerald-700 break-all">{scheme.url}</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-emerald-700 shrink-0" />
                </div>
              </a>
            ))}
          </div>
        </Card>

        <Card className="mt-6 border-0 shadow-xl bg-gradient-to-r from-cyan-700 to-emerald-700 text-white">
          <div className="flex items-start gap-3 text-sm">
            <ShieldCheck className="h-5 w-5 shrink-0" />
            <p>
              Only government-domain links are listed. Always verify eligibility and latest terms on the official page before applying.
            </p>
          </div>
          <div className="mt-3 flex items-start gap-3 text-sm text-cyan-100">
            <CircleAlert className="h-5 w-5 shrink-0" />
            <p>
              Chat assistant can now use this live schemes context to suggest relevant programs for your queries.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
