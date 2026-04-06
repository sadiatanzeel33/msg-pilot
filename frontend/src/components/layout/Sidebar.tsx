"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Send, Users, FileSpreadsheet, Settings, MessageSquare, LogOut, Activity,
} from "lucide-react";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/campaigns", label: "Campaigns", icon: Send },
  { href: "/contacts", label: "Contacts", icon: Users },
  { href: "/contacts?tab=upload", label: "Upload Excel", icon: FileSpreadsheet },
  { href: "/settings", label: "WhatsApp Session", icon: MessageSquare },
  { href: "/dashboard?tab=logs", label: "Activity Logs", icon: Activity },
];

export default function Sidebar({ onLogout }: { onLogout: () => void }) {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      {/* Brand */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-brand-600 flex items-center gap-2">
          <Send className="w-7 h-7" /> Msg-Pilot
        </h1>
        <p className="text-xs text-gray-400 mt-1">WhatsApp Automation</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {links.map((l) => {
          const active = pathname === l.href || (pathname === "/" && l.href === "/dashboard");
          return (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active ? "bg-brand-50 text-brand-700" : "text-gray-600 hover:bg-gray-100",
              )}
            >
              <l.icon className="w-5 h-5" />
              {l.label}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-200">
        <button onClick={onLogout} className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 w-full transition-colors">
          <LogOut className="w-5 h-5" /> Logout
        </button>
      </div>
    </aside>
  );
}
