"use client";

import { useState, useEffect } from "react";
import { Cloud, CloudRain, Wind, Droplets, Eye, Sun, ArrowDown, ArrowUp } from "lucide-react";
import Navbar from "../components/Navbar";
import { Card, StatCard, Alert } from "../components/common";

interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  wind_speed: number;
  weather_condition: string;
  feels_like: number;
  visibility: number;
}

interface Forecast {
  date: string;
  temp_max: number;
  temp_min: number;
  description: string;
  rainfall_prob: number;
  humidity: number;
}

export default function WeatherPage() {
  const [location, setLocation] = useState("Gujarat");
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<Forecast[]>([]);
  const [loading, setLoading] = useState(false);
  const [irrigationAdvice, setIrrigationAdvice] = useState<string[]>([]);
  const [sprayAdvice, setSprayAdvice] = useState<any>(null);

  const fetchWeather = async (loc: string) => {
    setLoading(true);
    try {
      const [weatherRes, forecastRes, irrigationRes, sprayRes] = await Promise.all([
        fetch(`http://localhost:8000/api/weather/${loc}`),
        fetch(`http://localhost:8000/api/weather/forecast/${loc}`),
        fetch(`http://localhost:8000/api/weather/irrigation-advice/${loc}`),
        fetch(`http://localhost:8000/api/weather/spray-recommendations/${loc}`),
      ]);

      if (weatherRes.ok) setWeather(await weatherRes.json());
      if (forecastRes.ok) {
        const data = await forecastRes.json();
        setForecast(data.forecast || []);
      }
      if (irrigationRes.ok) {
        const data = await irrigationRes.json();
        setIrrigationAdvice(data.irrigation_advice || []);
      }
      if (sprayRes.ok) {
        const data = await sprayRes.json();
        setSprayAdvice(data.spray_recommendations || {});
      }
    } catch (error) {
      console.error("Error fetching weather:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather(location);
  }, []);

  const handleLocationSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchWeather(location);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">🌤️ Weather & Climate</h1>

        {/* Location Input */}
        <form onSubmit={handleLocationSubmit} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter district/location"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              Check Weather
            </button>
          </div>
        </form>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin text-3xl">🌪️</div>
            <p className="text-gray-600 mt-2">Loading weather data...</p>
          </div>
        ) : weather ? (
          <>
            {/* Current Weather */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card className="bg-gradient-to-br from-blue-600 to-blue-700 text-white">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-3xl font-bold">{weather.temperature}°C</h2>
                    <p className="text-blue-100">{weather.weather_condition}</p>
                    <p className="text-sm text-blue-200 mt-1">Feels like {weather.feels_like}°C</p>
                  </div>
                  <Cloud className="h-16 w-16 text-blue-200" />
                </div>
              </Card>

              {/* Alerts */}
              <div className="space-y-3">
                {sprayAdvice?.is_good_time === false && (
                  <Alert
                    type="warning"
                    title="⚠️ Not Good for Spraying"
                    message={sprayAdvice.recommendations.join(", ")}
                  />
                )}
                {weather.rainfall > 20 && (
                  <Alert
                    type="info"
                    title="🌧️ Heavy Rain Expected"
                    message={`Rain probability: ${weather.rainfall}mm. Avoid irrigation today.`}
                  />
                )}
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard
                label="Humidity"
                value={weather.humidity}
                unit="%"
                icon={<Droplets className="h-5 w-5" />}
                color="blue"
              />
              <StatCard
                label="Wind Speed"
                value={weather.wind_speed}
                unit="km/h"
                icon={<Wind className="h-5 w-5" />}
                color="blue"
              />
              <StatCard
                label="Rainfall"
                value={weather.rainfall}
                unit="mm"
                icon={<CloudRain className="h-5 w-5" />}
                color="blue"
              />
              <StatCard
                label="Visibility"
                value={weather.visibility.toFixed(1)}
                unit="km"
                icon={<Eye className="h-5 w-5" />}
                color="blue"
              />
            </div>

            {/* 5-Day Forecast */}
            <Card title="📅 5-Day Forecast" className="mb-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {forecast.map((day, idx) => (
                  <div key={idx} className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                    <p className="text-sm font-semibold text-gray-700">
                      {new Date(day.date).toLocaleDateString("en-IN", { weekday: "short" })}
                    </p>
                    <div className="flex justify-between items-center my-2">
                      <span className="text-xl font-bold text-blue-600">{day.temp_max}°</span>
                      <span className="text-sm text-gray-600">{day.temp_min}°</span>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{day.description}</p>
                    <div className="flex gap-2 text-xs">
                      <span className="flex items-center gap-1">
                        <CloudRain className="h-3 w-3" /> {day.rainfall_prob.toFixed(0)}%
                      </span>
                      <span className="flex items-center gap-1">
                        <Droplets className="h-3 w-3" /> {day.humidity}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Irrigation Advice */}
            {irrigationAdvice.length > 0 && (
              <Card title="💧 Irrigation Recommendations" className="mb-8">
                <div className="space-y-3">
                  {irrigationAdvice.map((advice, idx) => (
                    <div key={idx} className="flex gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <Droplets className="h-5 w-5 text-blue-600 flex-shrink-0" />
                      <p className="text-gray-700">{advice}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Spraying Advice */}
            {sprayAdvice && (
              <Card title="🌬️ Pesticide/Fertilizer Spraying Advice">
                <div className="space-y-4">
                  <div className={`p-4 rounded-lg border-2 ${
                    sprayAdvice.is_good_time
                      ? "bg-green-50 border-green-300"
                      : "bg-red-50 border-red-300"
                  }`}>
                    <p className="font-semibold text-lg">
                      {sprayAdvice.is_good_time ? "✅ Good Time to Spray" : "❌ Not Recommended for Spraying"}
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <StatCard
                      label="Wind Speed (Ideal: 3-15)"
                      value={sprayAdvice.wind_speed}
                      unit="km/h"
                      color={sprayAdvice.wind_speed >= 3 && sprayAdvice.wind_speed <= 15 ? "green" : "red"}
                    />
                    <StatCard
                      label="Humidity"
                      value={sprayAdvice.humidity}
                      unit="%"
                      color={sprayAdvice.humidity < 85 ? "green" : "red"}
                    />
                    <StatCard
                      label="Rainfall"
                      value={sprayAdvice.rainfall}
                      unit="mm"
                      color={sprayAdvice.rainfall < 10 ? "green" : "red"}
                    />
                  </div>

                  {sprayAdvice.recommendations.length > 0 && (
                    <div className="pt-4 border-t">
                      <h4 className="font-semibold mb-2">Recommendations:</h4>
                      <ul className="space-y-2">
                        {sprayAdvice.recommendations.map((rec: string, idx: number) => (
                          <li key={idx} className="flex gap-2 text-sm">
                            <span className="text-orange-500">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </Card>
            )}
          </>
        ) : (
          <Alert type="info" title="No Data" message="Enter a location and click 'Check Weather'" />
        )}
      </div>
    </div>
  );
}
