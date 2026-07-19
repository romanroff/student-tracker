from datetime import datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.bot_service import (
    BotGradebook,
    DuplicateStudent,
    InvalidLessonBatch,
    ResourceNotFound,
    ScoreOutOfRange,
)
from backend.app.db import Base
from backend.app.models import Course, Lesson, LessonRecord, Student, User


@pytest.fixture()
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'bot.db'}")
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def seed_gradebook(session_factory):
    with session_factory() as session:
        owner = User(telegram_id=101, display_name="Teacher")
        stranger = User(telegram_id=202, display_name="Other")
        course = Course(owner=owner, name="Python")
        lesson = Lesson(course=course, title="Lecture 1", held_at=datetime(2026, 7, 20, 10), max_score=10)
        first = Student(course=course, name="Иванов")
        second = Student(course=course, name="Петров")
        session.add_all([owner, stranger, course, lesson, first, second])
        session.commit()
        return course.id, lesson.id, first.id, second.id


def test_bulk_attendance_is_atomic_and_tenant_scoped(session_factory) -> None:
    course_id, lesson_id, first_id, second_id = seed_gradebook(session_factory)
    service = BotGradebook(session_factory)

    service.save_attendance(101, course_id, lesson_id, {first_id: True, second_id: False})

    register = service.get_register(101, course_id, lesson_id)
    assert [(row.student_id, row.present) for row in register.students] == [
        (first_id, True),
        (second_id, False),
    ]
    with pytest.raises(ResourceNotFound):
        service.save_attendance(202, course_id, lesson_id, {first_id: False})


def test_student_management_and_score_validation_are_tenant_scoped(session_factory) -> None:
    course_id, lesson_id, first_id, _ = seed_gradebook(session_factory)
    service = BotGradebook(session_factory)

    added = service.add_student(101, course_id, "Сидоров")
    assert [student.name for student in service.list_students(101, course_id)] == ["Иванов", "Петров", "Сидоров"]
    service.delete_student(101, course_id, added.id)
    assert [student.name for student in service.list_students(101, course_id)] == ["Иванов", "Петров"]

    service.save_score(101, course_id, lesson_id, first_id, 9.5)
    assert service.get_register(101, course_id, lesson_id).students[0].score == 9.5
    with pytest.raises(ScoreOutOfRange):
        service.save_score(101, course_id, lesson_id, first_id, 11)
    with pytest.raises(ResourceNotFound):
        service.add_student(202, course_id, "Нарушитель")

    with Session(session_factory.kw["bind"]) as session:
        records = list(session.scalars(select(LessonRecord).where(LessonRecord.lesson_id == lesson_id)))
        assert len(records) == 1
        assert records[0].student_id == first_id
        assert records[0].score == 9.5


def test_teacher_creates_and_lists_courses_lessons_and_students(session_factory) -> None:
    service = BotGradebook(session_factory)
    user = service.ensure_user(303, "Доцент")
    assert user.telegram_id == 303
    assert service.ensure_user(303, "Профессор").display_name == "Профессор"

    course = service.add_course(303, " Алгоритмы ")
    assert [(item.id, item.name) for item in service.list_courses(303)] == [(course.id, "Алгоритмы")]
    student = service.add_student(303, course.id, " Студент ")
    with pytest.raises(DuplicateStudent):
        service.add_student(303, course.id, "Студент")

    lesson = service.add_lesson(303, course.id, " Лекция 1 ", datetime(2026, 7, 20), 5)
    assert [(item.id, item.title) for item in service.list_lessons(303, course.id)] == [(lesson.id, "Лекция 1")]
    service.save_attendance(303, course.id, lesson.id, {})
    service.save_score(303, course.id, lesson.id, student.id, None)
    row = service.get_register(303, course.id, lesson.id).students[0]
    assert row.present is None
    assert row.score is None

    with pytest.raises(ScoreOutOfRange):
        service.add_lesson(303, course.id, "Invalid", datetime(2026, 7, 20), -1)
    with pytest.raises(ResourceNotFound):
        service.list_courses(999)


def test_multiline_student_import_adds_unique_names_and_skips_duplicates(session_factory) -> None:
    course_id, _, _, _ = seed_gradebook(session_factory)
    service = BotGradebook(session_factory)

    result = service.add_students(
        101,
        course_id,
        [" Сидоров Сидор ", "", "Петров", "Сидоров Сидор", "Кузнецова Анна"],
    )

    assert result.added == 2
    assert result.skipped == 2
    assert [student.name for student in service.list_students(101, course_id)] == [
        "Иванов",
        "Кузнецова Анна",
        "Петров",
        "Сидоров Сидор",
    ]


def test_lesson_batch_preserves_type_and_reports_total_score(session_factory) -> None:
    course_id, _, _, _ = seed_gradebook(session_factory)
    service = BotGradebook(session_factory)

    result = service.add_lessons(
        101,
        course_id,
        [
            "Введение в Python; lecture; 0",
            "Введение в Python; practice; 10",
            "Типы данных; lecture; 0",
            "Типы данных; practice; 10",
            "Управляющие конструкции; lecture; 0",
            "Управляющие конструкции; practice; 10",
            "Функциональное программирование; lecture; 0",
            "Функциональное программирование; practice; 10",
            "Работа с файлами; lecture; 0",
            "Работа с файлами; practice; 10",
            "Основы ООП; lecture; 0",
            "Классы; practice; 10",
            "Генераторы, итераторы; practice; 10",
            "Работа с API; lecture; 0",
            "Работа с API; practice; 10",
            "Итог; practice; 20",
        ],
        held_at=datetime(2026, 9, 1, 9),
    )

    assert result.added == 16
    assert result.skipped == 0
    assert result.total_max_score == 100
    imported = [lesson for lesson in service.list_lessons(101, course_id) if lesson.title != "Lecture 1"]
    assert len(imported) == 16
    assert (imported[0].title, imported[0].kind, imported[0].max_score) == ("Введение в Python", "lecture", 0)
    assert (imported[-1].title, imported[-1].kind, imported[-1].max_score) == ("Итог", "practice", 20)


def test_invalid_lesson_batch_is_atomic_and_identifies_the_line(session_factory) -> None:
    course_id, _, _, _ = seed_gradebook(session_factory)
    service = BotGradebook(session_factory)

    with pytest.raises(InvalidLessonBatch, match="строка 2"):
        service.add_lessons(
            101,
            course_id,
            ["Введение; lecture; 0", "Практика; seminar; 10.5"],
            held_at=datetime(2026, 9, 1, 9),
        )

    assert [lesson.title for lesson in service.list_lessons(101, course_id)] == ["Lecture 1"]


def test_delete_course_cascades_academic_data_and_is_tenant_scoped(session_factory) -> None:
    course_id, lesson_id, first_id, _ = seed_gradebook(session_factory)
    service = BotGradebook(session_factory)
    service.save_attendance(101, course_id, lesson_id, {first_id: True})

    with pytest.raises(ResourceNotFound):
        service.delete_course(202, course_id)
    service.delete_course(101, course_id)

    assert service.list_courses(101) == []
    with Session(session_factory.kw["bind"]) as session:
        assert session.scalar(select(Course).where(Course.id == course_id)) is None
        assert session.scalar(select(Student).where(Student.course_id == course_id)) is None
        assert session.scalar(select(Lesson).where(Lesson.course_id == course_id)) is None
        assert session.scalar(select(LessonRecord).where(LessonRecord.lesson_id == lesson_id)) is None
