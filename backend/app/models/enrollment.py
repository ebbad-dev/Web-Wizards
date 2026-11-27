import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("exam_id", "candidate_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id: Mapped[str] = mapped_column(String, ForeignKey("examinations.id", ondelete="CASCADE"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    enrolled_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
