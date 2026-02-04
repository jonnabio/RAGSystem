"use client";

import {
  BarChart3,
  FileText,
  HelpCircle,
  LayoutDashboard,
  MessageSquare,
  Settings,
  User,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Documents", href: "/documents", icon: FileText },
  { label: "Chat", href: "/chat", icon: MessageSquare },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings },
  { label: "Help", href: "/help", icon: HelpCircle },
];

export default function Sidebar() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

  return (
    <aside className="w-64 bg-secondary h-screen border-r border-white/5 flex flex-col">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-white/5">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-accent-light flex items-center justify-center">
            <span className="text-white font-bold text-lg">R</span>
          </div>
          <div>
            <span className="text-lg font-bold text-white">RAG</span>
            <span className="text-lg font-bold text-accent"> System</span>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto custom-scrollbar">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg
                transition-all duration-200 group
                ${
                  active
                    ? "bg-gradient-to-r from-accent to-accent-light text-white shadow-lg shadow-accent/20"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }
              `}
            >
              <Icon
                className={`w-5 h-5 ${active ? "text-white" : "text-slate-400 group-hover:text-white"}`}
              />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="px-3 py-4 border-t border-white/5">
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/5 cursor-pointer transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">User</p>
            <p className="text-xs text-slate-400">View profile</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
