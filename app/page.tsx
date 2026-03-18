"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import {
  Send, Leaf, Droplets, Wind, MapPin, Activity,
  CheckCircle, Info, ChevronRight, Sprout,
  TrendingUp, Menu, Shield, Calendar,
  Flame, Snowflake, RefreshCw, Wheat,
} from "lucide-react";

// ─── Types ─────────────────────────────────────────────────────────

type RiskScores = {
  disease_risk: number;
  irrigation_need: number;
  spray_effectiveness: number;
  heat_stress: number;
  frost_risk: number;
  overall_alert: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
};
type ForecastDay = {
  date: string; max_temp: number; min_temp: number; rainfall: number;
  humidity: number; condition: string; uv_index: number; chance_of_rain: number;
};
type MessageData = {
  location?: string; weather_summary?: string; forecast?: ForecastDay[];
  risk_scores?: RiskScores; decisions?: string[]; action_plan?: string[];
  reason?: string; detected_crop?: string; season?: string;
};
type Message = { id: string; sender: "user" | "ai"; text: string; data?: MessageData; timestamp: string; };
type Tab = "chat" | "mandi" | "calendar" | "schemes";

// ─── Theme Tokens ───────────────────────────────────────────────────

const T = {
  bg:        "#f4f8f4",
  surface:   "#ffffff",
  sidebar:   "#f8fdf8",
  border:    "rgba(22,163,74,0.15)",
  borderMd:  "rgba(22,163,74,0.28)",
  green600:  "#16a34a",
  green700:  "#15803d",
  green800:  "#166534",
  green50:   "#f0fdf4",
  green100:  "#dcfce7",
  gold:      "#d97706",
  text:      "#14301a",
  textSec:   "#3d6b45",
  textMuted: "#6b8f73",
  shadow:    "0 2px 12px rgba(0,0,0,0.06)",
  shadowMd:  "0 4px 24px rgba(0,0,0,0.09)",
};

// ─── Static Data ────────────────────────────────────────────────────

const ALERT_CONFIG = {
  LOW:      { color: "#166534", bg: "#f0fdf4", border: "rgba(22,163,74,0.25)", icon: "🟢" },
  MEDIUM:   { color: "#92400e", bg: "#fffbeb", border: "rgba(251,191,36,0.4)",  icon: "🟡" },
  HIGH:     { color: "#9a3412", bg: "#fff7ed", border: "rgba(251,146,60,0.4)",  icon: "🟠" },
  CRITICAL: { color: "#991b1b", bg: "#fef2f2", border: "rgba(248,113,113,0.5)", icon: "🔴" },
};

const riskColor = (s: number) =>
  s >= 75 ? "#ef4444" : s >= 50 ? "#f97316" : s >= 30 ? "#eab308" : "#22c55e";

const CHIPS = [
  "Cotton advisory Rajkot",
  "Wheat weather Surat",
  "Cotton mandi price",
  "PM KISAN scheme",
  "Rice fertilizer NPK",
  "Cotton bollworm spray",
];

const MANDI = [
  { name: "Cotton",    gu: "કપàsAAAS",  min: 6201, max: 7344, msp: 7121, up: false, icon: "🌿" },
  { name: "Wheat",     gu: "ઘàÂUn",     min: 2115, max: 2420, msp: 2275, up: true,  icon: "🌾" },
  { name: "Rice",      gu: "ÃGR",        min: 2183, max: 2600, msp: 2300, up: true,  icon: "🌾" },
  { name: "Groundnut", gu: "Mgfal",      min: 5550, max: 6500, msp: 6783, up: false, icon: "🥜" },
  { name: "Soybean",   gu: "Soyb",       min: 3950, max: 4600, msp: 4892, up: true,  icon: "🫘" },
  { name: "Onion",     gu: "DungLi",     min: 400,  max: 2800, msp: null, up: true,  icon: "🧅" },
  { name: "Tomato",    gu: "TamETA",     min: 300,  max: 4000, msp: null, up: false, icon: "🍅" },
  { name: "Mustard",   gu: "SarSv",      min: 5200, max: 6000, msp: 5950, up: true,  icon: "🌻" },
];

