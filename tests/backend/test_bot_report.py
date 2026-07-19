from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.bot_report import render_course_summary
from backend.app.bot_service import BotGradebook, ResourceNotFound
from backend.app.db import Base


@pytest.fixture()
def service(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'report.db'}")
    Base.metadata.create_all(engine)
    gradebook = BotGradebook(sessionmaker(engine, expire_on_commit=False))
    gradebook.ensure_user(101, "Teacher")
    gradebook.ensure_user(202, "Other")
    return gradebook


def test_markdown_summary_contains_lessons_averages_totals_and_maximums(service: BotGradebook) -> None:
    course = service.add_course(101, "Python | 1")
    first = service.add_student(101, course.id, "Иванов | Иван")
    second = service.add_student(101, course.id, "Петров")
    lecture = service.add_lesson(101, course.id, "Введение", datetime(2026, 9, 1), 0, "lecture")
    practice = service.add_lesson(101, course.id, "Типы | данных", datetime(2026, 9, 2), 10, "practice")
    service.save_score(101, course.id, lecture.id, first.id, 0)
    service.save_score(101, course.id, practice.id, first.id, 8)
    service.save_score(101, course.id, practice.id, second.id, 10)

    markdown = render_course_summary(service.get_course_summary(101, course.id))

    assert "# Сводка по курсу: Python \\| 1" in markdown
    assert "| ФИО | Введение | Типы \\| данных | Ср. балл | Общий балл |" in markdown
    assert "| Максимум | 0 | 10 | — | 10 |" in markdown
    assert "| Иванов \\| Иван | 0 | 8 | 4 | 8 |" in markdown
    assert "| Петров | — | 10 | 10 | 10 |" in markdown

    with pytest.raises(ResourceNotFound):
        service.get_course_summary(202, course.id)
