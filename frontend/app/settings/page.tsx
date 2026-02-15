"use client";

import {
  AlertTriangle,
  Cpu,
  Database,
  Eye,
  EyeOff,
  Key,
  RefreshCcw,
  Save,
  Settings2,
  Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  AppSettings,
  getSettings,
  resetAllSystemData,
  saveSettings,
} from "../lib/settings";

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">(
    "idle",
  );

  useEffect(() => {
    setSettings(getSettings());
  }, []);

  const handleSave = () => {
    if (!settings) return;
    setIsSaving(true);
    try {
      saveSettings(settings);
      setSaveStatus("success");
      setTimeout(() => setSaveStatus("idle"), 2000);
    } catch (saveError) {
      setSaveStatus("error");
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (
      globalThis.confirm(
        "ARE YOU SURE? This will permanently delete ALL chat history, analytics, and document counts. This action cannot be undone.",
      )
    ) {
      resetAllSystemData();
    }
  };

  if (!settings) return null;

  let buttonClass = "bg-accent hover:bg-accent/90 text-white";
  if (saveStatus === "success") buttonClass = "bg-emerald-500 text-white";
  else if (saveStatus === "error") buttonClass = "bg-red-500 text-white";

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-accent/20 rounded-xl flex items-center justify-center">
            <Settings2 className="w-6 h-6 text-accent" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Settings</h1>
            <p className="text-slate-400 text-sm">
              Configure your API keys and model preferences
            </p>
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition-all ${buttonClass} disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isSaving ? (
            <RefreshCcw className="w-4 h-4 animate-spin" />
          ) : saveStatus === "success" ? (
            "Saved!"
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Changes
            </>
          )}
        </button>
      </div>

      <div className="space-y-6">
        {/* API Settings */}
        <div className="bg-secondary border border-white/5 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <Key className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">
              API Configuration
            </h2>
          </div>
          <div className="p-6">
            <label
              htmlFor="openrouter-key"
              className="block text-sm font-medium text-slate-300 mb-2"
            >
              OpenRouter API Key
            </label>
            <div className="relative">
              <input
                id="openrouter-key"
                type={showApiKey ? "text" : "password"}
                value={settings.openRouterKey}
                onChange={(e) =>
                  setSettings({ ...settings, openRouterKey: e.target.value })
                }
                placeholder="sk-or-v1-..."
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white
                         focus:border-accent/50 outline-none transition-colors pr-12"
              />
              <button
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                {showApiKey ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
            <p className="mt-2 text-xs text-slate-500 italic">
              Your key is stored locally in your browser and never sent to our
              servers.
            </p>
          </div>
        </div>

        {/* Organization Settings */}
        <div className="bg-secondary border border-white/5 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <div className="w-5 h-5 bg-purple-500/20 rounded flex items-center justify-center">
              <span className="text-purple-400 text-xs font-bold">ID</span>
            </div>
            <h2 className="text-lg font-semibold text-white">Organization</h2>
          </div>
          <div className="p-6">
            <label
              htmlFor="tenant-id"
              className="block text-sm font-medium text-slate-300 mb-2"
            >
              Tenant ID
            </label>
            <input
              id="tenant-id"
              type="text"
              value={settings.tenantId}
              onChange={(e) =>
                setSettings({ ...settings, tenantId: e.target.value })
              }
              placeholder="e.g. organization-a"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white
                       focus:border-purple-500/50 outline-none transition-colors"
            />
            <p className="mt-2 text-xs text-slate-500 italic">
              Data is isolated by Tenant ID. Changing this will switch to a
              different workspace.
            </p>
          </div>
        </div>

        {/* Model Preferences */}
        <div className="bg-secondary border border-white/5 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <Cpu className="w-5 h-5 text-accent" />
            <h2 className="text-lg font-semibold text-white">
              Model Preferences
            </h2>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div>
                <label
                  htmlFor="default-model"
                  className="block text-sm font-medium text-slate-300 mb-2"
                >
                  Default LLM Model
                </label>
                <select
                  id="default-model"
                  value={settings.defaultModel}
                  onChange={(e) =>
                    setSettings({ ...settings, defaultModel: e.target.value })
                  }
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white
                           focus:border-accent/50 outline-none transition-colors"
                >
                  <option
                    value="google/gemini-2.0-flash-exp:free"
                    className="bg-secondary"
                  >
                    Gemini 2.0 Flash (Free)
                  </option>
                  <option
                    value="meta-llama/llama-3.1-8b-instruct:free"
                    className="bg-secondary"
                  >
                    Llama 3.1 8B (Free)
                  </option>
                  <option
                    value="mistralai/mistral-7b-instruct:free"
                    className="bg-secondary"
                  >
                    Mistral 7B (Free)
                  </option>
                  <option
                    value="anthropic/claude-3.5-sonnet"
                    className="bg-secondary"
                  >
                    Claude 3.5 Sonnet
                  </option>
                  <option value="openai/gpt-4o" className="bg-secondary">
                    GPT-4o
                  </option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-slate-300">
                    Enable Streaming
                  </h3>
                  <p className="text-xs text-slate-500">
                    View responses as they are generated
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() =>
                    setSettings({
                      ...settings,
                      streamingEnabled: !settings.streamingEnabled,
                    })
                  }
                  className={`w-12 h-6 rounded-full p-1 transition-colors duration-200 ease-in-out
                            ${settings.streamingEnabled ? "bg-accent" : "bg-slate-700"}`}
                >
                  <div
                    className={`w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform duration-200
                              ${settings.streamingEnabled ? "translate-x-6" : "translate-x-0"}`}
                  />
                </button>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <label
                    htmlFor="temperature-range"
                    className="text-sm font-medium text-slate-300"
                  >
                    Temperature
                  </label>
                  <span className="text-accent text-sm font-bold">
                    {settings.temperature}
                  </span>
                </div>
                <input
                  id="temperature-range"
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      temperature: Number.parseFloat(e.target.value),
                    })
                  }
                  className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-slate-500">Focused</span>
                  <span className="text-[10px] text-slate-500">Creative</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label
                    htmlFor="top-p-range"
                    className="text-sm font-medium text-slate-300"
                  >
                    Top P
                  </label>
                  <span className="text-accent text-sm font-bold">
                    {settings.topP}
                  </span>
                </div>
                <input
                  id="top-p-range"
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.topP}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      topP: Number.parseFloat(e.target.value),
                    })
                  }
                  className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-accent"
                />
              </div>
            </div>
          </div>
        </div>

        {/* RAG Settings */}
        <div className="bg-secondary border border-white/5 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <Database className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-white">
              Retrieval Settings (RAG)
            </h2>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <div className="flex justify-between mb-2">
                <label
                  htmlFor="retrieval-k"
                  className="text-sm font-medium text-slate-300"
                >
                  Chunk Count (k)
                </label>
                <span className="text-emerald-400 text-sm font-bold">
                  {settings.retrievalK}
                </span>
              </div>
              <input
                id="retrieval-k"
                type="range"
                min="1"
                max="10"
                step="1"
                value={settings.retrievalK}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    retrievalK: Number.parseInt(e.target.value),
                  })
                }
                className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
              <p className="mt-2 text-[10px] text-slate-500 italic">
                Number of document segments retrieved per query. Higher values
                provide more context but use more tokens.
              </p>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label
                  htmlFor="similarity-threshold"
                  className="text-sm font-medium text-slate-300"
                >
                  Similarity Threshold
                </label>
                <span className="text-emerald-400 text-sm font-bold">
                  {settings.similarityThreshold}
                </span>
              </div>
              <input
                id="similarity-threshold"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={settings.similarityThreshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    similarityThreshold: Number.parseFloat(e.target.value),
                  })
                }
                className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
              <p className="mt-2 text-[10px] text-slate-500 italic">
                Minimum confidence score to include a chunk in the context.
              </p>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-red-500/5 border border-red-500/20 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-red-500/10 bg-red-500/[0.02] flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <h2 className="text-lg font-semibold text-red-500">Danger Zone</h2>
          </div>
          <div className="p-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="text-white font-medium">Reset All System Data</h3>
              <p className="text-slate-400 text-sm">
                Clear all chats, analytics, document tracking, and settings.
              </p>
            </div>
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-2 px-6 py-2 bg-red-500 hover:bg-red-600
                       text-white rounded-lg font-semibold transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Factory Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
