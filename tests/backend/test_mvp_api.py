from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DEV_AUTH_ENABLED", "true")
    with TestClient(app) as test_client:
        yield test_client


def auth(user_id: int, name: str = "Teacher") -> dict[str, str]:
    return {
        "X-Dev-Telegram-User-Id": str(user_id),
        "X-Dev-Telegram-Name": name,
    }


def test_teacher_manages_lesson_register(client: TestClient) -> None:
    course = client.post("/api/v1/courses", headers=auth(101), json={"name": "Python"})
    assert course.status_code == 201
    course_id = course.json()["id"]

    student = client.post(
        f"/api/v1/courses/{course_id}/students",
        headers=auth(101),
        json={"name": "Иван Иванов"},
    )
    assert student.status_code == 201
    student_id = student.json()["id"]

    lesson = client.post(
        f"/api/v1/courses/{course_id}/lessons",
        headers=auth(101),
        json={"title": "Функции", "held_at": "2026-07-19T10:00:00", "max_score": 10},
    )
    assert lesson.status_code == 201
    lesson_id = lesson.json()["id"]

    record = client.put(
        f"/api/v1/courses/{course_id}/lessons/{lesson_id}/students/{student_id}",
        headers=auth(101),
        json={"present": True, "score": 8},
    )
    assert record.status_code == 200
    assert record.json()["present"] is True
    assert record.json()["score"] == 8

    register = client.get(
        f"/api/v1/courses/{course_id}/lessons/{lesson_id}/register",
        headers=auth(101),
    )
    assert register.status_code == 200
    assert register.json()["students"] == [
        {"student_id": student_id, "student_name": "Иван Иванов", "present": True, "score": 8}
    ]


def test_courses_and_records_are_tenant_isolated(client: TestClient) -> None:
    first = client.post("/api/v1/courses", headers=auth(101), json={"name": "First"})
    second = client.post("/api/v1/courses", headers=auth(202), json={"name": "Second"})
    assert first.status_code == second.status_code == 201

    first_id = first.json()["id"]
    assert client.get("/api/v1/courses", headers=auth(101)).json() == [first.json()]
    assert client.get("/api/v1/courses", headers=auth(202)).json() == [second.json()]
    assert client.get(f"/api/v1/courses/{first_id}/students", headers=auth(202)).status_code == 404
    assert (
        client.post(
            f"/api/v1/courses/{first_id}/students",
            headers=auth(202),
            json={"name": "Intruder"},
        ).status_code
        == 404
    )


def test_health_is_public_but_api_requires_authentication(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/courses").status_code == 401


def test_score_cannot_exceed_lesson_maximum(client: TestClient) -> None:
    course_id = client.post("/api/v1/courses", headers=auth(101), json={"name": "Python"}).json()["id"]
    student_id = client.post(
        f"/api/v1/courses/{course_id}/students", headers=auth(101), json={"name": "Student"}
    ).json()["id"]
    lesson_id = client.post(
        f"/api/v1/courses/{course_id}/lessons",
        headers=auth(101),
        json={"title": "Lesson", "held_at": "2026-07-19T10:00:00", "max_score": 5},
    ).json()["id"]
    response = client.put(
        f"/api/v1/courses/{course_id}/lessons/{lesson_id}/students/{student_id}",
        headers=auth(101),
        json={"present": True, "score": 6},
    )
    assert response.status_code == 422
