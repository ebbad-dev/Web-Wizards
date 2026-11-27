"""User management endpoints — Administrator CRUD and self-service."""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserList, UserPublic, UserStatusUpdate, UserUpdate
from app.services.password import hash_password

logger = logging.getLogger("nigran360")
router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# GET /users  — Admin only
# ---------------------------------------------------------------------------

@router.get("", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserList:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return UserList(
        items=[UserPublic.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# POST /users  — Admin only
# ---------------------------------------------------------------------------

@router.post("", response_model=UserPublic, status_code=201)
async def create_user(
    body: UserCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    from fastapi import HTTPException

    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=body.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("Admin created user %s with role %s", user.id, user.role)
    return UserPublic.model_validate(user)


# ---------------------------------------------------------------------------
# GET /users/{id}  — Admin or self
# ---------------------------------------------------------------------------

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    from fastapi import HTTPException

    if current_user.role != "administrator" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic.model_validate(user)


# ---------------------------------------------------------------------------
# PATCH /users/{id}  — Admin or self (no role change)
# ---------------------------------------------------------------------------

@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: str,
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    from fastapi import HTTPException

    if current_user.role != "administrator" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.email is not None:
        # Check uniqueness
        dup = await db.execute(select(User).where(User.email == body.email, User.id != user_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = body.email

    await db.commit()
    await db.refresh(user)
    return UserPublic.model_validate(user)


# ---------------------------------------------------------------------------
# PATCH /users/{id}/status  — Admin only
# ---------------------------------------------------------------------------

@router.patch("/{user_id}/status", response_model=UserPublic)
async def update_user_status(
    user_id: str,
    body: UserStatusUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    from fastapi import HTTPException

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent last active administrator from deactivating themselves.
    if not body.is_active and user.id == admin.id and user.role == "administrator":
        count_result = await db.execute(
            select(func.count()).where(User.role == "administrator", User.is_active == True)  # noqa: E712
        )
        active_admins = count_result.scalar_one()
        if active_admins <= 1:
            raise HTTPException(
                status_code=409,
                detail="Cannot deactivate the last active administrator",
            )

    user.is_active = body.is_active
    await db.commit()
    await db.refresh(user)
    logger.info("Admin %s set user %s is_active=%s", admin.id, user.id, body.is_active)
    return UserPublic.model_validate(user)
