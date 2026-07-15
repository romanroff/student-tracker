import os
from tracker import Course
from utils import read_students_from_file, read_topics_from_file

DATA_FILE = "data/course_data.json"
STUDENTS_FILE = "data/students_list.txt"
TOPICS_FILE = "data/topics_list.txt"

def print_menu():
    """
    Display the main menu for the Teacher's Gradebook application.
    """
    print("\n" + "=" * 50)
    print("          📚 Учёт успеваемости студентов")
    print("=" * 50)
    print(" 1. Показать всех студентов")
    print(" 2. Добавить студента")
    print(" 3. Удалить студента")
    print(" 4. Добавить тему")
    print(" 5. Показать все темы")
    print(" 6. Выставить оценку")
    print(" 7. Показать оценки студента")
    print(" 8. Отметить посещаемость")
    print(" 9. Показать посещаемость по теме")
    print("10. Средний балл студента")
    print("11. Средний балл группы")
    print("12. Список должников по теме")
    print("13. Посещаемость студента (%)")
    print("14. Сводная таблица оценок")
    print("15. Сохранить и выйти")
    print("=" * 50)

def add_student_interactive(course):
    name = input("Введите имя студента: ").strip()
    if not name:
        print("❌ Имя не может быть пустым.")
        return
    try:
        course.add_student(name)
        print(f"✅ Студент '{name}' добавлен.")
    except ValueError as e:
        print(f"❌ {e}")

def remove_student_interactive(course):
    name = input("Введите имя студента для удаления: ").strip()
    if not name:
        print("❌ Имя не может быть пустым.")
        return
    try:
        course.remove_student(name)
        print(f"✅ Студент '{name}' удалён.")
    except ValueError as e:
        print(f"❌ {e}")

def add_topic_interactive(course):
    name = input("Введите название темы: ").strip()
    if not name:
        print("❌ Название не может быть пустым.")
        return
    topic_type = input("Введите тип (lecture/practice): ").strip()
    try:
        max_score = int(input("Введите максимальный балл: "))
    except ValueError:
        print("❌ Оценка должна быть целым числом.")
        return
    try:
        course.add_topic(name, topic_type, max_score)
    except ValueError as e:
        print(f"❌ {e}")

def show_topics(course, topic_type: str = None):
    """
    Displays topics filtered by type.
    If topic_type is None, shows all topics.
    """
    if topic_type is None:
        topics = course.topics
        title = "Все темы"
    else:
        topics = list(course.get_topics_by_type(topic_type))
        title = f"Темы типа '{topic_type}'"

    if not topics:
        print(f"\n📭 Список {title.lower()} пуст.")
        return

    print(f"\n📋 Список {title.lower()}:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic['topic_name']} ({topic['topic_type']}, макс. {topic['topic_max_score']} баллов)")

def set_grade_interactive(course):
    student = input("Введите имя студента: ").strip()
    if not student:
        print("❌ Имя не может быть пустым.")
        return
    topic = input("Введите название темы: ").strip()
    if not topic:
        print("❌ Название темы не может быть пустым.")
        return
    try:
        score = int(input("Введите оценку: "))
    except ValueError:
        print("❌ Оценка должна быть целым числом.")
        return
    try:
        course.set_grade(student, topic, score)
    except ValueError as e:
        print(f"❌ {e}")

def show_student_grades(course):
    student = input("Введите имя студента: ").strip()
    if not student:
        print("❌ Имя не может быть пустым.")
        return
    grades = course.get_all_grades(student)
    if not grades:
        print(f"📭 У студента '{student}' пока нет оценок.")
        return
    print(f"\n📊 Оценки студента '{student}':")
    for topic, score in grades.items():
        print(f"  {topic}: {score}")

def mark_attendance_interactive(course):
    student = input("Введите имя студента: ").strip()
    if not student:
        print("❌ Имя не может быть пустым.")
        return
    topic = input("Введите название темы: ").strip()
    if not topic:
        print("❌ Название темы не может быть пустым.")
        return
    present_input = input("Присутствовал? (да/нет): ").strip().lower()
    if present_input not in ('да', 'нет'):
        print("❌ Введите 'да' или 'нет'.")
        return
    present = present_input == 'да'
    try:
        course.mark_attendance(student, topic, present)
    except ValueError as e:
        print(f"❌ {e}")

def show_attendance_by_topic(course):
    topic = input("Введите название темы: ").strip()
    if not topic:
        print("❌ Название темы не может быть пустым.")
        return
    attendance_dict = course.get_attendance_by_topic(topic)
    if not attendance_dict:
        print(f"📭 По теме '{topic}' нет данных о посещаемости.")
        return
    print(f"\n📋 Посещаемость по теме '{topic}':")
    for student, present in attendance_dict.items():
        status = "✅ Присутствовал" if present else "❌ Отсутствовал"
        print(f"  {student}: {status}")

