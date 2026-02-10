"use client";

import { Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import ConversationHistory from "../components/chat/ConversationHistory";
import FeedbackButtons from "../components/chat/FeedbackButtons";
import InteractiveCitations from "../components/chat/InteractiveCitations";
import ThoughtProcess from "../components/chat/ThoughtProcess";
import SystemTransparency from "../components/SystemTransparency";
import { trackQuery } from "../lib/analytics";
import { AppSettings, getSettings } from "../lib/settings";

interface PipelineStep {
  step: string;
  label: string;
  duration_ms: number;
  details?: Record<string, unknown>;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  confidence?: number;
  pipeline_steps?: PipelineStep[];
  metadata?: {
    model: string;
    tokens: number;
    cost?: number;
  };
}

interface Source {
  rank: number;
  text: string;
  score: number;
  document_id?: string;
  metadata?: Record<string, unknown>;
}

interface Conversation {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  messages: Message[];
}

const STORAGE_KEY = "rag-conversations";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [appSettings, setAppSettings] = useState<AppSettings | null>(null);
  const [selectedModel, setSelectedModel] = useState("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string>();
  const [showArchView, setShowArchView] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load settings on mount
  useEffect(() => {
    const settings = getSettings();
    setAppSettings(settings);
    setSelectedModel(settings.defaultModel);

    // Listen for settings updates from the settings page
    const handleSettingsUpdate = (e: Event) => {
      const updated = (e as CustomEvent<AppSettings>).detail;
      setAppSettings(updated);
      // If we're not in an active conversation, update the current model to the new default
      if (!activeConversationId) {
        setSelectedModel(updated.defaultModel);
      }
    };

    window.addEventListener("settingsUpdated", handleSettingsUpdate);
    return () =>
      window.removeEventListener("settingsUpdated", handleSettingsUpdate);
  }, [activeConversationId]);

  // Load conversations from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Convert timestamp strings back to Date objects
        const convos = parsed.map((c: Conversation) => ({
          ...c,
          timestamp: new Date(c.timestamp),
        }));
        setConversations(convos);
      } catch (e) {
        console.error("Error loading conversations:", e);
      }
    }
  }, []);

  // Save conversations to localStorage when they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    }
  }, [conversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate a title from the first user message
  const generateTitle = (content: string): string => {
    const maxLen = 25;
    const cleaned = content.replace(/\n/g, " ").trim();
    if (cleaned.length <= maxLen) return cleaned;
    return cleaned.substring(0, maxLen) + "...";
  };

  // Create or update conversation after sending a message
  const updateConversation = (newMessages: Message[]) => {
    if (newMessages.length === 0) return;

    const firstUserMsg = newMessages.find((m) => m.role === "user");
    if (!firstUserMsg) return;

    const title = generateTitle(firstUserMsg.content);
    const lastMsg = newMessages[newMessages.length - 1];
    const preview =
      lastMsg.role === "assistant"
        ? generateTitle(lastMsg.content)
        : generateTitle(firstUserMsg.content);

    if (activeConversationId) {
      // Update existing conversation
      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeConversationId
            ? { ...c, messages: newMessages, preview, timestamp: new Date() }
            : c,
        ),
      );
    } else {
      // Create new conversation
      const newId = Date.now().toString();
      const newConvo: Conversation = {
        id: newId,
        title,
        preview,
        timestamp: new Date(),
        messages: newMessages,
      };
      setConversations((prev) => [newConvo, ...prev]);
      setActiveConversationId(newId);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const queryText = input.trim();
    const userMessage: Message = {
      role: "user",
      content: queryText,
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(appSettings?.openRouterKey
              ? { "X-OpenRouter-Key": appSettings.openRouterKey }
              : {}),
          },
          body: JSON.stringify({
            query: queryText,
            model: selectedModel,
            conversation_history: messages.map((m) => ({
              role: m.role,
              content: m.content,
            })),
            max_context_chunks: appSettings?.retrievalK || 5,
            temperature: appSettings?.temperature || 0.7,
            top_p: appSettings?.topP || 1.0,
            similarity_threshold: appSettings?.similarityThreshold || 0.7,
            stream: appSettings?.streamingEnabled !== false,
          }),
        },
      );

      if (response.ok) {
        const data = await response.json();

        const assistantMessage: Message = {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          confidence: data.confidence,
          pipeline_steps: data.pipeline_steps,
          metadata: {
            model: data.model,
            tokens: data.tokens_used,
            cost: data.cost,
          },
        };

        // Track analytics
        trackQuery({
          timestamp: new Date(),
          model: selectedModel,
          tokensUsed: data.tokens_used || 0,
          cost: data.cost || 0,
          confidence: data.confidence || 0,
          queryLength: queryText.length,
          responseLength: data.answer?.length || 0,
          queryText: queryText,
        });

        const updatedMessages = [...newMessages, assistantMessage];
        setMessages(updatedMessages);
        updateConversation(updatedMessages);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to get response");
      }
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      console.error("Error sending message:", err);
      const errorMessage: Message = {
        role: "assistant",
        content: err.message?.includes("rate-limited")
          ? err.message
          : "Sorry, I couldn't process your request. Please make sure the backend is running and documents are uploaded.",
      };
      const updatedMessages = [...newMessages, errorMessage];
      setMessages(updatedMessages);
      updateConversation(updatedMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setActiveConversationId(undefined);
  };

  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id);
    const convo = conversations.find((c) => c.id === id);
    if (convo) {
      setMessages(convo.messages);
    }
  };

  const handleDeleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      setMessages([]);
      setActiveConversationId(undefined);
    }
    // Update localStorage
    const updated = conversations.filter((c) => c.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const getConfidenceBadge = (confidence?: number) => {
    if (!confidence) return null;

    const percentage = Math.round(confidence * 100);
    let badgeClass = "bg-green-500/20 text-green-400";

    if (percentage < 70) {
      badgeClass = "bg-red-500/20 text-red-400";
    } else if (percentage < 90) {
      badgeClass = "bg-amber-500/20 text-amber-400";
    }

    return (
      <span className={`${badgeClass} text-xs px-2 py-1 rounded`}>
        ✓ Confidence: {percentage}%
      </span>
    );
  };

  return (
    <div className="flex h-full">
      {/* Conversation History Sidebar */}
      <ConversationHistory
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={handleSelectConversation}
        onNewChat={handleNewChat}
        onDelete={handleDeleteConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-white font-medium">Chat</span>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm
                         text-slate-200 outline-none cursor-pointer"
            >
              <option
                value="meta-llama/llama-3.3-70b-instruct:free"
                className="bg-secondary"
              >
                Llama 3.3 70B (Free)
              </option>
              <option
                value="nvidia/nemotron-3-nano-30b-a3b:free"
                className="bg-secondary"
              >
                Nemotron 3 Nano (Free)
              </option>
              <option
                value="mistralai/mistral-small-3.1-24b-instruct:free"
                className="bg-secondary"
              >
                Mistral Small (Free)
              </option>
              <option value="openai/gpt-4o" className="bg-secondary">
                GPT-4o
              </option>
              <option
                value="anthropic/claude-3.5-sonnet"
                className="bg-secondary"
              >
                Claude 3.5 Sonnet
              </option>
            </select>
          </div>
          <button
            onClick={() => setShowArchView(!showArchView)}
            className={`px-3 py-1.5 text-xs rounded-lg border transition-all ${
              showArchView
                ? "bg-indigo-500/20 border-indigo-500/50 text-indigo-300"
                : "bg-white/5 border-white/10 text-slate-400 hover:text-white"
            }`}
          >
            🏗️ Architect
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-6xl mb-6">💬</div>
              <h2 className="text-2xl font-bold mb-4 text-white">
                Start a conversation
              </h2>
              <p className="text-slate-400 mb-8">
                Ask questions about your uploaded documents
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                <button
                  onClick={() =>
                    setInput("What are the key findings in the research paper?")
                  }
                  className="card-hover text-left p-4"
                >
                  <div className="text-sm text-slate-300">
                    What are the key findings in the research paper?
                  </div>
                </button>

                <button
                  onClick={() => setInput("Summarize the main document")}
                  className="card-hover text-left p-4"
                >
                  <div className="text-sm text-slate-300">
                    Summarize the main document
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[70%] rounded-2xl px-5 py-4 ${
                      message.role === "user"
                        ? "bg-gradient-to-r from-accent to-accent-light text-white rounded-tr-sm"
                        : "bg-secondary border border-white/5 text-slate-200 rounded-tl-sm"
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">
                      {message.content}
                    </p>

                    {/* Sources - Interactive Citations */}
                    {message.sources && message.sources.length > 0 && (
                      <InteractiveCitations sources={message.sources} />
                    )}

                    {/* Thought Process */}
                    {message.pipeline_steps &&
                      message.pipeline_steps.length > 0 && (
                        <ThoughtProcess steps={message.pipeline_steps} />
                      )}

                    {/* Metadata + Feedback */}
                    {message.metadata && (
                      <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center gap-3 text-xs">
                        {getConfidenceBadge(message.confidence)}
                        <span className="text-slate-500">
                          Tokens: {message.metadata.tokens}
                        </span>
                        {message.metadata.cost && (
                          <span className="text-slate-500">
                            Cost: ${message.metadata.cost.toFixed(4)}
                          </span>
                        )}
                        <div className="ml-auto">
                          <FeedbackButtons
                            messageIndex={index}
                            query={
                              messages.find((m) => m.role === "user")?.content
                            }
                            answer={message.content}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-secondary border border-white/5 rounded-2xl rounded-tl-sm px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="spinner" />
                      <span className="text-slate-400">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="px-6 py-4 border-t border-white/5">
          <div className="max-w-4xl mx-auto flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3
                         text-white placeholder-slate-500 outline-none
                         focus:border-accent focus:ring-1 focus:ring-accent
                         transition-all duration-200"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="btn-primary px-6 py-3 flex items-center gap-2
                         disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Architect's View Sidebar */}
      {showArchView && (
        <div className="w-[420px] border-l border-white/5 bg-black/20 p-5 overflow-y-auto custom-scrollbar">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-bold text-white">
              🏗️ Architect&apos;s View
            </h2>
            <button
              onClick={() => setShowArchView(false)}
              className="text-slate-500 hover:text-white text-sm px-2"
            >
              ✕
            </button>
          </div>
          <SystemTransparency />
        </div>
      )}
    </div>
  );
}
