import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Result(Base):
    __tablename__ = "results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id: Mapped[str] = mapped_column(String, ForeignKey("attempts.id"), unique=True)
    exam_id: Mapped[str] = mapped_column(String, ForeignKey("examinations.id"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False,
                                                     default=lambda: str(uuid.uuid4()).replace("-", ""))
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    graded_by: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"), nullable=True)
