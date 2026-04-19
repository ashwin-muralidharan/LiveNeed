import { useState } from "react";
import api from "../api";
import VoiceInput from "../components/VoiceInput";
import UrgencyBadge from "../components/UrgencyBadge";
import { useToast } from "../components/Toast";

const CATEGORY_ICONS = {
  medical: "🏥", food: "🍲", shelter: "🏠",
  safety: "🛡️", education: "📚", other: "📋",
};

export default function SubmitNeed() {
  const [rawText, setRawText] = useState("");
  const [locationHint, setLocationHint] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const addToast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!rawText.trim()) { addToast("Please describe the need", "error"); return; }
    setSubmitting(true);
    setResult(null);
    try {
      const submitRes = await api.post("/submit-need", { raw_text: rawText, location_hint: locationHint || null });
      const needId = submitRes.data.need_id;
      setSubmitting(false);
      setAnalyzing(true);
      const analyzeRes = await api.post("/analyze", { need_id: needId });
      setResult({ needId, ...analyzeRes.data });
      addToast("Need submitted and analyzed!");
    } catch (err) {
      addToast(err.response?.data?.detail || "Failed to submit", "error");
    } finally { setSubmitting(false); setAnalyzing(false); }
  };

  const handleVoice = (t) => { setRawText((p) => (p ? p + " " + t : t)); addToast("Voice captured!"); };
  const handleReset = () => { setRawText(""); setLocationHint(""); setResult(null); };

  if (result) {
    return (
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 animate-fade-in-up">
        <div className="glass-card p-6 border-l-4 border-l-emerald-500 mb-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Need Submitted & Analyzed</h3>
              <p className="text-sm text-gray-400">Need ID: #{result.needId}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-5">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Category</div>
              <div className="text-lg font-semibold text-white flex items-center gap-2">
                <span>{CATEGORY_ICONS[result.category] || "📋"}</span>
                {result.category.charAt(0).toUpperCase() + result.category.slice(1)}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Urgency</div>
              <UrgencyBadge score={result.urgency_score} size="lg" />
            </div>
          </div>
          {result.entities && Object.values(result.entities).some((a) => a?.length > 0) && (
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Extracted Entities</div>
              <div className="flex flex-wrap gap-2">
                {result.entities.location?.map((l, i) => <span key={i} className="px-2 py-1 rounded-lg bg-blue-500/10 text-blue-300 text-xs border border-blue-500/20">📍 {l}</span>)}
                {result.entities.person?.map((p, i) => <span key={i} className="px-2 py-1 rounded-lg bg-purple-500/10 text-purple-300 text-xs border border-purple-500/20">👤 {p}</span>)}
                {result.entities.org?.map((o, i) => <span key={i} className="px-2 py-1 rounded-lg bg-teal-500/10 text-teal-300 text-xs border border-teal-500/20">🏢 {o}</span>)}
              </div>
            </div>
          )}
        </div>
        <div className="flex gap-3">
          <button onClick={handleReset} className="btn-primary flex-1">Submit Another</button>
          <a href="/" className="btn-secondary flex-1 text-center">Dashboard</a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Report a Need</h1>
        <p className="text-gray-400 text-sm sm:text-base">Describe a community need using text or voice. Our AI will analyze, categorize, and prioritize it.</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="glass-card p-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Describe the need <span className="text-rose-400">*</span></label>
          <div className="flex gap-3">
            <textarea id="need-text-input" value={rawText} onChange={(e) => setRawText(e.target.value)} placeholder="e.g., Family of 5 urgently needs food and medical supplies..." rows={5} className="input-field flex-1 resize-none" maxLength={2000} />
            <VoiceInput onTranscript={handleVoice} />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs text-gray-500">Use microphone for voice input</span>
            <span className="text-xs text-gray-500">{rawText.length}/2000</span>
          </div>
          <label className="block text-sm font-medium text-gray-300 mt-5 mb-2">Location <span className="text-gray-500">(optional)</span></label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 0115 0z" /></svg>
            <input id="location-hint-input" type="text" value={locationHint} onChange={(e) => setLocationHint(e.target.value)} placeholder="e.g., Downtown District" className="input-field !pl-10" />
          </div>
        </div>
        <button type="submit" disabled={submitting || analyzing || !rawText.trim()} className="btn-primary w-full !py-3.5 text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
          {(submitting || analyzing) ? (<><svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>{submitting ? "Submitting..." : "AI Analyzing..."}</>) : (<><svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>Submit & Analyze</>)}
        </button>
      </form>
    </div>
  );
}
