import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  trend?: string;
  trendUp?: boolean;
  icon: LucideIcon;
}

export default function StatCard({
  title,
  value,
  trend,
  trendUp = true,
  icon: Icon,
}: StatCardProps) {
  return (
    <div
      className="bg-gradient-to-br from-[#0f1d32] to-[#0a1628]
                    border border-white/10 rounded-2xl p-6
                    hover:border-accent/30 hover:shadow-lg hover:shadow-accent/5
                    transition-all duration-300"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium uppercase tracking-wide">
            {title}
          </p>
          <h3 className="text-white text-3xl font-bold mt-2">{value}</h3>
          {trend && (
            <p
              className={`text-xs mt-2 flex items-center gap-1 ${
                trendUp ? "text-green-400" : "text-red-400"
              }`}
            >
              <span>{trendUp ? "↑" : "↓"}</span>
              <span>{trend}</span>
            </p>
          )}
        </div>
        <div
          className="w-14 h-14 bg-accent/20 rounded-xl
                        flex items-center justify-center"
        >
          <Icon className="w-7 h-7 text-accent" />
        </div>
      </div>
    </div>
  );
}
