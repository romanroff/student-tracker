import os
from datetime import datetime
from io import BytesIO
from typing import Any, cast

from sqlalchemy.orm import sessionmaker
from telegram import CallbackQuery, InputFile, Update
from telegram import User as TelegramUser
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from backend.app.bot_report import render_course_summary, render_debtors_report, render_student_statistics
from backend.app.bot_service import (
    BotGradebook,
    DuplicateStudent,
    InvalidLessonBatch,
    ResourceNotFound,
    ScoreOutOfRange,
)
from backend.app.bot_ui import (
    AttendanceDraft,
    attendance_menu,
    course_menu,
    courses_menu,
    delete_course_confirmation,
    delete_lesson_confirmation,
    delete_student_confirmation,
    lesson_menu,
    lessons_menu,
    main_menu,
    scores_menu,
    students_menu,
)
from backend.app.config import Settings
from backend.app.db import create_database_engine

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL") or None


def _display_name(user: TelegramUser) -> str:
    return user.full_name or user.username or f"Telegram {user.id}"


def _service(context: ContextTypes.DEFAULT_TYPE) -> BotGradebook:
    return cast(BotGradebook, context.application.bot_data["gradebook"])


def _user_data(context: ContextTypes.DEFAULT_TYPE) -> dict[Any, Any]:
    if context.user_data is None:
        raise RuntimeError("User data storage is unavailable")
    return context.user_data


def _identity(update: Update) -> tuple[int, str]:
    user = update.effective_user
    if user is None:
        raise ResourceNotFound
    return user.id, _display_name(user)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    telegram_id, display_name = _identity(update)
    _service(context).ensure_user(telegram_id, display_name)
    _user_data(context).clear()
    await update.message.reply_text(
        "Student Tracker — управление курсами, студентами, посещаемостью и оценками.",
        reply_markup=main_menu(WEBAPP_URL),
    )


