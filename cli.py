import os
from tracker import Course
from utils import read_students_from_file

DATA_FILE = "data/course_data.json"
STUDENTS_FILE = "data/students_list.txt"

def print_menu():
    """
    Print the main menu options for the Teacher's Grade Management System.

    Displays a formatted console menu with a list of available actions,
    such as managing students, topics, grades, and attendance, 
    bordered by separator lines for better readability.

    Returns:
        None
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
    print("10. Сводная таблица оценок")
    print("11. Сохранить и выйти")
    print("=" * 50)

def add_student_interactive(course):
    """
    Interactively prompts the user to input a student's name and adds it to the specified course.

    This function requests a student's name via the console. If the input is empty 
    (after stripping whitespace), it prints an error message and exits. Otherwise, 
    it attempts to add the student to the course object. If the addition is successful, 
    a success message is printed; if a ValueError occurs (e.g., the student already exists), 
    the error message is displayed.

    Parameters
    ----------
    course : object
        A course object that must implement the `add_student(name)` method. 
        This method should raise a ValueError if the student cannot be added.

    Returns
    -------
    None
    """
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
    """
    Interactively removes a student from the course after prompting for their name.

    Args:
        course: The course object from which to remove the student.
                The course object must have a remove_student method.

    Returns:
        None. Prints appropriate success or error messages to the console.
    """
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
    """
    Function to interactively add a new topic to a course.

    This function prompts the user to input topic details and validates the inputs.
    If any input is invalid, it displays an appropriate error message and returns.

    Args:
        course: The course object to which the topic will be added.

    The function performs the following steps:
    1. Prompts for and retrieves the topic name, stripping whitespace.
       - If the name is empty, displays an error and returns.
    2. Prompts for and retrieves the topic type (lecture/practice), stripping whitespace.
    3. Prompts for and retrieves the maximum score as an integer.
       - If the input is not a valid integer, displays an error and returns.
    4. Attempts to add the topic to the course.
       - If a ValueError occurs, displays the error message.

    Error Handling:
    - Empty topic name: "❌ Название не может быть пустым."
    - Non-integer score input: "❌ Оценка должна быть целым числом."
    - Other validation errors: "❌ " followed by the specific error message.
    """
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

def show_topics(course):
    """
    Displays a list of topics for a given course with their details.
    
    The function retrieves all topics from the course and prints them in a formatted way.
    If no topics are found, it displays a message indicating an empty list.
    
    Args:
        course: A course object that contains topics. The object must have a 
                'get_all_topics()' method that returns a list of topic dictionaries.
                
    Each topic dictionary should contain at least the following keys:
        - topic_name (str): The name of the topic
        - topic_type (str): The type/category of the topic
        - topic_max_score (int): The maximum possible score for the topic
        
    The function prints:
        - If no topics: "📭 Список тем пуст."
        - If topics exist: A numbered list with topic details including name, 
          type, and maximum score
          
    Returns:
        None: This function doesn't return any value, it only prints to console.
    """
    topics = course.get_all_topics()
    if not topics:
        print("\n📭 Список тем пуст.")
        return
    print("\n📋 Список тем:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic['topic_name']} ({topic['topic_type']}, макс. {topic['topic_max_score']} баллов)")

def set_grade_interactive(course):
    """
    Interactive function to set a grade for a student in a specific topic.
    
    This function prompts the user to input student name, topic, and score,
    validates the inputs, and then sets the grade in the course.
    
    Args:
        course: The course object containing the set_grade method
        
    The function performs the following operations:
    1. Prompts for and validates student name (non-empty)
    2. Prompts for and validates topic name (non-empty)
    3. Prompts for and validates score (must be an integer)
    4. Attempts to set the grade in the course
    5. Handles any ValueError exceptions that may occur
    
    Error handling:
    - Empty student name or topic name
    - Non-integer score input
    - Any ValueError from course.set_grade method
    
    Returns:
        None. The function returns early if any validation fails.
    """
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
    """
    Display all grades for a specific student in a course.

    This function prompts the user to enter a student's name, validates the input,
    and retrieves and displays all grades associated with that student. If the
    student name is empty or no grades are found, appropriate messages are displayed.

    Args:
        course: A course object that must have a 'get_all_grades' method to
                retrieve student grades.

    Returns:
        None: This function doesn't return any value, it only prints information
              to the console.

    The function handles the following cases:
        - Empty student name input
        - Student with no recorded grades
        - Successful display of student grades

    Example:
        >>> show_student_grades(my_course)
        # Prompts for student name and displays their grades
    """
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
    """
    Interactive function to mark attendance for a student in a course.
    
    The function prompts for student name, topic, and attendance status,
    validates the inputs, and updates the attendance record.
    
    Args:
        course: Course object containing the attendance marking functionality
        
    The function performs the following steps:
        1. Prompts for and validates student name (non-empty)
        2. Prompts for and validates topic name (non-empty)
        3. Prompts for and validates attendance status (yes/no)
        4. Calls the course's mark_attendance method with validated inputs
        5. Handles ValueError exceptions from the attendance marking
        
    Error handling:
        - Prints error messages for invalid inputs
        - Returns early if any input is invalid
        - Catches and displays ValueError from course.mark_attendance
    """
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
    """
    Displays attendance information for a specific topic in a course.

    This function prompts the user to enter a topic name, validates the input,
    and then retrieves and displays the attendance data for that topic.

    Args:
        course: The course object containing attendance data. This object should
                have a 'get_attendance_by_topic' method that accepts a topic name
                and returns a dictionary of student attendance.

    Returns:
        None: The function prints the attendance information to the console or
              an appropriate message if no data is available.

    The function handles the following cases:
        - Empty topic name input
        - Topic with no attendance data
        - Successful display of attendance data with visual indicators
    """
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
    Display all grades for each student across all topics in a tabular format.
    
    The function prints a formatted table with student names as rows and topics as columns.
    If no grades are available, it displays a message indicating that.
    
    Args:
        course: A Course object containing students, topics, and grades data.
                The Course object should have:
                - grades: A dictionary or similar structure storing student grades
                - students: A collection of student names
                - topics: A list of topic dictionaries with 'topic_name' key
                - get_all_grades(student): A method to retrieve all grades for a student
    
    Returns:
        None. The function prints directly to the console.
    
    Note:
        - The table formatting uses left-justified text with specific column widths
        - Student names are padded to 25 characters
        - Each topic column is padded to 15 characters
        - Missing grades are displayed as "-"
        - If there are no grades at all, a message "📭 Оценок пока нет." is displayed
    """
    if not course.grades:
        print("📭 Оценок пока нет.")
        return
    print("\n📊 Сводная таблица оценок:")
    all_students = sorted(course.students)
    all_topics = [topic['topic_name'] for topic in course.topics]
    
    header = "Студент".ljust(25)
    for topic in all_topics:
        header += topic.ljust(15)
    print(header)
    print("-" * (25 + 15 * len(all_topics)))
    
    for student in all_students:
        row = student.ljust(25)
        grades = course.get_all_grades(student)
        for topic in all_topics:
            score = grades.get(topic, "-")
            row += str(score).ljust(15)
        print(row)

