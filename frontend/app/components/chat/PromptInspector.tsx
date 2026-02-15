"use client";

import { Check, ChevronDown, ChevronRight, Copy, Terminal } from "lucide-react";
import { useState } from "react";

interface PromptInspectorProps {
  debugInfo: {
    final_prompt?: { role: string; content: string }[];
    system_prompt?: string;
    user_query?: string;
    context_used?: string;
  };
}

export default function PromptInspector({ debugInfo }: PromptInspectorProps) {
  // Always default to open when used in SystemTransparency
  const [isOpen, setIsOpen] = useState(true);
  const [viewMode, setViewMode] = useState<"parsed" | "json">("parsed");
  const [activeTab, setActiveTab] = useState<
    "system" | "context" | "conversation"
  >("system");
  const [copied, setCopied] = useState(false);

  if (!debugInfo) return null;

  const handleCopy = () => {
    const textToCopy =
      viewMode === "json"
        ? JSON.stringify(debugInfo.final_prompt, null, 2)
        : `SYSTEM PROMPT:\n${debugInfo.system_prompt}\n\nUSER QUERY:\n${debugInfo.user_query}\n\nCONTEXT:\n${debugInfo.context_used}`;

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-2 border border-slate-700/50 rounded-lg overflow-hidden bg-[#0d1117]">
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 bg-slate-800/50 hover:bg-slate-800/80 transition-colors"
      >
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <Terminal size={14} className="text-accent" />
          <span>PROMPT INSPECTOR</span>
        </div>
        {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>

      {/* Content */}
      {isOpen && (
        <div className="p-0">
          {/* Toolbar */}
          <div className="flex items-center justify-between px-3 py-2 border-b border-slate-700/50 bg-slate-900/50">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode("parsed")}
                className={`text-xs px-2 py-1 rounded transition-colors ${
                  viewMode === "parsed"
                    ? "bg-accent/20 text-accent"
                    : "text-slate-500 hover:text-slate-300"
                }`}
              >
                Parsed View
              </button>
              <button
                onClick={() => setViewMode("json")}
                className={`text-xs px-2 py-1 rounded transition-colors ${
                  viewMode === "json"
                    ? "bg-accent/20 text-accent"
                    : "text-slate-500 hover:text-slate-300"
                }`}
              >
                Raw JSON
              </button>
            </div>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-white transition-colors"
            >
              {copied ? (
                <Check size={12} className="text-green-400" />
              ) : (
                <Copy size={12} />
              )}
              <span>{copied ? "Copied!" : "Copy"}</span>
            </button>
          </div>

          {/* Body */}
          <div className="p-4 overflow-x-auto">
            {viewMode === "json" ? (
              <pre className="text-[10px] sm:text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
                {JSON.stringify(debugInfo.final_prompt, null, 2)}
              </pre>
            ) : (
              <div className="space-y-4">
                {/* Tabs for Parsed View */}
                <div className="flex border-b border-slate-700/50 mb-3">
                  {[
                    { id: "system", label: "System Prompt" },
                    { id: "context", label: "Injected Context" },
                    { id: "conversation", label: "Full Conversation" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() =>
                        setActiveTab(
                          tab.id as "system" | "context" | "conversation",
                        )
                      }
                      className={`text-xs px-3 py-1.5 border-b-2 transition-colors -mb-[1px] ${
                        activeTab === tab.id
                          ? "border-accent text-accent"
                          : "border-transparent text-slate-500 hover:text-slate-300"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <div className="font-mono text-xs leading-relaxed max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
                  {activeTab === "system" && (
                    <div className="text-[#a5d6ff]">
                      <div className="text-slate-500 mb-2">
                        {'// The "Persona" and instructions given to the AI'}
                      </div>
                      {debugInfo.system_prompt || "No system prompt found."}
                    </div>
                  )}

                  {activeTab === "context" && (
                    <div className="text-[#7ee787]">
                      <div className="text-slate-500 mb-2">
                        {"// The RAG chunks injected into the prompt"}
                      </div>
                      {debugInfo.context_used ||
                        "No context was injected for this query."}
                    </div>
                  )}

                  {activeTab === "conversation" && (
                    <div className="space-y-3">
                      <div className="text-slate-500">
                        {"// The full message history sent to the API"}
                      </div>
                      {debugInfo.final_prompt?.map((msg, idx) => {
                        let roleColor = "text-green-400";
                        if (msg.role === "system")
                          roleColor = "text-purple-400";
                        else if (msg.role === "user")
                          roleColor = "text-blue-400";

                        return (
                          <div
                            key={`${msg.role}-${idx}`}
                            className="border-l-2 border-slate-700 pl-3"
                          >
                            <span
                              className={`text-[10px] uppercase font-bold mb-1 block ${roleColor}`}
                            >
                              {msg.role}
                            </span>
                            <div className="text-slate-300 whitespace-pre-wrap">
                              {msg.content}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
