"use client";

import { useState } from "react";
import { Upload, CheckCircle, Zap, Beaker, MapPin, AlertCircle } from "lucide-react";
import Navbar from "../components/Navbar";
import { Card, StatCard, Alert } from "../components/common";

interface SoilAnalysis {
  soil_type: string;
  fertility_level: string;
  moisture_condition: string;
  ph_level: number;
  recommended_crops: string[];
  fertilizer_suggestions: string[];
  detailed_report: string;
  report_en?: string;
  report_gu?: string;
  report_hi?: string;
  confidence_score: number;
}

export default function SoilPage() {
  const [location, setLocation] = useState("Ahmedabad, Gujarat");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<SoilAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.type.startsWith("image/")) {
        setError("Please upload a valid image file (JPG, PNG, WEBP).");
        return;
      }
      if (selectedFile.size > 8 * 1024 * 1024) {
        setError("Image is too large. Please upload a file under 8 MB.");
        return;
      }

      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError(null);
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("farmer_id", "demo_farmer");
    formData.append("location", location);
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/soil/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorBody = await res.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Soil analysis failed. Please try again.");
      }

      const data = await res.json();
      setResult(data.analysis);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Unexpected error during soil analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#fff7ed_0%,_#fffbeb_35%,_#f8fafc_100%)]">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8 md:py-10">
        <div className="mb-8 rounded-2xl bg-gradient-to-r from-amber-600 via-orange-600 to-rose-600 p-6 text-white shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-wider text-amber-100">Smart Soil Lab</p>
              <h1 className="mt-1 text-3xl font-bold md:text-4xl">Soil Photo to Field Report</h1>
              <p className="mt-2 max-w-2xl text-sm text-amber-100 md:text-base">
                Upload one soil image and get fertility, moisture, pH, recommended crops, and input suggestions.
              </p>
            </div>
            <Beaker className="h-10 w-10 shrink-0 text-amber-100" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card title="📸 Upload Soil Sample Photo" className="lg:col-span-2 border-0 shadow-xl">
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Field Location
                </label>
                <div className="relative">
                  <MapPin className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="District, State"
                    className="w-full rounded-lg border border-amber-200 bg-amber-50/40 py-2 pl-10 pr-3 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div className="cursor-pointer rounded-xl border-2 border-dashed border-amber-300 bg-amber-50/40 p-8 text-center transition hover:border-amber-500">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="fileInput"
                />
                <label htmlFor="fileInput" className="cursor-pointer">
                  {preview ? (
                    <div className="space-y-3">
                      <img src={preview} alt="Soil preview" className="mx-auto h-52 rounded-lg object-cover" />
                      <p className="text-sm text-green-600 font-semibold">✓ Image selected</p>
                      {file && <p className="text-xs text-gray-500">{file.name}</p>}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Upload className="mx-auto h-12 w-12 text-amber-500" />
                      <p className="font-medium text-gray-800">Drop soil photo or click to upload</p>
                      <p className="text-sm text-gray-500">Best result: clear daylight photo from 6-inch depth</p>
                    </div>
                  )}
                </label>
              </div>

              {error && (
                <Alert
                  type="danger"
                  title="Analysis Error"
                  message={error}
                />
              )}

              <button
                onClick={handleAnalyze}
                disabled={!file || loading}
                className="w-full rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-6 py-3 font-medium text-white transition hover:from-amber-700 hover:to-orange-700 disabled:cursor-not-allowed disabled:from-gray-400 disabled:to-gray-400"
              >
                {loading ? "🔬 Analyzing..." : "🔬 Analyze Soil"}
              </button>

              <Alert
                type="info"
                title="📸 How to Take Photo"
                message="Dig 6 inches deep. Take clear photo in sunlight. Show soil texture, color, and composition clearly."
              />
            </div>
          </Card>

          <Card title="ℹ️ What You Get" className="border-0 shadow-xl">
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
                <p className="font-semibold text-amber-900">Soil Type</p>
                <p className="text-amber-700 text-xs mt-1">Clay, sandy, loamy, or silty</p>
              </div>

              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <p className="font-semibold text-green-900">Fertility Level</p>
                <p className="text-green-700 text-xs mt-1">
                  Nutrient content assessment
                </p>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="font-semibold text-blue-900">Moisture</p>
                <p className="text-blue-700 text-xs mt-1">
                  Water retention capacity
                </p>
              </div>

              <div className="p-3 bg-rose-50 rounded-lg border border-rose-200">
                <p className="font-semibold text-rose-900">pH Level</p>
                <p className="text-rose-700 text-xs mt-1">Acidity and alkalinity estimate</p>
              </div>
            </div>
          </Card>
        </div>

        {result && (
          <div className="mt-8 space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Soil Type"
                value={result.soil_type.toUpperCase()}
                color="yellow"
              />
              <StatCard
                label="Fertility"
                value={result.fertility_level.toUpperCase()}
                color="green"
              />
              <StatCard
                label="Moisture"
                value={result.moisture_condition.toUpperCase()}
                color="blue"
              />
              <StatCard
                label="pH Level"
                value={Number(result.ph_level || 0).toFixed(1)}
                color="red"
              />
            </div>

            <Card title="📊 Detailed Soil Report">
              <div className="space-y-4">
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-700">English</p>
                  <p className="text-sm leading-relaxed text-gray-800">{result.report_en || result.detailed_report}</p>
                </div>
                <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-700">Gujarati (ગુજરાતી)</p>
                  <p className="text-sm leading-relaxed text-gray-800">{result.report_gu || "ગુજરાતી રિપોર્ટ ઉપલબ્ધ નથી."}</p>
                </div>
                <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-orange-700">Hindi (हिन्दी)</p>
                  <p className="text-sm leading-relaxed text-gray-800">{result.report_hi || "हिन्दी रिपोर्ट उपलब्ध नहीं है।"}</p>
                </div>
              </div>
            </Card>

            <Card title="🌾 Recommended Crops">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {result.recommended_crops.map((crop, idx) => (
                  <div key={idx} className="p-4 bg-green-50 border-2 border-green-300 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="font-semibold text-green-900">{crop}</span>
                    </div>
                    <p className="text-sm text-green-700">
                      Suitable for {result.soil_type} soil with {result.fertility_level} fertility
                    </p>
                  </div>
                ))}
              </div>
            </Card>

            <Card title="🌿 Fertilizer Recommendations">
              <div className="space-y-3">
                {result.fertilizer_suggestions.map((suggestion, idx) => (
                  <div key={idx} className="flex gap-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <Zap className="h-5 w-5 text-amber-600 flex-shrink-0" />
                    <p className="text-gray-700">{suggestion}</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card title="📈 Soil Improvement Plan">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <p className="font-semibold text-blue-900 mb-2">Immediate Actions</p>
                  <ul className="space-y-1 text-sm text-blue-700">
                    <li>✓ Remove crop residues</li>
                    <li>✓ Apply recommended fertilizer</li>
                    <li>✓ Plan irrigation schedule</li>
                  </ul>
                </div>

                <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
                  <p className="font-semibold text-green-900 mb-2">Long-term Strategy</p>
                  <ul className="space-y-1 text-sm text-green-700">
                    <li>✓ Add organic matter yearly</li>
                    <li>✓ Practice crop rotation</li>
                    <li>✓ Soil testing every 2 years</li>
                  </ul>
                </div>
              </div>
            </Card>

            <Card className="bg-gradient-to-r from-rose-600 to-orange-600 text-white border-0 shadow-xl">
              <div>
                <h3 className="text-xl font-bold mb-3">🧪 pH Adjustment</h3>
                {Number(result.ph_level || 0) < 6 && (
                  <p className="mb-3">
                    Your soil is acidic (pH {Number(result.ph_level || 0).toFixed(1)}). <strong>Recommendation:</strong> Apply lime/crushed limestone at 2-3 tons/acre.
                  </p>
                )}
                {Number(result.ph_level || 0) > 7.5 && (
                  <p className="mb-3">
                    Your soil is alkaline (pH {Number(result.ph_level || 0).toFixed(1)}). <strong>Recommendation:</strong> Add sulfur or use acidifying fertilizers.
                  </p>
                )}
                {Number(result.ph_level || 0) >= 6 && Number(result.ph_level || 0) <= 7.5 && (
                  <p className="mb-3">
                    Your soil pH ({Number(result.ph_level || 0).toFixed(1)}) is well-balanced. No adjustment needed at this time.
                  </p>
                )}

                <div className="bg-white bg-opacity-20 rounded-lg p-3 text-sm">
                  <p className="font-semibold mb-1">Ideal pH Ranges:</p>
                  <p>Most crops: 6.0-7.5 | Rice: 5.5-7.0 | Sugarcane: 6.0-8.0</p>
                </div>

                <div className="mt-3 flex items-center gap-2 text-sm text-amber-100">
                  <AlertCircle className="h-4 w-4" />
                  Confidence: {(result.confidence_score * 100).toFixed(0)}%
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
