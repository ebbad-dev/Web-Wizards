import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchMe,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  type LoginPayload,
  type RegisterPayload,
} from "@/services/auth.service";
import { setAccessToken } from "@/lib/axios";
import { useAuthStore } from "@/stores/auth.store";

export function useAuth() {
  const { user, isAuthenticated, isInitialising, setUser, logout: storeLogout } =
    useAuthStore();
  const navigate = useNavigate();

  const login = useCallback(
    async (payload: LoginPayload) => {
      const data = await apiLogin(payload);
      setUser(data.user);
      return data;
    },
    [setUser]
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      return apiRegister(payload);
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      setAccessToken(null);
      storeLogout();
      navigate("/login", { replace: true });
    }
  }, [storeLogout, navigate]);

  const refreshUser = useCallback(async () => {
    try {
      const me = await fetchMe();
      setUser(me);
    } catch {
      setUser(null);
    }
  }, [setUser]);

  return { user, isAuthenticated, isInitialising, login, register, logout, refreshUser };
}
