"use client";

import {
  AlertCircle,
  CheckCircle,
  ChevronDown,
  Coins,
  MessageSquare,
  TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatTokens, getAggregatedStats } from "../lib/analytics";

// Model colors
const MODEL_COLORS: { [key: string]: string } = {
  "GPT-4": "#f97316",
  Claude: "#3b82f6",
  Llama: "#22c55e",
  Mistral: "#8b5cf6",
  Gemma: "#ec4899",
  Phi: "#06b6d4",
  Other: "#6b7280",
};

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState(7);
  const [stats, setStats] = useState<ReturnType<
    typeof getAggregatedStats
  > | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    // Load analytics data
    const loadStats = () => {
      const data = getAggregatedStats(timeRange);
      setStats(data);
      setIsLoading(false);
    };

    loadStats();
    // Refresh every 5 seconds to catch new data
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, [timeRange]);

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="spinner" />
      </div>
    );
  }

  const hasData = stats && stats.totalQueries > 0;

  // Prepare chart data
  const tokenUsageData =
    stats?.dailyStats.map((day) => ({
      day: new Date(day.date).toLocaleDateString("en-US", { weekday: "short" }),
      tokens: day.tokens,
    })) || [];

  const modelDistributionData = stats
    ? Object.entries(stats.modelCounts).map(([name, value]) => ({
        name,
        value,
        color: MODEL_COLORS[name] || MODEL_COLORS.Other,
      }))
    : [];

  const costBreakdownData =
    stats?.dailyStats.map((day) => {
      const dayData: { day: string; [key: string]: string | number } = {
        day: new Date(day.date).toLocaleDateString("en-US", {
          weekday: "short",
        }),
      };
      Object.entries(day.modelBreakdown).forEach(([model, count]) => {
        // Estimate cost per model based on query count
        dayData[model] = Number(((day.cost / day.queries) * count).toFixed(2));
      });
      return dayData;
    }) || [];

  // Get unique models for bar chart
  const uniqueModels = stats
    ? [
        ...new Set(
          stats.dailyStats.flatMap((d) => Object.keys(d.modelBreakdown)),
        ),
      ]
    : [];

  const statCards = [
    {
      label: "Total Queries",
      value: stats?.totalQueries.toLocaleString() || "0",
      trend: hasData ? "Live data" : undefined,
      icon: MessageSquare,
      iconBg: "bg-accent/20",
      iconColor: "text-accent",
    },
    {
      label: "Total Tokens",
      value: formatTokens(stats?.totalTokens || 0),
      icon: TrendingUp,
      iconBg: "bg-blue-500/20",
      iconColor: "text-blue-400",
    },
    {
      label: "Total Cost",
      value: `$${(stats?.totalCost || 0).toFixed(2)}`,
      subtext: hasData
        ? Object.entries(stats?.modelCounts || {})
            .map(([m, c]) => `${m}: ${c}`)
            .join(" | ")
        : undefined,
      icon: Coins,
      iconBg: "bg-green-500/20",
      iconColor: "text-green-400",
    },
    {
      label: "Avg Confidence",
      value: `${stats?.avgConfidence || 0}%`,
      icon: CheckCircle,
      iconBg: "bg-emerald-500/20",
      iconColor: "text-emerald-400",
      valueColor:
        stats?.avgConfidence && stats.avgConfidence >= 80
          ? "text-emerald-400"
          : "text-amber-400",
    },
  ];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Analytics</h1>
        <div className="relative">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="appearance-none flex items-center gap-2 bg-white/5 border border-white/10
                       rounded-lg px-4 py-2 pr-10 text-sm text-slate-300
                       hover:bg-white/10 transition-colors cursor-pointer outline-none"
          >
            <option value={7} className="bg-secondary">
              Last 7 Days
            </option>
            <option value={14} className="bg-secondary">
              Last 14 Days
            </option>
            <option value={30} className="bg-secondary">
              Last 30 Days
            </option>
            <option value={90} className="bg-secondary">
              Last 90 Days
            </option>
          </select>
          <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>
      </div>

      {/* No Data State */}
      {!hasData && (
        <div className="bg-secondary border border-white/5 rounded-xl p-12 text-center mb-8">
          <AlertCircle className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            No Analytics Data Yet
          </h3>
          <p className="text-slate-400 mb-4">
            Start chatting with your documents to see usage analytics here.
          </p>
          <a
            href="/chat"
            className="btn-primary inline-flex items-center gap-2 px-6 py-2"
          >
            Start Chatting
          </a>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="bg-secondary border border-white/5 rounded-xl p-5"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-slate-400 text-xs font-medium">
                  {stat.label}
                </p>
                <h3
                  className={`text-2xl font-bold mt-1 ${stat.valueColor || "text-white"}`}
                >
                  {stat.value}
                </h3>
                {stat.trend && (
                  <p className="text-green-400 text-xs mt-1">{stat.trend}</p>
                )}
                {stat.subtext && (
                  <p className="text-slate-500 text-xs mt-1 truncate max-w-[180px]">
                    {stat.subtext}
                  </p>
                )}
              </div>
              <div
                className={`w-10 h-10 ${stat.iconBg} rounded-lg flex items-center justify-center`}
              >
                <stat.icon className={`w-5 h-5 ${stat.iconColor}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {hasData && (
        <>
          {/* Charts Row 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Token Usage Over Time */}
            <div className="bg-secondary border border-white/5 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4">
                Token Usage Over Time
              </h3>
              <div className="h-64 min-h-[256px] relative">
                {isMounted && tokenUsageData.length > 0 ? (
                  <ResponsiveContainer
                    key="token-usage-chart"
                    width="100%"
                    height="100%"
                    debounce={100}
                  >
                    <AreaChart data={tokenUsageData}>
                      <defs>
                        <linearGradient
                          id="tokenGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor="#f97316"
                            stopOpacity={0.4}
                          />
                          <stop
                            offset="95%"
                            stopColor="#f97316"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                      <YAxis
                        stroke="#64748b"
                        fontSize={12}
                        tickFormatter={(value) => formatTokens(value)}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#0f1729",
                          border: "1px solid #1e293b",
                          borderRadius: "8px",
                        }}
                        labelStyle={{ color: "#fff" }}
                      />
                      <Area
                        type="monotone"
                        dataKey="tokens"
                        stroke="#f97316"
                        strokeWidth={2}
                        fill="url(#tokenGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-500">
                    No token data available
                  </div>
                )}
              </div>
            </div>

            {/* Model Usage Distribution */}
            <div className="bg-secondary border border-white/5 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4">
                Model Usage Distribution
              </h3>
              <div className="h-64 min-h-[256px] relative flex items-center justify-center">
                {isMounted && modelDistributionData.length > 0 ? (
                  <ResponsiveContainer
                    key="model-pie-chart"
                    width="100%"
                    height="100%"
                    debounce={100}
                  >
                    <PieChart>
                      <Pie
                        data={modelDistributionData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={2}
                        dataKey="value"
                        labelLine={false}
                      >
                        {modelDistributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#0f1729",
                          border: "1px solid #1e293b",
                          borderRadius: "8px",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-slate-500">No model data available</div>
                )}
              </div>
            </div>
          </div>

          {/* Charts Row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Average Confidence by Model */}
            <div className="bg-secondary border border-white/5 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4">
                Average Confidence by Model
              </h3>
              <div className="space-y-4">
                {stats?.modelConfidenceAvg &&
                stats.modelConfidenceAvg.length > 0 ? (
                  stats.modelConfidenceAvg.map((item) => (
                    <div key={item.model}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-slate-400 text-sm">
                          {item.model}
                        </span>
                        <span className="text-white text-sm font-medium">
                          {item.confidence}%
                        </span>
                      </div>
                      <div className="w-full bg-white/5 rounded-full h-3">
                        <div
                          className="h-3 rounded-full transition-all duration-500"
                          style={{
                            width: `${item.confidence}%`,
                            backgroundColor:
                              MODEL_COLORS[item.model] || MODEL_COLORS.Other,
                          }}
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 text-center py-8">
                    No confidence data available
                  </div>
                )}
              </div>
            </div>

            {/* Cost Breakdown */}
            <div className="bg-secondary border border-white/5 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4">Cost Breakdown</h3>
              <div className="h-64 min-h-[256px] relative">
                {isMounted &&
                costBreakdownData.length > 0 &&
                uniqueModels.length > 0 ? (
                  <ResponsiveContainer
                    key="cost-breakdown-chart"
                    width="100%"
                    height="100%"
                    debounce={100}
                  >
                    <BarChart data={costBreakdownData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                      <YAxis
                        stroke="#64748b"
                        fontSize={12}
                        tickFormatter={(value) => `$${value}`}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#0f1729",
                          border: "1px solid #1e293b",
                          borderRadius: "8px",
                        }}
                      />
                      <Legend />
                      {uniqueModels.map((model) => (
                        <Bar
                          key={model}
                          dataKey={model}
                          name={model}
                          stackId="a"
                          fill={MODEL_COLORS[model] || MODEL_COLORS.Other}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-500">
                    No cost data available
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
