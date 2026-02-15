"use client";

import { Bell, Search } from "lucide-react";
import { useState } from "react";

export default function TopBar() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="h-16 bg-secondary border-b border-white/5 px-6 flex items-center justify-between">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search documents, queries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm
                       text-white placeholder-slate-500
                       focus:border-accent focus:ring-1 focus:ring-accent
                       transition-all duration-200 outline-none"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-white/5 transition-colors">
          <Bell className="w-5 h-5 text-slate-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent rounded-full" />
        </button>

        {/* User Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent to-accent-light flex items-center justify-center cursor-pointer">
          <span className="text-white text-sm font-semibold">U</span>
        </div>
      </div>
    </header>
  );
}
