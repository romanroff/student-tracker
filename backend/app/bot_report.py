from backend.app.bot_service import CourseSummary, DebtorsReport, StudentStatistics


def render_course_summary(summary: CourseSummary) -> str:
    headers = ["ФИО", *(lesson.title for lesson in summary.lessons), "Ср. балл", "Общий балл"]
    lines = [
        f"# Сводка по курсу: {_escape(summary.course_name)}",
        "",
        _row(headers),
        _row(["---"] * len(headers)),
        _row(
            [
                "Максимум",
                *(_number(lesson.max_score) for lesson in summary.lessons),
                "—",
                _number(summary.total_max_score),
            ]
        ),
    ]
    lines.extend(
        _row(
            [
                student.name,
                *(_number(score) if score is not None else "—" for score in student.scores),
                _number(student.average_score) if student.average_score is not None else "—",
                _number(student.total_score),
            ]
        )
        for student in summary.students
    )
    return "\n".join(lines) + "\n"


def render_student_statistics(statistics: StudentStatistics) -> str:
    average = _number(statistics.average_score) if statistics.average_score is not None else "—"
    attendance = (
        f"{_number(statistics.attendance_rate)}% ({statistics.present_count}/{statistics.attendance_count})"
        if statistics.attendance_rate is not None
        else "нет отметок"
    )
    lines = [
        f"# Статистика студента: {_escape(statistics.student_name)}",
        "",
        f"**Курс:** {_escape(statistics.course_name)}",
        f"**Средний балл:** {average}",
        f"**Общий балл:** {_number(statistics.total_score)}",
        f"**Посещаемость:** {attendance}",
        "",
        _row(["Занятие", "Тип", "Оценка", "Посещение"]),
        _row(["---", "---", "---", "---"]),
    ]
    lines.extend(
        _row(
            [
                lesson.title,
                lesson.kind,
                f"{_number(lesson.score)} / {_number(lesson.max_score)}" if lesson.score is not None else "—",
                "да" if lesson.present is True else "нет" if lesson.present is False else "—",
            ]
        )
        for lesson in statistics.lessons
    )
    return "\n".join(lines) + "\n"


def render_debtors_report(report: DebtorsReport) -> str:
    lines = [
        f"# Должники: {_escape(report.lesson_title)}",
        "",
        f"**Курс:** {_escape(report.course_name)}",
        f"**Проходной балл:** {_number(report.pass_score)} / {_number(report.max_score)}",
        "",
        _row(["ФИО", "Оценка"]),
        _row(["---", "---"]),
    ]
    lines.extend(
        _row([student.student_name, _number(student.score) if student.score is not None else "—"])
        for student in report.students
    )
    if not report.students:
        lines.append("Все студенты набрали проходной балл.")
    return "\n".join(lines) + "\n"


def _row(values: list[str] | tuple[str, ...]) -> str:
    return "| " + " | ".join(_escape(value) for value in values) + " |"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _number(value: float) -> str:
    return f"{value:g}"
