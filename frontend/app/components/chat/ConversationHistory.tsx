"use client";

import { Clock, Plus, Trash2 } from "lucide-react";

interface Conversation {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
}

interface ConversationHistoryProps {
  conversations: Conversation[];
  activeId?: string;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onDelete?: (id: string) => void;
}

export default function ConversationHistory({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
}: ConversationHistoryProps) {
  // Group conversations by date
  const groupByDate = (convos: Conversation[]) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);

    const groups: { [key: string]: Conversation[] } = {
      Today: [],
      Yesterday: [],
      "This Week": [],
      Earlier: [],
    };

    convos.forEach((convo) => {
      const date = new Date(convo.timestamp);
      if (date.toDateString() === today.toDateString()) {
        groups["Today"].push(convo);
      } else if (date.toDateString() === yesterday.toDateString()) {
        groups["Yesterday"].push(convo);
      } else if (date > lastWeek) {
        groups["This Week"].push(convo);
      } else {
        groups["Earlier"].push(convo);
      }
    });

    return groups;
  };

  const groupedConversations = groupByDate(conversations);

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(id);
    }
  };

  return (
    <aside className="w-64 bg-secondary border-r border-white/5 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-white/5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">
            Conversation History
          </h2>
        </div>
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2
                     border border-accent text-accent rounded-lg px-4 py-2
                     hover:bg-accent/10 transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        {Object.entries(groupedConversations).map(
          ([group, convos]) =>
            convos.length > 0 && (
              <div key={group} className="mb-4">
                <p className="text-xs text-slate-500 font-medium px-2 mb-2 uppercase">
                  {group}
                </p>
                <div className="space-y-1">
                  {convos.map((convo) => (
                    <div
                      key={convo.id}
                      onClick={() => onSelect(convo.id)}
                      className={`group w-full text-left px-3 py-2.5 rounded-lg transition-colors cursor-pointer
                        ${
                          activeId === convo.id
                            ? "bg-white/10 text-white"
                            : "text-slate-400 hover:bg-white/5 hover:text-white"
                        }`}
                    >
                      <div className="flex items-start gap-2">
                        <Clock className="w-4 h-4 mt-0.5 flex-shrink-0 opacity-50" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {convo.title}
                          </p>
                          <p className="text-xs text-slate-500 truncate mt-0.5">
                            {convo.preview}
                          </p>
                        </div>
                        {onDelete && (
                          <button
                            onClick={(e) => handleDelete(e, convo.id)}
                            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20
                                       rounded transition-all"
                            title="Delete conversation"
                          >
                            <Trash2 className="w-3 h-3 text-red-400" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ),
        )}

        {conversations.length === 0 && (
          <div className="text-center py-8">
            <p className="text-slate-500 text-sm">No conversations yet</p>
            <p className="text-slate-600 text-xs mt-1">
              Start a new chat to begin
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