def show_all_grades(course):
    """
    Выводит сводную таблицу оценок только для практических занятий.
    Ширина колонок автоматически подстраивается под длину названий.
    """
    if not course.grades:
        print("📭 Оценок пока нет.")
        return

    all_students = sorted(course.students)
    all_topics = [topic['topic_name'] for topic in course.topics if topic['topic_type'] == 'practice']

    if not all_topics:
        print("📭 Нет практических занятий для отображения.")
        return

    student_width = max(len(s) for s in all_students + ["Студент"])
    topic_widths = {topic: max(len(topic), 6) for topic in all_topics}

    print("\n📊 Сводная таблица оценок (практики):")

    header = "Студент".ljust(student_width + 2)
    for topic in all_topics:
        header += topic.ljust(topic_widths[topic] + 2)
    print(header)
    print("-" * len(header))

    for student in all_students:
        row = student.ljust(student_width + 2)
        grades = course.get_all_grades(student)
        for topic in all_topics:
            score = grades.get(topic, "-")
            row += str(score).ljust(topic_widths[topic] + 2)
        print(row)

def show_student_average(course):
    student = input("Введите имя студента: ").strip()
    if not student:
        print("❌ Имя не может быть пустым.")
        return
    try:
        avg = course.get_student_average(student)
        print(f"📊 Средний балл студента '{student}': {avg}")
    except ValueError as e:
        print(f"❌ {e}")

def show_group_average(course):
    avg = course.get_group_average()
    print(f"📊 Средний балл группы: {avg}")

def show_debtors(course):
    topic = input("Введите название темы: ").strip()
    if not topic:
        print("❌ Название не может быть пустым.")
        return
    try:
        pass_score = int(input("Введите проходной балл: "))
    except ValueError:
        print("❌ Проходной балл должен быть целым числом.")
        return
    try:
        debtors = course.get_debtors(topic, pass_score)
        if not debtors:
            print(f"✅ Все студенты сдали тему '{topic}'.")
        else:
            print(f"\n📋 Список должников по теме '{topic}':")
            for i, name in enumerate(debtors, 1):
                print(f"  {i}. {name}")
    except ValueError as e:
        print(f"❌ {e}")

def show_attendance_rate(course):
    student = input("Введите имя студента: ").strip()
    if not student:
        print("❌ Имя не может быть пустым.")
        return
    try:
        rate = course.get_attendance_rate(student)
        print(f"📊 Посещаемость студента '{student}': {rate}%")
    except ValueError as e:
        print(f"❌ {e}")

def save_and_exit(course):
    try:
        course.save_to_file(DATA_FILE)
        print(f"💾 Данные сохранены в файл '{DATA_FILE}'.")
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
    print("👋 До свидания!")

def main():
    course = Course("Python for beginners")

    if os.path.exists(DATA_FILE):
        try:
            course.load_from_file(DATA_FILE)
            print("✅ Данные загружены из файла.")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить данные: {e}")
            print("ℹ️ Начинаем с пустого курса.")
    else:
        if os.path.exists(STUDENTS_FILE):
            try:
                students = read_students_from_file(STUDENTS_FILE)
                for name in students:
                    course.add_student(name)
                print(f"✅ Загружено {len(students)} студентов из файла.")
            except Exception as e:
                print(f"⚠️ Не удалось загрузить студентов: {e}")
        else:
            print("ℹ️ Файл с именами студентов не найден. Начинаем с пустого курса.")
        
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
            print("ℹ️ Файл с темами не найден. Начинаем с пустого курса.")

    while True:
        print_menu()
        choice = input("Выберите действие (1-15): ").strip()

        if choice == "1":
            course.get_all_students()
        elif choice == "2":
            add_student_interactive(course)
        elif choice == "3":
            remove_student_interactive(course)
        elif choice == "4":
            add_topic_interactive(course)
        elif choice == "5":
            print("\n1. Показать все темы")
            print("2. Показать только лекции")
            print("3. Показать только практики")
            sub_choice = input("Выберите вариант (1-3): ").strip()
            if sub_choice == "1":
                show_topics(course, None)
            elif sub_choice == "2":
                show_topics(course, 'lecture')
            elif sub_choice == "3":
                show_topics(course, 'practice')
            else:
                print("❌ Неверный выбор.")
        elif choice == "6":
            set_grade_interactive(course)
        elif choice == "7":
            show_student_grades(course)
        elif choice == "8":
            mark_attendance_interactive(course)
        elif choice == "9":
            show_attendance_by_topic(course)
        elif choice == "10":
            show_student_average(course)
        elif choice == "11":
            show_group_average(course)
        elif choice == "12":
            show_debtors(course)
        elif choice == "13":
            show_attendance_rate(course)
        elif choice == "14":
            show_all_grades(course)
        elif choice == "15":
            save_and_exit(course)
            break
        else:
            print("❌ Неверный выбор. Пожалуйста, выберите число от 1 до 15.")

if __name__ == "__main__":
    main()