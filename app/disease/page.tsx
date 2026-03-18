"use client";

import { useState } from "react";
import { Upload, ShieldAlert, Microscope, Stethoscope } from "lucide-react";
import Navbar from "../components/Navbar";
import { Card, Alert } from "../components/common";

interface DiseaseResult {
  disease_detected: string;
  confidence_score: number;
  treatment_suggestions: string[];
  severity_level: string;
  action_required: string;
  detailed_report?: string;
  report_en?: string;
  report_gu?: string;
  report_hi?: string;
}

export default function DiseasePage() {
  const [crop, setCrop] = useState("wheat");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<DiseaseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.type.startsWith("image/")) {
        setError("Please upload a valid crop image (JPG, PNG, WEBP).");
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
    formData.append("crop", crop);
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/disease/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorBody = await res.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Disease analysis failed. Please try again.");
      }

      const data = await res.json();
      setResult(data.disease_analysis);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Unexpected error during disease analysis.");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "mild":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "moderate":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "severe":
        return "bg-red-100 text-red-800 border-red-300";
      default:
        return "bg-green-100 text-green-800 border-green-300";
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#fff1f2_0%,_#fff7ed_35%,_#f8fafc_100%)]">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8 md:py-10">
        <div className="mb-8 rounded-2xl bg-gradient-to-r from-rose-600 via-red-600 to-orange-600 p-6 text-white shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-wider text-rose-100">Leaf & Crop Health AI</p>
              <h1 className="mt-1 text-3xl font-bold md:text-4xl">Disease Detection Report</h1>
              <p className="mt-2 max-w-2xl text-sm text-rose-100 md:text-base">
                Upload crop photos to detect likely disease, severity, and treatment actions in one view.
              </p>
            </div>
            <Microscope className="h-10 w-10 shrink-0 text-rose-100" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card title="📸 Analyze Crop Image" className="lg:col-span-2 border-0 shadow-xl">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Crop Type
                </label>
                <select
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
                >
                  <option value="wheat">Wheat</option>
                  <option value="rice">Rice</option>
                  <option value="cotton">Cotton</option>
                  <option value="maize">Maize</option>
                </select>
              </div>

              <div className="cursor-pointer rounded-xl border-2 border-dashed border-rose-300 bg-rose-50/40 p-8 text-center transition hover:border-rose-500">
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
                      <img src={preview} alt="Crop preview" className="mx-auto h-52 rounded-lg object-cover" />
                      <p className="text-sm text-green-600 font-semibold">✓ Image selected</p>
                      {file && <p className="text-xs text-gray-500">{file.name}</p>}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Upload className="h-12 w-12 text-rose-500 mx-auto" />
                      <p className="text-gray-700 font-medium">Drop crop image or click to upload</p>
                      <p className="text-sm text-gray-500">PNG, JPG up to 5MB</p>
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
                className="w-full rounded-lg bg-gradient-to-r from-rose-600 to-red-600 px-6 py-3 font-medium text-white transition hover:from-rose-700 hover:to-red-700 disabled:cursor-not-allowed disabled:from-gray-400 disabled:to-gray-400"
              >
                {loading ? "🔍 Analyzing..." : "🔍 Analyze Disease"}
              </button>

              <Alert
                type="info"
                title="📸 Photography Tips"
                message="Take clear photos of affected leaves in good lighting. Show the entire affected area for accurate diagnosis."
              />
            </div>
          </Card>

          <Card title="ℹ️ How It Works" className="border-0 shadow-xl">
            <div className="space-y-3 text-sm">
              <p className="text-gray-700">
                <strong>Step 1:</strong> Select your crop type
              </p>
              <p className="text-gray-700">
                <strong>Step 2:</strong> Take a clear photo of affected area
              </p>
              <p className="text-gray-700">
                <strong>Step 3:</strong> Upload and wait for analysis
              </p>
              <p className="text-gray-700">
                <strong>Step 4:</strong> Get treatment recommendations
              </p>

              <div className="mt-4 pt-4 border-t">
                <p className="font-semibold text-gray-800 mb-2">Common Diseases:</p>
                <ul className="space-y-1 text-gray-700">
                  <li>• Leaf Spot & Blight</li>
                  <li>• Rust & Powdery Mildew</li>
                  <li>• Wilt & Yellow Mosaic</li>
                  <li>• Sheath Blight & Blast</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>

        {/* Results Section */}
        {result && (
          <div className="mt-8 space-y-6">
            <Card className="bg-gradient-to-r from-rose-600 to-red-700 text-white border-0 shadow-xl">
              <div className="space-y-4">
                <div>
                  <h3 className="text-2xl font-bold">{result.disease_detected}</h3>
                  <p className="text-red-100 mt-1">{result.action_required}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <p className="text-red-700 text-sm">Confidence</p>
                    <p className="text-3xl font-bold text-black">{(result.confidence_score * 100).toFixed(0)}%</p>
                  </div>
                  <div className={`rounded-lg border-2 p-4 ${getSeverityColor(result.severity_level)}`}>
                    <p className="text-sm font-semibold capitalize text-blue-800">{result.severity_level} Severity</p>
                    <p className="text-2xl font-bold text-blue-900 mt-1">{result.severity_level === "mild" ? "😊" : result.severity_level === "moderate" ? "😟" : "😱"}</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card title="💊 Treatment Recommendations">
              <ol className="space-y-3">
                {result.treatment_suggestions.map((treatment, idx) => (
                  <li key={idx} className="flex gap-3">
                    <span className="font-semibold text-red-600 flex-shrink-0">{idx + 1}.</span>
                    <span className="text-gray-700">{treatment}</span>
                  </li>
                ))}
              </ol>
            </Card>

            <Card title="📋 Detailed Disease Report">
              <div className="space-y-4">
                <div className="rounded-lg border border-rose-200 bg-rose-50 p-4">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-rose-700">English</p>
                  <p className="text-sm leading-relaxed text-gray-800">{result.report_en || result.action_required}</p>
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

            <Card title="🛡️ Preventive Measures">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
                  <p className="font-semibold text-green-900 mb-2">Regular Monitoring</p>
                  <p className="text-sm text-green-700">Scout your fields daily and remove infected plants immediately.</p>
                </div>
                <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <p className="font-semibold text-blue-900 mb-2">Crop Rotation</p>
                  <p className="text-sm text-blue-700">Change crops annually to break disease cycles in soil.</p>
                </div>
                <div className="p-4 bg-rose-50 border-l-4 border-rose-500 rounded">
                  <p className="font-semibold text-rose-900 mb-2">Resistant Varieties</p>
                  <p className="text-sm text-rose-700">Use disease-resistant seed varieties for future plantings.</p>
                </div>
                <div className="p-4 bg-orange-50 border-l-4 border-orange-500 rounded">
                  <p className="font-semibold text-orange-900 mb-2">Field Hygiene</p>
                  <p className="text-sm text-orange-700">Keep field clean and remove crop residues properly.</p>
                </div>
              </div>
            </Card>

            <Card title="⏰ Recommended Timeline">
              <div className="space-y-3">
                <div className="flex gap-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="text-2xl">⚡</div>
                  <div>
                    <p className="font-semibold text-red-900">Immediate (Today)</p>
                    <p className="text-sm text-red-700">Remove infected leaves or plants</p>
                  </div>
                </div>
                <div className="flex gap-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="text-2xl">📅</div>
                  <div>
                    <p className="font-semibold text-orange-900">Within 2-3 Days</p>
                    <p className="text-sm text-orange-700">Apply recommended treatment</p>
                  </div>
                </div>
                <div className="flex gap-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-2xl">🔄</div>
                  <div>
                    <p className="font-semibold text-green-900">Follow-up</p>
                    <p className="text-sm text-green-700">Monitor crop and repeat treatment if needed</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card title="🧑‍⚕️ Expert Note" className="border-0 shadow-xl">
              <div className="flex items-start gap-3 text-sm text-gray-700">
                <Stethoscope className="mt-0.5 h-5 w-5 text-rose-600" />
                <p>
                  AI detection is advisory. For severe spread or uncertain visual symptoms, confirm with a local agri expert or lab before spraying.
                </p>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
