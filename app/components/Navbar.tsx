"use client";

import { useState } from "react";
import { Tractor, Cloud, Leaf, BarChart3, MessageSquare, Menu, Home, LogOut } from "lucide-react";
import Link from "next/link";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-green-700 text-white sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <Tractor className="h-6 w-6" />
            <span>Kisan Saathi</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex gap-8 items-center">
            <Link href="/" className="hover:text-green-100 transition flex items-center gap-1">
              <Home className="h-4 w-4" /> Home
            </Link>
            <Link href="/dashboard" className="hover:text-green-100 transition">
              Dashboard
            </Link>
            <Link href="/soil" className="hover:text-green-100 transition flex items-center gap-1">
              <Leaf className="h-4 w-4" /> Soil
            </Link>
            <Link href="/weather" className="hover:text-green-100 transition flex items-center gap-1">
              <Cloud className="h-4 w-4" /> Weather
            </Link>
            <Link href="/crops" className="hover:text-green-100 transition">
              Crops
            </Link>
            <Link href="/disease" className="hover:text-green-100 transition">
              Disease
            </Link>
            <Link href="/market" className="hover:text-green-100 transition flex items-center gap-1">
              <BarChart3 className="h-4 w-4" /> Market
            </Link>
          </div>

          {/* Hamburger Menu */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 hover:bg-green-600 rounded"
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link href="/" className="block px-4 py-2 hover:bg-green-600 rounded">
              Home
            </Link>
            <Link href="/dashboard" className="block px-4 py-2 hover:bg-green-600 rounded">
              Dashboard
            </Link>
            <Link href="/soil" className="block px-4 py-2 hover:bg-green-600 rounded">
              Soil Analysis
            </Link>
            <Link href="/weather" className="block px-4 py-2 hover:bg-green-600 rounded">
              Weather
            </Link>
            <Link href="/crops" className="block px-4 py-2 hover:bg-green-600 rounded">
              Crop Advisory
            </Link>
            <Link href="/disease" className="block px-4 py-2 hover:bg-green-600 rounded">
              Disease Detection
            </Link>
            <Link href="/market" className="block px-4 py-2 hover:bg-green-600 rounded">
              Market Prices
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
