import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base

QUESTION_TYPES = ("single_mcq", "multi_select", "written")
DIFFICULTIES = ("easy", "medium", "hard")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        PgEnum(*QUESTION_TYPES, name="question_type"), nullable=False
    )
    difficulty: Mapped[str] = mapped_column(
        PgEnum(*DIFFICULTIES, name="difficulty"), nullable=False, default="medium"
    )
    category: Mapped[str] = mapped_column(String(255), nullable=False, default="General")
    marks: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    model_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Choice(Base):
    __tablename__ = "choices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id: Mapped[str] = mapped_column(String, ForeignKey("questions.id", ondelete="CASCADE"))
    choice_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)


class ExamQuestion(Base):
    """Frozen snapshot: links a question to an exam with an order."""
    __tablename__ = "exam_questions"
    __table_args__ = (UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id: Mapped[str] = mapped_column(String, ForeignKey("examinations.id", ondelete="CASCADE"))
    question_id: Mapped[str] = mapped_column(String, ForeignKey("questions.id"))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    marks_override: Mapped[float | None] = mapped_column(Float, nullable=True)
