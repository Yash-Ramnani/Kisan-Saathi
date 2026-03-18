"use client";

import Link from "next/link";
import {
  CloudSun,
  FlaskConical,
  Leaf,
  Bug,
  LineChart,
  MessageCircle,
  ArrowRight,
  CheckCircle2,
  Bell,
  Wheat,
} from "lucide-react";
import Navbar from "../components/Navbar";

const modules = [
  {
    title: "AI Chat Advisor",
    subtitle: "Ask in English or Gujarati",
    href: "/",
    icon: MessageCircle,
    color: "from-emerald-600 to-green-600",
  },
  {
    title: "Soil Analysis",
    subtitle: "Upload soil photo for full report",
    href: "/soil",
    icon: FlaskConical,
    color: "from-amber-600 to-orange-600",
  },
  {
    title: "Disease Detection",
    subtitle: "Leaf and crop disease diagnosis",
    href: "/disease",
    icon: Bug,
    color: "from-rose-600 to-red-600",
  },
  {
    title: "Weather Insights",
    subtitle: "Actionable weather intelligence",
    href: "/weather",
    icon: CloudSun,
    color: "from-sky-600 to-cyan-600",
  },
  {
    title: "Crop Advisory",
    subtitle: "Season and soil-based crop planning",
    href: "/crops",
    icon: Leaf,
    color: "from-lime-600 to-green-600",
  },
  {
    title: "Market Trends",
    subtitle: "Latest mandi pricing signals",
    href: "/market",
    icon: LineChart,
    color: "from-indigo-600 to-blue-600",
  },
];

const quickStats = [
  { label: "Active Advisory", value: "6 Modules", icon: CheckCircle2 },
  { label: "Field Alerts", value: "Real-time", icon: Bell },
  { label: "Supported Crops", value: "Multi-Crop", icon: Wheat },
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#ecfeff_0%,_#f0fdf4_35%,_#f8fafc_100%)]">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-8 md:py-10">
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-700 via-green-700 to-teal-700 p-6 text-white shadow-2xl md:p-10">
          <div className="absolute -right-12 -top-12 h-48 w-48 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute -bottom-16 -left-16 h-52 w-52 rounded-full bg-cyan-200/20 blur-2xl" />

          <div className="relative">
            <p className="text-sm uppercase tracking-widest text-emerald-100">Kisan Saathi Command Center</p>
            <h1 className="mt-2 text-3xl font-black leading-tight md:text-5xl">
              Smart Farming Dashboard
            </h1>
            <p className="mt-3 max-w-3xl text-sm text-emerald-100 md:text-base">
              Monitor decisions, run analyses, and take action from one place. Open any module below to continue your workflow.
            </p>

            <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
              {quickStats.map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.label} className="rounded-xl border border-white/20 bg-white/10 p-4 backdrop-blur-sm">
                    <div className="flex items-center gap-2 text-emerald-100">
                      <Icon className="h-4 w-4" />
                      <span className="text-xs uppercase tracking-wider">{item.label}</span>
                    </div>
                    <p className="mt-2 text-xl font-bold">{item.value}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link
                key={module.title}
                href={module.href}
                className="group rounded-2xl border border-gray-200 bg-white p-5 shadow-lg transition hover:-translate-y-1 hover:shadow-xl"
              >
                <div className={`inline-flex rounded-xl bg-gradient-to-r ${module.color} p-3 text-white shadow-md`}>
                  <Icon className="h-5 w-5" />
                </div>

                <h2 className="mt-4 text-xl font-bold text-gray-900">{module.title}</h2>
                <p className="mt-1 text-sm text-gray-600">{module.subtitle}</p>

                <div className="mt-4 flex items-center gap-2 text-sm font-semibold text-emerald-700">
                  Open Module
                  <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
                </div>
              </Link>
            );
          })}
        </section>
      </main>
    </div>
  );
}
