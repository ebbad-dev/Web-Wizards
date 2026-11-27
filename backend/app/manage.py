"""Management commands for NIGRAN-360.

Usage:
    python -m app.manage create-admin
"""
from __future__ import annotations

import asyncio
import getpass
import re
import sys
import uuid

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _prompt(label: str) -> str:
    value = input(f"{label}: ").strip()
    if not value:
        print(f"ERROR: {label} must not be empty.", file=sys.stderr)
        sys.exit(1)
    return value


def _prompt_password() -> str:
    pw = getpass.getpass("Password (input hidden): ")
    if len(pw) < 8:
        print("ERROR: Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)
    confirm = getpass.getpass("Confirm password: ")
    if pw != confirm:
        print("ERROR: Passwords do not match.", file=sys.stderr)
        sys.exit(1)
    return pw


async def _create_admin(email: str, full_name: str, password: str) -> None:
    from sqlalchemy import select

    import app.models  # noqa: F401 — registers all models
    from app.database.session import AsyncSessionLocal
    from app.models.user import User
    from app.services.password import hash_password

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        if result.scalar_one_or_none() is not None:
            print(f"ERROR: An account with email '{email}' already exists.", file=sys.stderr)
            sys.exit(1)

        # Count existing admins as a safety check.
        from sqlalchemy import func
        count_res = await db.execute(
            select(func.count()).where(User.role == "administrator")
        )
        existing_count = count_res.scalar_one()
        if existing_count > 0:
            answer = input(
                f"WARNING: {existing_count} administrator(s) already exist. "
                "Create another? [y/N]: "
            ).strip().lower()
            if answer != "y":
                print("Aborted.", file=sys.stderr)
                sys.exit(0)

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role="administrator",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        # Print only the user ID and email — never the password or hash.
        print(f"Administrator created: id={user.id}  email={user.email}")


def cmd_create_admin() -> None:
    print("=== NIGRAN-360 — Create Administrator ===")
    email = _prompt("Email").lower()
    if not EMAIL_RE.match(email):
        print("ERROR: Invalid email address.", file=sys.stderr)
        sys.exit(1)
    full_name = _prompt("Full name")
    password = _prompt_password()
    asyncio.run(_create_admin(email, full_name, password))


COMMANDS = {
    "create-admin": cmd_create_admin,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python -m app.manage <command>", file=sys.stderr)
        print(f"Available commands: {', '.join(COMMANDS)}", file=sys.stderr)
        sys.exit(1)
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
