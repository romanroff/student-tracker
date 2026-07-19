from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models import Course, Lesson, LessonRecord, Student, User
from backend.app.schemas import LessonOut, RecordOut, RegisterOut


class ResourceNotFound(Exception):
    pass


class DuplicateStudent(Exception):
    pass


class ScoreOutOfRange(Exception):
    pass


class InvalidLessonBatch(ValueError):
    pass


@dataclass(frozen=True)
class StudentBatchResult:
    added: int
    skipped: int


@dataclass(frozen=True)
class LessonBatchResult:
    added: int
    skipped: int
    total_max_score: float


@dataclass(frozen=True)
class SummaryLesson:
    id: int
    title: str
    max_score: float


@dataclass(frozen=True)
class SummaryStudent:
    name: str
    scores: tuple[float | None, ...]
    average_score: float | None
    total_score: float


@dataclass(frozen=True)
class CourseSummary:
    course_name: str
    lessons: tuple[SummaryLesson, ...]
    students: tuple[SummaryStudent, ...]
    total_max_score: float


@dataclass(frozen=True)
class StudentLessonStatistics:
    title: str
    kind: str
    max_score: float
    score: float | None
    present: bool | None


@dataclass(frozen=True)
class StudentStatistics:
    course_name: str
    student_name: str
    lessons: tuple[StudentLessonStatistics, ...]
    average_score: float | None
    total_score: float
    present_count: int
    attendance_count: int
    attendance_rate: float | None


@dataclass(frozen=True)
class DebtorRow:
    student_name: str
    score: float | None


@dataclass(frozen=True)
class DebtorsReport:
    course_name: str
    lesson_title: str
    max_score: float
    pass_score: float
    students: tuple[DebtorRow, ...]


