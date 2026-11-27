from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

ALLOWED_ROLES = ("administrator", "examiner", "candidate")


class UserCreate(BaseModel):
    """Admin-only: create examiner or candidate accounts."""
    email: EmailStr
    full_name: str
    password: str
    role: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("full_name must not be empty")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        if v not in ALLOWED_ROLES:
            raise ValueError(f"role must be one of {ALLOWED_ROLES}")
        return v


class UserUpdate(BaseModel):
    """Fields a user (or admin) can update. Role change handled separately."""
    full_name: str | None = None
    email: EmailStr | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip().lower()

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("full_name must not be empty")
        return v


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    items: list[UserPublic]
    total: int
    page: int
    page_size: int
