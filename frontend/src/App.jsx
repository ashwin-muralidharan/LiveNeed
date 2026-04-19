import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import SubmitNeed from "./pages/SubmitNeed.jsx";
import VolunteerReg from "./pages/VolunteerReg.jsx";
import { ToastProvider } from "./components/Toast.jsx";
import { useState } from "react";

const NAV_LINKS = [
  { to: "/", label: "Dashboard", icon: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
    </svg>
  )},
  { to: "/submit", label: "Report Need", icon: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
  )},
  { to: "/volunteer", label: "Volunteer", icon: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM3 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 019.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
    </svg>
  )},
];

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <ToastProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          {/* Navigation */}
          <nav className="sticky top-0 z-40 border-b border-white/10 bg-gray-950/80 backdrop-blur-xl">
            <div className="max-w-6xl mx-auto px-4 sm:px-6">
              <div className="flex items-center justify-between h-16">
                {/* Logo */}
                <NavLink to="/" className="flex items-center gap-2.5 group">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center shadow-lg shadow-brand-500/25 group-hover:shadow-brand-500/40 transition-shadow">
                    <span className="text-white font-bold text-sm">LN</span>
                  </div>
                  <span className="text-lg font-bold text-white tracking-tight">
                    Live<span className="text-brand-400">Need</span>
                  </span>
                </NavLink>

                {/* Desktop nav */}
                <div className="hidden sm:flex items-center gap-1">
                  {NAV_LINKS.map((link) => (
                    <NavLink
                      key={link.to}
                      to={link.to}
                      end={link.to === "/"}
                      className={({ isActive }) =>
                        `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                          isActive
                            ? "bg-brand-500/15 text-brand-300 border border-brand-500/25"
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        }`
                      }
                    >
                      {link.icon}
                      {link.label}
                    </NavLink>
                  ))}
                </div>

                {/* Mobile menu button */}
                <button
                  onClick={() => setMobileOpen(!mobileOpen)}
                  className="sm:hidden w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    {mobileOpen ? (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                    )}
                  </svg>
                </button>
              </div>

              {/* Mobile nav */}
              {mobileOpen && (
                <div className="sm:hidden pb-4 space-y-1 animate-fade-in">
                  {NAV_LINKS.map((link) => (
                    <NavLink
                      key={link.to}
                      to={link.to}
                      end={link.to === "/"}
                      onClick={() => setMobileOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                          isActive
                            ? "bg-brand-500/15 text-brand-300 border border-brand-500/25"
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        }`
                      }
                    >
                      {link.icon}
                      {link.label}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          </nav>

          {/* Main content */}
          <main>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/submit" element={<SubmitNeed />} />
              <Route path="/volunteer" element={<VolunteerReg />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="border-t border-white/5 mt-16 py-6">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center">
              <p className="text-xs text-gray-600">
                LiveNeed — AI-Powered Community Resource Platform • Built for Google Hackathon
              </p>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </ToastProvider>
  );
}
