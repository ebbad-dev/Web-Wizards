import api, { setAccessToken } from "@/lib/axios";
import type { AuthUser } from "@/stores/auth.store";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  full_name: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const res = await api.post<LoginResponse>("/auth/login", payload);
  setAccessToken(res.data.access_token);
  return res.data;
}

export async function register(payload: RegisterPayload): Promise<AuthUser> {
  const res = await api.post<AuthUser>("/auth/register", payload);
  return res.data;
}

export async function fetchMe(): Promise<AuthUser> {
  const res = await api.get<AuthUser>("/auth/me");
  return res.data;
}

export async function logout(): Promise<void> {
  const csrf = _getCsrfCookie();
  await api.post(
    "/auth/logout",
    {},
    { headers: csrf ? { "X-CSRF-Token": csrf } : {} }
  );
  setAccessToken(null);
}

/** Restore session on page reload via HttpOnly refresh cookie. */
export async function restoreSession(): Promise<string | null> {
  try {
    const csrf = _getCsrfCookie();
    const res = await api.post<{ access_token: string }>(
      "/auth/refresh",
      {},
      {
        withCredentials: true,
        headers: csrf ? { "X-CSRF-Token": csrf } : {},
      }
    );
    const token = res.data.access_token;
    setAccessToken(token);
    return token;
  } catch {
    return null;
  }
}

function _getCsrfCookie(): string | undefined {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrf_token="))
    ?.split("=")[1];
}
