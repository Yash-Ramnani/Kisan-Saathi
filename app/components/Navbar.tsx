"use client";

import { useState } from "react";
import { Tractor, Cloud, Leaf, BarChart3, Menu, Home, Landmark, LayoutDashboard, Sprout, Bug } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Home", icon: Home, exact: true },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/soil", label: "Soil", icon: Leaf },
  { href: "/weather", label: "Weather", icon: Cloud },
  { href: "/crops", label: "Crops", icon: Sprout },
  { href: "/disease", label: "Disease", icon: Bug },
  { href: "/market", label: "Market", icon: BarChart3 },
  { href: "/schemes", label: "Schemes", icon: Landmark },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (href: string, exact = false) => {
    if (exact) return pathname === href;
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-emerald-800 bg-gradient-to-r from-emerald-700 via-green-700 to-teal-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 rounded-full px-3 py-1.5 font-bold text-xl transition hover:bg-white/10">
            <Tractor className="h-6 w-6" />
            <span>Kisan Saathi</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-1 rounded-full border border-white/20 bg-white/5 p-2 px-10  backdrop-blur-sm">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href, item.exact);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-medium transition ${
                    active
                      ? "bg-white text-emerald-800 shadow-md"
                      : "text-emerald-50 hover:bg-white/15 hover:text-white"
                  }`}
                >
                  {Icon && <Icon className="h-4 w-4" />}
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Hamburger Menu */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden rounded-lg p-2 transition hover:bg-white/15"
            aria-label="Toggle navigation menu"
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4">
            <div className="space-y-2 rounded-2xl border border-white/20 bg-white/10 p-3 backdrop-blur-sm">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href, item.exact);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition ${
                      active
                        ? "bg-white text-emerald-800"
                        : "text-emerald-50 hover:bg-white/15 hover:text-white"
                    }`}
                  >
                    {Icon && <Icon className="h-4 w-4" />}
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
