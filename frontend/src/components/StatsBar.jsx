import { useEffect, useState } from "react";

function AnimatedCounter({ value, duration = 1000 }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (value === 0) { setDisplay(0); return; }
    let start = 0;
    const step = value / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [value, duration]);

  return <span>{display}</span>;
}

const STAT_CONFIGS = [
  {
    key: "active_needs",
    label: "Active Needs",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    ),
    gradient: "from-rose-600/20 to-rose-500/10",
    iconBg: "bg-rose-500/20",
    iconColor: "text-rose-400",
    borderColor: "border-rose-500/20",
  },
  {
    key: "fulfilled_needs",
    label: "Fulfilled",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    gradient: "from-emerald-600/20 to-emerald-500/10",
    iconBg: "bg-emerald-500/20",
    iconColor: "text-emerald-400",
    borderColor: "border-emerald-500/20",
  },
  {
    key: "volunteers_registered",
    label: "Volunteers",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
      </svg>
    ),
    gradient: "from-brand-600/20 to-brand-500/10",
    iconBg: "bg-brand-500/20",
    iconColor: "text-brand-400",
    borderColor: "border-brand-500/20",
  },
];

export default function StatsBar({ stats }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {STAT_CONFIGS.map((cfg, i) => (
        <div
          key={cfg.key}
          className={`glass-card stat-glow p-5 bg-gradient-to-br ${cfg.gradient} border ${cfg.borderColor} animate-fade-in-up`}
          style={{ animationDelay: `${i * 100}ms`, animationFillMode: "both" }}
        >
          <div className="flex items-center gap-4">
            <div className={`flex-shrink-0 w-12 h-12 rounded-xl ${cfg.iconBg} flex items-center justify-center ${cfg.iconColor}`}>
              {cfg.icon}
            </div>
            <div>
              <div className="text-3xl font-bold text-white">
                <AnimatedCounter value={stats[cfg.key] || 0} />
              </div>
              <div className="text-sm text-gray-400 font-medium">{cfg.label}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
