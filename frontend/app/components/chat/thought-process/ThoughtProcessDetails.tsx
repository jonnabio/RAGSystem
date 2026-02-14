interface PipelineStep {
  step: string;
  label: string;
  duration_ms: number;
  details?: Record<string, unknown>;
}

interface ThoughtProcessDetailsProps {
  step: PipelineStep;
}

export default function ThoughtProcessDetails({
  step,
}: ThoughtProcessDetailsProps) {
  if (!step.details) return null;

  // 1. Decomposition Visualization (Routing)
  if (step.step === "routing" && Array.isArray(step.details.sub_queries)) {
    const subQueries = step.details.sub_queries as string[];

    return (
      <div className="flex flex-col gap-3 p-3 bg-black/20 rounded border border-white/5">
        <div className="text-xs text-indigo-400 font-medium mb-1 flex items-center gap-2">
          <span>🔀</span> Query Decomposition
        </div>

        <div className="relative pl-4 border-l border-indigo-500/30 space-y-3">
          {subQueries.map((sq, idx) => (
            <div key={idx} className="relative group">
              {/* Connector dot */}
              <div className="absolute -left-[21px] top-2.5 w-2.5 h-[1px] bg-indigo-500/30"></div>

              <div className="p-2.5 bg-indigo-950/20 border border-indigo-500/20 rounded text-xs text-indigo-200">
                &quot;{sq}&quot;
              </div>
            </div>
          ))}
        </div>
        <div className="text-[10px] text-slate-500 mt-1 italic">
          The system broke the complex user query into simple sub-queries for
          better retrieval.
        </div>
      </div>
    );
  }

  // 2. Retrieval Visualization
  if (
    step.step === "retrieval" &&
    typeof step.details.vector_hits === "number"
  ) {
    const vectorHits = step.details.vector_hits as number;
    const keywordHits = step.details.keyword_hits as number;
    const total = vectorHits + keywordHits;
    const vectorPct = total > 0 ? (vectorHits / total) * 100 : 0;
    const keywordPct = total > 0 ? (keywordHits / total) * 100 : 0;

    return (
      <div className="flex flex-col gap-3 p-3 bg-black/20 rounded border border-white/5">
        <div className="text-xs text-emerald-400 font-medium mb-1 flex items-center gap-2">
          <span>🔬</span> Hybrid Search Results
        </div>

        {/* Bar Chart Duel */}
        <div className="space-y-2">
          {/* Vector Bar */}
          <div>
            <div className="flex justify-between text-[10px] text-cyan-400 mb-1">
              <span>Vector Search (Semantic)</span>
              <span>{vectorHits} chunks</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.6)]"
                style={{ width: `${vectorPct}%` }}
              ></div>
            </div>
          </div>

          {/* Keyword Bar */}
          <div>
            <div className="flex justify-between text-[10px] text-fuchsia-400 mb-1">
              <span>Keyword Search (Exact)</span>
              <span>{keywordHits} chunks</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-fuchsia-500 shadow-[0_0_8px_rgba(217,70,239,0.6)]"
                style={{ width: `${keywordPct}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 mt-2">
          <div className="p-2 bg-slate-800/50 rounded border border-white/5 text-center">
            <div className="text-[10px] text-slate-400">Total Merged</div>
            <div className="text-sm font-bold text-white">
              {step.details.candidates as number}
            </div>
          </div>
          <div className="p-2 bg-slate-800/50 rounded border border-white/5 text-center">
            <div className="text-[10px] text-slate-400">Sources</div>
            <div className="text-sm font-bold text-white">
              {step.details.sources as number}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Fallback: Raw JSON
  return (
    <div className="p-3 bg-black/20 rounded border border-white/5 text-[10px] font-mono text-slate-400 overflow-x-auto">
      <pre>{JSON.stringify(step.details, null, 2)}</pre>
    </div>
  );
}
