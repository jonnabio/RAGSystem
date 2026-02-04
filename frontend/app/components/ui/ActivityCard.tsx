import { Database, FileText, MessageSquare } from "lucide-react";

type ActivityType = "upload" | "query" | "index";

interface ActivityCardProps {
  type: ActivityType;
  title: string;
  description: string;
  time: string;
  onView?: () => void;
}

const activityConfig = {
  upload: {
    icon: FileText,
    iconBg: "bg-blue-500/20",
    iconColor: "text-blue-400",
  },
  query: {
    icon: MessageSquare,
    iconBg: "bg-accent/20",
    iconColor: "text-accent",
  },
  index: {
    icon: Database,
    iconBg: "bg-green-500/20",
    iconColor: "text-green-400",
  },
};

export default function ActivityCard({
  type,
  title,
  description,
  time,
  onView,
}: ActivityCardProps) {
  const config = activityConfig[type];
  const Icon = config.icon;

  return (
    <div
      className="bg-secondary border border-white/5 rounded-xl p-4
                    hover:border-white/10 transition-all duration-200"
    >
      <div className="flex items-start gap-3">
        <div
          className={`w-10 h-10 ${config.iconBg} rounded-lg
                        flex items-center justify-center flex-shrink-0`}
        >
          <Icon className={`w-5 h-5 ${config.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-white text-sm font-medium truncate">{title}</p>
          <p className="text-slate-400 text-xs mt-0.5 truncate">
            {description}
          </p>
          <p className="text-slate-500 text-xs mt-2">{time}</p>
        </div>
        {onView && (
          <button
            onClick={onView}
            className="text-xs px-3 py-1.5 bg-white/5 hover:bg-white/10
                       text-slate-300 rounded-lg transition-colors"
          >
            View
          </button>
        )}
      </div>
    </div>
  );
}
