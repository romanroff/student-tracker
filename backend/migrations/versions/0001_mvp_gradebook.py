"""Create tenant-isolated MVP gradebook tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_mvp_gradebook"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_courses_owner_id", "courses", ["owner_id"])
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.UniqueConstraint("course_id", "name", name="uq_student_course_name"),
    )
    op.create_index("ix_students_course_id", "students", ["course_id"])
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("held_at", sa.DateTime(), nullable=False),
        sa.Column("max_score", sa.Float(), nullable=False),
        sa.CheckConstraint("max_score >= 0", name="ck_lesson_max_score"),
    )
    op.create_index("ix_lessons_course_id", "lessons", ["course_id"])
    op.create_table(
        "lesson_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("present", sa.Boolean(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.CheckConstraint("score IS NULL OR score >= 0", name="ck_record_score"),
        sa.UniqueConstraint("lesson_id", "student_id", name="uq_lesson_student_record"),
    )
    op.create_index("ix_lesson_records_lesson_id", "lesson_records", ["lesson_id"])
    op.create_index("ix_lesson_records_student_id", "lesson_records", ["student_id"])


def downgrade() -> None:
    op.drop_table("lesson_records")
    op.drop_table("lessons")
    op.drop_table("students")
    op.drop_table("courses")
    op.drop_table("users")
