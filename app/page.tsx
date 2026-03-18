"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Tractor, ThermometerSun, Leaf, AlertTriangle, Droplet, MapPin, Activity, CheckCircle, Info, Mic, Copy, Download } from "lucide-react";
import Navbar from "./components/Navbar";
import { Card, Alert, StatCard } from "./components/common";

type Message = {
  id: string;
  sender: "user" | "ai";
  text: string;
  data?: {
    location?: string;
    weather_summary?: string;
    risk_scores?: {
      disease_risk: number;
      irrigation_need: number;
      spray_effectiveness: number;
    };
    decisions?: string[];
    action_plan?: string[];
    reason?: string;
  };
  timestamp: string;
};

const isJsonString = (str: string) => {
  try {
    const trimmed = str.trim();
    if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
      JSON.parse(trimmed);
      return true;
    }
  } catch {
    return false;
  }
  return false;
};

export default function ChatDashboard() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "ai",
      text: "नमस्ते! 👋 मैं कि सान साथी हूँ, आपका स्मार्ट खेती सहायक। आप मुझसे फसल सलाह, मौसम, बीमारी और बाजार कीमतों के बारे में पूछ सकते हैं।\n\nHello! 👋 I'm Kisan Saathi, your smart agriculture assistant. Ask me about crops, weather, diseases, and market prices!",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<"en" | "gu">("en");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          language: language === "gu" ? "gu" : "en",
        }),
      });

      if (response.ok) {
        const data = await response.json();

        const aiMessage: Message = {
          id: Date.now().toString(),
          sender: "ai",
          text: data.reply,
          data: data,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, aiMessage]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            sender: "ai",
            text: "I apologize, but I encountered an error processing your request. Please check if the backend server is running.",
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: "ai",
          text: "Connection error. Please ensure the backend server is running on http://localhost:8000",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessageContent = (message: Message) => {
    return (
      <div className="space-y-3">
        <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{message.text}</p>

        {/* Display structured data if available */}
        {message.data && (
          <div className="space-y-3 mt-4">
            {message.data.location && (
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-gray-500" />
                <strong>Location:</strong> {message.data.location}
              </div>
            )}

            {message.data.weather_summary && (
              <Card title="🌤️ Weather Summary">
                <p className="text-gray-700">{message.data.weather_summary}</p>
              </Card>
            )}

            {message.data.risk_scores && (
              <Card title="⚠️ Risk Assessment">
                <div className="grid grid-cols-3 gap-2">
                  <StatCard
                    label="Disease Risk"
                    value={message.data.risk_scores.disease_risk}
                    unit="%"
                    color="red"
                  />
                  <StatCard
                    label="Irrigation Need"
                    value={message.data.risk_scores.irrigation_need}
                    unit="%"
                    color="blue"
                  />
                  <StatCard
                    label="Spray Timing"
                    value={message.data.risk_scores.spray_effectiveness}
                    unit="%"
                    color="green"
                  />
                </div>
              </Card>
            )}

            {message.data.decisions && message.data.decisions.length > 0 && (
              <Card title="✅ Recommendations">
                <ul className="space-y-2">
                  {message.data.decisions.map((decision, idx) => (
                    <li key={idx} className="flex gap-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span>{decision}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {message.data.action_plan && message.data.action_plan.length > 0 && (
              <Card title="📋 Action Plan">
                <ol className="space-y-2">
                  {message.data.action_plan.map((action, idx) => (
                    <li key={idx} className="flex gap-2 text-sm">
                      <span className="font-semibold text-green-600">{idx + 1}.</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ol>
              </Card>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Navbar />

      <div className="flex gap-4 p-4 max-w-7xl mx-auto w-full">
        {/* Quick Stats Sidebar */}
        <div className="hidden lg:w-64 lg:flex flex-col gap-3">
          <Card title="📍 Location" icon={<MapPin className="h-5 w-5 text-green-600" />}>
            <input
              type="text"
              placeholder="Enter your district"
              className="w-full px-3 py-2 border rounded-lg text-sm"
              defaultValue="Gujarat"
            />
          </Card>

          <Card title="🌾 Your Crops" icon={<Leaf className="h-5 w-5 text-green-600" />}>
            <div className="space-y-2 text-sm">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="rounded" />
                Wheat
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="rounded" />
                Cotton
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                Rice
              </label>
            </div>
          </Card>

          <Card title="🔔 Quick Actions">
            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
                🌦️ Weather
              </button>
              <button className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
                💰 Market Price
              </button>
              <button className="w-full px-3 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700">
                🐛 Disease Check
              </button>
            </div>
          </Card>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-white rounded-lg shadow-lg overflow-hidden max-w-4xl mx-auto w-full lg:w-auto">
          {/* Header */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Tractor className="h-6 w-6" />
              <div>
                <h1 className="font-bold">Kisan Saathi AI Chat</h1>
                <p className="text-sm text-green-100">Your smart farming assistant</p>
              </div>
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as "en" | "gu")}
              className="px-3 py-2 bg-green-50 text-green-900 rounded-lg text-sm font-medium"
            >
              <option value="en">English</option>
              <option value="gu">ગુજરાતી</option>
            </select>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-2xl rounded-lg p-4 ${
                    message.sender === "user"
                      ? "bg-green-600 text-white rounded-br-none"
                      : "bg-gray-100 text-gray-800 rounded-bl-none border border-gray-200"
                  }`}
                >
                  {renderMessageContent(message)}
                  <p
                    className={`text-xs mt-2 ${
                      message.sender === "user" ? "text-green-100" : "text-gray-500"
                    }`}
                  >
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2">
                <div className="bg-gray-100 rounded-lg p-4 border border-gray-200">
                  <div className="flex gap-2">
                    <div className="h-3 w-3 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="h-3 w-3 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="h-3 w-3 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t bg-white p-4">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me about crops, weather, markets, or diseases..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-600"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-2"
              >
                <Send className="h-5 w-5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
            <p className="text-xs text-gray-500 mt-2">
              💡 Try: "What's the weather?", "Disease in my wheat?", "Rice prices today?"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
