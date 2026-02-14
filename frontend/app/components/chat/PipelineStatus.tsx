interface PipelineStep {
  step: string;
  label: string;
  duration_ms: number;
  details?: Record<string, unknown>;
}

interface PipelineStatusProps {
  steps: PipelineStep[];
  totalTime: number;
}

const STAGE_CONFIG: Record<
  string,
  { label: string; icon: string; color: string }
> = {
  routing: { label: "Plan", icon: "🧠", color: "bg-indigo-500" },
  embedding: { label: "Embed", icon: "🔢", color: "bg-blue-500" },
  retrieval: { label: "Search", icon: "🔎", color: "bg-emerald-500" },
  reranking: { label: "Rank", icon: "🎯", color: "bg-amber-500" },
  generation: { label: "Answer", icon: "✨", color: "bg-violet-500" },
};

const ORDERED_STAGES = [
  "routing",
  "embedding",
  "retrieval",
  "reranking",
  "generation",
];

export default function PipelineStatus({
  steps,
  totalTime,
}: PipelineStatusProps) {
  // Map executed steps to the ordered stages
  // If a step is missing (e.g. reranking skipped), it won't be highlighed

  // Group steps by their base stage name
  const executedStages = new Set(steps.map((s) => s.step));

  return (
    <div className="mb-4 mt-2">
      <div className="flex items-center justify-between relative">
        {/* Connecting Line */}
        <div className="absolute top-1/2 left-0 w-full h-0.5 bg-white/10 -z-0"></div>

        {ORDERED_STAGES.map((stageKey) => {
          const isExecuted = executedStages.has(stageKey);
          const config = STAGE_CONFIG[stageKey];
          // Find specific step data if executed
          const stepData = steps.find((s) => s.step === stageKey);

          return (
            <div
              key={stageKey}
              className="relative z-10 flex flex-col items-center group"
            >
              {/* Dot/Icon */}
              <div
                className={`
                                w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300
                                ${
                                  isExecuted
                                    ? `${config.color} border-white text-white shadow-[0_0_10px_rgba(255,255,255,0.3)] scale-110`
                                    : "bg-slate-800 border-white/10 text-slate-600 grayscale scale-90"
                                }
                            `}
              >
                <span className="text-xs">{config.icon}</span>
              </div>

              {/* Label */}
              <div
                className={`
                                mt-2 text-[10px] font-medium uppercase tracking-wider transition-colors
                                ${isExecuted ? "text-white" : "text-slate-600"}
                            `}
              >
                {config.label}
              </div>

              {/* Tooltip on Hover */}
              {isExecuted && stepData && (
                <div className="absolute bottom-full mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20">
                  <div className="bg-slate-900 border border-white/10 text-slate-200 text-xs px-2 py-1 rounded shadow-xl">
                    {stepData.label} ({stepData.duration_ms.toFixed(0)}ms)
                  </div>
                  <div className="w-2 h-2 bg-slate-900 border-r border-b border-white/10 rotate-45 mx-auto -mt-1"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div className="text-right mt-1">
        <span className="text-[10px] text-slate-500 font-mono">
          Total Latency: {(totalTime / 1000).toFixed(2)}s
        </span>
      </div>
    </div>
  );
}
