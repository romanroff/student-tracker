import os
import sys
import traceback
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from tracker import Course
from utils import read_students_from_file, read_topics_from_file

# =====================================================
# ГЛОБАЛЬНЫЙ ПЕРЕХВАТЧИК ОШИБОК
# =====================================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    print("❌ КРИТИЧЕСКАЯ НЕОБРАБОТАННАЯ ОШИБКА:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler

# =====================================================
# НАСТРОЙКИ
# =====================================================
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable not set!")

DATA_FILE = "data/course_data.json"
STUDENTS_FILE = "data/students_list.txt"
TOPICS_FILE = "data/topics_list.txt"

# =====================================================
# ЗАГРУЗКА КУРСА
# =====================================================
course = Course("Python for beginners")

if os.path.exists(DATA_FILE):
    try:
        course.load_from_file(DATA_FILE)
        print("✅ Данные загружены из JSON.")
    except Exception as e:
        print(f"⚠️ Не удалось загрузить данные: {e}")
        print("ℹ️ Начинаем с пустого курса.")
else:
    print("ℹ️ JSON-файл не найден. Загружаем студентов и темы из файлов...")

    if os.path.exists(STUDENTS_FILE):
        try:
            students = read_students_from_file(STUDENTS_FILE)
            for name in students:
                course.add_student(name)
            print(f"✅ Загружено {len(students)} студентов из файла.")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить студентов: {e}")
    else:
        print("ℹ️ Файл со студентами не найден.")

    if os.path.exists(TOPICS_FILE):
        try:
            topics = read_topics_from_file(TOPICS_FILE)
            for topic in topics:
                course.add_topic(
                    topic['topic_name'],
                    topic['topic_type'],
                    topic['topic_max_score']
                )
            print(f"✅ Загружено {len(topics)} тем из файла.")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить темы: {e}")
    else:
        print("ℹ️ Файл с темами не найден.")

# =====================================================
# ОБРАБОТЧИКИ КОМАНД
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — приветствие и список команд."""
    print(f"📨 Команда /start от {update.effective_user.first_name}")
    await update.message.reply_text(
        "📚 Бот для учёта успеваемости\n\n"
        "Доступные команды:\n"
        "/students — список студентов\n"
        "/topics [lecture|practice] — список тем (можно указать тип)\n"
        "/add_student Имя — добавить студента\n"
        "/remove_student Имя — удалить студента\n"
        "/add_topic Название тип макс_балл — добавить тему\n"
        "/set_grade Студент Тема Оценка — выставить оценку\n"
        "/mark_attendance Студент Тема да/нет — отметить посещаемость\n"
        "/grades Студент — показать оценки студента\n"
        "/grades_table — сводная таблица оценок (только практики)\n"
        "/debtors Тема проходной_балл — список должников\n"
        "/attendance_rate Студент — процент посещаемости\n"
        "/save — сохранить данные"
    )

async def students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список всех студентов."""
    print(f"📨 Команда /students от {update.effective_user.first_name}")
    try:
        if not course.students:
            await update.message.reply_text("📭 Список студентов пуст.")
            return
        text = "\n".join(course.students)
        await update.message.reply_text(f"📋 Студенты:\n{text}")
    except Exception as e:
        print(f"❌ Ошибка в students: {e}")
        traceback.print_exc()
        await update.message.reply_text("⚠️ Произошла внутренняя ошибка.")

