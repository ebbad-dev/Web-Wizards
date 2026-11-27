"""Unit tests for password hashing service."""
import pytest

from app.services.password import hash_password, needs_rehash, verify_password


def test_hash_returns_argon2_string():
    h = hash_password("SecurePass1!")
    assert h.startswith("$argon2id$")


def test_verify_correct_password():
    h = hash_password("SecurePass1!")
    assert verify_password("SecurePass1!", h) is True


def test_verify_wrong_password():
    h = hash_password("SecurePass1!")
    assert verify_password("WrongPass99!", h) is False


def test_verify_empty_string():
    h = hash_password("SecurePass1!")
    assert verify_password("", h) is False


def test_hash_too_short_raises():
    with pytest.raises(ValueError, match="at least 8"):
        hash_password("short")


def test_needs_rehash_fresh_hash_is_false():
    h = hash_password("SecurePass1!")
    assert needs_rehash(h) is False


def test_two_hashes_differ():
    h1 = hash_password("SecurePass1!")
    h2 = hash_password("SecurePass1!")
    assert h1 != h2
