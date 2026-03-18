"use client";

import { AlertCircle, Cloud, AlertTriangle, Droplet } from "lucide-react";

interface AlertProps {
  type: "warning" | "danger" | "info" | "success";
  title: string;
  message: string;
}

export function Alert({ type, title, message }: AlertProps) {
  const styles = {
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    danger: "bg-red-50 border-red-200 text-red-800",
    info: "bg-blue-50 border-blue-200 text-blue-800",
    success: "bg-green-50 border-green-200 text-green-800",
  };

  const icons = {
    warning: <AlertTriangle className="h-5 w-5 text-yellow-600" />,
    danger: <AlertCircle className="h-5 w-5 text-red-600" />,
    info: <Cloud className="h-5 w-5 text-blue-600" />,
    success: <Droplet className="h-5 w-5 text-green-600" />,
  };

  return (
    <div className={`border rounded-lg p-4 ${styles[type]}`}>
      <div className="flex gap-3">
        {icons[type]}
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p className="text-sm mt-1">{message}</p>
        </div>
      </div>
    </div>
  );
}

interface CardProps {
  title?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, icon, children, className = "" }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border border-gray-100 ${className}`}>
      {(title || icon) && (
        <div className="flex items-center gap-2 mb-4">
          {icon}
          {title && <h3 className="text-lg font-semibold text-gray-800">{title}</h3>}
        </div>
      )}
      {children}
    </div>
  );
}

interface StatProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  color?: "green" | "blue" | "yellow" | "red";
}

export function StatCard({ label, value, unit, icon, color = "green" }: StatProps) {
  const colorClasses: Record<"green" | "blue" | "yellow" | "red", string> = {
    green: "bg-green-100 text-green-700",
    blue: "bg-blue-100 text-blue-700",
    yellow: "bg-yellow-100 text-yellow-700",
    red: "bg-red-100 text-red-700",
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 border border-gray-100">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-600 text-sm font-medium">{label}</p>
          <p className="text-2xl font-bold text-gray-800 mt-2">
            {value} {unit && <span className="text-lg">{unit}</span>}
          </p>
        </div>
        {icon && (
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
