/**
 * Auth store — Zustand.
 *
 * Access token lives in src/lib/axios.ts (module closure).
 * This store holds user identity and loading state only.
 * Nothing is persisted to localStorage or sessionStorage.
 */
import { create } from "zustand";

export type UserRole = "administrator" | "examiner" | "candidate";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isInitialising: boolean;
  setUser: (user: AuthUser | null) => void;
  setInitialising: (value: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  isAuthenticated: false,
  isInitialising: true,

  setUser: (user) =>
    set({ user, isAuthenticated: user !== null }),

  setInitialising: (value) =>
    set({ isInitialising: value }),

  logout: () =>
    set({ user: null, isAuthenticated: false }),
}));
