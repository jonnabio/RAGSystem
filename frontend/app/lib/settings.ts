"use client";

export interface AppSettings {
  // API Settings
  openRouterKey: string;

  // Chat Preferences
  defaultModel: string;
  temperature: number;
  topP: number;
  streamingEnabled: boolean;

  // RAG Settings
  retrievalK: number;
  similarityThreshold: number;

  // UI Settings
  refreshInterval: number; // in milliseconds
  tenantId: string;
}

const DEFAULT_SETTINGS: AppSettings = {
  openRouterKey: "",
  defaultModel: "nvidia/nemotron-3-nano-30b-a3b:free",
  temperature: 0.7,
  topP: 1,
  streamingEnabled: true,
  retrievalK: 4,
  similarityThreshold: 0.7,
  refreshInterval: 5000,
  tenantId: "default",
};

const SETTINGS_KEY = "rag_system_app_settings";

/**
 * Retrieves all application settings from localStorage
 */
export const getSettings = (): AppSettings => {
  if (typeof globalThis.window === "undefined") return DEFAULT_SETTINGS;

  try {
    const stored = localStorage.getItem(SETTINGS_KEY);
    if (!stored) return DEFAULT_SETTINGS;

    const parsed = JSON.parse(stored);
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch (error) {
    console.error("Error loading settings:", error);
    return DEFAULT_SETTINGS;
  }
};

/**
 * Updates application settings and persists them to localStorage
 */
export const saveSettings = (updates: Partial<AppSettings>): AppSettings => {
  if (typeof globalThis.window === "undefined") return DEFAULT_SETTINGS;

  const current = getSettings();
  const updated = { ...current, ...updates };

  localStorage.setItem(SETTINGS_KEY, JSON.stringify(updated));

  // Dispatch custom event to notify other components of setting changes
  globalThis.window.dispatchEvent(
    new CustomEvent("settingsUpdated", { detail: updated }),
  );

  return updated;
};

/**
 * Resets all application data including settings, history, and analytics
 */
export const resetAllSystemData = () => {
  if (globalThis.window === undefined) return;

  // Clear core storage keys
  localStorage.removeItem(SETTINGS_KEY);
  localStorage.removeItem("rag-conversations");
  localStorage.removeItem("rag-analytics");
  localStorage.removeItem("rag-activity");

  // Notify system
  globalThis.window.dispatchEvent(new Event("systemDataReset"));

  // Hard reload to clear in-memory states
  globalThis.window.location.reload();
};