class BotGradebook:
    """Application service for trusted Telegram identities.

    Public methods accept a Telegram id and enforce ownership before every
    query or mutation. Telegram callback ids are never authorization evidence.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def ensure_user(self, telegram_id: int, display_name: str) -> User:
        with self.session_factory() as session:
            user = session.scalar(select(User).where(User.telegram_id == telegram_id))
            if user is None:
                user = User(telegram_id=telegram_id, display_name=display_name)
                session.add(user)
            elif user.display_name != display_name:
                user.display_name = display_name
            session.commit()
            session.refresh(user)
            return user

    def list_courses(self, telegram_id: int) -> list[Course]:
        with self.session_factory() as session:
            user = self._user(session, telegram_id)
            return list(session.scalars(select(Course).where(Course.owner_id == user.id).order_by(Course.id)))

    def add_course(self, telegram_id: int, name: str) -> Course:
        with self.session_factory() as session:
            user = self._user(session, telegram_id)
            course = Course(owner_id=user.id, name=name.strip())
            session.add(course)
            session.commit()
            session.refresh(course)
            return course

    def delete_course(self, telegram_id: int, course_id: int) -> None:
        with self.session_factory() as session:
            course = self._course(session, telegram_id, course_id)
            session.delete(course)
            session.commit()

    def get_course_summary(self, telegram_id: int, course_id: int) -> CourseSummary:
        with self.session_factory() as session:
            course = self._course(session, telegram_id, course_id)
            lessons = list(
                session.scalars(select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.held_at, Lesson.id))
            )
            students = list(
                session.scalars(select(Student).where(Student.course_id == course_id).order_by(Student.name))
            )
            lesson_ids = [lesson.id for lesson in lessons]
            records = {
                (record.student_id, record.lesson_id): record.score
                for record in session.scalars(select(LessonRecord).where(LessonRecord.lesson_id.in_(lesson_ids)))
            }
            summary_students: list[SummaryStudent] = []
            for student in students:
                scores = tuple(records.get((student.id, lesson.id)) for lesson in lessons)
                assigned = [score for score in scores if score is not None]
                summary_students.append(
                    SummaryStudent(
                        name=student.name,
                        scores=scores,
                        average_score=sum(assigned) / len(assigned) if assigned else None,
                        total_score=sum(assigned),
                    )
                )
            return CourseSummary(
                course_name=course.name,
                lessons=tuple(SummaryLesson(lesson.id, lesson.title, lesson.max_score) for lesson in lessons),
                students=tuple(summary_students),
                total_max_score=sum(lesson.max_score for lesson in lessons),
            )

    def get_student_statistics(self, telegram_id: int, course_id: int, student_id: int) -> StudentStatistics:
        with self.session_factory() as session:
            course = self._course(session, telegram_id, course_id)
            student = self._student(session, course_id, student_id)
            lessons = list(
                session.scalars(select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.held_at, Lesson.id))
            )
            records = {
                record.lesson_id: record
                for record in session.scalars(select(LessonRecord).where(LessonRecord.student_id == student_id))
            }
            rows = tuple(
                StudentLessonStatistics(
                    title=lesson.title,
                    kind=lesson.kind,
                    max_score=lesson.max_score,
                    score=records[lesson.id].score if lesson.id in records else None,
                    present=records[lesson.id].present if lesson.id in records else None,
                )
                for lesson in lessons
            )
            assigned = [row.score for row in rows if row.score is not None]
            marked = [row.present for row in rows if row.present is not None]
            present_count = sum(value is True for value in marked)
            return StudentStatistics(
                course_name=course.name,
                student_name=student.name,
                lessons=rows,
                average_score=sum(assigned) / len(assigned) if assigned else None,
                total_score=sum(assigned),
                present_count=present_count,
                attendance_count=len(marked),
                attendance_rate=100 * present_count / len(marked) if marked else None,
            )

    def list_students(self, telegram_id: int, course_id: int) -> list[Student]:
        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            return list(session.scalars(select(Student).where(Student.course_id == course_id).order_by(Student.name)))

    def add_student(self, telegram_id: int, course_id: int, name: str) -> Student:
        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            student = Student(course_id=course_id, name=name.strip())
            session.add(student)
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise DuplicateStudent from exc
            session.refresh(student)
            return student

    def add_students(self, telegram_id: int, course_id: int, names: list[str]) -> StudentBatchResult:
        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            existing = set(session.scalars(select(Student.name).where(Student.course_id == course_id)))
            new_names: list[str] = []
            seen = set(existing)
            skipped = 0
            for raw_name in names:
                name = raw_name.strip()
                if not name:
                    continue
                if name in seen:
                    skipped += 1
                    continue
                seen.add(name)
                new_names.append(name)
            session.add_all(Student(course_id=course_id, name=name) for name in new_names)
            session.commit()
            return StudentBatchResult(added=len(new_names), skipped=skipped)

    def delete_student(self, telegram_id: int, course_id: int, student_id: int) -> None:
        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            student = self._student(session, course_id, student_id)
            session.delete(student)
            session.commit()

    def delete_lesson(self, telegram_id: int, course_id: int, lesson_id: int) -> None:
        with self.session_factory() as session:
            lesson = self._lesson(session, telegram_id, course_id, lesson_id)
            session.delete(lesson)
            session.commit()

    def list_lessons(self, telegram_id: int, course_id: int) -> list[Lesson]:
        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            return list(
                session.scalars(
                    select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.held_at.desc(), Lesson.id)
                )
            )

    def add_lesson(
        self,
        telegram_id: int,
        course_id: int,
        title: str,
        held_at: datetime,
        max_score: float = 10,
        kind: str = "practice",
    ) -> Lesson:
        if max_score < 0 or not kind.strip():
            raise ScoreOutOfRange
        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            lesson = Lesson(
                course_id=course_id,
                title=title.strip(),
                kind=kind.strip(),
                held_at=held_at,
                max_score=max_score,
            )
            session.add(lesson)
            session.commit()
            session.refresh(lesson)
            return lesson

    def add_lessons(
        self,
        telegram_id: int,
        course_id: int,
        lines: list[str],
        held_at: datetime,
    ) -> LessonBatchResult:
        parsed: list[tuple[str, str, int]] = []
        for line_number, raw_line in enumerate(lines, start=1):
            if not raw_line.strip():
                continue
            fields = [field.strip() for field in raw_line.split(";")]
            if len(fields) != 3:
                raise InvalidLessonBatch(f"строка {line_number}: ожидаются 3 поля через ';'")
            title, kind, score_text = fields
            try:
                max_score = int(score_text)
            except ValueError as exc:
                raise InvalidLessonBatch(f"строка {line_number}: максимум должен быть целым числом") from exc
            if not title or len(title) > 200:
                raise InvalidLessonBatch(f"строка {line_number}: некорректное название")
            if not kind or len(kind) > 20:
                raise InvalidLessonBatch(f"строка {line_number}: некорректный тип")
            if max_score < 0 or max_score > 10_000:
                raise InvalidLessonBatch(f"строка {line_number}: некорректный максимум")
            parsed.append((title, kind, max_score))

        with self.session_factory() as session:
            self._course(session, telegram_id, course_id)
            existing = {
                (lesson.title, lesson.kind, lesson.max_score)
                for lesson in session.scalars(select(Lesson).where(Lesson.course_id == course_id))
            }
            unique: list[tuple[str, str, int]] = []
            seen = set(existing)
            skipped = 0
            for item in parsed:
                if item in seen:
                    skipped += 1
                    continue
                seen.add(item)
                unique.append(item)
            session.add_all(
                Lesson(course_id=course_id, title=title, kind=kind, held_at=held_at, max_score=max_score)
                for title, kind, max_score in unique
            )
            session.commit()
            return LessonBatchResult(
                added=len(unique),
                skipped=skipped,
                total_max_score=sum(max_score for _, _, max_score in parsed),
            )

    def get_register(self, telegram_id: int, course_id: int, lesson_id: int) -> RegisterOut:
        with self.session_factory() as session:
            lesson = self._lesson(session, telegram_id, course_id, lesson_id)
            students = list(
                session.scalars(select(Student).where(Student.course_id == course_id).order_by(Student.name))
            )
            records = {
                record.student_id: record
                for record in session.scalars(select(LessonRecord).where(LessonRecord.lesson_id == lesson_id))
            }
            return RegisterOut(
                lesson=LessonOut.model_validate(lesson),
                students=[
                    RecordOut(
                        student_id=student.id,
                        student_name=student.name,
                        present=records[student.id].present if student.id in records else None,
                        score=records[student.id].score if student.id in records else None,
                    )
                    for student in students
                ],
            )

    def get_debtors(
        self,
        telegram_id: int,
        course_id: int,
        lesson_id: int,
        pass_score: float,
    ) -> DebtorsReport:
        with self.session_factory() as session:
            course = self._course(session, telegram_id, course_id)
            lesson = self._lesson(session, telegram_id, course_id, lesson_id)
            if pass_score < 0 or pass_score > lesson.max_score:
                raise ScoreOutOfRange
            students = list(
                session.scalars(select(Student).where(Student.course_id == course_id).order_by(Student.name))
            )
            scores = {
                record.student_id: record.score
                for record in session.scalars(select(LessonRecord).where(LessonRecord.lesson_id == lesson_id))
            }
            debtor_rows: list[DebtorRow] = []
            for student in students:
                score = scores.get(student.id)
                if score is None or score < pass_score:
                    debtor_rows.append(DebtorRow(student.name, score))
            debtors = tuple(debtor_rows)
            return DebtorsReport(course.name, lesson.title, lesson.max_score, pass_score, debtors)

    def save_attendance(
        self,
        telegram_id: int,
        course_id: int,
        lesson_id: int,
        attendance: Mapping[int, bool],
    ) -> None:
        with self.session_factory() as session:
            self._lesson(session, telegram_id, course_id, lesson_id)
            students = {
                student.id
                for student in session.scalars(
                    select(Student).where(Student.course_id == course_id, Student.id.in_(attendance))
                )
            }
            if students != set(attendance):
                raise ResourceNotFound
            records = {
                record.student_id: record
                for record in session.scalars(
                    select(LessonRecord).where(
                        LessonRecord.lesson_id == lesson_id,
                        LessonRecord.student_id.in_(attendance),
                    )
                )
            }
            for student_id, present in attendance.items():
                record = records.get(student_id)
                if record is None:
                    record = LessonRecord(lesson_id=lesson_id, student_id=student_id)
                    session.add(record)
                record.present = present
            session.commit()

    def save_score(
        self,
        telegram_id: int,
        course_id: int,
        lesson_id: int,
        student_id: int,
        score: float | None,
    ) -> None:
        with self.session_factory() as session:
            lesson = self._lesson(session, telegram_id, course_id, lesson_id)
            self._student(session, course_id, student_id)
            if score is not None and (score < 0 or score > lesson.max_score):
                raise ScoreOutOfRange
            record = session.scalar(
                select(LessonRecord).where(
                    LessonRecord.lesson_id == lesson_id,
                    LessonRecord.student_id == student_id,
                )
            )
            if record is None:
                record = LessonRecord(lesson_id=lesson_id, student_id=student_id)
                session.add(record)
            record.score = score
            session.commit()

    @staticmethod
    def _user(session: Session, telegram_id: int) -> User:
        user = session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            raise ResourceNotFound
        return user

    def _course(self, session: Session, telegram_id: int, course_id: int) -> Course:
        user = self._user(session, telegram_id)
        course = session.scalar(select(Course).where(Course.id == course_id, Course.owner_id == user.id))
        if course is None:
            raise ResourceNotFound
        return course

    def _lesson(self, session: Session, telegram_id: int, course_id: int, lesson_id: int) -> Lesson:
        self._course(session, telegram_id, course_id)
        lesson = session.scalar(select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id))
        if lesson is None:
            raise ResourceNotFound
        return lesson

    @staticmethod
    def _student(session: Session, course_id: int, student_id: int) -> Student:
        student = session.scalar(select(Student).where(Student.id == student_id, Student.course_id == course_id))
        if student is None:
            raise ResourceNotFound
        return student
