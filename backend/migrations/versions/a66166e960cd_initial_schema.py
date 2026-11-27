"""initial_schema

Revision ID: a66166e960cd
Revises:
Create Date: 2026-11-27 00:00:00.000000

Initial schema covering all 13 approved NIGRAN-360 models:
  users, examinations, questions, choices, exam_questions,
  enrollments, attempts, attempt_answers, results,
  disputes, dispute_audits, exam_events, announcements

NOTE: The Attempt model does not carry a UniqueConstraint(exam_id, candidate_id)
because the attempt retake / concurrency policy has not yet been finalised with
Person 2.  That constraint is tracked as D3 and must be added before the
candidate attempt engine is integrated (Phase 4).
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a66166e960cd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ENUM types ---
    user_role = sa.Enum("administrator", "examiner", "candidate", name="user_role")
    exam_status = sa.Enum("draft", "published", "ongoing", "completed", name="exam_status")
    question_type = sa.Enum("single_mcq", "multi_select", "written", name="question_type")
    difficulty = sa.Enum("easy", "medium", "hard", name="difficulty")
    attempt_status = sa.Enum("in_progress", "submitted", "expired", name="attempt_status")
    dispute_category = sa.Enum(
        "grading_error", "ambiguous_question", "technical_incident", "other",
        name="dispute_category",
    )
    dispute_status = sa.Enum(
        "submitted", "under_review", "resolved", "rejected",
        name="dispute_status",
    )

    # Create ENUMs explicitly so they exist before first use.
    for enum in (user_role, exam_status, question_type, difficulty,
                 attempt_status, dispute_category, dispute_status):
        enum.create(op.get_bind(), checkfirst=True)

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("administrator", "examiner", "candidate", name="user_role",
                                  create_type=False), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- examinations ---
    op.create_table(
        "examinations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Enum("draft", "published", "ongoing", "completed",
                                    name="exam_status", create_type=False), nullable=False,
                  server_default="draft"),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("total_marks", sa.Integer(), nullable=False),
        sa.Column("passing_marks", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("randomize_questions", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("randomize_choices", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_sandbox", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- questions ---
    op.create_table(
        "questions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.Enum("single_mcq", "multi_select", "written",
                                           name="question_type", create_type=False), nullable=False),
        sa.Column("difficulty", sa.Enum("easy", "medium", "hard",
                                        name="difficulty", create_type=False), nullable=False,
                  server_default="medium"),
        sa.Column("category", sa.String(255), nullable=False, server_default="General"),
        sa.Column("marks", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("model_answer", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- choices ---
    op.create_table(
        "choices",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("question_id", sa.String(), sa.ForeignKey("questions.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("choice_text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )

    # --- exam_questions ---
    op.create_table(
        "exam_questions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("exam_id", sa.String(), sa.ForeignKey("examinations.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("question_id", sa.String(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("marks_override", sa.Float(), nullable=True),
        sa.UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),
    )

    # --- enrollments ---
    op.create_table(
        "enrollments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("exam_id", sa.String(), sa.ForeignKey("examinations.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("candidate_id", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("enrolled_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("exam_id", "candidate_id"),
    )

    # --- attempts ---
    # NOTE: No UniqueConstraint(exam_id, candidate_id) — retake policy pending Person 2 (D3).
    op.create_table(
        "attempts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("exam_id", sa.String(), sa.ForeignKey("examinations.id"), nullable=False),
        sa.Column("candidate_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("in_progress", "submitted", "expired",
                                    name="attempt_status", create_type=False), nullable=False,
                  server_default="in_progress"),
        sa.Column("is_sandbox", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("question_order", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )

    # --- attempt_answers ---
    op.create_table(
        "attempt_answers",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("attempt_id", sa.String(), sa.ForeignKey("attempts.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("question_id", sa.String(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("selected_choice_ids", sa.JSON(), nullable=True),
        sa.Column("written_response", sa.Text(), nullable=True),
        sa.Column("is_marked_for_review", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        sa.Column("auto_score", sa.Float(), nullable=True),
        sa.Column("manual_score", sa.Float(), nullable=True),
        sa.Column("grader_note", sa.Text(), nullable=True),
        sa.Column("saved_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- results ---
    op.create_table(
        "results",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("attempt_id", sa.String(), sa.ForeignKey("attempts.id"), nullable=False,
                  unique=True),
        sa.Column("exam_id", sa.String(), sa.ForeignKey("examinations.id"), nullable=False),
        sa.Column("candidate_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("max_score", sa.Float(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_code", sa.String(64), nullable=False, unique=True),
        sa.Column("graded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("graded_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
    )

    # --- disputes ---
    op.create_table(
        "disputes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("attempt_id", sa.String(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("result_id", sa.String(), sa.ForeignKey("results.id"), nullable=False),
        sa.Column("candidate_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.Enum("grading_error", "ambiguous_question",
                                      "technical_incident", "other",
                                      name="dispute_category", create_type=False), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("submitted", "under_review", "resolved", "rejected",
                                    name="dispute_status", create_type=False), nullable=False,
                  server_default="submitted"),
        sa.Column("original_score", sa.Float(), nullable=True),
        sa.Column("revised_score", sa.Float(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )

    # --- dispute_audits ---
    op.create_table(
        "dispute_audits",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("dispute_id", sa.String(), sa.ForeignKey("disputes.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("actor_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- exam_events ---
    op.create_table(
        "exam_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("exam_id", sa.String(), sa.ForeignKey("examinations.id"), nullable=False),
        sa.Column("attempt_id", sa.String(), sa.ForeignKey("attempts.id"), nullable=True),
        sa.Column("candidate_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- announcements ---
    op.create_table(
        "announcements",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("exam_id", sa.String(), sa.ForeignKey("examinations.id"), nullable=False),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    # Drop in reverse dependency order.
    op.drop_table("announcements")
    op.drop_table("exam_events")
    op.drop_table("dispute_audits")
    op.drop_table("disputes")
    op.drop_table("results")
    op.drop_table("attempt_answers")
    op.drop_table("attempts")
    op.drop_table("enrollments")
    op.drop_table("exam_questions")
    op.drop_table("choices")
    op.drop_table("questions")
    op.drop_table("examinations")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # Drop ENUMs.
    for name in ("dispute_status", "dispute_category", "attempt_status",
                 "difficulty", "question_type", "exam_status", "user_role"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
