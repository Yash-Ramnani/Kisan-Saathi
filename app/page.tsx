"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Tractor, ThermometerSun, Leaf, AlertTriangle, Droplet, MapPin, Activity, CheckCircle, Info } from "lucide-react";

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
  } catch (e) {
    return false;
  }
  return false;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "ai",
      text: "Namaste! I am Kisan Saathi 🌾, your Smart Farming AI Assistant.\n\nનમસ્તે! હું કિસાન સાથી છું, તમારો સ્માર્ટ ખેતી AI સહાયક.\n\nHow can I help you today? (Ask me about weather, irrigation, risk of disease, etc.)",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMsg.text }),
      });

      if (!response.ok) {
        throw new Error("API responded with an error");
      }

      const data = await response.json();
      
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: data.reply,
        data: {
          location: data.location,
          weather_summary: data.weather_summary,
          risk_scores: data.risk_scores,
          decisions: data.decisions,
          action_plan: data.action_plan,
          reason: data.reason
        },
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error(error);
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: "Apologies, there was an error connecting to the Kisan Saathi server. Please ensure the backend is running. \n\nક્ષમા કરશો, કિસાન સાથી સર્વર સાથે જોડાવામાં ભૂલ આવી હતી.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 40) return "bg-green-500";
    if (score < 70) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 items-center justify-center p-0 md:p-4 font-sans">
      <div className="w-full max-w-3xl flex flex-col h-full bg-white md:rounded-2xl shadow-2xl overflow-hidden border border-gray-200">
        
        {/* Header */}
        <header className="bg-emerald-700 text-white p-4 flex items-center shadow-md z-10 shrink-0">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-emerald-700 font-bold text-xl mr-3 shadow-sm border-2 border-emerald-500">
            <Tractor size={24} />
          </div>
          <div className="flex flex-col">
            <h1 className="text-xl font-bold leading-tight">Kisan Saathi</h1>
            <span className="text-emerald-100 text-xs flex items-center">
              <span className="w-2 h-2 rounded-full bg-green-400 mr-1 animate-pulse"></span>
              AI Agronomist Online
            </span>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto p-4 chat-bg flex flex-col gap-4">
          <div className="text-center my-2 text-xs text-gray-500 bg-white/60 mx-auto px-3 py-1 rounded-full shadow-sm">
            End-to-End Encrypted Intelligence
          </div>

          {messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col max-w-[85%] sm:max-w-[75%] ${msg.sender === "user" ? "self-end" : "self-start"}`}>
              <div 
                className={`p-3 rounded-2xl shadow-md relative ${
                  msg.sender === "user" ? "bubble-user" : "bubble-ai"
                }`}
              >
                {/* Structured AI Reply */}
                {msg.sender === "ai" && msg.data && (msg.data.weather_summary || msg.data.decisions) && (
                  <div className="mb-3 flex flex-col gap-3 bg-gray-50/50 p-3 rounded-xl border border-gray-100">
                    
                    {/* Location & Weather */}
                    {msg.data.location && (
                      <div className="flex flex-col border-b border-gray-200 pb-2">
                        <div className="flex items-center text-emerald-700 font-semibold text-sm mb-1">
                          <MapPin size={14} className="mr-1" />
                          {msg.data.location}
                        </div>
                        {msg.data.weather_summary && (
                          <div className="flex items-center text-gray-700 text-sm">
                            <ThermometerSun size={14} className="mr-1 text-orange-500" />
                            {msg.data.weather_summary}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Risk Scores */}
                    {msg.data.risk_scores && (
                      <div className="flex flex-col gap-1.5 border-b border-gray-200 pb-2">
                        <div className="flex items-center text-red-600 font-semibold text-sm">
                          <Activity size={14} className="mr-1" /> Risk Intelligence
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                          <div className="bg-white p-2 rounded-lg border border-gray-100 shadow-sm flex flex-col items-center">
                            <Leaf size={14} className="text-gray-500 mb-1" />
                            <span className="text-xs text-center text-gray-500 mb-1">Disease Risk</span>
                            <div className="w-full bg-gray-200 rounded-full h-1.5 mb-1">
                              <div className={`h-1.5 rounded-full ${getRiskColor(msg.data.risk_scores.disease_risk)}`} style={{ width: `${msg.data.risk_scores.disease_risk}%` }}></div>
                            </div>
                            <span className="text-xs font-bold text-gray-700">{msg.data.risk_scores.disease_risk}/100</span>
                          </div>
                          <div className="bg-white p-2 rounded-lg border border-gray-100 shadow-sm flex flex-col items-center">
                            <Droplet size={14} className="text-gray-500 mb-1" />
                            <span className="text-xs text-center text-gray-500 mb-1">Water Need</span>
                            <div className="w-full bg-gray-200 rounded-full h-1.5 mb-1">
                              <div className={`h-1.5 rounded-full ${getRiskColor(msg.data.risk_scores.irrigation_need)}`} style={{ width: `${msg.data.risk_scores.irrigation_need}%` }}></div>
                            </div>
                            <span className="text-xs font-bold text-gray-700">{msg.data.risk_scores.irrigation_need}/100</span>
                          </div>
                          <div className="bg-white p-2 rounded-lg border border-gray-100 shadow-sm flex flex-col items-center">
                            <AlertTriangle size={14} className="text-gray-500 mb-1" />
                            <span className="text-xs text-center text-gray-500 mb-1">Spray Eff.</span>
                            <div className="w-full bg-gray-200 rounded-full h-1.5 mb-1">
                              <div className={`h-1.5 rounded-full ${msg.data.risk_scores.spray_effectiveness > 50 ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${msg.data.risk_scores.spray_effectiveness}%` }}></div>
                            </div>
                            <span className="text-xs font-bold text-gray-700">{msg.data.risk_scores.spray_effectiveness}/100</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Decisions & Action Plan */}
                    {(msg.data.decisions || msg.data.action_plan) && (
                      <div className="flex flex-col gap-2">
                        {msg.data.decisions && msg.data.decisions.length > 0 && (
                          <div>
                            <div className="flex items-center text-blue-700 font-semibold text-sm mb-1">
                              <Info size={14} className="mr-1" /> AI Decisions
                            </div>
                            <ul className="text-sm text-gray-700 pl-5 list-disc space-y-0.5">
                              {msg.data.decisions.map((d, i) => <li key={i}>{d}</li>)}
                            </ul>
                          </div>
                        )}
                        {msg.data.action_plan && msg.data.action_plan.length > 0 && (
                          <div className="mt-1">
                            <div className="flex items-center text-emerald-700 font-semibold text-sm mb-1">
                              <CheckCircle size={14} className="mr-1" /> Action Plan
                            </div>
                            <ul className="text-sm text-gray-700 pl-5 list-decimal space-y-0.5">
                              {msg.data.action_plan.map((a, i) => <li key={i}>{a}</li>)}
                            </ul>
                          </div>
                        )}
                        {msg.data.reason && (
                           <div className="mt-2 text-xs text-gray-500 italic border-t border-gray-200 pt-2">
                             <strong>Reason:</strong> {msg.data.reason}
                           </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Text Message Content */}
                {!isJsonString(msg.text) && (
                  <div className="text-sm whitespace-pre-wrap leading-relaxed pb-3">
                    {msg.text.split('\n').map((line, i) => (
                      <span key={i}>
                        {line}
                        {i !== msg.text.split('\n').length - 1 && <br />}
                      </span>
                    ))}
                  </div>
                )}
                
                <div className="text-[10px] text-gray-400 absolute bottom-1 right-2">
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex flex-col self-start max-w-[75%]">
              <div className="p-3 rounded-2xl bubble-ai shadow-md flex items-center gap-1.5 text-sm text-gray-500">
                <Leaf size={14} className="text-emerald-500 animate-pulse" />
                <span>Kisan Saathi is thinking</span>
                <span className="flex">
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mx-[1px] typing-dot"></span>
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mx-[1px] typing-dot"></span>
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mx-[1px] typing-dot"></span>
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Input Area */}
        <footer className="bg-gray-50 p-3 flex gap-2 border-t border-gray-200 shrink-0 shadow-[0_-2px_10px_rgba(0,0,0,0.02)] sm:p-4">
          <div className="flex-1 rounded-full bg-white flex items-center shadow-sm border border-gray-300 overflow-hidden pr-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message..." 
              className="flex-1 bg-transparent border-none outline-none py-3 px-4 text-sm text-gray-800"
              disabled={isLoading}
            />
          </div>
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="w-12 h-12 rounded-full bg-emerald-600 text-white flex justify-center items-center shadow-md hover:bg-emerald-700 hover:shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} className="ml-1" />
          </button>
        </footer>
      </div>
    </div>
  );
}
