"use client";

import { Coins, FileText, MessageSquare, Upload } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import ActivityCard from "./components/ui/ActivityCard";
import StatCard from "./components/ui/StatCard";
import { Activity, getActivities, getAggregatedStats } from "./lib/analytics";

interface Stats {
  documents: number;
  queries: number;
  tokens: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    documents: 0,
    queries: 0,
    tokens: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [activities, setActivities] = useState<Activity[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch documents count from API
        const docResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/documents`,
        );
        let docCount = 0;
        if (docResponse.ok) {
          const documents = await docResponse.json();
          docCount = documents.length;
        }

        // Get analytics and activities from local storage
        const analytics = getAggregatedStats();
        const recentActivities = getActivities();

        setStats({
          documents: docCount,
          queries: analytics.totalQueries,
          tokens: analytics.totalTokens,
        });
        setActivities(recentActivities);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Listen for real-time activity updates
    const handleUpdate = () => {
      fetchData();
    };

    if (globalThis.window !== undefined) {
      globalThis.window.addEventListener("activityUpdated", handleUpdate);
      globalThis.window.addEventListener("systemDataReset", handleUpdate);
      globalThis.window.addEventListener("storage", handleUpdate); // Listen for changes from other tabs
    }

    // Refresh data every 10 seconds (fallback)
    const interval = setInterval(fetchData, 10000);
    return () => {
      clearInterval(interval);
      if (globalThis.window !== undefined) {
        globalThis.window.removeEventListener("activityUpdated", handleUpdate);
        globalThis.window.removeEventListener("systemDataReset", handleUpdate);
        globalThis.window.removeEventListener("storage", handleUpdate);
      }
    };
  }, []);

  const formatTokens = (tokens: number) => {
    if (tokens >= 1000) {
      return (tokens / 1000).toFixed(1) + "K";
    }
    return tokens.toString();
  };

  return (
    <div className="p-8">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">DASHBOARD</h1>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Documents"
          value={isLoading ? "..." : stats.documents}
          trend="+3% last week"
          trendUp={true}
          icon={FileText}
        />
        <StatCard
          title="Queries"
          value={isLoading ? "..." : stats.queries}
          trend="+12% last week"
          trendUp={true}
          icon={MessageSquare}
        />
        <StatCard
          title="Tokens"
          value={isLoading ? "..." : formatTokens(stats.tokens)}
          trend="+5.1K last week"
          trendUp={true}
          icon={Coins}
        />
      </div>

      {/* Upload Button */}
      <div className="flex justify-end mb-8">
        <Link href="/documents">
          <button className="btn-primary flex items-center gap-2 px-6 py-3">
            <Upload className="w-5 h-5" />
            Upload Document
          </button>
        </Link>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4 uppercase tracking-wide">
          Recent Activity
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {activities.length > 0 ? (
            activities.slice(0, 6).map((activity) => (
              <ActivityCard
                key={activity.id}
                type={activity.type}
                title={activity.title}
                description={activity.description}
                time={
                  activity.timestamp
                    ? new Date(activity.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : ""
                }
                onView={() => console.log("View", activity.id)}
              />
            ))
          ) : (
            <div className="md:col-span-3 py-12 bg-secondary/50 border border-dashed border-white/10 rounded-xl text-center">
              <p className="text-slate-500">No recent activity</p>
            </div>
          )}
        </div>
      </div>

      {/* API Status Indicator */}
      <div className="fixed bottom-4 right-4">
        <div className="glass-orange px-4 py-2 rounded-lg flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${isLoading ? "bg-amber-400 animate-pulse" : "bg-green-400"}`}
          />
          <span className="text-sm">
            {isLoading ? "Connecting..." : "API Connected"}
          </span>
        </div>
      </div>
    </div>
  );
}