const CALENDAR_DATA = [
  { crop: "Cotton",  stage: "Boll Development",  months: "Sep–Oct", color: "#16a34a", advice: "Reduce irrigation. Monitor bollworm. Spray ethephon for early boll opening." },
  { crop: "Wheat",   stage: "Pre-Sowing Prep",   months: "Oct–Nov", color: "#d97706", advice: "Deep ploughing, apply FYM 10 t/ha, procure certified seed." },
  { crop: "Rice",    stage: "Harvest Ready",      months: "Oct–Nov", color: "#0891b2", advice: "Drain field 10 days before harvest. Check grain moisture < 20%." },
  { crop: "Potato",  stage: "Sowing Window",      months: "Oct–Nov", color: "#7c3aed", advice: "Prepare ridges, apply basal NPK, treat seed-tubers with fungicide." },
  { crop: "Mustard", stage: "Sowing Window",      months: "Oct–Nov", color: "#b45309", advice: "Sow at 5 cm depth, 30 cm row spacing, treat seed with fungicide." },
];

const SCHEMES = [
  { icon: "💰", title: "PM KISAN",           benefit: "₹6,000/year",  desc: "Direct bank transfer in 3 installments",         tag: "Active",      tagColor: "#166534", tagBg: "#dcfce7" },
  { icon: "🛡️", title: "PM Fasal Bima",      benefit: "2% Premium",   desc: "Full crop loss coverage by government subsidy",   tag: "Kharif open", tagColor: "#1e40af", tagBg: "#dbeafe" },
  { icon: "💳", title: "Kisan Credit Card",  benefit: "4% Interest",  desc: "Up to ₹3 lakh flexible crop loan from any bank",  tag: "Always open", tagColor: "#166534", tagBg: "#dcfce7" },
  { icon: "🧪", title: "Soil Health Card",   benefit: "Free",         desc: "Free soil NPK + micronutrient test every 2 years", tag: "Always open", tagColor: "#166534", tagBg: "#dcfce7" },
  { icon: "☀️", title: "PM KUSUM Solar",     benefit: "90% Subsidy",  desc: "Solar irrigation pump at only 10% of cost",       tag: "Limited",     tagColor: "#92400e", tagBg: "#fef3c7" },
  { icon: "🏛️", title: "Gujarat CM Sahay",   benefit: "₹25,000/ha",  desc: "Mukhyamantri Kisan Sahay — no premium needed",    tag: "Gujarat",     tagColor: "#6d28d9", tagBg: "#ede9fe" },
];

// ─── Sub-components ─────────────────────────────────────────────────

function RiskBar({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span style={{ fontSize: 11, color: T.textMuted, display: "flex", alignItems: "center", gap: 4 }}>{icon} {label}</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: riskColor(value) }}>{value}/100</span>
      </div>
      <div style={{ height: 5, borderRadius: 99, background: "rgba(0,0,0,0.08)", overflow: "hidden" }}>
        <div className="risk-bar-fill" style={{ height: "100%", width: `${value}%`, background: riskColor(value) }} />
      </div>
    </div>
  );
}

function WeatherBadge({ data }: { data: MessageData }) {
  if (!data.weather_summary) return null;
  const parts = data.weather_summary.split("|").map(p => p.trim()).filter(Boolean);
  return (
    <div style={{ background: T.green50, border: `1px solid ${T.border}`, borderRadius: 10, padding: 10, marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: T.green700, display: "flex", alignItems: "center", gap: 4 }}>
          <MapPin size={11} /> {data.location}
        </span>
        {data.season && <span style={{ fontSize: 10, color: T.gold, background: "#fffbeb", padding: "2px 8px", borderRadius: 99, border: "1px solid #fde68a" }}>{data.season}</span>}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2px 12px" }}>
        {parts.map((p, i) => <div key={i} style={{ fontSize: 11, color: T.textSec }}>{p}</div>)}
      </div>
    </div>
  );
}

