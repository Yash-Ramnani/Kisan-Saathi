"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import {
  Send,
  Tractor,
  Leaf,
  MapPin,
  CheckCircle,
  Sparkles,
  Bot,
  UserRound,
  CloudSun,
  LineChart,
  Bug,
  Landmark,
} from "lucide-react";
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

const quickPrompts = [
  "Best irrigation plan for cotton this week",
  "Show mandi trend for wheat today",
  "Leaf spots in rice, what should I spray?",
  "Government schemes for small farmers in Gujarat",
];

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

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: messageText,
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
          message: messageText,
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

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage(input);
  };

  const submitPrompt = async (prompt: string) => {
    setInput(prompt);
    await sendMessage(prompt);
  };

  const renderMessageContent = (message: Message) => {
    return (
      <div className="space-y-3">
        <p className={`whitespace-pre-wrap leading-relaxed ${message.sender === "user" ? "text-white" : "text-gray-800"}`}>
          {message.text}
        </p>

        {/* Display structured data if available */}
        {message.data && message.sender === "ai" && (
          <div className="space-y-3 mt-4">
            {message.data.location && (
              <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                <MapPin className="h-4 w-4" />
                <strong>Location:</strong>
                <span>{message.data.location}</span>
              </div>
            )}

            {message.data.weather_summary && (
              <Card title="Weather Summary">
                <p className="text-gray-700 text-sm">{message.data.weather_summary}</p>
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
              <Card title="Recommendations">
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
              <Card title="Action Plan">
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
    <div className="h-screen overflow-hidden bg-[radial-gradient(circle_at_0%_0%,_#dcfce7_0%,_#ecfeff_35%,_#f8fafc_100%)]">
      <Navbar />

      <div className="mx-auto grid h-[calc(100vh-64px)] w-full max-w-7xl grid-cols-1 gap-4 px-4 py-3 lg:grid-cols-[280px_1fr]">
        <div className="hidden lg:flex lg:flex-col lg:gap-4 lg:overflow-y-auto lg:pr-1">
          <Card className="border-0 shadow-xl bg-gradient-to-br from-emerald-700 via-green-700 to-teal-700 text-white">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-emerald-100">
                <Sparkles className="h-4 w-4" />
                <span className="text-xs uppercase tracking-widest">AI Command Panel</span>
              </div>
              <h2 className="text-xl font-bold">Kisan Saathi</h2>
              <p className="text-sm text-emerald-100">
                Ask about crops, weather, disease, market, and farmer schemes with live links.
              </p>
            </div>
          </Card>

          <Card title="Quick Navigation" icon={<Leaf className="h-5 w-5 text-emerald-700" />} className="border-0 shadow-lg">
            <div className="space-y-2">
              <Link href="/weather" className="flex items-center gap-2 rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-sm font-medium text-sky-800 hover:bg-sky-100">
                <CloudSun className="h-4 w-4" /> Weather Insights
              </Link>
              <Link href="/market" className="flex items-center gap-2 rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-800 hover:bg-indigo-100">
                <LineChart className="h-4 w-4" /> Market Trends
              </Link>
              <Link href="/disease" className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-800 hover:bg-rose-100">
                <Bug className="h-4 w-4" /> Disease Check
              </Link>
              <Link href="/schemes" className="flex items-center gap-2 rounded-lg border border-teal-200 bg-teal-50 px-3 py-2 text-sm font-medium text-teal-800 hover:bg-teal-100">
                <Landmark className="h-4 w-4" /> Govt Schemes
              </Link>
            </div>
          </Card>

          <Alert
            type="info"
            title="Tip"
            message="Include crop + location in your question for sharper recommendations."
          />
        </div>

        <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-2xl border border-emerald-100 bg-white/90 shadow-2xl backdrop-blur-sm">
          <div className="flex items-center justify-between border-b border-emerald-100 bg-gradient-to-r from-emerald-700 via-green-700 to-teal-700 p-4 text-white">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-white/15 p-2">
                <Tractor className="h-6 w-6" />
              </div>
              <div>
                <h1 className="font-bold tracking-wide">Kisan Saathi AI Chat</h1>
                <p className="text-sm text-emerald-100">Your field decision assistant</p>
              </div>
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as "en" | "gu")}
              className="rounded-lg bg-white/90 px-3 py-2 text-sm font-medium text-emerald-900"
            >
              <option value="en">English</option>
              <option value="gu">ગુજરાતી</option>
            </select>
          </div>

          <div className="border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-cyan-50 px-4 py-3">
            <div className="flex flex-wrap gap-2">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => submitPrompt(prompt)}
                  disabled={loading}
                  className="rounded-full border border-emerald-200 bg-white px-3 py-1.5 text-xs font-medium text-emerald-800 hover:border-emerald-400 hover:bg-emerald-50 disabled:opacity-60"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top,_#f0fdfa_0%,_#ffffff_35%,_#f8fafc_100%)] p-5">
            <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                  <div className={`flex max-w-3xl items-end gap-2 ${message.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    <div className={`rounded-full p-2 ${message.sender === "user" ? "bg-emerald-600 text-white" : "bg-white text-emerald-700 border border-emerald-200"}`}>
                      {message.sender === "user" ? <UserRound className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    </div>
                <div
                        className={`rounded-2xl p-4 shadow-md ${
                    message.sender === "user"
                            ? "rounded-br-sm bg-gradient-to-r from-emerald-600 to-green-600 text-white"
                            : "rounded-bl-sm border border-gray-200 bg-white text-gray-800"
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
              </div>
            ))}
            {loading && (
                <div className="flex gap-2">
                  <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
                  <div className="flex gap-2">
                      <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-bounce"></div>
                      <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-bounce delay-100"></div>
                      <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
            )}
            <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="border-t border-emerald-100 bg-white p-4">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me about crops, weather, markets, or diseases..."
                className="flex-1 rounded-xl border border-emerald-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-green-600 px-4 py-3 font-medium text-white hover:from-emerald-700 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-400"
              >
                <Send className="h-5 w-5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
            <p className="mt-2 text-xs text-gray-500">
              Try: "Should I irrigate cotton today in Rajkot?" or "Best farmer scheme for drip irrigation"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
