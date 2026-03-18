"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, MapPin, BarChart3 } from "lucide-react";
import Navbar from "../components/Navbar";
import { Card, StatCard, Alert } from "../components/common";

interface MarketData {
  crop: string;
  current_price: number;
  week_ago_price: number;
  trend: string;
  nearby_prices: Record<string, number>;
  best_mandi: string;
  recommendation: string;
}

export default function MarketPage() {
  const [crop, setCrop] = useState("wheat");
  const [market, setMarket] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(false);
  const crops = ["wheat", "rice", "cotton", "maize", "groundnut"];

  const fetchMarket = async (selectedCrop: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/market/insights/${selectedCrop}`);
      if (res.ok) {
        setMarket(await res.json());
      }
    } catch (error) {
      console.error("Error fetching market data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCropSelect = (selectedCrop: string) => {
    setCrop(selectedCrop);
    fetchMarket(selectedCrop);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">💰 Market Prices & Insights</h1>

        {/* Crop Selection */}
        <Card title="🌾 Select Crop" className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {crops.map((c) => (
              <button
                key={c}
                onClick={() => handleCropSelect(c)}
                className={`px-4 py-3 rounded-lg font-medium transition ${
                  crop === c
                    ? "bg-purple-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </button>
            ))}
          </div>
        </Card>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block text-4xl">💹</div>
            <p className="text-gray-600 mt-2">Loading market data...</p>
          </div>
        ) : market ? (
          <>
            {/* Price Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card className="border-2 border-purple-300">
                <div className="text-center">
                  <p className="text-gray-600 text-sm mb-2">Current Price</p>
                  <p className="text-4xl font-bold text-purple-600">₹{market.current_price}</p>
                  <p className="text-xs text-gray-500 mt-2">/quintal</p>
                </div>
              </Card>

              <Card className="border-2 border-blue-300">
                <div className="text-center">
                  <p className="text-gray-600 text-sm mb-2">Week Ago</p>
                  <p className="text-4xl font-bold text-blue-600">₹{market.week_ago_price}</p>
                  <p className={`text-sm font-semibold mt-2 ${
                    market.current_price > market.week_ago_price ? "text-green-600" : "text-red-600"
                  }`}>
                    {market.current_price > market.week_ago_price ? "↑" : "↓"}{" "}
                    ₹{Math.abs(market.current_price - market.week_ago_price)}
                  </p>
                </div>
              </Card>

              <Card className="border-2 border-green-300">
                <div className="text-center">
                  <p className="text-gray-600 text-sm mb-2">Trend</p>
                  <p className="text-4xl font-bold text-green-600">
                    {market.trend === "up" ? "📈" : market.trend === "down" ? "📉" : "➡️"}
                  </p>
                  <p className="text-sm font-semibold text-gray-700 mt-2 capitalize">{market.trend}</p>
                </div>
              </Card>
            </div>

            {/* Recommendation Alert */}
            <Alert
              type={market.trend === "up" ? "success" : "info"}
              title="💡 Market Recommendation"
              message={market.recommendation}
            />

            {/* Nearby Mandis */}
            <Card title="🏪 Prices in Nearby Mandis" className="mt-8 mb-8">
              <div className="space-y-3">
                {Object.entries(market.nearby_prices).map(([mandi, price]) => (
                  <div key={mandi} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-3">
                      <MapPin className="h-5 w-5 text-purple-600" />
                      <span className="font-semibold text-gray-800">{mandi}</span>
                      {mandi === market.best_mandi && (
                        <span className="bg-green-200 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                          ⭐ Best Price
                        </span>
                      )}
                    </div>
                    <p className="text-2xl font-bold text-purple-600">₹{price}</p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Selling Tips */}
            <Card title="📋 Selling Tips">
              <div className="space-y-3">
                <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <p className="font-semibold text-blue-900">Best Mandi to Sell</p>
                  <p className="text-sm text-blue-700 mt-1">{market.best_mandi}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
                    <p className="font-semibold text-green-900">📊 Market Analysis</p>
                    <p className="text-sm text-green-700 mt-1">
                      Prices are {market.trend === "up" ? "increasing" : "decreasing"}. 
                      {market.trend === "up" ? " Consider waiting for peak prices." : " Sell soon to avoid losses."}
                    </p>
                  </div>

                  <div className="p-4 bg-orange-50 border-l-4 border-orange-500 rounded">
                    <p className="font-semibold text-orange-900">⏰ Timing Suggestion</p>
                    <p className="text-sm text-orange-700 mt-1">
                      Best selling window: 3-5 days. Monitor daily for price movements.
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </>
        ) : (
          <Card>
            <p className="text-center text-gray-600">Select a crop to view market prices</p>
          </Card>
        )}
      </div>
    </div>
  );
}
