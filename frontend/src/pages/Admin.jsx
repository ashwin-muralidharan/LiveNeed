import { useState, useEffect, useCallback } from "react";
import api from "../api";
import { useToast } from "../components/Toast";
import { useAuth } from "../components/AuthContext";

const SKILL_OPTIONS = ["medical", "logistics", "counseling", "education", "construction", "general"];
const STATUS_OPTIONS = ["pending", "assigned", "fulfilled"];

const STATUS_COLORS = {
  pending: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  assigned: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  fulfilled: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
};

export default function Admin() {
  const [tab, setTab] = useState("needs");
  const [needs, setNeeds] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [pendingAdmins, setPendingAdmins] = useState([]);
  const [adminList, setAdminList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingStatus, setEditingStatus] = useState(null);
  const [editingVol, setEditingVol] = useState(null);
  const addToast = useToast();
  const { admin, authHeaders, logout } = useAuth();

  const SUPER_ADMIN_EMAILS = ["maneesh@gmail.com", "ashwin@gmail.com"];
  const isSuperAdmin = admin && SUPER_ADMIN_EMAILS.includes(admin.email);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [n, v, p, a] = await Promise.all([
        api.get("/admin/needs", { headers: authHeaders }),
        api.get("/admin/volunteers", { headers: authHeaders }),
        api.get("/auth/pending", { headers: authHeaders }),
        api.get("/auth/admins", { headers: authHeaders }),
      ]);
      setNeeds(n.data);
      setVolunteers(v.data);
      setPendingAdmins(p.data);
      setAdminList(a.data);
    } catch (err) {
      addToast("Failed to load admin data", "error");
    } finally { setLoading(false); }
  }, [addToast, authHeaders]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // --- Need actions ---
  const handleStatusChange = async (needId, newStatus) => {
    try {
      await api.patch(`/admin/needs/${needId}/status`, { status: newStatus }, { headers: authHeaders });
      addToast(`Need #${needId} status updated to ${newStatus}`);
      setEditingStatus(null);
      fetchData();
    } catch (err) { addToast(err.response?.data?.detail || "Failed to update status", "error"); }
  };

  const handleDeleteNeed = async (needId) => {
    if (!window.confirm(`Delete Need #${needId}? This cannot be undone.`)) return;
    try {
      await api.delete(`/admin/needs/${needId}`, { headers: authHeaders });
      addToast(`Need #${needId} deleted`);
      fetchData();
    } catch (err) { addToast("Failed to delete need", "error"); }
  };

  // --- Volunteer actions ---
  const handleToggleActive = async (vol) => {
    try {
      await api.patch(`/admin/volunteers/${vol.id}`, { is_active: !vol.is_active }, { headers: authHeaders });
      addToast(`${vol.name} ${vol.is_active ? "deactivated" : "activated"}`);
      fetchData();
    } catch (err) { addToast("Failed to update volunteer", "error"); }
  };

  const handleDeleteVolunteer = async (vol) => {
    if (!window.confirm(`Remove ${vol.name}? This cannot be undone.`)) return;
    try {
      await api.delete(`/admin/volunteers/${vol.id}`, { headers: authHeaders });
      addToast(`${vol.name} removed`);
      fetchData();
    } catch (err) { addToast("Failed to remove volunteer", "error"); }
  };

  const handleUpdateVolunteer = async (volId, updates) => {
    try {
      await api.patch(`/admin/volunteers/${volId}`, updates, { headers: authHeaders });
      addToast("Volunteer updated");
      setEditingVol(null);
      fetchData();
    } catch (err) { addToast("Failed to update", "error"); }
  };

  // --- Pending admin actions ---
  const handleApproveAdmin = async (adminId, name) => {
    try {
      await api.post(`/auth/approve/${adminId}`, {}, { headers: authHeaders });
      addToast(`${name} approved`);
      fetchData();
    } catch (err) { addToast("Failed to approve", "error"); }
  };

  const handleRejectAdmin = async (adminId, name) => {
    if (!window.confirm(`Reject ${name}'s registration?`)) return;
    try {
      await api.post(`/auth/reject/${adminId}`, {}, { headers: authHeaders });
      addToast(`${name} rejected`);
      fetchData();
    } catch (err) { addToast("Failed to reject", "error"); }
  };

  // --- Admin delete actions ---
  const handleDeleteAdmin = async (targetAdmin) => {
    if (!window.confirm(`Remove admin ${targetAdmin.name} (${targetAdmin.email})? This cannot be undone.`)) return;
    try {
      await api.delete(`/auth/admins/${targetAdmin.id}`, { headers: authHeaders });
      addToast(`${targetAdmin.name} removed from admin list`);
      fetchData();
    } catch (err) { addToast(err.response?.data?.detail || "Failed to delete admin", "error"); }
  };

  const urgencyColor = (s) => s >= 70 ? "text-rose-400" : s >= 40 ? "text-amber-400" : "text-emerald-400";

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      {/* Header with admin info + logout */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-1">Admin Panel</h1>
          <p className="text-gray-400 text-sm">Logged in as <span className="text-brand-300 font-medium">{admin?.email}</span></p>
        </div>
        <button onClick={logout}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-rose-400 hover:border-rose-500/30 hover:bg-rose-500/10 transition-all text-sm w-fit">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
          </svg>
          Logout
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white/5 rounded-xl p-1 border border-white/10 w-fit flex-wrap">
        {[
          { key: "needs", label: "Needs", count: needs.length, icon: "📋" },
          { key: "volunteers", label: "Volunteers", count: volunteers.length, icon: "👥" },
          { key: "approvals", label: "Approvals", count: pendingAdmins.length, icon: "🔐" },
          { key: "admins", label: "Admins", count: adminList.length, icon: "🛡️" },
        ].map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
              tab === t.key
                ? "bg-brand-500/20 text-brand-300 border border-brand-500/30 shadow-lg shadow-brand-500/10"
                : "text-gray-400 hover:text-white hover:bg-white/5"
            }`}>
            <span>{t.icon}</span> {t.label}
            <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${
              t.key === "approvals" && t.count > 0 ? "bg-rose-500/30 text-rose-300" :
              tab === t.key ? "bg-brand-500/30" : "bg-white/10"
            }`}>
              {t.count}
            </span>
          </button>
        ))}
      </div>

      {loading && (
        <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="skeleton h-16 w-full" />)}</div>
      )}

      {/* =================== NEEDS TAB =================== */}
      {!loading && tab === "needs" && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">ID</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Description</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Category</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Urgency</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Status</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Location</th>
                  <th className="text-right py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {needs.map((need) => (
                  <tr key={need.id} className="border-b border-white/5 hover:bg-white/[0.03] transition-colors">
                    <td className="py-3 px-4 text-gray-400 font-mono text-xs">#{need.id}</td>
                    <td className="py-3 px-4 text-gray-200 max-w-xs">
                      <span className="line-clamp-2">{need.raw_text}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-gray-300">
                        {need.category || "—"}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`font-bold ${urgencyColor(need.urgency_score || 0)}`}>
                        {(need.urgency_score || 0).toFixed(0)}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {editingStatus === need.id ? (
                        <div className="flex gap-1">
                          {STATUS_OPTIONS.map((s) => (
                            <button key={s} onClick={() => handleStatusChange(need.id, s)}
                              className={`px-2 py-1 rounded text-xs border transition-all ${
                                s === need.status
                                  ? STATUS_COLORS[s] + " font-bold"
                                  : "bg-white/5 border-white/10 text-gray-400 hover:bg-white/10"
                              }`}>
                              {s}
                            </button>
                          ))}
                          <button onClick={() => setEditingStatus(null)} className="px-2 py-1 text-xs text-gray-500 hover:text-white">
                            ✕
                          </button>
                        </div>
                      ) : (
                        <button onClick={() => setEditingStatus(need.id)}
                          className={`px-2.5 py-1 rounded-lg border text-xs font-medium ${STATUS_COLORS[need.status] || STATUS_COLORS.pending}`}>
                          {need.status}
                        </button>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs max-w-[120px] truncate">
                      {need.location_hint || "—"}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button onClick={() => handleDeleteNeed(need.id)}
                        className="p-1.5 rounded-lg hover:bg-rose-500/20 text-gray-500 hover:text-rose-400 transition-all"
                        title="Delete need">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {needs.length === 0 && (
            <div className="py-12 text-center text-gray-500">No needs found.</div>
          )}
        </div>
      )}

      {/* =================== VOLUNTEERS TAB =================== */}
      {!loading && tab === "volunteers" && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">ID</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Name</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Email</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Skills</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Location</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Status</th>
                  <th className="text-right py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {volunteers.map((vol) => (
                  <tr key={vol.id} className={`border-b border-white/5 hover:bg-white/[0.03] transition-colors ${!vol.is_active ? "opacity-50" : ""}`}>
                    <td className="py-3 px-4 text-gray-400 font-mono text-xs">#{vol.id}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                          {vol.name?.charAt(0) || "?"}
                        </div>
                        {editingVol === vol.id ? (
                          <EditVolunteerInline vol={vol} onSave={handleUpdateVolunteer} onCancel={() => setEditingVol(null)} />
                        ) : (
                          <span className="text-white font-medium">{vol.name}</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs">{vol.email}</td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {(vol.skills || "").split(",").filter(Boolean).map((skill) => (
                          <span key={skill} className="px-1.5 py-0.5 rounded text-[10px] bg-brand-500/10 text-brand-300 border border-brand-500/20">
                            {skill.trim()}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs">
                      {vol.latitude && vol.longitude
                        ? `${Number(vol.latitude).toFixed(2)}, ${Number(vol.longitude).toFixed(2)}`
                        : "—"}
                    </td>
                    <td className="py-3 px-4">
                      <button onClick={() => handleToggleActive(vol)}
                        className={`px-2.5 py-1 rounded-lg border text-xs font-medium transition-all ${
                          vol.is_active
                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/30"
                            : "bg-rose-500/20 text-rose-300 border-rose-500/30 hover:bg-rose-500/30"
                        }`}>
                        {vol.is_active ? "Active" : "Inactive"}
                      </button>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => setEditingVol(editingVol === vol.id ? null : vol.id)}
                          className="p-1.5 rounded-lg hover:bg-brand-500/20 text-gray-500 hover:text-brand-400 transition-all"
                          title="Edit volunteer">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                          </svg>
                        </button>
                        <button onClick={() => handleDeleteVolunteer(vol)}
                          className="p-1.5 rounded-lg hover:bg-rose-500/20 text-gray-500 hover:text-rose-400 transition-all"
                          title="Remove volunteer">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {volunteers.length === 0 && (
            <div className="py-12 text-center text-gray-500">No volunteers registered.</div>
          )}
        </div>
      )}

      {/* =================== APPROVALS TAB =================== */}
      {!loading && tab === "approvals" && (
        <div>
          {pendingAdmins.length === 0 ? (
            <div className="glass-card py-12 text-center">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-gray-400">No pending registrations</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingAdmins.map((pa) => (
                <div key={pa.id} className="glass-card p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center">
                      <span className="text-amber-300 font-bold">{pa.name?.charAt(0)}</span>
                    </div>
                    <div>
                      <p className="text-white font-medium">{pa.name}</p>
                      <p className="text-gray-400 text-xs">{pa.email}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleApproveAdmin(pa.id, pa.name)}
                      className="px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 text-xs font-medium transition-all flex items-center gap-1.5">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                      </svg>
                      Approve
                    </button>
                    <button onClick={() => handleRejectAdmin(pa.id, pa.name)}
                      className="px-4 py-2 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 text-xs font-medium transition-all flex items-center gap-1.5">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =================== ADMINS TAB =================== */}
      {!loading && tab === "admins" && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">ID</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Admin</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Email</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Role</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Joined</th>
                  {isSuperAdmin && (
                    <th className="text-right py-3 px-4 text-gray-500 font-medium text-xs uppercase tracking-wider">Actions</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {adminList.map((a) => (
                  <tr key={a.id} className={`border-b border-white/5 hover:bg-white/[0.03] transition-colors ${a.id === admin?.admin_id ? "bg-brand-500/[0.05]" : ""}`}>
                    <td className="py-3 px-4 text-gray-400 font-mono text-xs">#{a.id}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-xs flex-shrink-0 ${
                          a.is_super
                            ? "bg-gradient-to-br from-amber-500 to-orange-600"
                            : "bg-gradient-to-br from-brand-500 to-purple-600"
                        }`}>
                          {a.name?.charAt(0) || "?"}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-white font-medium">{a.name}</span>
                          {a.id === admin?.admin_id && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-brand-500/20 text-brand-300 border border-brand-500/20">You</span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs">{a.email}</td>
                    <td className="py-3 px-4">
                      {a.is_super ? (
                        <span className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-medium">
                          ⭐ Super Admin
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-gray-300 text-xs font-medium">
                          Admin
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs">
                      {a.created_at ? new Date(a.created_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }) : "—"}
                    </td>
                    {isSuperAdmin && (
                      <td className="py-3 px-4 text-right">
                        {!a.is_super && a.id !== admin?.admin_id ? (
                          <button onClick={() => handleDeleteAdmin(a)}
                            className="p-1.5 rounded-lg hover:bg-rose-500/20 text-gray-500 hover:text-rose-400 transition-all"
                            title={`Remove ${a.name}`}>
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                            </svg>
                          </button>
                        ) : (
                          <span className="text-gray-600 text-xs">—</span>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {adminList.length === 0 && (
            <div className="py-12 text-center text-gray-500">No admins found.</div>
          )}
        </div>
      )}
    </div>
  );
}


function EditVolunteerInline({ vol, onSave, onCancel }) {
  const [name, setName] = useState(vol.name);
  const [skills, setSkills] = useState((vol.skills || "").split(",").map((s) => s.trim()).filter(Boolean));

  const toggleSkill = (skill) => {
    setSkills((prev) => prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]);
  };

  const handleSave = () => {
    onSave(vol.id, { name, skills: skills.join(",") });
  };

  return (
    <div className="flex flex-col gap-2 min-w-[200px]">
      <input type="text" value={name} onChange={(e) => setName(e.target.value)}
        className="input-field !py-1.5 !px-2 text-sm" placeholder="Name" />
      <div className="flex flex-wrap gap-1">
        {SKILL_OPTIONS.map((skill) => (
          <button key={skill} type="button" onClick={() => toggleSkill(skill)}
            className={`px-2 py-0.5 rounded text-[10px] border transition-all ${
              skills.includes(skill) ? "bg-brand-500/20 border-brand-500/40 text-brand-300" : "bg-white/5 border-white/10 text-gray-500"
            }`}>
            {skill}
          </button>
        ))}
      </div>
      <div className="flex gap-1">
        <button onClick={handleSave} className="px-2 py-1 rounded text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30">
          Save
        </button>
        <button onClick={onCancel} className="px-2 py-1 rounded text-xs text-gray-500 hover:text-white">
          Cancel
        </button>
      </div>
    </div>
  );
}
