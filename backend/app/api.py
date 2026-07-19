from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.auth import get_current_user
from backend.app.db import get_session
from backend.app.models import Course, Lesson, LessonRecord, Student, User
from backend.app.schemas import (
    CourseCreate,
    CourseOut,
    LessonCreate,
    LessonOut,
    RecordOut,
    RecordUpdate,
    RegisterOut,
    StudentCreate,
    StudentOut,
    UserOut,
)

router = APIRouter(prefix="/api/v1")


def owned_course(session: Session, user: User, course_id: int) -> Course:
    course = session.scalar(select(Course).where(Course.id == course_id, Course.owner_id == user.id))
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    return course


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/courses", response_model=list[CourseOut])
def list_courses(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list[Course]:
    return list(session.scalars(select(Course).where(Course.owner_id == user.id).order_by(Course.id)))


@router.post("/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Course:
    course = Course(owner_id=user.id, name=payload.name.strip())
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:
    session.delete(owned_course(session, user, course_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/courses/{course_id}/students", response_model=list[StudentOut])
def list_students(
    course_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[Student]:
    owned_course(session, user, course_id)
    return list(session.scalars(select(Student).where(Student.course_id == course_id).order_by(Student.name)))


@router.post("/courses/{course_id}/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    course_id: int,
    payload: StudentCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Student:
    owned_course(session, user, course_id)
    student = Student(course_id=course_id, name=payload.name.strip())
    session.add(student)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Student already exists") from exc
    session.refresh(student)
    return student


@router.delete("/courses/{course_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    course_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:
    owned_course(session, user, course_id)
    student = session.scalar(select(Student).where(Student.id == student_id, Student.course_id == course_id))
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    session.delete(student)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/courses/{course_id}/lessons", response_model=list[LessonOut])
def list_lessons(
    course_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[Lesson]:
    owned_course(session, user, course_id)
    return list(session.scalars(select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.held_at.desc())))


@router.post("/courses/{course_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
def create_lesson(
    course_id: int,
    payload: LessonCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Lesson:
    owned_course(session, user, course_id)
    lesson = Lesson(course_id=course_id, **payload.model_dump())
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return lesson


@router.delete("/courses/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    course_id: int,
    lesson_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:
    owned_course(session, user, course_id)
    lesson = session.scalar(select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id))
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found")
    session.delete(lesson)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def course_lesson_student(
    session: Session, user: User, course_id: int, lesson_id: int, student_id: int
) -> tuple[Lesson, Student]:
    owned_course(session, user, course_id)
    lesson = session.scalar(select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id))
    student = session.scalar(select(Student).where(Student.id == student_id, Student.course_id == course_id))
    if lesson is None or student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson or student not found")
    return lesson, student


@router.put("/courses/{course_id}/lessons/{lesson_id}/students/{student_id}", response_model=RecordOut)
def update_record(
    course_id: int,
    lesson_id: int,
    student_id: int,
    payload: RecordUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> RecordOut:
    lesson, student = course_lesson_student(session, user, course_id, lesson_id, student_id)
    if payload.score is not None and payload.score > lesson.max_score:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Score exceeds lesson maximum")
    record = session.scalar(
        select(LessonRecord).where(LessonRecord.lesson_id == lesson_id, LessonRecord.student_id == student_id)
    )
    if record is None:
        record = LessonRecord(lesson_id=lesson_id, student_id=student_id)
        session.add(record)
    record.present = payload.present
    record.score = payload.score
    session.commit()
    return RecordOut(
        student_id=student.id,
        student_name=student.name,
        present=record.present,
        score=record.score,
    )


@router.get("/courses/{course_id}/lessons/{lesson_id}/register", response_model=RegisterOut)
def get_register(
    course_id: int,
    lesson_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> RegisterOut:
    owned_course(session, user, course_id)
    lesson = session.scalar(select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id))
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found")
    students = list(session.scalars(select(Student).where(Student.course_id == course_id).order_by(Student.name)))
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
