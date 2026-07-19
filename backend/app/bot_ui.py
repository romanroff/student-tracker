from dataclasses import dataclass

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from backend.app.models import Course, Lesson, Student
from backend.app.schemas import RegisterOut

PAGE_SIZE = 8


@dataclass(frozen=True)
class AttendanceDraft:
    course_id: int
    lesson_id: int
    values: dict[int, bool]

    def toggle(self, student_id: int) -> "AttendanceDraft":
        if student_id not in self.values:
            return self
        values = dict(self.values)
        values[student_id] = not values[student_id]
        return AttendanceDraft(self.course_id, self.lesson_id, values)

    def set_all(self, present: bool) -> "AttendanceDraft":
        return AttendanceDraft(self.course_id, self.lesson_id, dict.fromkeys(self.values, present))


def main_menu(webapp_url: str | None = None) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton("📚 Мои курсы", callback_data="courses")]]
    if webapp_url:
        rows.append([InlineKeyboardButton("🌐 Открыть Mini App", web_app=WebAppInfo(webapp_url))])
    return InlineKeyboardMarkup(rows)


def courses_menu(courses: list[Course]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(course.name, callback_data=f"course:{course.id}")] for course in courses]
    rows.extend(
        [
            [InlineKeyboardButton("➕ Добавить курс", callback_data="course_add")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="home")],
        ]
    )
    return InlineKeyboardMarkup(rows)


def course_menu(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👥 Студенты", callback_data=f"students:{course_id}")],
            [InlineKeyboardButton("🗓 Занятия", callback_data=f"lessons:{course_id}")],
            [InlineKeyboardButton("📊 Сводка (.md)", callback_data=f"course_report:{course_id}")],
            [InlineKeyboardButton("🗑 Удалить курс", callback_data=f"course_del:{course_id}")],
            [InlineKeyboardButton("◀ К курсам", callback_data="courses")],
        ]
    )


def delete_course_confirmation(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Да, удалить курс", callback_data=f"course_del_confirm:{course_id}")],
            [InlineKeyboardButton("Отмена", callback_data=f"course:{course_id}")],
        ]
    )


def students_menu(course_id: int, students: list[Student]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(student.name, callback_data=f"student_report:{course_id}:{student.id}"),
            InlineKeyboardButton("🗑", callback_data=f"student_del:{course_id}:{student.id}"),
        ]
        for student in students
    ]
    rows.extend(
        [
            [InlineKeyboardButton("➕ Добавить студентов", callback_data=f"student_add:{course_id}")],
            [InlineKeyboardButton("◀ К курсу", callback_data=f"course:{course_id}")],
        ]
    )
    return InlineKeyboardMarkup(rows)


def delete_student_confirmation(course_id: int, student_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Да, удалить", callback_data=f"student_del_confirm:{course_id}:{student_id}")],
            [InlineKeyboardButton("Отмена", callback_data=f"students:{course_id}")],
        ]
    )


def lessons_menu(course_id: int, lessons: list[Lesson]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                f"{lesson.title} · {lesson.kind} · {lesson.max_score:g}",
                callback_data=f"lesson:{course_id}:{lesson.id}",
            )
        ]
        for lesson in lessons
    ]
    rows.extend(
        [
            [InlineKeyboardButton("➕ Добавить занятия", callback_data=f"lesson_add:{course_id}")],
            [InlineKeyboardButton("◀ К курсу", callback_data=f"course:{course_id}")],
        ]
    )
    return InlineKeyboardMarkup(rows)


def lesson_menu(course_id: int, lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Посещаемость", callback_data=f"attendance:{course_id}:{lesson_id}:0")],
            [InlineKeyboardButton("✏ Оценки", callback_data=f"scores:{course_id}:{lesson_id}:0")],
            [InlineKeyboardButton("📋 Должники", callback_data=f"debtors:{course_id}:{lesson_id}")],
            [InlineKeyboardButton("🗑 Удалить занятие", callback_data=f"lesson_del:{course_id}:{lesson_id}")],
            [InlineKeyboardButton("◀ К занятиям", callback_data=f"lessons:{course_id}")],
        ]
    )


def delete_lesson_confirmation(course_id: int, lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Да, удалить занятие", callback_data=f"lesson_del_confirm:{course_id}:{lesson_id}")],
            [InlineKeyboardButton("Отмена", callback_data=f"lesson:{course_id}:{lesson_id}")],
        ]
    )


def attendance_menu(draft: AttendanceDraft, register: RegisterOut, page: int) -> InlineKeyboardMarkup:
    start = page * PAGE_SIZE
    visible = register.students[start : start + PAGE_SIZE]
    rows = [
        [
            InlineKeyboardButton(
                f"{'✅' if draft.values[row.student_id] else '⬜'} {row.student_name}",
                callback_data=(f"attendance_toggle:{draft.course_id}:{draft.lesson_id}:{row.student_id}:{page}"),
            )
        ]
        for row in visible
    ]
    navigation: list[InlineKeyboardButton] = []
    if page > 0:
        navigation.append(
            InlineKeyboardButton("◀", callback_data=f"attendance:{draft.course_id}:{draft.lesson_id}:{page - 1}")
        )
    if start + PAGE_SIZE < len(register.students):
        navigation.append(
            InlineKeyboardButton("▶", callback_data=f"attendance:{draft.course_id}:{draft.lesson_id}:{page + 1}")
        )
    if navigation:
        rows.append(navigation)
    rows.extend(
        [
            [
                InlineKeyboardButton(
                    "✅ Отметить всех", callback_data=f"attendance_all:{draft.course_id}:{draft.lesson_id}:1:{page}"
                ),
                InlineKeyboardButton(
                    "⬜ Снять всех", callback_data=f"attendance_all:{draft.course_id}:{draft.lesson_id}:0:{page}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "💾 Сохранить", callback_data=f"attendance_save:{draft.course_id}:{draft.lesson_id}"
                )
            ],
            [InlineKeyboardButton("✖ Отмена", callback_data=f"lesson:{draft.course_id}:{draft.lesson_id}")],
        ]
    )
    return InlineKeyboardMarkup(rows)


def scores_menu(course_id: int, lesson_id: int, register: RegisterOut, page: int) -> InlineKeyboardMarkup:
    start = page * PAGE_SIZE
    visible = register.students[start : start + PAGE_SIZE]
    rows = [
        [
            InlineKeyboardButton(
                f"{row.student_name}: {_score_text(row.score)}",
                callback_data=f"score_set:{course_id}:{lesson_id}:{row.student_id}",
            )
        ]
        for row in visible
    ]
    navigation: list[InlineKeyboardButton] = []
    if page > 0:
        navigation.append(InlineKeyboardButton("◀", callback_data=f"scores:{course_id}:{lesson_id}:{page - 1}"))
    if start + PAGE_SIZE < len(register.students):
        navigation.append(InlineKeyboardButton("▶", callback_data=f"scores:{course_id}:{lesson_id}:{page + 1}"))
    if navigation:
        rows.append(navigation)
    rows.append([InlineKeyboardButton("◀ К занятию", callback_data=f"lesson:{course_id}:{lesson_id}")])
    return InlineKeyboardMarkup(rows)


def _score_text(score: float | None) -> str:
    return "—" if score is None else f"{score:g}"
