export default function UrgencyBadge({ score, size = "md" }) {
  const getColor = (s) => {
    if (s >= 70) return { bg: "bg-rose-500/20", text: "text-rose-400", border: "border-rose-500/30", glow: "shadow-rose-500/20", label: "Critical" };
    if (s >= 40) return { bg: "bg-amber-500/20", text: "text-amber-400", border: "border-amber-500/30", glow: "shadow-amber-500/20", label: "Moderate" };
    return { bg: "bg-emerald-500/20", text: "text-emerald-400", border: "border-emerald-500/30", glow: "shadow-emerald-500/20", label: "Low" };
  };

  const color = getColor(score);
  const sizeClasses = size === "lg" ? "text-lg px-4 py-2" : size === "sm" ? "text-xs px-2 py-1" : "text-sm px-3 py-1.5";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold shadow-lg ${color.bg} ${color.text} ${color.border} ${color.glow} ${sizeClasses}`}
    >
      <span className={`w-2 h-2 rounded-full ${score >= 70 ? "bg-rose-400 animate-pulse" : score >= 40 ? "bg-amber-400" : "bg-emerald-400"}`} />
      {score.toFixed(0)}
      <span className="opacity-70 font-normal">• {color.label}</span>
    </span>
  );
}