async def _edit(query: CallbackQuery, text: str, reply_markup: Any) -> None:
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def _send_markdown(
    update: Update, context: ContextTypes.DEFAULT_TYPE, content: str, filename: str, caption: str
) -> None:
    chat = update.effective_chat
    if chat is None:
        raise ResourceNotFound
    await context.bot.send_document(
        chat_id=chat.id,
        document=InputFile(BytesIO(content.encode("utf-8")), filename=filename),
        caption=caption,
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return
    await query.answer()
    telegram_id, display_name = _identity(update)
    service = _service(context)
    service.ensure_user(telegram_id, display_name)
    parts = query.data.split(":")
    action = parts[0]
    try:
        if action == "home":
            _user_data(context).clear()
            await _edit(query, "Главное меню", main_menu(WEBAPP_URL))
        elif action == "courses":
            courses = service.list_courses(telegram_id)
            await _edit(query, "Ваши курсы:" if courses else "Курсов пока нет.", courses_menu(courses))
        elif action == "course_add":
            _user_data(context)["awaiting"] = "course"
            await _edit(query, "Отправьте название нового курса.", main_menu(WEBAPP_URL))
        elif action == "course":
            course_id = int(parts[1])
            courses = service.list_courses(telegram_id)
            course = next((item for item in courses if item.id == course_id), None)
            if course is None:
                raise ResourceNotFound
            await _edit(query, f"Курс: {course.name}", course_menu(course_id))
        elif action == "course_del":
            course_id = int(parts[1])
            courses = service.list_courses(telegram_id)
            course = next((item for item in courses if item.id == course_id), None)
            if course is None:
                raise ResourceNotFound
            await _edit(
                query,
                f"Удалить курс «{course.name}»? Будут удалены все студенты, занятия, оценки и посещаемость.",
                delete_course_confirmation(course_id),
            )
        elif action == "course_report":
            course_id = int(parts[1])
            summary = service.get_course_summary(telegram_id, course_id)
            await _send_markdown(
                update,
                context,
                render_course_summary(summary),
                f"course-{course_id}-summary.md",
                f"Сводка по курсу «{summary.course_name}»",
            )
        elif action == "course_del_confirm":
            course_id = int(parts[1])
            service.delete_course(telegram_id, course_id)
            _user_data(context).clear()
            courses = service.list_courses(telegram_id)
            await _edit(query, "Курс и все связанные данные удалены.", courses_menu(courses))
        elif action == "students":
            course_id = int(parts[1])
            students = service.list_students(telegram_id, course_id)
            await _edit(query, "Студенты:" if students else "Студентов пока нет.", students_menu(course_id, students))
        elif action == "student_add":
            course_id = int(parts[1])
            service.list_students(telegram_id, course_id)
            _user_data(context)["awaiting"] = f"student:{course_id}"
            await _edit(
                query,
                "Отправьте список студентов: одно ФИО на каждой строке.",
                course_menu(course_id),
            )
        elif action == "student_del":
            course_id, student_id = map(int, parts[1:3])
            students = service.list_students(telegram_id, course_id)
            student = next((item for item in students if item.id == student_id), None)
            if student is None:
                raise ResourceNotFound
            await _edit(
                query,
                f"Удалить студента «{student.name}»? Оценки и посещаемость также будут удалены.",
                delete_student_confirmation(course_id, student_id),
            )
        elif action == "student_report":
            course_id, student_id = map(int, parts[1:3])
            statistics = service.get_student_statistics(telegram_id, course_id, student_id)
            await _send_markdown(
                update,
                context,
                render_student_statistics(statistics),
                f"course-{course_id}-student-{student_id}.md",
                f"Статистика: {statistics.student_name}",
            )
        elif action == "student_del_confirm":
            course_id, student_id = map(int, parts[1:3])
            service.delete_student(telegram_id, course_id, student_id)
            students = service.list_students(telegram_id, course_id)
            await _edit(query, "Студент удалён.", students_menu(course_id, students))
        elif action == "lessons":
            course_id = int(parts[1])
            lessons = service.list_lessons(telegram_id, course_id)
            await _edit(query, "Занятия:" if lessons else "Занятий пока нет.", lessons_menu(course_id, lessons))
        elif action == "lesson_add":
            course_id = int(parts[1])
            service.list_lessons(telegram_id, course_id)
            _user_data(context)["awaiting"] = f"lesson:{course_id}"
            await _edit(
                query,
                "Отправьте занятия, по одному на строке:\n"
                "Название; тип; целый максимум\n\n"
                "Пример:\nВведение в Python; lecture; 0\nВведение в Python; practice; 10",
                course_menu(course_id),
            )
        elif action == "lesson":
            course_id, lesson_id = map(int, parts[1:3])
            register = service.get_register(telegram_id, course_id, lesson_id)
            _user_data(context).pop("attendance", None)
            await _edit(
                query,
                f"Занятие: {register.lesson.title}\n"
                f"Тип: {register.lesson.kind}\n"
                f"Максимум: {register.lesson.max_score:g}",
                lesson_menu(course_id, lesson_id),
            )
        elif action == "debtors":
            course_id, lesson_id = map(int, parts[1:3])
            service.get_register(telegram_id, course_id, lesson_id)
            _user_data(context)["awaiting"] = f"debtors:{course_id}:{lesson_id}"
            await _edit(query, "Введите проходной балл для выбранного занятия.", lesson_menu(course_id, lesson_id))
        elif action == "lesson_del":
            course_id, lesson_id = map(int, parts[1:3])
            register = service.get_register(telegram_id, course_id, lesson_id)
            await _edit(
                query,
                f"Удалить занятие «{register.lesson.title}»? Оценки и посещаемость будут удалены.",
                delete_lesson_confirmation(course_id, lesson_id),
            )
        elif action == "lesson_del_confirm":
            course_id, lesson_id = map(int, parts[1:3])
            service.delete_lesson(telegram_id, course_id, lesson_id)
            lessons = service.list_lessons(telegram_id, course_id)
            await _edit(query, "Занятие и связанные записи удалены.", lessons_menu(course_id, lessons))
        elif action in {"attendance", "attendance_toggle", "attendance_all"}:
            await _attendance_callback(query, context, service, telegram_id, parts)
        elif action == "attendance_save":
            course_id, lesson_id = map(int, parts[1:3])
            draft = _user_data(context).get("attendance")
            if not isinstance(draft, AttendanceDraft) or (draft.course_id, draft.lesson_id) != (course_id, lesson_id):
                raise ResourceNotFound
            service.save_attendance(telegram_id, course_id, lesson_id, draft.values)
            _user_data(context).pop("attendance", None)
            await _edit(query, "Посещаемость сохранена.", lesson_menu(course_id, lesson_id))
        elif action == "scores":
            course_id, lesson_id, page = map(int, parts[1:4])
            register = service.get_register(telegram_id, course_id, lesson_id)
            await _edit(query, f"Оценки — {register.lesson.title}", scores_menu(course_id, lesson_id, register, page))
        elif action == "score_set":
            course_id, lesson_id, student_id = map(int, parts[1:4])
            service.get_register(telegram_id, course_id, lesson_id)
            _user_data(context)["awaiting"] = f"score:{course_id}:{lesson_id}:{student_id}"
            await _edit(query, "Введите оценку числом или '-' для удаления.", lesson_menu(course_id, lesson_id))
        elif action == "noop":
            return
    except (ResourceNotFound, ValueError):
        await _edit(query, "Ресурс недоступен или был удалён.", main_menu(WEBAPP_URL))


async def _attendance_callback(
    query: CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    service: BotGradebook,
    telegram_id: int,
    parts: list[str],
) -> None:
    action = parts[0]
    course_id, lesson_id = map(int, parts[1:3])
    register = service.get_register(telegram_id, course_id, lesson_id)
    draft = _user_data(context).get("attendance")
    if not isinstance(draft, AttendanceDraft) or (draft.course_id, draft.lesson_id) != (course_id, lesson_id):
        draft = AttendanceDraft(
            course_id, lesson_id, {row.student_id: row.present is True for row in register.students}
        )
    if action == "attendance":
        page = int(parts[3])
    elif action == "attendance_toggle":
        student_id, page = map(int, parts[3:5])
        draft = draft.toggle(student_id)
    else:
        present, page = map(int, parts[3:5])
        draft = draft.set_all(bool(present))
    _user_data(context)["attendance"] = draft
    text = f"Посещаемость — {register.lesson.title}" if register.students else "В курсе пока нет студентов."
    await _edit(query, text, attendance_menu(draft, register, page))


async def text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    telegram_id, display_name = _identity(update)
    service = _service(context)
    service.ensure_user(telegram_id, display_name)
    awaiting = _user_data(context).pop("awaiting", None)
    if not isinstance(awaiting, str):
        await update.message.reply_text(
            "Используйте кнопки меню или команду /start.", reply_markup=main_menu(WEBAPP_URL)
        )
        return
    try:
        parts = awaiting.split(":")
        if parts[0] == "course":
            service.add_course(telegram_id, update.message.text)
            await update.message.reply_text(
                "Курс добавлен.", reply_markup=courses_menu(service.list_courses(telegram_id))
            )
        elif parts[0] == "student":
            course_id = int(parts[1])
            student_result = service.add_students(telegram_id, course_id, update.message.text.splitlines())
            await update.message.reply_text(
                f"Добавлено: {student_result.added}. Пропущено повторов: {student_result.skipped}.",
                reply_markup=students_menu(course_id, service.list_students(telegram_id, course_id)),
            )
        elif parts[0] == "lesson":
            course_id = int(parts[1])
            lesson_result = service.add_lessons(
                telegram_id,
                course_id,
                update.message.text.splitlines(),
                held_at=datetime.now(),
            )
            await update.message.reply_text(
                f"Добавлено занятий: {lesson_result.added}. Пропущено повторов: {lesson_result.skipped}. "
                f"Сумма максимальных баллов: {lesson_result.total_max_score:g}.",
                reply_markup=lessons_menu(course_id, service.list_lessons(telegram_id, course_id)),
            )
        elif parts[0] == "score":
            course_id, lesson_id, student_id = map(int, parts[1:4])
            raw_score = update.message.text.strip()
            service.save_score(
                telegram_id, course_id, lesson_id, student_id, None if raw_score == "-" else float(raw_score)
            )
            register = service.get_register(telegram_id, course_id, lesson_id)
            await update.message.reply_text(
                "Оценка сохранена.", reply_markup=scores_menu(course_id, lesson_id, register, 0)
            )
        elif parts[0] == "debtors":
            course_id, lesson_id = map(int, parts[1:3])
            report = service.get_debtors(telegram_id, course_id, lesson_id, float(update.message.text.strip()))
            await _send_markdown(
                update,
                context,
                render_debtors_report(report),
                f"course-{course_id}-lesson-{lesson_id}-debtors.md",
                f"Должники: {report.lesson_title}",
            )
    except DuplicateStudent:
        await update.message.reply_text("Студент с таким именем уже существует.", reply_markup=main_menu(WEBAPP_URL))
    except InvalidLessonBatch as exc:
        await update.message.reply_text(f"Не удалось добавить занятия: {exc}.", reply_markup=main_menu(WEBAPP_URL))
    except ScoreOutOfRange:
        await update.message.reply_text(
            "Оценка должна быть от 0 до максимума занятия.", reply_markup=main_menu(WEBAPP_URL)
        )
    except (ResourceNotFound, ValueError):
        await update.message.reply_text(
            "Некорректные данные или ресурс недоступен.", reply_markup=main_menu(WEBAPP_URL)
        )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required")
    settings = Settings()
    engine = create_database_engine(settings.database_url)
    factory = sessionmaker(engine, expire_on_commit=False)
    application = Application.builder().token(BOT_TOKEN).build()
    application.bot_data["gradebook"] = BotGradebook(factory)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callbacks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_input))
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
