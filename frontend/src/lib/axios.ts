/**
 * Axios instance with in-memory access token storage.
 *
 * Access token lives only in this module's closure — never in localStorage
 * or sessionStorage. On page reload, auth is restored by calling the
 * /auth/refresh endpoint (which reads the HttpOnly refresh cookie).
 */
import axios, { type AxiosRequestConfig } from "axios";

// In-memory token store — not accessible from external scripts.
let _accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  _accessToken = token;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // send HttpOnly refresh + csrf cookies
});

// Attach Bearer token from memory on every request.
api.interceptors.request.use((config) => {
  if (_accessToken) {
    config.headers.Authorization = `Bearer ${_accessToken}`;
  }
  return config;
});

// On 401, attempt one silent refresh then retry the original request.
let _refreshing: Promise<string | null> | null = null;

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original: AxiosRequestConfig & { _retried?: boolean } = err.config;

    if (err.response?.status === 401 && !original._retried) {
      original._retried = true;

      if (!_refreshing) {
        _refreshing = _doRefresh();
      }

      const newToken = await _refreshing;
      _refreshing = null;

      if (newToken) {
        setAccessToken(newToken);
        original.headers = {
          ...original.headers,
          Authorization: `Bearer ${newToken}`,
        };
        return api(original);
      }

      // Refresh failed — clear token and redirect to login.
      setAccessToken(null);
      window.location.href = "/login";
    }

    return Promise.reject(err);
  }
);

async function _doRefresh(): Promise<string | null> {
  try {
    // Read the CSRF cookie set by the server (non-HttpOnly).
    const csrf = _getCsrfCookie();
    const res = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL ?? "/api/v1"}/auth/refresh`,
      {},
      {
        withCredentials: true,
        headers: csrf ? { "X-CSRF-Token": csrf } : {},
      }
    );
    return (res.data as { access_token: string }).access_token ?? null;
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

export default api;
