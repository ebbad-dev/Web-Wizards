"""Simple in-process sliding-window rate limiter for login attempts.

LIMITATION: state is per-process. Multi-worker deployments will have
independent windows per worker. For competition/single-worker use this
is sufficient. A Redis-backed implementation would be needed for
multi-worker deployments.
"""
from __future__ import annotations

import threading
import time
from collections import deque

_MAX_ATTEMPTS = 10
_WINDOW_SECONDS = 15 * 60  # 15 minutes

_lock = threading.Lock()
_windows: dict[str, deque[float]] = {}


def _safe_ip(ip: str | None) -> str:
    """Return a safe IP key. Never trust X-Forwarded-For blindly."""
    if not ip:
        return "unknown"
    # Accept only the direct connection IP; ignore forwarded headers.
    return ip.split(",")[0].strip()[:45]


def check_login_rate_limit(ip: str | None) -> bool:
    """Return True if the IP is within rate-limit bounds.
    Call BEFORE processing login credentials.
    """
    key = _safe_ip(ip)
    now = time.monotonic()
    cutoff = now - _WINDOW_SECONDS

    with _lock:
        if key not in _windows:
            _windows[key] = deque()
        window = _windows[key]

        # Remove timestamps outside the window.
        while window and window[0] < cutoff:
            window.popleft()

        if len(window) >= _MAX_ATTEMPTS:
            return False

        window.append(now)
        return True


def reset_rate_limit(ip: str | None) -> None:
    """Clear the rate-limit window for an IP. Use in tests only."""
    key = _safe_ip(ip)
    with _lock:
        _windows.pop(key, None)
