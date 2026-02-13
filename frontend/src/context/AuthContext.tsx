"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1` : "http://localhost:9010/api/v1";

interface AuthContextType {
  user: User | null;
  apiKey: string | null;
  loading: boolean;
  login: (email: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  apiKey: null,
  loading: true,
  login: async () => false,
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore session
  useEffect(() => {
    const initAuth = async () => {
      const storedKey = localStorage.getItem("c87_api_key");
      if (storedKey) {
        setApiKey(storedKey);
        try {
          const res = await fetch(`${API_BASE}/users/me`, {
            headers: { "X-API-KEY": storedKey }
          });
          if (res.ok) {
            const userData = await res.json();
            setUser(userData);
          } else {
            // Invalid key
            localStorage.removeItem("c87_api_key");
            setApiKey(null);
          }
        } catch (e) {
            console.error(e);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!res.ok) throw new Error("Login failed");

      const data = await res.json();
      // data = { api_key, tier, balance }
      
      const newKey = data.api_key;
      localStorage.setItem("c87_api_key", newKey);
      setApiKey(newKey);
      
      setUser({
        id: "current", // API doesn't return ID in login response, but /me does. Using placeholder.
        email: email,
        tier: data.tier,
        balance: data.balance
      });
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem("c87_api_key");
    setUser(null);
    setApiKey(null);
  };

  return (
    <AuthContext.Provider value={{ user, apiKey, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
