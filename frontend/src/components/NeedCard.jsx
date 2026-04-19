import { useState } from "react";
import UrgencyBadge from "./UrgencyBadge";

const CATEGORY_CONFIG = {
  medical: { icon: "🏥", color: "bg-rose-500/20 text-rose-300 border-rose-500/30" },
  food: { icon: "🍲", color: "bg-amber-500/20 text-amber-300 border-amber-500/30" },
  shelter: { icon: "🏠", color: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
  safety: { icon: "🛡️", color: "bg-red-500/20 text-red-300 border-red-500/30" },
  education: { icon: "📚", color: "bg-purple-500/20 text-purple-300 border-purple-500/30" },
  other: { icon: "📋", color: "bg-gray-500/20 text-gray-300 border-gray-500/30" },
};

const STATUS_CONFIG = {
  pending: { label: "Pending", color: "bg-amber-500/20 text-amber-300 border-amber-500/30" },
  assigned: { label: "Assigned", color: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
  fulfilled: { label: "Fulfilled", color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
};

export default function NeedCard({ need, onFindVolunteer, onMarkFulfilled, index = 0 }) {
  const [expanded, setExpanded] = useState(false);
  const catCfg = CATEGORY_CONFIG[need.category] || CATEGORY_CONFIG.other;
  const statusCfg = STATUS_CONFIG[need.status] || STATUS_CONFIG.pending;

  const urgencyBorderColor =
    need.urgency_score >= 70 ? "border-l-rose-500" : need.urgency_score >= 40 ? "border-l-amber-500" : "border-l-emerald-500";

  const entities = typeof need.entities === "string" ? JSON.parse(need.entities || "{}") : need.entities || {};
  const hasEntities = Object.values(entities).some((arr) => arr && arr.length > 0);

  return (
    <div
      className={`glass-card border-l-4 ${urgencyBorderColor} overflow-hidden animate-fade-in-up`}
      style={{ animationDelay: `${index * 80}ms`, animationFillMode: "both" }}
    >
      <div className="p-5">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border text-xs font-medium ${catCfg.color}`}>
              <span>{catCfg.icon}</span>
              {need.category.charAt(0).toUpperCase() + need.category.slice(1)}
            </span>
            <span className={`inline-flex items-center px-2.5 py-1 rounded-lg border text-xs font-medium ${statusCfg.color}`}>
              {statusCfg.label}
            </span>
          </div>
          <UrgencyBadge score={need.urgency_score} size="sm" />
        </div>

        {/* Need text */}
        <p className="text-gray-200 leading-relaxed mb-3 text-sm">
          {expanded ? need.raw_text : need.raw_text.slice(0, 150)}
          {need.raw_text.length > 150 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="ml-1 text-brand-400 hover:text-brand-300 font-medium transition-colors"
            >
              {expanded ? "Show less" : "...Read more"}
            </button>
          )}
        </p>

        {/* Location hint */}
        {need.location_hint && (
          <div className="flex items-center gap-1.5 text-xs text-gray-400 mb-3">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 0115 0z" />
            </svg>
            {need.location_hint}
          </div>
        )}

        {/* Entities (expandable) */}
        {hasEntities && expanded && (
          <div className="flex flex-wrap gap-2 mb-3">
            {entities.location?.map((loc, i) => (
              <span key={`loc-${i}`} className="px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-300 text-xs border border-blue-500/20">
                📍 {loc}
              </span>
            ))}
            {entities.person?.map((p, i) => (
              <span key={`per-${i}`} className="px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-300 text-xs border border-purple-500/20">
                👤 {p}
              </span>
            ))}
            {entities.org?.map((o, i) => (
              <span key={`org-${i}`} className="px-2 py-0.5 rounded-md bg-teal-500/10 text-teal-300 text-xs border border-teal-500/20">
                🏢 {o}
              </span>
            ))}
          </div>
        )}

        {/* Urgency bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span>Urgency</span>
            <span>{need.urgency_score.toFixed(0)}/100</span>
          </div>
          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full urgency-bar transition-all duration-1000 ease-out"
              style={{ width: `${Math.min(need.urgency_score, 100)}%` }}
            />
          </div>
        </div>

        {/* Actions */}
        {need.status !== "fulfilled" && (
          <div className="flex gap-2 flex-wrap">
            {need.status === "pending" && (
              <button
                onClick={() => onFindVolunteer && onFindVolunteer(need)}
                className="btn-primary text-xs !px-4 !py-2"
              >
                <span className="flex items-center gap-1.5">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                  </svg>
                  Find Volunteer
                </span>
              </button>
            )}
            {need.status === "assigned" && (
              <button
                onClick={() => onMarkFulfilled && onMarkFulfilled(need)}
                className="btn-success text-xs !px-4 !py-2"
              >
                <span className="flex items-center gap-1.5">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  Mark Fulfilled
                </span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
