from datetime import UTC, datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    courses: Mapped[list["Course"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    owner: Mapped[User] = relationship(back_populates="courses")
    students: Mapped[list["Student"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("course_id", "name", name="uq_student_course_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    course: Mapped[Course] = relationship(back_populates="students")
    records: Mapped[list["LessonRecord"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (CheckConstraint("max_score >= 0", name="ck_lesson_max_score"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(20), default="practice")
    held_at: Mapped[datetime] = mapped_column(DateTime)
    max_score: Mapped[float] = mapped_column(Float, default=10)
    course: Mapped[Course] = relationship(back_populates="lessons")
    records: Mapped[list["LessonRecord"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class LessonRecord(Base):
    __tablename__ = "lesson_records"
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id", name="uq_lesson_student_record"),
        CheckConstraint("score IS NULL OR score >= 0", name="ck_record_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    present: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    lesson: Mapped[Lesson] = relationship(back_populates="records")
    student: Mapped[Student] = relationship(back_populates="records")
