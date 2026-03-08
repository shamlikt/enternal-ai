"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { api } from "./api";
import type { User, AuthTokens, AuthState } from "@/types";

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const fetchCurrentUser = useCallback(async (token: string) => {
    try {
      const user = await api.get<User>("/auth/me");
      setState({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
      localStorage.removeItem("access_token");
      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchCurrentUser(token);
    } else {
      setState((s) => ({ ...s, isLoading: false }));
    }
  }, [fetchCurrentUser]);

  const login = useCallback(async (username: string, password: string) => {
    const tokens = await api.postForm<AuthTokens>("/auth/login", {
      username,
      password,
    });
    localStorage.setItem("access_token", tokens.access_token);
    await fetchCurrentUser(tokens.access_token);
  }, [fetchCurrentUser]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