function ForecastStrip({ forecast }: { forecast: ForecastDay[] }) {
  return (
    <div style={{ marginTop: 10 }}>
      <p style={{ fontSize: 10, color: T.textMuted, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>5-Day Forecast</p>
      <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 2 }}>
        {forecast.slice(0, 5).map((day, i) => (
          <div key={i} className="forecast-card" style={{ padding: "8px 10px", minWidth: 58, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", background: "#fff" }}>
            <span style={{ fontSize: 10, color: T.textMuted }}>{day.date.slice(5)}</span>
            <span style={{ fontSize: 16, margin: "3px 0" }}>{day.chance_of_rain > 50 ? "🌧️" : day.chance_of_rain > 20 ? "⛅" : "☀️"}</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: T.text }}>{day.max_temp}°</span>
            <span style={{ fontSize: 10, color: T.textMuted }}>{day.min_temp}°</span>
            <span style={{ fontSize: 10, color: "#2563eb" }}>{day.chance_of_rain}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RiskPanel({ risks }: { risks: RiskScores }) {
  const cfg = ALERT_CONFIG[risks.overall_alert] || ALERT_CONFIG.LOW;
  return (
    <div style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, borderRadius: 10, padding: 12, marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: cfg.color, display: "flex", alignItems: "center", gap: 4 }}>
          <Activity size={12} /> Risk Intelligence
        </span>
        <span className={risks.overall_alert === "CRITICAL" ? "alert-critical" : ""} style={{ fontSize: 11, fontWeight: 700, padding: "2px 10px", borderRadius: 99, background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }}>
          {cfg.icon} {risks.overall_alert}
        </span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <RiskBar label="Disease Risk"       value={risks.disease_risk}        icon={<Leaf size={10}/>} />
        <RiskBar label="Irrigation Need"    value={risks.irrigation_need}     icon={<Droplets size={10}/>} />
        <RiskBar label="Spray Effective."   value={risks.spray_effectiveness} icon={<Wind size={10}/>} />
        <RiskBar label="Heat Stress"        value={risks.heat_stress}         icon={<Flame size={10}/>} />
        <RiskBar label="Frost Risk"         value={risks.frost_risk}          icon={<Snowflake size={10}/>} />
      </div>
    </div>
  );
}

function AIMessage({ msg }: { msg: Message }) {
  const [open, setOpen] = useState(false);
  const parts = msg.text.split("---");
  const gu = parts[0]?.trim();
  const en = parts[1]?.trim();

  return (
    <div className="msg-enter" style={{ alignSelf: "flex-start", maxWidth: "min(88%, 600px)" }}>
      <div className="bubble-ai" style={{ padding: "14px 16px" }}>
        {msg.data?.weather_summary && <WeatherBadge data={msg.data} />}
        {msg.data?.risk_scores && msg.data.risk_scores.overall_alert !== "LOW" && (
          <RiskPanel risks={msg.data.risk_scores} />
        )}
        <div style={{ fontSize: 13, lineHeight: 1.65, color: T.text, marginBottom: 8 }}>
          {gu && (
            <div style={{ borderBottom: `1px solid ${T.border}`, paddingBottom: 8, marginBottom: 8, fontWeight: 500 }}>
              {gu.split("\n").map((l, i) => <span key={i}>{l}<br /></span>)}
            </div>
          )}
          {en && (
            <div style={{ fontSize: 12, color: T.textMuted, lineHeight: 1.6 }}>
              {en.split("\n").map((l, i) => <span key={i}>{l}<br /></span>)}
            </div>
          )}
          {!gu && !en && <span>{msg.text}</span>}
        </div>
        {msg.data?.forecast && msg.data.forecast.length > 0 && <ForecastStrip forecast={msg.data.forecast} />}
        {(msg.data?.decisions?.length || msg.data?.action_plan?.length) && (
          <>
            <button onClick={() => setOpen(!open)} style={{ marginTop: 8, fontSize: 11, color: T.green600, background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 4, padding: 0, fontFamily: "inherit", fontWeight: 500 }}>
              <ChevronRight size={11} style={{ transform: open ? "rotate(90deg)" : "none", transition: "transform 0.2s" }} />
              {open ? "Hide" : "View"} decisions & action plan
            </button>
            {open && (
              <div style={{ marginTop: 10, paddingTop: 10, borderTop: `1px solid ${T.border}` }}>
                {msg.data?.decisions?.map((d, i) => (
                  <div key={i} style={{ fontSize: 12, color: T.text, display: "flex", gap: 6, marginBottom: 5 }}>
                    <span style={{ color: T.green600, flexShrink: 0 }}>•</span><span>{d}</span>
                  </div>
                ))}
                {msg.data?.action_plan?.map((a, i) => (
                  <div key={i} style={{ fontSize: 12, color: T.text, display: "flex", gap: 6, marginBottom: 5 }}>
                    <span style={{ color: T.green700, fontWeight: 700, flexShrink: 0 }}>{i + 1}.</span><span>{a}</span>
                  </div>
                ))}
                {msg.data?.reason && <p style={{ fontSize: 11, color: T.textMuted, fontStyle: "italic", marginTop: 8, paddingTop: 8, borderTop: `1px solid ${T.border}` }}>{msg.data.reason}</p>}
              </div>
            )}
          </>
        )}
        <div style={{ fontSize: 10, color: "#c4cfc5", marginTop: 8, textAlign: "right" }}>{msg.timestamp}</div>
      </div>
    </div>
  );
}

// ─── Main Page ──────────────────────────────────────────────────────

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([{
    id: "w", sender: "ai",
    text: "🌾 Namaste! I'm Kisan Saathi, your AI Agronomist.\n\nAsk me about *crops, weather, irrigation, pests* or *mandi prices* — in Gujarati, Hindi or English!\n\nNamaste! Hu tamne kheti, havaman, paani ane bazar viTe madad karish. 🙏",
    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState("");
  const [crops, setCrops] = useState<string[]>([]);
  const [tab, setTab] = useState<Tab>("chat");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const sendMessage = useCallback(async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    setMessages(p => [...p, { id: Date.now().toString(), sender: "user", text: msg, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, current_location: location || undefined, known_crops: crops.length ? crops : undefined }),
      });
      const d = await res.json();
      setMessages(p => [...p, {
        id: (Date.now() + 1).toString(), sender: "ai", text: d.reply,
        data: { location: d.location, weather_summary: d.weather_summary, forecast: d.forecast, risk_scores: d.risk_scores, decisions: d.decisions, action_plan: d.action_plan, reason: d.reason, detected_crop: d.detected_crop, season: d.season },
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }]);
      if (d.location && d.location !== "unknown") setLocation(d.location);
      if (d.detected_crop && d.detected_crop !== "unknown") setCrops(p => p.includes(d.detected_crop) ? p : [...p, d.detected_crop]);
    } catch {
      setMessages(p => [...p, { id: (Date.now()+1).toString(), sender: "ai",
        text: "⚠️ Could not connect to server. Please make sure the backend is running on port 8000.", timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
    } finally { setLoading(false); inputRef.current?.focus(); }
  }, [input, loading, location, crops]);

  const detectLocation = () => navigator.geolocation?.getCurrentPosition(async pos => {
    try {
      const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&format=json`);
      const d = await r.json();
      const city = d.address.city || d.address.state_district || d.address.state || "";
      if (city) { setLocation(city); setMessages(p => [...p, { id: Date.now().toString(), sender: "ai", text: `📍 Location saved: *${city}* ✅\nAll weather & advice will now be for ${city}!`, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]); }
    } catch { /* ignore */ }
  });

  const TABS = [
    { id: "chat"    , icon: <Leaf size={14}/>,        label: "AI Chat" },
    { id: "mandi"   , icon: <TrendingUp size={14}/>,   label: "Mandi Prices" },
    { id: "calendar", icon: <Calendar size={14}/>,     label: "Crop Calendar" },
    { id: "schemes" , icon: <Shield size={14}/>,       label: "Govt Schemes" },
  ] as const;

  // shared header style
  const H2 = { fontSize: 15, fontWeight: 700, color: T.text, margin: 0 };
  const Subtext = { fontSize: 11, color: T.textMuted, margin: 0, marginTop: 1 };

  return (
    <div className="app-bg" style={{ display: "flex", height: "100vh", overflow: "hidden" }}>

      {/* ── Sidebar ─────────────────────────────── */}
      <aside className="sidebar" style={{ width: 240, display: "flex", flexDirection: "column", flexShrink: 0 }}>

        {/* Logo */}
        <div style={{ padding: "18px 16px 14px", borderBottom: `1px solid ${T.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 40, height: 40, borderRadius: 11, background: "linear-gradient(135deg,#16a34a,#166534)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 14px rgba(22,163,74,0.3)" }}>
              <Sprout size={20} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 14, color: T.text, letterSpacing: "-0.01em" }}>Kisan Saathi</div>
              <div style={{ fontSize: 10, color: T.green600, fontWeight: 500 }}>AI Agronomist</div>
            </div>
          </div>
        </div>

        {/* Live indicator */}
        <div style={{ padding: "10px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#16a34a", display: "inline-block", boxShadow: "0 0 6px rgba(22,163,74,0.6)" }} />
          <span style={{ fontSize: 11, color: T.green700, fontWeight: 500 }}>AI Engine Online</span>
        </div>

        {/* Profile */}
        <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}` }}>
          <p style={{ fontSize: 9, color: T.textMuted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8, fontWeight: 600 }}>Your Profile</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: T.textSec }}>
              <MapPin size={12} color={T.textMuted} />
              <span style={{ flex: 1 }}>{location || "Location not set"}</span>
              {!location && (
                <button onClick={detectLocation} style={{ fontSize: 10, color: T.green600, background: "none", border: "none", cursor: "pointer", fontFamily: "inherit", fontWeight: 600 }}>
                  Detect
                </button>
              )}
            </div>
            {crops.length > 0 && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: T.textSec }}>
                <Wheat size={12} color={T.textMuted} /> <span>{crops.join(", ")}</span>
              </div>
            )}
          </div>
        </div>

        {/* Stats */}
        <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}` }}>
          {[
            { label: "Messages Sent",   value: messages.filter(m=>m.sender==="user").length },
            { label: "Crops Tracked",   value: crops.length },
          ].map(s => (
            <div key={s.label} className="stat-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 10px", marginBottom: 6, borderRadius: 8, background: T.green50 }}>
              <span style={{ fontSize: 11, color: T.textMuted }}>{s.label}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: T.green700 }}>{s.value}</span>
            </div>
          ))}
        </div>

        {/* Nav */}
        <nav style={{ padding: "12px 10px", flex: 1 }}>
          <p style={{ fontSize: 9, color: T.textMuted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8, padding: "0 4px", fontWeight: 600 }}>Features</p>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} className={`feature-tab ${tab === t.id ? "active" : ""}`}>
              {t.icon} {t.label}
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div style={{ padding: "10px 16px", borderTop: `1px solid ${T.border}`, fontSize: 10, color: "#b0c4b4", textAlign: "center", lineHeight: 1.5 }}>
          Groq LLaMA 3.3 · WeatherAPI.com<br />Made for Indian Farmers 🌾
        </div>
      </aside>

      {/* ── Main Area ────────────────────────────── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>

        {/* Header */}
        <header className="glass" style={{ padding: "12px 20px", display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
          <div style={{ flex: 1 }}>
            <h2 style={H2}>
              {tab === "chat"     && "🌱 AI Crop Advisory"}
              {tab === "mandi"   && "💹 Mandi Prices"}
              {tab === "calendar" && "📅 Crop Calendar"}
              {tab === "schemes"  && "🏛️ Government Schemes"}
            </h2>
            <p style={Subtext}>
              {location ? `📍 ${location}` : "Set your location for hyper-local advice"}
              {crops.length > 0 && ` · 🌾 ${crops.join(", ")}`}
            </p>
          </div>
          {!location && (
            <button onClick={detectLocation} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, background: T.green50, color: T.green700, border: `1.5px solid ${T.border}`, padding: "8px 14px", borderRadius: 9, cursor: "pointer", fontFamily: "inherit", fontWeight: 600, transition: "all 0.18s", boxShadow: "0 1px 4px rgba(0,0,0,0.06)" }}>
              <MapPin size={13} /> Set Location
            </button>
          )}
        </header>

        {/* ── CHAT TAB ── */}
        {tab === "chat" && (
          <>
            <main className="chat-area scroll-area" style={{ flex: 1, padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
              {messages.map(msg => (
                <div key={msg.id} style={{ display: "flex", justifyContent: msg.sender === "user" ? "flex-end" : "flex-start" }}>
                  {msg.sender === "user" ? (
                    <div className="msg-enter bubble-user" style={{ maxWidth: "80%", padding: "10px 14px" }}>
                      <p style={{ fontSize: 13, margin: 0, lineHeight: 1.5 }}>{msg.text}</p>
                      <p style={{ fontSize: 10, color: "rgba(255,255,255,0.55)", margin: "4px 0 0", textAlign: "right" }}>{msg.timestamp}</p>
                    </div>
                  ) : <AIMessage msg={msg} />}
                </div>
              ))}
              {loading && (
                <div className="msg-enter" style={{ alignSelf: "flex-start" }}>
                  <div className="bubble-ai" style={{ padding: "10px 14px", display: "flex", alignItems: "center", gap: 8 }}>
                    <Leaf size={13} color={T.green600} />
                    <span style={{ fontSize: 12, color: T.textMuted }}>AI is thinking...</span>
                    <span style={{ display: "flex", gap: 3 }}>
                      {[0,1,2].map(i => <span key={i} className="typing-dot" style={{ width: 6, height: 6, borderRadius: "50%", display: "block" }} />)}
                    </span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </main>

            {/* Quick chips */}
            {messages.length < 3 && (
              <div style={{ padding: "8px 16px", display: "flex", gap: 8, overflowX: "auto", borderTop: `1px solid ${T.border}`, background: T.surface, flexShrink: 0 }}>
                {CHIPS.map(c => (
                  <button key={c} onClick={() => sendMessage(c)} className="chip">{c}</button>
                ))}
              </div>
            )}

            {/* Input bar */}
            <footer className="glass" style={{ padding: "12px 16px", borderTop: `1px solid ${T.border}`, flexShrink: 0 }}>
              <div style={{ display: "flex", gap: 10, alignItems: "center", maxWidth: 860, margin: "0 auto" }}>
                <input
                  ref={inputRef} value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), sendMessage())}
                  placeholder="Ask about crops, weather, irrigation… (Gujarati / Hindi / English)"
                  className="chat-input" style={{ flex: 1 }} autoFocus
                />
                <button onClick={() => sendMessage()} disabled={!input.trim() || loading} className="send-btn">
                  {loading ? <RefreshCw size={17} style={{ animation: "spin 1s linear infinite" }} /> : <Send size={17} />}
                </button>
              </div>
              <p style={{ textAlign: "center", fontSize: 10, color: "#c4d0c6", marginTop: 6 }}>Multilingual · Gujarati · Hindi · English</p>
            </footer>
          </>
        )}

        {/* ── MANDI TAB ── */}
        {tab === "mandi" && (
          <div className="scroll-area" style={{ flex: 1, padding: 20 }}>
            <div style={{ maxWidth: 720, margin: "0 auto" }}>
              {/* Data source banner */}
              <div style={{ background: "#fffbeb", border: "1px solid #fde68a", borderRadius: 10, padding: "10px 14px", marginBottom: 16, display: "flex", alignItems: "flex-start", gap: 8 }}>
                <span style={{ fontSize: 16 }}>ℹ️</span>
                <div>
                  <p style={{ fontSize: 12, fontWeight: 600, color: "#92400e", margin: 0 }}>Data Source: CACP MSP + AGMARKNET Regional Estimates</p>
                  <p style={{ fontSize: 11, color: "#b45309", margin: "2px 0 0" }}>
                    Prices based on Government MSP 2025-26 + AGMARKNET market averages with regional adjustments.
                    Add <code style={{ background: "#fef3c7", padding: "0 4px", borderRadius: 3 }}>DATA_GOV_API_KEY</code> in <code style={{ background: "#fef3c7", padding: "0 4px", borderRadius: 3 }}>backend/.env</code> for live AGMARKNET data.
                  </p>
                </div>
              </div>

              <p style={{ fontSize: 12, color: T.textMuted, marginBottom: 14 }}>
                {new Date().toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })} · Tap any crop to get AI market analysis
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                {MANDI.map(c => (
                  <div key={c.name} className="scheme-card" style={{ padding: 14, borderRadius: 14 }}
                    onClick={() => { setTab("chat"); setTimeout(() => sendMessage(`${c.name} mandi price ${location||"Gujarat"}`), 100); }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 14, color: T.text, display: "flex", alignItems: "center", gap: 5 }}>
                          {c.icon} {c.name}
                        </div>
                        <div style={{ fontSize: 10, color: T.textMuted, marginTop: 1 }}>{c.gu}</div>
                      </div>
                      <span style={{ fontSize: 11, fontWeight: 700, color: c.up ? "#16a34a" : "#dc2626", display: "flex", alignItems: "center", gap: 3, background: c.up ? "#f0fdf4" : "#fef2f2", padding: "3px 8px", borderRadius: 99 }}>
                        <TrendingUp size={10} style={{ transform: c.up ? "none" : "scaleY(-1)" }} />
                        {c.up ? "Rising" : "Falling"}
                      </span>
                    </div>
                    <div style={{ display: "flex", gap: 14 }}>
                      {[["Min", c.min, T.text], ["Max", c.max, T.text], ...(c.msp ? [["MSP", c.msp, T.gold]] : [])].map(([l, v, col]) => (
                        <div key={String(l)}>
                          <div style={{ fontSize: 10, color: T.textMuted }}>{l}</div>
                          <div style={{ fontSize: 13, fontWeight: 700, color: String(col) }}>₹{Number(v).toLocaleString()}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ marginTop: 8, fontSize: 10, color: T.textMuted, borderTop: `1px solid ${T.border}`, paddingTop: 6 }}>
                      per quintal · Tap for AI market analysis →
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── CALENDAR TAB ── */}
        {tab === "calendar" && (
          <div className="scroll-area" style={{ flex: 1, padding: 20 }}>
            <div style={{ maxWidth: 720, margin: "0 auto" }}>
              <p style={{ fontSize: 12, color: T.textMuted, marginBottom: 14 }}>Current growth stages & what to do right now — tap for AI advice</p>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {CALENDAR_DATA.map(item => (
                  <div key={item.crop} className="scheme-card" style={{ padding: 16, display: "flex", gap: 14 }}
                    onClick={() => { setTab("chat"); setTimeout(() => sendMessage(`${item.crop} current stage advice`), 100); }}>
                    <div style={{ width: 4, background: item.color, borderRadius: 99, flexShrink: 0, minHeight: 60 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                        <span style={{ fontWeight: 700, fontSize: 15, color: T.text }}>{item.crop}</span>
                        <span style={{ fontSize: 10, background: T.green50, color: T.textSec, padding: "2px 10px", borderRadius: 99, border: `1px solid ${T.border}` }}>{item.months}</span>
                      </div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: item.color, marginBottom: 5 }}>{item.stage}</div>
                      <div style={{ fontSize: 12, color: T.textMuted, lineHeight: 1.6 }}>{item.advice}</div>
                      <div style={{ fontSize: 10, color: T.green600, marginTop: 6, fontWeight: 500 }}>Tap for detailed AI advice →</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── SCHEMES TAB ── */}
        {tab === "schemes" && (
          <div className="scroll-area" style={{ flex: 1, padding: 20 }}>
            <div style={{ maxWidth: 720, margin: "0 auto" }}>
              <p style={{ fontSize: 12, color: T.textMuted, marginBottom: 14 }}>Tap any scheme for eligibility, documents & how to apply</p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                {SCHEMES.map(s => (
                  <div key={s.title} className="scheme-card" style={{ padding: 16 }}
                    onClick={() => { setTab("chat"); setTimeout(() => sendMessage(`tell me about ${s.title} government scheme eligibility and documents`), 100); }}>
                    <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                      <span style={{ fontSize: 26, flexShrink: 0 }}>{s.icon}</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 700, fontSize: 13, color: T.text, marginBottom: 2 }}>{s.title}</div>
                        <div style={{ fontSize: 14, fontWeight: 800, color: T.green600, marginBottom: 5 }}>{s.benefit}</div>
                        <div style={{ fontSize: 11, color: T.textMuted, lineHeight: 1.5, marginBottom: 8 }}>{s.desc}</div>
                        <span style={{ fontSize: 10, fontWeight: 600, background: s.tagBg, color: s.tagColor, border: `1px solid ${s.tagColor}33`, padding: "2px 9px", borderRadius: 99 }}>{s.tag}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
      <style>{`@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}
