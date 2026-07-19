from datetime import datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.bot_report import render_debtors_report, render_student_statistics
from backend.app.bot_service import BotGradebook, ResourceNotFound, ScoreOutOfRange
from backend.app.db import Base
from backend.app.models import Lesson, LessonRecord


@pytest.fixture()
def gradebook(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'analytics.db'}")
    Base.metadata.create_all(engine)
    service = BotGradebook(sessionmaker(engine, expire_on_commit=False))
    service.ensure_user(101, "Teacher")
    service.ensure_user(202, "Other")
    return service, sessionmaker(engine, expire_on_commit=False)


def test_student_markdown_contains_scores_and_explicit_attendance_rate(gradebook) -> None:
    service, _ = gradebook
    course = service.add_course(101, "Python")
    student = service.add_student(101, course.id, "Иванов")
    first = service.add_lesson(101, course.id, "Первая", datetime(2026, 9, 1), 10)
    second = service.add_lesson(101, course.id, "Вторая", datetime(2026, 9, 2), 10)
    service.save_score(101, course.id, first.id, student.id, 8)
    service.save_score(101, course.id, second.id, student.id, 10)
    service.save_attendance(101, course.id, first.id, {student.id: True})
    service.save_attendance(101, course.id, second.id, {student.id: False})

    report = service.get_student_statistics(101, course.id, student.id)
    markdown = render_student_statistics(report)

    assert report.average_score == 9
    assert report.total_score == 18
    assert report.attendance_rate == 50
    assert "**Посещаемость:** 50% (1/2)" in markdown
    assert "| Первая | practice | 8 / 10 | да |" in markdown
    with pytest.raises(ResourceNotFound):
        service.get_student_statistics(202, course.id, student.id)


def test_debtors_report_uses_missing_or_below_pass_score(gradebook) -> None:
    service, _ = gradebook
    course = service.add_course(101, "Python")
    low = service.add_student(101, course.id, "Низкий")
    service.add_student(101, course.id, "Без оценки")
    passed = service.add_student(101, course.id, "Сдал")
    lesson = service.add_lesson(101, course.id, "Контрольная", datetime(2026, 9, 1), 10)
    service.save_score(101, course.id, lesson.id, low.id, 4)
    service.save_score(101, course.id, lesson.id, passed.id, 8)

    report = service.get_debtors(101, course.id, lesson.id, 6)
    markdown = render_debtors_report(report)

    assert [(row.student_name, row.score) for row in report.students] == [("Без оценки", None), ("Низкий", 4)]
    assert "| Без оценки | — |" in markdown
    assert "| Низкий | 4 |" in markdown
    with pytest.raises(ScoreOutOfRange):
        service.get_debtors(101, course.id, lesson.id, 11)


def test_confirmed_lesson_deletion_cascades_records_and_is_tenant_scoped(gradebook) -> None:
    service, factory = gradebook
    course = service.add_course(101, "Python")
    student = service.add_student(101, course.id, "Иванов")
    lesson = service.add_lesson(101, course.id, "Удалить", datetime(2026, 9, 1), 10)
    service.save_score(101, course.id, lesson.id, student.id, 8)

    with pytest.raises(ResourceNotFound):
        service.delete_lesson(202, course.id, lesson.id)
    service.delete_lesson(101, course.id, lesson.id)

    with Session(factory.kw["bind"]) as session:
        assert session.scalar(select(Lesson).where(Lesson.id == lesson.id)) is None
        assert session.scalar(select(LessonRecord).where(LessonRecord.lesson_id == lesson.id)) is None
