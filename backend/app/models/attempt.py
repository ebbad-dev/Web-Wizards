import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as PgEnum, Boolean, Float, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base

ATTEMPT_STATUSES = ("in_progress", "submitted", "expired")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id: Mapped[str] = mapped_column(String, ForeignKey("examinations.id"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        PgEnum(*ATTEMPT_STATUSES, name="attempt_status"), nullable=False, default="in_progress"
    )
    is_sandbox: Mapped[bool] = mapped_column(Boolean, default=False)
    question_order: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id: Mapped[str] = mapped_column(String, ForeignKey("attempts.id", ondelete="CASCADE"))
    question_id: Mapped[str] = mapped_column(String, ForeignKey("questions.id"))
    selected_choice_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    written_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_marked_for_review: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    manual_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    grader_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
