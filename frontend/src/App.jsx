import { BrowserRouter, Routes, Route, NavLink, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import SubmitNeed from "./pages/SubmitNeed.jsx";
import VolunteerReg from "./pages/VolunteerReg.jsx";
import Admin from "./pages/Admin.jsx";
import AdminLogin from "./pages/AdminLogin.jsx";
import AdminRegister from "./pages/AdminRegister.jsx";
import { ToastProvider } from "./components/Toast.jsx";
import { AuthProvider, useAuth } from "./components/AuthContext.jsx";
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
  { to: "/admin", label: "Admin", icon: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )},
];

/* Protected route wrapper — redirects to login if not authenticated */
function ProtectedAdmin() {
  const { admin, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-500/30 border-t-brand-400 rounded-full animate-spin" />
      </div>
    );
  }

  if (!admin) return <Navigate to="/admin/login" replace />;
  return <Admin />;
}

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <ToastProvider>
      <AuthProvider>
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
                <Route path="/admin" element={<ProtectedAdmin />} />
                <Route path="/admin/login" element={<AdminLogin />} />
                <Route path="/admin/register" element={<AdminRegister />} />
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
      </AuthProvider>
    </ToastProvider>
  );
}