def save_and_exit(course):
    """
    Save course data to file and exit the program.
    
    This function attempts to save the provided course object to a data file,
    prints a success or error message, and then terminates the program.
    
    Args:
        course: The course object containing data to be saved to file.
        
    Returns:
        None
        
    Raises:
        SystemExit: Always exits with code 0 after attempting to save data.
        
    Side Effects:
        - Writes course data to DATA_FILE if successful
        - Prints status messages to console
        - Terminates the program execution
    """
    try:
        course.save_to_file(DATA_FILE)
        print(f"💾 Данные сохранены в файл '{DATA_FILE}'.")
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
    print("👋 До свидания!")
    exit(0)

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
            print("ℹ️ Файл с данными не найден. Начинаем с пустого курса.")
    
    while True:
        print_menu()
        choice = input("Выберите действие (1-11): ").strip()
        
        if choice == "1":
            course.get_all_students()
        elif choice == "2":
            add_student_interactive(course)
        elif choice == "3":
            remove_student_interactive(course)
        elif choice == "4":
            add_topic_interactive(course)
        elif choice == "5":
            show_topics(course)
        elif choice == "6":
            set_grade_interactive(course)
        elif choice == "7":
            show_student_grades(course)
        elif choice == "8":
            mark_attendance_interactive(course)
        elif choice == "9":
            show_attendance_by_topic(course)
        elif choice == "10":
            show_all_grades(course)
        elif choice == "11":
            save_and_exit(course)
        else:
            print("❌ Неверный выбор. Пожалуйста, выберите число от 1 до 11.")

if __name__ == "__main__":
    main()