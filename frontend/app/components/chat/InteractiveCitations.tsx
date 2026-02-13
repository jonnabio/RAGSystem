"use client";

import { useState } from "react";

interface Source {
  rank: number;
  text: string;
  score: number;
  document_id?: string;
  metadata?: Record<string, unknown>;
}

interface InteractiveCitationsProps {
  sources: Source[];
}

function getRelevanceBadge(score: number) {
  // For cross-encoder scores, higher is better (can be negative)
  // Normalize display: > 0 = High, -5 to 0 = Medium, < -5 = Low
  if (score > 0) {
    return {
      label: "High",
      className: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    };
  } else if (score > -5) {
    return {
      label: "Medium",
      className: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    };
  } else {
    return {
      label: "Low",
      className: "bg-red-500/20 text-red-400 border-red-500/30",
    };
  }
}

function getRetrievalBadge(method: string) {
  switch (method) {
    case "vector":
      return {
        label: "Vector",
        className: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      };
    case "keyword":
      return {
        label: "Keyword",
        className: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      };
    case "multi-hop":
      return {
        label: "Multi-Hop",
        className: "bg-pink-500/20 text-pink-400 border-pink-500/30",
      };
    default:
      return {
        label: method,
        className: "bg-slate-500/20 text-slate-400 border-slate-500/30",
      };
  }
}

function getSourceIcon(metadata?: Record<string, unknown>) {
  const source = metadata?.source_type as string | undefined;
  if (source === "pdf" || source === "PDF") return "📄";
  if (source === "docx" || source === "DOCX") return "📝";
  if (source === "code") return "💾";
  // Default: try to guess from document_id
  return "📄";
}

export default function InteractiveCitations({
  sources,
}: InteractiveCitationsProps) {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-white/10">
      <p className="text-accent text-sm font-medium mb-3 flex items-center gap-2">
        <span>📎</span>
        <span>Sources ({sources.length})</span>
      </p>
      <div className="space-y-2">
        {sources.map((source, idx) => {
          const badge = getRelevanceBadge(source.score);
          const icon = getSourceIcon(source.metadata);
          const isExpanded = expandedIdx === idx;

          return (
            <div
              key={source.document_id || `src-${idx}`}
              role="button"
              tabIndex={0}
              className="group rounded-lg border border-white/5 bg-white/[0.02]
                         hover:bg-white/[0.04] hover:border-white/10
                         transition-all duration-200 cursor-pointer overflow-hidden"
              onClick={() => setExpandedIdx(isExpanded ? null : idx)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setExpandedIdx(isExpanded ? null : idx);
                }
              }}
            >
              {/* Header row */}
              <div className="flex items-center gap-2 px-3 py-2">
                {/* Rank badge */}
                <span className="text-xs font-mono text-accent w-5 shrink-0">
                  [{idx + 1}]
                </span>

                {/* Source icon */}
                <span className="text-xs shrink-0">{icon}</span>

                {/* Text preview */}
                <span className="text-xs text-slate-300 flex-1 truncate">
                  {source.text.substring(0, 80)}...
                </span>

                {/* Relevance badge */}
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 ${badge.className}`}
                >
                  {badge.label}
                </span>

                {/* Expand indicator */}
                <span
                  className={`text-slate-500 text-xs transition-transform duration-200 ${
                    isExpanded ? "rotate-180" : ""
                  }`}
                >
                  ▾
                </span>
              </div>

              {/* Expanded content */}
              {isExpanded && (
                <div className="px-3 pb-3 pt-1 border-t border-white/5 animate-fadeIn">
                  <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {source.text}
                  </p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] text-slate-500">
                    <span>Score: {source.score.toFixed(4)}</span>
                    {source.document_id && (
                      <span>Doc: {source.document_id.substring(0, 8)}...</span>
                    )}
                    {/* Retrieval Methods */}
                    {(source.metadata?.retrieval_methods as string[])?.map(
                      (method) => {
                        const badge = getRetrievalBadge(method);
                        return (
                          <span
                            key={method}
                            className={`px-1.5 py-0.5 rounded border ${badge.className}`}
                          >
                            {badge.label}
                          </span>
                        );
                      },
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
