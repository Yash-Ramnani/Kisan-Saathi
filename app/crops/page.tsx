"use client";

import { useState } from "react";
import { Sprout, Droplet, Leaf, AlertCircle, CheckCircle } from "lucide-react";
import Navbar from "../components/Navbar";
import { Card, StatCard, Alert } from "../components/common";

interface CropAdvice {
  crop: string;
  growth_stage: string;
  irrigation_plan: string[];
  fertilizer_plan: string[];
  pest_risks: string[];
  disease_risks: string[];
  next_actions: string[];
}

export default function CropsPage() {
  const [crop, setCrop] = useState("wheat");
  const [location, setLocation] = useState("Gujarat");
  const [soilType, setSoilType] = useState("loamy");
  const [advice, setAdvice] = useState<CropAdvice | null>(null);
  const [loading, setLoading] = useState(false);

  const crops = ["wheat", "rice", "cotton", "maize", "groundnut"];
  const soilTypes = ["clay", "sandy", "loamy", "silty"];

  const fetchAdvice = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/api/crops/advisory/${crop}/${location}/${soilType}`
      );
      if (res.ok) {
        setAdvice(await res.json());
      }
    } catch (error) {
      console.error("Error fetching crop advice:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">🌾 Crop Advisory</h1>

        {/* Input Section */}
        <Card title="📋 Select Your Crop & Conditions" className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Crop Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Crop Type
              </label>
              <div className="space-y-2">
                {crops.map((c) => (
                  <label key={c} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="crop"
                      value={c}
                      checked={crop === c}
                      onChange={(e) => setCrop(e.target.value)}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-700 capitalize">{c}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Soil Type */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Soil Type
              </label>
              <div className="space-y-2">
                {soilTypes.map((st) => (
                  <label key={st} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="soil"
                      value={st}
                      checked={soilType === st}
                      onChange={(e) => setSoilType(e.target.value)}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-700 capitalize">{st}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Location
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter district"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-600"
              />
            </div>
          </div>

          <button
            onClick={fetchAdvice}
            disabled={loading}
            className="mt-6 w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 font-semibold transition"
          >
            {loading ? "🔍 Generating Advice..." : "🔍 Get Crop Advice"}
          </button>
        </Card>

        {/* Results Section */}
        {advice ? (
          <div className="space-y-6">
            {/* Header */}
            <Card className="bg-gradient-to-r from-green-600 to-green-700 text-white">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-3xl font-bold capitalize">{advice.crop}</h2>
                  <p className="text-green-100 mt-2">
                    Growth Stage: <span className="font-semibold">{advice.growth_stage}</span>
                  </p>
                </div>
                <Sprout className="h-16 w-16 text-green-200 opacity-50" />
              </div>
            </Card>

            {/* Irrigation Plan */}
            <Card title="💧 Irrigation Schedule" icon={<Droplet className="h-5 w-5 text-blue-600" />}>
              <div className="space-y-2">
                {advice.irrigation_plan.map((plan, idx) => (
                  <div key={idx} className="flex gap-3 p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                    <Droplet className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    <p className="text-gray-700">{plan}</p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Fertilizer Plan */}
            <Card title="🌿 Fertilizer Schedule" icon={<Leaf className="h-5 w-5 text-green-600" />}>
              <div className="space-y-2">
                {advice.fertilizer_plan.map((fert, idx) => (
                  <div key={idx} className="flex gap-3 p-3 bg-green-50 border-l-4 border-green-500 rounded">
                    <Leaf className="h-5 w-5 text-green-600 flex-shrink-0" />
                    <p className="text-gray-700">{fert}</p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Risk Assessment */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Pest Risks */}
              <Card title="🐛 Common Pests">
                <div className="space-y-2">
                  {advice.pest_risks.map((pest, idx) => (
                    <div key={idx} className="flex gap-2 p-2 bg-orange-50 rounded border border-orange-200">
                      <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">{pest}</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Disease Risks */}
              <Card title="🤒 Disease Management">
                <div className="space-y-2">
                  {advice.disease_risks.map((disease, idx) => (
                    <div key={idx} className="flex gap-2 p-2 bg-red-50 rounded border border-red-200">
                      <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">{disease}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Action Plan */}
            <Card title="✅ Immediate Actions" icon={<CheckCircle className="h-5 w-5 text-green-600" />}>
              <ol className="space-y-3">
                {advice.next_actions.map((action, idx) => (
                  <li key={idx} className="flex gap-3">
                    <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-green-200 text-green-700 font-semibold flex-shrink-0">
                      {idx + 1}
                    </span>
                    <p className="text-gray-700">{action}</p>
                  </li>
                ))}
              </ol>
            </Card>

            {/* Companion Planting */}
            <Card title="👥 Companion Planting">
              <div className="bg-purple-50 border border-purple-300 rounded-lg p-4">
                <p className="text-sm text-gray-700 mb-4">
                  Growing compatible crops together can improve soil health and reduce pests.
                </p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {["Pulses", "Vegetables", "Herbs"].map((companion, idx) => (
                    <div key={idx} className="p-3 bg-white border border-purple-200 rounded-lg text-center">
                      <p className="font-semibold text-purple-700">{companion}</p>
                      <p className="text-xs text-gray-600 mt-1">Compatible with {advice.crop}</p>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            {/* Tips */}
            <Card title="💡 Farming Tips">
              <div className="space-y-3">
                <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <p className="font-semibold text-blue-900 mb-1">📊 Monitor Regularly</p>
                  <p className="text-sm text-blue-700">Scout your fields daily for early signs of pests or diseases.</p>
                </div>
                <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
                  <p className="font-semibold text-green-900 mb-1">🔄 Crop Rotation</p>
                  <p className="text-sm text-green-700">Change crops annually to maintain soil health and break pest cycles.</p>
                </div>
                <div className="p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
                  <p className="font-semibold text-yellow-900 mb-1">💧 Water Management</p>
                  <p className="text-sm text-yellow-700">Irrigate during early morning or late evening to reduce water loss.</p>
                </div>
              </div>
            </Card>
          </div>
        ) : (
          <Alert
            type="info"
            title="Get Started"
            message="Select your crop, soil type, and location above, then click 'Get Crop Advice' to receive personalized recommendations."
          />
        )}
      </div>
    </div>
  );
}
