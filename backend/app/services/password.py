from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

MIN_LENGTH = 8


def hash_password(plaintext: str) -> str:
    """Return an Argon2id hash of *plaintext*. Never log the return value."""
    if len(plaintext) < MIN_LENGTH:
        raise ValueError(f"Password must be at least {MIN_LENGTH} characters")
    return _ph.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Return True when *plaintext* matches *hashed*. Never raise on mismatch."""
    try:
        return _ph.verify(hashed, plaintext)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(hashed: str) -> bool:
    """Return True if the stored hash should be upgraded to current parameters."""
    return _ph.check_needs_rehash(hashed)