async def topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает темы. Можно указать тип: /topics lecture или /topics practice"""
    print(f"📨 Команда /topics от {update.effective_user.first_name}")
    try:
        topic_type = context.args[0].lower() if context.args else None

        if topic_type not in (None, 'lecture', 'practice'):
            await update.message.reply_text("❌ Укажите 'lecture' или 'practice', или без параметра для всех тем.")
            return

        if topic_type is None:
            topics_list = course.topics
            title = "📋 Все темы:"
        else:
            topics_list = list(course.get_topics_by_type(topic_type))
            title = f"📋 Темы типа '{topic_type}':"

        if not topics_list:
            await update.message.reply_text(f"📭 Нет тем типа '{topic_type}'." if topic_type else "📭 Список тем пуст.")
            return

        text = title + "\n"
        for i, topic in enumerate(topics_list, 1):
            text += f"{i}. {topic['topic_name']} ({topic['topic_type']}, макс. {topic['topic_max_score']})\n"

        await update.message.reply_text(text)
    except Exception as e:
        print(f"❌ Ошибка в topics: {e}")
        traceback.print_exc()
        await update.message.reply_text("⚠️ Произошла внутренняя ошибка.")

async def add_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет студента."""
    print(f"📨 Команда /add_student от {update.effective_user.first_name}")
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите имя: /add_student Иванов")
            return
        name = " ".join(context.args)
        course.add_student(name)
        await update.message.reply_text(f"✅ Студент '{name}' добавлен.")
    except Exception as e:
        print(f"❌ Ошибка в add_student: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def remove_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет студента."""
    print(f"📨 Команда /remove_student от {update.effective_user.first_name}")
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите имя: /remove_student Иванов")
            return
        name = " ".join(context.args)
        course.remove_student(name)
        await update.message.reply_text(f"✅ Студент '{name}' удалён.")
    except Exception as e:
        print(f"❌ Ошибка в remove_student: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def add_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет тему."""
    print(f"📨 Команда /add_topic от {update.effective_user.first_name}")
    try:
        if len(context.args) < 3:
            await update.message.reply_text("❌ Формат: /add_topic Название тип макс_балл")
            return
        name = context.args[0]
        topic_type = context.args[1].lower()
        try:
            max_score = int(context.args[2])
        except ValueError:
            await update.message.reply_text("❌ Максимальный балл должен быть числом.")
            return
        course.add_topic(name, topic_type, max_score)
        await update.message.reply_text(f"✅ Тема '{name}' добавлена.")
    except Exception as e:
        print(f"❌ Ошибка в add_topic: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def set_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выставляет оценку студенту за тему (только для практик)."""
    print(f"📨 Команда /set_grade от {update.effective_user.first_name}")
    try:
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Формат: /set_grade Студент Тема Оценка\n"
                "Пример: /set_grade Сазонова А. А. Pandas 13"
            )
            return

        *name_parts, topic, score_str = context.args

        student = " ".join(name_parts).strip()
        if not student:
            await update.message.reply_text("❌ Имя студента не может быть пустым.")
            return

        try:
            score = int(score_str)
        except ValueError:
            await update.message.reply_text("❌ Оценка должна быть числом (например: 5, 12, 15).")
            return

        # Дополнительная проверка: тема должна быть практикой
        is_practice = False
        for t in course.topics:
            if t['topic_name'] == topic:
                if t['topic_type'] == 'practice' and t['topic_max_score'] > 0:
                    is_practice = True
                break

        if not is_practice:
            await update.message.reply_text(
                f"❌ Тема '{topic}' является лекцией или не найдена. "
                "Оценки можно ставить только для практик."
            )
            return

        course.set_grade(student, topic, score)
        await update.message.reply_text(
            f"✅ Оценка {score} для '{student}' по теме '{topic}' сохранена."
        )

    except Exception as e:
        print(f"❌ Ошибка в set_grade: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def mark_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмечает посещаемость."""
    print(f"📨 Команда /mark_attendance от {update.effective_user.first_name}")
    try:
        if len(context.args) < 3:
            await update.message.reply_text("❌ Формат: /mark_attendance Студент Тема да/нет")
            return
        *name_parts, topic, present_str = context.args
        student = " ".join(name_parts).strip()
        if not student:
            await update.message.reply_text("❌ Имя студента не может быть пустым.")
            return
        present = present_str.lower() in ('да', 'yes', 'true', '1')
        course.mark_attendance(student, topic, present)
        await update.message.reply_text(f"✅ Посещаемость для '{student}' по теме '{topic}' отмечена.")
    except Exception as e:
        print(f"❌ Ошибка в mark_attendance: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def grades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает оценки студента."""
    print(f"📨 Команда /grades от {update.effective_user.first_name}")
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите имя: /grades Иванов")
            return
        student = " ".join(context.args)
        grades_dict = course.get_all_grades(student)
        if not grades_dict:
            await update.message.reply_text(f"📭 У студента '{student}' пока нет оценок.")
            return
        text = "\n".join(f"{topic}: {score}" for topic, score in grades_dict.items())
        await update.message.reply_text(f"📊 Оценки '{student}':\n{text}")
    except Exception as e:
        print(f"❌ Ошибка в grades: {e}")
        traceback.print_exc()
        await update.message.reply_text("⚠️ Произошла ошибка при получении оценок.")

async def grades_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает сводную таблицу оценок только по практикам."""
    print(f"📨 Команда /grades_table от {update.effective_user.first_name}")
    try:
        if not course.grades:
            await update.message.reply_text("📭 Оценок пока нет.")
            return

        all_students = sorted(course.students)
        all_topics = [t['topic_name'] for t in course.topics if t['topic_type'] == 'practice']

        if not all_topics:
            await update.message.reply_text("📭 Нет практических занятий для отображения.")
            return

        # Динамическая ширина
        student_width = max(len(s) for s in all_students + ["Студент"])
        topic_widths = {t: max(len(t), 6) for t in all_topics}

        text = "📊 Сводная таблица оценок (практики):\n"
        header = "Студент".ljust(student_width + 2)
        for topic in all_topics:
            header += topic.ljust(topic_widths[topic] + 2)
        text += header + "\n"
        text += "-" * len(header) + "\n"

        for student in all_students:
            row = student.ljust(student_width + 2)
            grades = course.get_all_grades(student)
            for topic in all_topics:
                score = grades.get(topic, "-")
                row += str(score).ljust(topic_widths[topic] + 2)
            text += row + "\n"

        await update.message.reply_text(f"<pre>{text}</pre>", parse_mode='HTML')
    except Exception as e:
        print(f"❌ Ошибка в grades_table: {e}")
        traceback.print_exc()
        await update.message.reply_text("⚠️ Произошла ошибка при формировании таблицы.")

async def debtors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает должников по теме."""
    print(f"📨 Команда /debtors от {update.effective_user.first_name}")
    try:
        if len(context.args) < 2:
            await update.message.reply_text("❌ Формат: /debtors Тема проходной_балл")
            return
        topic = context.args[0]
        try:
            pass_score = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Проходной балл должен быть числом.")
            return
        debtors_list = course.get_debtors(topic, pass_score)
        if not debtors_list:
            await update.message.reply_text(f"✅ Все студенты сдали тему '{topic}'.")
        else:
            text = "\n".join(debtors_list)
            await update.message.reply_text(f"📋 Должники по теме '{topic}':\n{text}")
    except Exception as e:
        print(f"❌ Ошибка в debtors: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def attendance_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает процент посещаемости студента."""
    print(f"📨 Команда /attendance_rate от {update.effective_user.first_name}")
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите имя: /attendance_rate Иванов")
            return
        student = " ".join(context.args)
        rate = course.get_attendance_rate(student)
        await update.message.reply_text(f"📊 Посещаемость студента '{student}': {rate}%")
    except Exception as e:
        print(f"❌ Ошибка в attendance_rate: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ {e}")

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет данные."""
    print(f"📨 Команда /save от {update.effective_user.first_name}")
    try:
        course.save_to_file(DATA_FILE)
        await update.message.reply_text("💾 Данные сохранены.")
    except Exception as e:
        print(f"❌ Ошибка в save: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка при сохранении: {e}")

# =====================================================
# FLASK-СЕРВЕР ДЛЯ RENDER (ПИНГ)
# =====================================================
web_app = Flask('')

@web_app.route('/')
def home():
    return "✅ Bot is alive!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

# =====================================================
# ЗАПУСК БОТА
# =====================================================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("students", students))
    app.add_handler(CommandHandler("topics", topics))
    app.add_handler(CommandHandler("add_student", add_student))
    app.add_handler(CommandHandler("remove_student", remove_student))
    app.add_handler(CommandHandler("add_topic", add_topic))
    app.add_handler(CommandHandler("set_grade", set_grade))
    app.add_handler(CommandHandler("mark_attendance", mark_attendance))
    app.add_handler(CommandHandler("grades", grades))
    app.add_handler(CommandHandler("grades_table", grades_table))
    app.add_handler(CommandHandler("debtors", debtors))
    app.add_handler(CommandHandler("attendance_rate", attendance_rate))
    app.add_handler(CommandHandler("save", save))

    # Запускаем Flask-сервер в отдельном потоке (для Render)
    threading.Thread(target=run_web, daemon=True).start()

    print("🤖 Бот запущен. Нажми Ctrl+C для остановки.")
    try:
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Бот упал в run_polling: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()