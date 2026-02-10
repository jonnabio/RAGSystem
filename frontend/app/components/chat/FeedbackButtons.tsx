"use client";

import { useState } from "react";

interface FeedbackButtonsProps {
  messageIndex: number;
  query?: string;
  answer?: string;
}

const FEEDBACK_REASONS = [
  { id: "inaccurate", label: "Inaccurate" },
  { id: "hallucination", label: "Hallucination" },
  { id: "irrelevant", label: "Irrelevant" },
  { id: "other", label: "Other" },
];

export default function FeedbackButtons({
  messageIndex,
  query,
  answer,
}: FeedbackButtonsProps) {
  const [rating, setRating] = useState<"up" | "down" | null>(null);
  const [showReasons, setShowReasons] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const sendFeedback = async (
    selectedRating: "up" | "down",
    reason?: string,
  ) => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message_index: messageIndex,
          rating: selectedRating,
          reason: reason || null,
          query: query || null,
          answer: answer?.substring(0, 500) || null,
        }),
      });
      setSubmitted(true);
    } catch (err) {
      console.error("Failed to send feedback:", err);
    }
  };

  const handleThumbsUp = () => {
    setRating("up");
    setShowReasons(false);
    sendFeedback("up");
  };

  const handleThumbsDown = () => {
    setRating("down");
    setShowReasons(true);
  };

  const handleReasonSelect = (reason: string) => {
    setShowReasons(false);
    sendFeedback("down", reason);
  };

  if (submitted && rating === "up") {
    return (
      <span className="text-emerald-400 text-xs flex items-center gap-1">
        <span>👍</span> Thanks!
      </span>
    );
  }

  if (submitted && rating === "down") {
    return (
      <span className="text-amber-400 text-xs flex items-center gap-1">
        <span>📝</span> Feedback recorded
      </span>
    );
  }

  return (
    <div className="relative flex items-center gap-1">
      <button
        onClick={handleThumbsUp}
        className={`p-1 rounded transition-all text-xs ${
          rating === "up"
            ? "text-emerald-400"
            : "text-slate-500 hover:text-emerald-400 hover:bg-emerald-500/10"
        }`}
        title="Helpful"
      >
        👍
      </button>
      <button
        onClick={handleThumbsDown}
        className={`p-1 rounded transition-all text-xs ${
          rating === "down"
            ? "text-red-400"
            : "text-slate-500 hover:text-red-400 hover:bg-red-500/10"
        }`}
        title="Not helpful"
      >
        👎
      </button>

      {/* Reason dropdown */}
      {showReasons && (
        <div className="absolute bottom-full right-0 mb-1 bg-secondary border border-white/10 rounded-lg shadow-xl p-1.5 z-10 min-w-[140px] animate-fadeIn">
          <p className="text-[10px] text-slate-500 px-2 py-1">Why?</p>
          {FEEDBACK_REASONS.map((reason) => (
            <button
              key={reason.id}
              onClick={() => handleReasonSelect(reason.id)}
              className="block w-full text-left text-xs text-slate-300 hover:bg-white/5
                         px-2 py-1.5 rounded transition-colors"
            >
              {reason.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
