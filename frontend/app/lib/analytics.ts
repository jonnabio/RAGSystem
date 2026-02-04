// Analytics data types and storage utilities

export interface QueryAnalytics {
  id: string;
  timestamp: Date;
  model: string;
  tokensUsed: number;
  cost: number;
  confidence: number;
  queryLength: number;
  responseLength: number;
  queryText?: string;
}

export interface Activity {
  id: string;
  type: "upload" | "query" | "index";
  title: string;
  description: string;
  timestamp: Date;
}

export interface DailyStats {
  date: string; // YYYY-MM-DD
  queries: number;
  tokens: number;
  cost: number;
  avgConfidence: number;
  modelBreakdown: { [model: string]: number };
}

const ANALYTICS_KEY = "rag-analytics";
const ACTIVITY_KEY = "rag-activity";

// Save a query to analytics
export function trackQuery(data: Omit<QueryAnalytics, "id">) {
  const analytics = getAnalytics();
  const newEntry: QueryAnalytics = {
    ...data,
    id: Date.now().toString(),
    timestamp: new Date(data.timestamp),
  };
  analytics.push(newEntry);

  // Also track as activity
  // Also track as activity
  let queryPreview = "New Query";
  if (data.queryText) {
    queryPreview =
      data.queryText.length > 30
        ? data.queryText.substring(0, 30) + "..."
        : data.queryText;
  }

  trackActivity({
    type: "query",
    title: `Query: "${queryPreview}"`,
    description: `${getModelShortName(data.model)} • ${data.tokensUsed} tokens`,
    timestamp: data.timestamp,
  });

  // Keep last 1000 queries to avoid localStorage limits
  const trimmed = analytics.slice(-1000);
  try {
    localStorage.setItem(ANALYTICS_KEY, JSON.stringify(trimmed));
  } catch (err) {
    console.error("Failed to save analytics to localStorage:", err);
  }
}

// Track an activity
export function trackActivity(data: Omit<Activity, "id">) {
  const activities = getActivities();
  const newActivity: Activity = {
    ...data,
    id: Date.now().toString(),
    timestamp: new Date(data.timestamp),
  };

  const updated = [newActivity, ...activities].slice(0, 50); // Keep last 50

  try {
    localStorage.setItem(ACTIVITY_KEY, JSON.stringify(updated));
  } catch (err) {
    console.error("Failed to save activity to localStorage:", err);
  }

  // Notify system of activity change
  if (globalThis.window !== undefined) {
    try {
      const event = new CustomEvent("activityUpdated");
      globalThis.window.dispatchEvent(event);
    } catch (e) {
      // Fallback for environments where CustomEvent constructor might fail
      const event = globalThis.window.document.createEvent("CustomEvent");
      event.initCustomEvent("activityUpdated", false, false, null);
      globalThis.window.dispatchEvent(event);
    }
  }
}

// Get activities
export function getActivities(): Activity[] {
  try {
    const stored = localStorage.getItem(ACTIVITY_KEY);
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    return parsed.map((a: Activity) => ({
      ...a,
      timestamp: new Date(a.timestamp),
    }));
  } catch {
    return [];
  }
}

// Get all analytics
export function getAnalytics(): QueryAnalytics[] {
  try {
    const stored = localStorage.getItem(ANALYTICS_KEY);
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    return parsed.map((q: QueryAnalytics) => ({
      ...q,
      timestamp: new Date(q.timestamp),
    }));
  } catch {
    return [];
  }
}

// Get aggregated stats
export function getAggregatedStats(daysBack: number = 7) {
  const analytics = getAnalytics();
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - daysBack);

  const filtered = analytics.filter((q) => new Date(q.timestamp) >= cutoff);

  // Calculate totals
  const totalQueries = filtered.length;
  const totalTokens = filtered.reduce((sum, q) => sum + q.tokensUsed, 0);
  const totalCost = filtered.reduce((sum, q) => sum + q.cost, 0);
  const avgConfidence =
    filtered.length > 0
      ? filtered.reduce((sum, q) => sum + q.confidence, 0) / filtered.length
      : 0;

  // Model distribution
  const modelCounts: { [key: string]: number } = {};
  filtered.forEach((q) => {
    const modelName = getModelShortName(q.model);
    modelCounts[modelName] = (modelCounts[modelName] || 0) + 1;
  });

  // Daily breakdown for charts
  const dailyMap: { [date: string]: DailyStats } = {};
  filtered.forEach((q) => {
    const dateStr = new Date(q.timestamp).toISOString().split("T")[0];
    if (!dailyMap[dateStr]) {
      dailyMap[dateStr] = {
        date: dateStr,
        queries: 0,
        tokens: 0,
        cost: 0,
        avgConfidence: 0,
        modelBreakdown: {},
      };
    }
    dailyMap[dateStr].queries++;
    dailyMap[dateStr].tokens += q.tokensUsed;
    dailyMap[dateStr].cost += q.cost;

    const modelName = getModelShortName(q.model);
    dailyMap[dateStr].modelBreakdown[modelName] =
      (dailyMap[dateStr].modelBreakdown[modelName] || 0) + 1;
  });

  // Calculate daily averages for confidence
  Object.keys(dailyMap).forEach((date) => {
    const dayQueries = filtered.filter(
      (q) => new Date(q.timestamp).toISOString().split("T")[0] === date,
    );
    dailyMap[date].avgConfidence =
      dayQueries.length > 0
        ? dayQueries.reduce((sum, q) => sum + q.confidence, 0) /
          dayQueries.length
        : 0;
  });

  // Sort by date and convert to array
  const dailyStats = Object.values(dailyMap).sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  );

  // Model confidence averages
  const modelConfidence: { [model: string]: { total: number; count: number } } =
    {};
  filtered.forEach((q) => {
    const modelName = getModelShortName(q.model);
    if (!modelConfidence[modelName]) {
      modelConfidence[modelName] = { total: 0, count: 0 };
    }
    modelConfidence[modelName].total += q.confidence;
    modelConfidence[modelName].count++;
  });

  const modelConfidenceAvg = Object.entries(modelConfidence).map(
    ([model, data]) => ({
      model,
      confidence: Math.round((data.total / data.count) * 100),
    }),
  );

  return {
    totalQueries,
    totalTokens,
    totalCost,
    avgConfidence: Math.round(avgConfidence * 100),
    modelCounts,
    dailyStats,
    modelConfidenceAvg,
  };
}

// Get short model name for display
function getModelShortName(fullName: string): string {
  if (fullName.includes("gpt-4")) return "GPT-4";
  if (fullName.includes("claude")) return "Claude";
  if (fullName.includes("llama")) return "Llama";
  if (fullName.includes("mistral")) return "Mistral";
  if (fullName.includes("gemma")) return "Gemma";
  if (fullName.includes("phi")) return "Phi";
  return "Other";
}

// Format token count for display
export function formatTokens(tokens: number): string {
  if (tokens >= 1000000) return (tokens / 1000000).toFixed(1) + "M";
  if (tokens >= 1000) return (tokens / 1000).toFixed(1) + "K";
  return tokens.toString();
}

// Clear analytics (for testing)
export function clearAnalytics() {
  localStorage.removeItem(ANALYTICS_KEY);
}
