import { useState } from "react";
import api from "../api";
import { useToast } from "../components/Toast";

const SKILL_OPTIONS = ["medical", "logistics", "counseling", "education", "construction", "general"];

const SKILL_ICONS = {
  medical: "🏥", logistics: "📦", counseling: "💬",
  education: "📚", construction: "🔨", general: "⚡",
};

export default function VolunteerReg() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [skills, setSkills] = useState([]);
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(null);
  const addToast = useToast();

  const toggleSkill = (skill) => {
    setSkills((prev) => prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]);
  };

  const useMyLocation = () => {
    if (!navigator.geolocation) { addToast("Geolocation not supported", "error"); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => { setLat(pos.coords.latitude.toFixed(4)); setLon(pos.coords.longitude.toFixed(4)); addToast("Location captured!"); },
      () => addToast("Could not get location", "error")
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || skills.length === 0) {
      addToast("Please fill in name, email, and select at least one skill", "error"); return;
    }
    setSubmitting(true);
    try {
      const res = await api.post("/register-volunteer", {
        name: name.trim(), email: email.trim(), role: "volunteer",
        skills: skills.join(","),
        latitude: lat ? parseFloat(lat) : null,
        longitude: lon ? parseFloat(lon) : null,
      });
      setSuccess(res.data);
      addToast("Registration successful! 🎉");
    } catch (err) {
      addToast(err.response?.data?.detail || "Registration failed", "error");
    } finally { setSubmitting(false); }
  };

  if (success) {
    return (
      <div className="max-w-lg mx-auto px-4 sm:px-6 py-8 animate-fade-in-up">
        <div className="glass-card p-8 text-center border-l-4 border-l-emerald-500">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Welcome aboard!</h2>
          <p className="text-gray-400 mb-4">You've been registered as a volunteer.</p>
          <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-left mb-6">
            <p className="text-sm text-gray-300"><span className="text-gray-500">Name:</span> {success.name}</p>
            <p className="text-sm text-gray-300 mt-1"><span className="text-gray-500">Email:</span> {success.email}</p>
            <p className="text-sm text-gray-300 mt-1"><span className="text-gray-500">ID:</span> #{success.volunteer_id}</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => { setSuccess(null); setName(""); setEmail(""); setSkills([]); setLat(""); setLon(""); }} className="btn-secondary flex-1">Register Another</button>
            <a href="/" className="btn-primary flex-1 text-center">Dashboard</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Join as Volunteer</h1>
        <p className="text-gray-400 text-sm sm:text-base">Register your skills and location to get matched with community needs.</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="glass-card p-6 space-y-5">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Full Name <span className="text-rose-400">*</span></label>
            <input id="vol-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="John Doe" className="input-field" />
          </div>
          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email <span className="text-rose-400">*</span></label>
            <input id="vol-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="john@example.com" className="input-field" />
          </div>
          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Skills <span className="text-rose-400">*</span></label>
            <div className="flex flex-wrap gap-2">
              {SKILL_OPTIONS.map((skill) => (
                <button key={skill} type="button" onClick={() => toggleSkill(skill)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all duration-200 flex items-center gap-2 ${
                    skills.includes(skill) ? "bg-brand-500/20 border-brand-500/40 text-brand-300 shadow-lg shadow-brand-500/10" : "bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20"
                  }`}>
                  <span>{SKILL_ICONS[skill]}</span>
                  {skill.charAt(0).toUpperCase() + skill.slice(1)}
                </button>
              ))}
            </div>
          </div>
          {/* Location */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-300">Location <span className="text-gray-500">(optional)</span></label>
              <button type="button" onClick={useMyLocation} className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors">
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                Use my location
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input type="number" step="any" value={lat} onChange={(e) => setLat(e.target.value)} placeholder="Latitude" className="input-field" />
              <input type="number" step="any" value={lon} onChange={(e) => setLon(e.target.value)} placeholder="Longitude" className="input-field" />
            </div>
          </div>
        </div>
        <button type="submit" disabled={submitting || !name.trim() || !email.trim() || skills.length === 0}
          className="btn-primary w-full !py-3.5 text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
          {submitting ? (<><svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Registering...</>) : (<><svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM3 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 019.374 21c-2.331 0-4.512-.645-6.374-1.766z" /></svg>Register as Volunteer</>)}
        </button>
      </form>
    </div>
  );
}
