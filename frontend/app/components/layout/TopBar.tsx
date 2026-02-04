"use client";

import { Bell, Search } from "lucide-react";
import { useState } from "react";

interface TopBarProps {
  selectedModel?: string;
  onModelChange?: (model: string) => void;
}

const modelOptions = [
  { value: "meta-llama/llama-3-70b-instruct", label: "Llama 3 70B (Free)" },
  { value: "mistralai/mistral-7b-instruct:free", label: "Mistral 7B (Free)" },
  { value: "google/gemma-7b-it:free", label: "Gemma 7B (Free)" },
  {
    value: "microsoft/phi-3-mini-128k-instruct:free",
    label: "Phi-3 Mini (Free)",
  },
  { value: "meta-llama/llama-3-8b-instruct:free", label: "Llama 3 8B (Free)" },
  { value: "openai/gpt-4-turbo", label: "GPT-4 Turbo" },
  { value: "anthropic/claude-3-opus", label: "Claude 3 Opus" },
  { value: "google/gemini-pro", label: "Gemini Pro" },
];

export default function TopBar({ selectedModel, onModelChange }: TopBarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [currentModel, setCurrentModel] = useState(
    selectedModel || "meta-llama/llama-3-70b-instruct",
  );

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newModel = e.target.value;
    setCurrentModel(newModel);
    onModelChange?.(newModel);
  };

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
        {/* Model Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Model:</span>
          <select
            value={currentModel}
            onChange={handleModelChange}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm
                       text-slate-200 outline-none cursor-pointer
                       focus:border-accent transition-all duration-200"
          >
            {modelOptions.map((option) => (
              <option
                key={option.value}
                value={option.value}
                className="bg-secondary text-slate-200"
              >
                {option.label}
              </option>
            ))}
          </select>
        </div>

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
