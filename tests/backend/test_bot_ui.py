from datetime import datetime

from backend.app.bot_ui import (
    PAGE_SIZE,
    AttendanceDraft,
    attendance_menu,
    course_menu,
    courses_menu,
    delete_course_confirmation,
    delete_student_confirmation,
    lesson_menu,
    lessons_menu,
    main_menu,
    scores_menu,
    students_menu,
)
from backend.app.models import Course, Lesson, Student
from backend.app.schemas import LessonOut, RecordOut, RegisterOut


def register(student_count: int) -> RegisterOut:
    return RegisterOut(
        lesson=LessonOut(id=7, title="Lecture 1", kind="lecture", held_at=datetime(2026, 7, 20), max_score=10),
        students=[
            RecordOut(student_id=index, student_name=f"Student {index}", present=index % 2 == 0, score=None)
            for index in range(1, student_count + 1)
        ],
    )


def test_attendance_draft_toggles_without_mutating_previous_state() -> None:
    original = AttendanceDraft(course_id=3, lesson_id=7, values={1: False, 2: True})
    changed = original.toggle(1)

    assert original.values == {1: False, 2: True}
    assert changed.values == {1: True, 2: True}
    assert changed.set_all(False).values == {1: False, 2: False}


def test_attendance_keyboard_is_paginated_and_callback_data_is_bounded() -> None:
    lesson_register = register(PAGE_SIZE + 1)
    draft = AttendanceDraft(3, 7, {row.student_id: row.present is True for row in lesson_register.students})

    keyboard = attendance_menu(draft, lesson_register, page=0)
    callbacks = [button.callback_data for row in keyboard.inline_keyboard for button in row if button.callback_data]

    assert callbacks[0] == "attendance_toggle:3:7:1:0"
    assert any(value == "attendance:3:7:1" for value in callbacks)
    assert any(value == "attendance_save:3:7" for value in callbacks)
    assert all(len(value.encode()) <= 64 for value in callbacks)


def test_main_menu_does_not_require_a_mini_app_url() -> None:
    keyboard = main_menu()
    assert keyboard.inline_keyboard[0][0].callback_data == "courses"
    assert all(button.web_app is None for row in keyboard.inline_keyboard for button in row)


def test_navigation_menus_expose_gradebook_actions() -> None:
    course = Course(id=3, owner_id=1, name="Python")
    student = Student(id=4, course_id=3, name="Иванов")
    lesson = Lesson(id=7, course_id=3, title="Lecture 1", held_at=datetime(2026, 7, 20), max_score=10)

    assert courses_menu([course]).inline_keyboard[0][0].callback_data == "course:3"
    course_callbacks = [button.callback_data for row in course_menu(3).inline_keyboard for button in row]
    assert course_callbacks == ["students:3", "lessons:3", "course_report:3", "course_del:3", "courses"]
    assert delete_course_confirmation(3).inline_keyboard[0][0].callback_data == "course_del_confirm:3"
    assert students_menu(3, [student]).inline_keyboard[0][0].callback_data == "student_report:3:4"
    assert students_menu(3, [student]).inline_keyboard[0][1].callback_data == "student_del:3:4"
    assert delete_student_confirmation(3, 4).inline_keyboard[0][0].callback_data == "student_del_confirm:3:4"
    assert lessons_menu(3, [lesson]).inline_keyboard[0][0].callback_data == "lesson:3:7"
    assert lesson_menu(3, 7).inline_keyboard[0][0].callback_data == "attendance:3:7:0"
    lesson_callbacks = [button.callback_data for row in lesson_menu(3, 7).inline_keyboard for button in row]
    assert "debtors:3:7" in lesson_callbacks
    assert "lesson_del:3:7" in lesson_callbacks


def test_score_keyboard_paginates_and_displays_existing_scores() -> None:
    lesson_register = register(PAGE_SIZE + 1)
    lesson_register.students[0].score = 8.5

    first_page = scores_menu(3, 7, lesson_register, 0)
    second_page = scores_menu(3, 7, lesson_register, 1)

    assert first_page.inline_keyboard[0][0].text.endswith("8.5")
    assert any(button.callback_data == "scores:3:7:1" for row in first_page.inline_keyboard for button in row)
    assert any(button.callback_data == "scores:3:7:0" for row in second_page.inline_keyboard for button in row)


def test_main_menu_includes_optional_mini_app_button() -> None:
    keyboard = main_menu("https://example.test")
    assert keyboard.inline_keyboard[1][0].web_app is not None
