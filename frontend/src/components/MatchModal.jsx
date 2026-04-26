export default function MatchModal({ matches, need, onAssign, onClose }) {
  if (!matches) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative w-full max-w-lg glass-card border border-white/15 p-6 animate-bounce-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-all"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <h3 className="text-lg font-bold text-white mb-1">Volunteer Matches</h3>
        <p className="text-sm text-gray-400 mb-5">
          For: <span className="text-gray-300">{need?.raw_text?.slice(0, 60)}...</span>
        </p>

        {/* Matches list */}
        {matches.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-3">😔</div>
            <p className="text-gray-400">No matching volunteers available right now.</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
            {matches.map((match, i) => (
              <div
                key={match.volunteer_id}
                className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/[0.08] transition-all animate-fade-in-up"
                style={{ animationDelay: `${i * 60}ms`, animationFillMode: "both" }}
              >
                {/* Avatar */}
                <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                  {match.name?.charAt(0) || "?"}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white text-sm">{match.name}</div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {match.skills?.map((skill) => (
                      <span key={skill} className="px-1.5 py-0.5 rounded text-[10px] bg-brand-500/10 text-brand-300 border border-brand-500/20">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Score */}
                <div className="flex-shrink-0 text-right">
                  <div className="text-lg font-bold text-white">{match.match_score.toFixed(0)}</div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider">Score</div>
                  {match.distance_km != null && (
                    <div className="text-[10px] text-gray-500 mt-0.5">{match.distance_km.toFixed(1)} km</div>
                  )}
                </div>

                {/* Assign button */}
                <button
                  onClick={() => onAssign && onAssign(match.volunteer_id)}
                  className="flex-shrink-0 btn-success text-xs !px-3 !py-1.5"
                >
                  Assign
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
