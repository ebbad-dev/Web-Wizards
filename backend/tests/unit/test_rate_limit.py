"""Unit tests for in-process rate limiter."""

from app.core.rate_limit import check_login_rate_limit, reset_rate_limit

_IP = "10.0.0.1"
_MAX = 10


def setup_function():
    reset_rate_limit(_IP)


def test_allows_up_to_max_attempts():
    for _ in range(_MAX):
        assert check_login_rate_limit(_IP) is True


def test_blocks_on_eleventh_attempt():
    for _ in range(_MAX):
        check_login_rate_limit(_IP)
    assert check_login_rate_limit(_IP) is False


def test_reset_clears_counter():
    for _ in range(_MAX):
        check_login_rate_limit(_IP)
    reset_rate_limit(_IP)
    assert check_login_rate_limit(_IP) is True


def test_different_ips_are_independent():
    ip2 = "10.0.0.2"
    reset_rate_limit(ip2)
    for _ in range(_MAX):
        check_login_rate_limit(_IP)
    # Exhausted _IP — ip2 must still work
    assert check_login_rate_limit(ip2) is True
    reset_rate_limit(ip2)
