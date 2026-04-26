import { useState, useEffect, useCallback } from "react";
import api from "../api";
import StatsBar from "../components/StatsBar";
import NeedCard from "../components/NeedCard";
import MatchModal from "../components/MatchModal";
import { useToast } from "../components/Toast";

export default function Dashboard() {
  const [needs, setNeeds] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [matchModal, setMatchModal] = useState(null); // { need, matches }
  const addToast = useToast();

  const fetchData = useCallback(async () => {
    try {
      const [needsRes, statsRes] = await Promise.all([
        api.get("/prioritize"),
        api.get("/stats"),
      ]);
      setNeeds(needsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleFindVolunteer = async (need) => {
    try {
      const res = await api.post("/match", { need_id: need.id });
      setMatchModal({ need, matches: res.data.matches || [] });
    } catch (err) {
      addToast("Failed to find volunteers", "error");
    }
  };

  const handleAssign = async (volunteerId) => {
    if (!matchModal) return;
    try {
      await api.post("/assign", {
        need_id: matchModal.need.id,
        volunteer_id: volunteerId,
      });
      addToast("Volunteer assigned successfully!");
      setMatchModal(null);
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || "Failed to assign volunteer", "error");
    }
  };

  const handleMarkFulfilled = async (need) => {
    try {
      // We need to find the assigned volunteer for this need
      const assignmentsRes = await api.get("/assignments");
      const assignment = assignmentsRes.data.find((a) => a.need_id === need.id);
      if (!assignment) {
        addToast("No active assignment found for this need", "error");
        return;
      }
      await api.post("/verify-impact", {
        need_id: need.id,
        volunteer_id: assignment.volunteer_id,
        notes: "Marked fulfilled from dashboard",
      });
      addToast("Need marked as fulfilled! 🎉");
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || "Failed to mark fulfilled", "error");
    }
  };

  // Separate needs by status
  const activeNeeds = needs.filter((n) => n.status !== "fulfilled");
  const fulfilledNeeds = needs.filter((n) => n.status === "fulfilled");

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      {/* Hero section */}
      <div className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
          Command Center
        </h1>
        <p className="text-gray-400 text-sm sm:text-base">
          Real-time overview of community needs, volunteer assignments, and impact metrics.
        </p>
      </div>

      {/* Stats */}
      <div className="mb-8">
        <StatsBar stats={stats} />
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="skeleton h-40 w-full" />
          ))}
        </div>
      )}

      {/* Active needs */}
      {!loading && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
              Active Needs
              <span className="text-sm font-normal text-gray-500 ml-1">({activeNeeds.length})</span>
            </h2>
            <button
              onClick={fetchData}
              className="btn-secondary text-xs !px-3 !py-1.5 flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
              </svg>
              Refresh
            </button>
          </div>

          {activeNeeds.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <div className="text-5xl mb-4">✨</div>
              <h3 className="text-xl font-semibold text-white mb-2">All Clear!</h3>
              <p className="text-gray-400">No active needs right now. Check back soon or submit a new need.</p>
            </div>
          ) : (
            <div className="space-y-4 mb-10">
              {activeNeeds.map((need, i) => (
                <NeedCard
                  key={need.id}
                  need={need}
                  index={i}
                  onFindVolunteer={handleFindVolunteer}
                  onMarkFulfilled={handleMarkFulfilled}
                />
              ))}
            </div>
          )}

          {/* Fulfilled needs */}
          {fulfilledNeeds.length > 0 && (
            <>
              <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-4 mt-8">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Fulfilled
                <span className="text-sm font-normal text-gray-500 ml-1">({fulfilledNeeds.length})</span>
              </h2>
              <div className="space-y-4 opacity-60">
                {fulfilledNeeds.map((need, i) => (
                  <NeedCard key={need.id} need={need} index={i} />
                ))}
              </div>
            </>
          )}
        </>
      )}

      {/* Match modal */}
      {matchModal && (
        <MatchModal
          matches={matchModal.matches}
          need={matchModal.need}
          onAssign={handleAssign}
          onClose={() => setMatchModal(null)}
        />
      )}
    </div>
  );
}
