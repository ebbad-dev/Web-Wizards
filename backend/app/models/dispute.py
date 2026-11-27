import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base

DISPUTE_STATUSES = ("submitted", "under_review", "resolved", "rejected")
DISPUTE_CATEGORIES = ("grading_error", "ambiguous_question", "technical_incident", "other")


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id: Mapped[str] = mapped_column(String, ForeignKey("attempts.id"))
    result_id: Mapped[str] = mapped_column(String, ForeignKey("results.id"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(
        PgEnum(*DISPUTE_CATEGORIES, name="dispute_category"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        PgEnum(*DISPUTE_STATUSES, name="dispute_status"), nullable=False, default="submitted"
    )
    original_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    revised_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class DisputeAudit(Base):
    __tablename__ = "dispute_audits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dispute_id: Mapped[str] = mapped_column(String, ForeignKey("disputes.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
