"use client";

import { useState } from "react";

interface PipelineStep {
  step: string;
  label: string;
  duration_ms: number;
  details?: Record<string, unknown>;
}

interface ThoughtProcessProps {
  steps: PipelineStep[];
}

const STEP_ICONS: Record<string, string> = {
  embedding: "🔤",
  retrieval: "🔍",
  reranking: "🎯",
  generation: "✨",
};

const STEP_COLORS: Record<string, string> = {
  embedding: "from-blue-500/20 to-blue-600/10 border-blue-500/30",
  retrieval: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30",
  reranking: "from-amber-500/20 to-amber-600/10 border-amber-500/30",
  generation: "from-violet-500/20 to-violet-600/10 border-violet-500/30",
};

const STEP_TEXT_COLORS: Record<string, string> = {
  embedding: "text-blue-400",
  retrieval: "text-emerald-400",
  reranking: "text-amber-400",
  generation: "text-violet-400",
};

export default function ThoughtProcess({ steps }: ThoughtProcessProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!steps || steps.length === 0) return null;

  const totalTime = steps.reduce((sum, s) => sum + s.duration_ms, 0);

  return (
    <div className="mt-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-xs text-slate-400 hover:text-slate-200 transition-colors group"
      >
        <span className="text-sm">🧠</span>
        <span className="group-hover:underline">Thought Process</span>
        <span className="text-slate-600">({totalTime.toFixed(0)}ms total)</span>
        <span
          className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
        >
          ▾
        </span>
      </button>

      {isOpen && (
        <div className="mt-2 space-y-1.5 animate-fadeIn">
          {steps.map((step, idx) => {
            const icon = STEP_ICONS[step.step] || "⚙️";
            const bgColor =
              STEP_COLORS[step.step] ||
              "from-slate-500/20 to-slate-600/10 border-slate-500/30";
            const textColor = STEP_TEXT_COLORS[step.step] || "text-slate-400";

            // Calculate width as percentage of total time (min 15% for visibility)
            const widthPct = Math.max(15, (step.duration_ms / totalTime) * 100);

            return (
              <div key={idx} className="flex items-center gap-2">
                {/* Timeline connector */}
                <div className="flex flex-col items-center w-5">
                  <span className="text-xs">{icon}</span>
                  {idx < steps.length - 1 && (
                    <div className="w-px h-3 bg-white/10 mt-0.5" />
                  )}
                </div>

                {/* Step bar */}
                <div
                  className={`flex items-center justify-between px-2.5 py-1 rounded-md border bg-gradient-to-r ${bgColor}`}
                  style={{ width: `${widthPct}%`, minWidth: "140px" }}
                >
                  <span className={`text-xs font-medium ${textColor}`}>
                    {step.label}
                  </span>
                  <span className="text-[10px] text-slate-500 ml-2 whitespace-nowrap">
                    {step.duration_ms.toFixed(0)}ms
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
