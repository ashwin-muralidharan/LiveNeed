import { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "../api";

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("admin_token"));
  const [loading, setLoading] = useState(true);

  // On mount, verify stored token
  useEffect(() => {
    if (!token) { setLoading(false); return; }
    api.get("/auth/me", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => { setAdmin(res.data); })
      .catch(() => { localStorage.removeItem("admin_token"); setToken(null); })
      .finally(() => setLoading(false));
  }, [token]);

  const login = useCallback(async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    const { token: t, ...adminData } = res.data;
    localStorage.setItem("admin_token", t);
    setToken(t);
    setAdmin(adminData);
    return adminData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("admin_token");
    setToken(null);
    setAdmin(null);
  }, []);

  // Helper: get auth headers
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  return (
    <AuthContext.Provider value={{ admin, token, loading, login, logout, authHeaders }}>
      {children}
    </AuthContext.Provider>
  );
}
