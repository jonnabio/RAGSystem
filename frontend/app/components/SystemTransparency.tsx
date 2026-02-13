"use client";

import { useCallback, useEffect, useState } from "react";

interface SystemInfo {
  chunking: {
    chunk_size: number;
    chunk_overlap: number;
    strategy: string;
  };
  embedding: {
    model: string;
    dimensions: number;
    provider: string;
  };
  vector_database: {
    engine: string;
    path: string;
    index_type: string;
    search_method: string;
  };
  llm: {
    default_model: string;
    provider: string;
    max_retrieval_chunks: number;
  };
}

interface SystemStats {
  documents_indexed: number;
  total_chunks: number;
  vector_db_status: string;
}

interface PipelineStep {
  id: string;
  stage: string;
  status: string;
  message: string;
  detail?: Record<string, unknown>;
  duration_ms?: number;
}

interface PipelineRun {
  id: string;
  pipeline_type: string;
  label: string;
  status: string;
  steps: PipelineStep[];
  started_at: string;
}

interface EvaluationResults {
  timestamp: string;
  scores: {
    faithfulness: number;
    answer_relevancy: number;
    context_precision: number;
  };
  sample_count: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function SystemTransparency() {
  const [info, setInfo] = useState<SystemInfo | null>(null);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [evalResults, setEvalResults] = useState<EvaluationResults | null>(
    null,
  );
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [infoRes, statsRes, eventsRes] = await Promise.all([
        fetch(`${API_URL}/api/system/info`),
        fetch(`${API_URL}/api/system/stats`),
        fetch(`${API_URL}/api/system/events?limit=8`),
      ]);
      if (infoRes.ok) setInfo(await infoRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      if (eventsRes.ok) {
        const data = await eventsRes.json();
        setRuns(data.runs || []);
      }
      const evalRes = await fetch(`${API_URL}/api/evaluation/results`);
      if (evalRes.ok) {
        const data = await evalRes.json();
        if (data.scores) setEvalResults(data);
      }
    } catch {
      /* backend not reachable */
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      if (!cancelled) {
        await fetchData();
      }
    };
    poll();
    const interval = setInterval(poll, 3000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [fetchData]);

  const runBenchmark = async () => {
    setIsEvaluating(true);
    try {
      const res = await fetch(`${API_URL}/api/evaluation/run`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setEvalResults(data);
      }
    } catch (e) {
      console.error("Evaluation failed", e);
    } finally {
      setIsEvaluating(false);
    }
  };

  const stageIcons: Record<string, string> = {
    validation: "🔍",
    saving: "💾",
    parsing: "📄",
    indexing: "📦",
    embedding: "🧮",
    retrieval: "🔎",
    generation: "🤖",
  };

  const statusColors: Record<string, string> = {
    running: "text-blue-400 animate-pulse",
    completed: "text-emerald-400",
    error: "text-red-400",
    pending: "text-slate-500",
  };

  const overlapPercent = info
    ? (info.chunking.chunk_overlap / info.chunking.chunk_size) * 100
    : 0;
  const chunkPercent = 100 - overlapPercent;

  return (
    <div className="space-y-6 text-sm">
      {/* ── RAG Pipeline Architecture ── */}
      <section>
        <SectionTitle>RAG Pipeline Architecture</SectionTitle>
        <div className="bg-white/5 rounded-xl p-4">
          <div className="flex items-center justify-between gap-2">
            {[
              {
                icon: "📄",
                label: "Ingest",
                tip: "Documents are uploaded and read (PDF, TXT, etc.)",
              },
              {
                icon: "✂️",
                label: "Chunk",
                tip: "Text is split into smaller overlapping segments",
              },
              {
                icon: "🧮",
                label: "Embed",
                tip: "Each chunk is converted into a numerical vector",
              },
              {
                icon: "📦",
                label: "Store",
                tip: "Vectors are saved in LanceDB for fast lookup",
              },
              {
                icon: "🔎",
                label: "Retrieve",
                tip: "Relevant chunks are found via similarity search",
              },
              {
                icon: "🤖",
                label: "Generate",
                tip: "LLM produces an answer using retrieved context",
              },
            ].map((step, i, arr) => (
              <div
                key={step.label}
                className="flex items-center gap-1"
                title={step.tip}
              >
                <div className="flex flex-col items-center cursor-help">
                  <span className="text-lg">{step.icon}</span>
                  <span className="text-[11px] text-slate-400 mt-0.5 whitespace-nowrap">
                    {step.label}
                  </span>
                </div>
                {i < arr.length - 1 && (
                  <span className="text-slate-600 text-xs mx-1">→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Active Agents ── */}
      <section>
        <SectionTitle>Active Agents</SectionTitle>
        <div className="space-y-2">
          <AgentRow
            icon="🤖"
            label="LLM Provider"
            value={info?.llm.default_model || "—"}
            sub={info?.llm.provider || "OpenRouter"}
            status="active"
            tooltip="The large language model that generates answers from retrieved context"
          />
          <AgentRow
            icon="🧮"
            label="Embedding Model"
            value={info?.embedding.model || "—"}
            sub={`${info?.embedding.dimensions || 3072}d vectors · ${info?.embedding.provider || "OpenRouter"}`}
            status="active"
            tooltip="Converts text into numerical vectors for similarity search"
          />
          <AgentRow
            icon="📦"
            label="Vector Database"
            value={info?.vector_database.engine || "—"}
            sub={info?.vector_database.path || "data/vectors"}
            status={
              stats?.vector_db_status === "connected" ? "active" : "inactive"
            }
            tooltip="Stores document vectors and performs fast nearest-neighbour lookups"
          />
        </div>
      </section>

      {/* ── Chunking Strategy ── */}
      <section>
        <SectionTitle>Chunking Strategy</SectionTitle>
        {info && (
          <div className="bg-white/5 rounded-xl p-4 space-y-3">
            <div className="text-slate-300 text-[13px] mb-2">
              {info.chunking.strategy}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div
                className="bg-white/5 rounded-lg p-3 text-center cursor-help"
                title="How many words fit in one chunk — larger chunks give more context but may dilute relevance"
              >
                <div className="text-2xl font-bold text-white">
                  {info.chunking.chunk_size}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Words / Chunk
                </div>
              </div>
              <div
                className="bg-white/5 rounded-lg p-3 text-center cursor-help"
                title="Words shared between consecutive chunks — prevents ideas from being cut off at boundaries"
              >
                <div className="text-2xl font-bold text-amber-400">
                  {info.chunking.chunk_overlap}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Overlap Words
                </div>
              </div>
            </div>
            {/* Visual overlap bar */}
            <div>
              <div className="flex gap-0.5 h-5 rounded-lg overflow-hidden">
                <div
                  className="bg-indigo-500/60 flex items-center justify-center text-[10px] text-white/80"
                  style={{ width: `${chunkPercent}%` }}
                >
                  Chunk
                </div>
                <div
                  className="bg-amber-400/70 flex items-center justify-center text-[10px] text-black/70 font-medium"
                  style={{ width: `${overlapPercent}%` }}
                >
                  OL
                </div>
              </div>
              <div className="flex justify-between mt-1 text-[11px] text-slate-500">
                <span>{chunkPercent.toFixed(0)}% unique</span>
                <span>{overlapPercent.toFixed(1)}% overlap</span>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* ── Quality Metrics (Ragas) ── */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <SectionTitle>Quality Metrics (Ragas)</SectionTitle>
          <button
            onClick={runBenchmark}
            disabled={isEvaluating}
            className={`text-[10px] px-2 py-0.5 rounded border border-accent/30 text-accent hover:bg-accent/10 transition-colors disabled:opacity-50`}
          >
            {isEvaluating ? "Evaluating..." : "Run Benchmark"}
          </button>
        </div>
        <div className="bg-white/5 rounded-xl p-4 space-y-4">
          {!evalResults ? (
            <p className="text-slate-500 italic text-[12px]">
              No evaluation results yet. Run a benchmark to measure RAG quality.
            </p>
          ) : (
            <>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center">
                  <div className="text-lg font-bold text-emerald-400">
                    {(evalResults.scores.faithfulness * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-slate-400 uppercase">
                    Faithfulness
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-amber-400">
                    {(evalResults.scores.answer_relevancy * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-slate-400 uppercase">
                    Relevance
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-indigo-400">
                    {(evalResults.scores.context_precision * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-slate-400 uppercase">
                    Precision
                  </div>
                </div>
              </div>
              <div className="pt-2 border-t border-white/5 flex justify-between items-center text-[10px] text-slate-500">
                <span>
                  Last Run: {new Date(evalResults.timestamp).toLocaleString()}
                </span>
                <span>n={evalResults.sample_count} samples</span>
              </div>
            </>
          )}
        </div>
      </section>

      {/* ── Storage Metrics ── */}
      <section>
        <SectionTitle>Storage Metrics</SectionTitle>
        <div className="grid grid-cols-3 gap-3">
          <MetricCard
            label="Documents"
            value={stats?.documents_indexed ?? 0}
            icon="📁"
            tooltip="Total files uploaded and indexed in the vector database"
          />
          <MetricCard
            label="Chunks"
            value={stats?.total_chunks ?? 0}
            icon="🧩"
            tooltip="Total text segments stored — each chunk is searched independently during retrieval"
          />
          <MetricCard
            label="Avg Chunks/Doc"
            value={
              stats && stats.documents_indexed > 0
                ? Math.round(stats.total_chunks / stats.documents_indexed)
                : 0
            }
            icon="📊"
            tooltip="Average segments per document — higher means longer documents or smaller chunk sizes"
          />
        </div>
      </section>

      {/* ── Retrieval Configuration ── */}
      <section>
        <SectionTitle>Retrieval Configuration</SectionTitle>
        <div className="bg-white/5 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-3">
            <span className="text-xl">🔎</span>
            <div>
              <div className="text-white text-[14px] font-medium">
                {info?.vector_database.search_method ||
                  "Vector Similarity (L2 distance)"}
              </div>
              <div className="text-slate-400 text-[12px]">
                Semantic nearest-neighbour search
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 pt-1">
            <InfoPill
              label="Top K"
              value={String(info?.llm.max_retrieval_chunks || 5)}
              tooltip="Number of most-relevant chunks sent to the LLM as context"
            />
            <InfoPill
              label="Index"
              value={info?.vector_database.index_type || "IVF-PQ"}
              tooltip="Vector index structure — affects search speed vs accuracy tradeoff"
            />
            <InfoPill
              label="Distance"
              value="L2 (Euclidean)"
              tooltip="How similarity is measured — lower L2 distance means more similar vectors"
            />
            <InfoPill
              label="Dims"
              value={String(info?.embedding.dimensions || 3072)}
              tooltip="Vector dimensionality — more dimensions capture finer semantic nuances"
            />
          </div>
        </div>
      </section>

      {/* ── System Configuration ── */}
      <section>
        <SectionTitle>System Configuration</SectionTitle>
        <div className="bg-white/5 rounded-xl p-4 space-y-2">
          <ConfigRow
            label="Backend"
            value="FastAPI + Uvicorn"
            tooltip="Python async web framework serving the RAG API"
          />
          <ConfigRow
            label="Frontend"
            value="Next.js 16 (React)"
            tooltip="React-based UI framework with server-side rendering"
          />
          <ConfigRow
            label="Vector Store"
            value={info?.vector_database.engine || "LanceDB"}
            tooltip="Embedded columnar database optimized for fast vector similarity search"
          />
          <ConfigRow
            label="LLM Router"
            value={info?.llm.provider || "OpenRouter"}
            tooltip="Routes requests to various LLM providers (Llama, GPT, Claude, etc.)"
          />
          <ConfigRow
            label="Embedding API"
            value={info?.embedding.provider || "OpenRouter"}
            tooltip="API used to convert text into embedding vectors"
          />
          <ConfigRow
            label="Storage"
            value="Local filesystem"
            tooltip="Documents and vector data are stored on the local disk"
          />
        </div>
      </section>

      {/* ── Pipeline Log ── */}
      <section>
        <SectionTitle>Pipeline Log</SectionTitle>
        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
          {runs.length === 0 && (
            <p className="text-slate-500 italic text-[13px]">
              No pipeline activity yet — upload a document or send a query.
            </p>
          )}
          {runs.map((run) => (
            <button
              key={run.id}
              className="w-full text-left bg-white/5 rounded-xl overflow-hidden cursor-pointer hover:bg-white/10 transition-colors"
              onClick={() => setExpanded(expanded === run.id ? null : run.id)}
            >
              {/* Run header */}
              <div className="px-4 py-3 flex items-center gap-3">
                <span className={`text-base ${statusColors[run.status]}`}>
                  {run.status === "running"
                    ? "●"
                    : run.status === "completed"
                      ? "✓"
                      : "✕"}
                </span>
                <span className="text-white text-[13px] truncate flex-1">
                  {run.label}
                </span>
                <span className="text-[11px] text-slate-500 uppercase font-medium px-2 py-0.5 bg-white/5 rounded">
                  {run.pipeline_type}
                </span>
              </div>

              {/* Expanded steps */}
              {expanded === run.id && (
                <div className="border-t border-white/5 px-4 py-3 space-y-2">
                  {run.steps.map((step) => (
                    <div
                      key={step.id}
                      className="flex items-start gap-3 text-[13px]"
                    >
                      <span className="text-base mt-0.5">
                        {stageIcons[step.stage] || "⚙️"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <span className={statusColors[step.status]}>
                          {step.message}
                        </span>
                        {step.duration_ms != null && (
                          <span className="text-slate-500 ml-2 text-[12px]">
                            {step.duration_ms.toFixed(0)}ms
                          </span>
                        )}
                        {step.detail && (
                          <div className="text-[12px] text-slate-500 mt-1 space-x-2 break-all">
                            {Object.entries(step.detail).map(([k, v]) => {
                              const formatted =
                                typeof v === "number"
                                  ? v % 1 === 0
                                    ? v
                                    : Number(v).toFixed(2)
                                  : String(v);
                              return (
                                <span key={k}>
                                  <span className="text-slate-400">{k}:</span>{" "}
                                  {formatted}
                                </span>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ── Sub-components ── */

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
      {children}
    </h3>
  );
}

function AgentRow({
  icon,
  label,
  value,
  sub,
  status,
  tooltip,
}: {
  icon: string;
  label: string;
  value: string;
  sub?: string;
  status: "active" | "inactive";
  tooltip?: string;
}) {
  return (
    <div
      className="flex items-center gap-3 bg-white/5 rounded-xl px-4 py-3 cursor-help"
      title={tooltip}
    >
      <span className="text-xl">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="text-[11px] text-slate-500 uppercase tracking-wide">
          {label}
        </div>
        <div className="text-white truncate text-[13px] font-medium">
          {value}
        </div>
        {sub && <div className="text-[11px] text-slate-500 mt-0.5">{sub}</div>}
      </div>
      <span
        className={`w-2.5 h-2.5 rounded-full shrink-0 ${
          status === "active"
            ? "bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]"
            : "bg-red-400"
        }`}
      />
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon,
  tooltip,
}: {
  label: string;
  value: number;
  icon: string;
  tooltip?: string;
}) {
  return (
    <div
      className="bg-white/5 rounded-xl p-4 text-center cursor-help"
      title={tooltip}
    >
      <div className="text-2xl">{icon}</div>
      <div className="text-white font-bold text-2xl mt-1">{value}</div>
      <div className="text-[11px] text-slate-400 mt-0.5">{label}</div>
    </div>
  );
}

function InfoPill({
  label,
  value,
  tooltip,
}: {
  label: string;
  value: string;
  tooltip?: string;
}) {
  return (
    <div
      className="bg-white/5 rounded-lg px-3 py-2 flex justify-between items-center cursor-help"
      title={tooltip}
    >
      <span className="text-slate-400 text-[12px]">{label}</span>
      <span className="text-white text-[13px] font-mono">{value}</span>
    </div>
  );
}

function ConfigRow({
  label,
  value,
  tooltip,
}: {
  label: string;
  value: string;
  tooltip?: string;
}) {
  return (
    <div
      className="flex justify-between items-center py-1 cursor-help"
      title={tooltip}
    >
      <span className="text-slate-400 text-[13px]">{label}</span>
      <span className="text-white text-[13px]">{value}</span>
    </div>
  );
}
