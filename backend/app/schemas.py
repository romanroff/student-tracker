from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserOut(OrmModel):
    id: int
    telegram_id: int
    display_name: str


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class CourseOut(OrmModel):
    id: int
    name: str


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class StudentOut(OrmModel):
    id: int
    name: str


class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    kind: str = Field(default="practice", min_length=1, max_length=20)
    held_at: datetime
    max_score: float = Field(default=10, ge=0, le=10_000)


class LessonOut(OrmModel):
    id: int
    title: str
    kind: str
    held_at: datetime
    max_score: float


class RecordUpdate(BaseModel):
    present: bool | None = None
    score: float | None = Field(default=None, ge=0)


class RecordOut(BaseModel):
    student_id: int
    student_name: str
    present: bool | None
    score: float | None


class RegisterOut(BaseModel):
    lesson: LessonOut
    students: list[RecordOut]
