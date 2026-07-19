# Backend Domain

The approved target is a Python 3.12 FastAPI service under `backend/` using
Pydantic validation, SQLAlchemy persistence, and Alembic migrations. Endpoints
delegate to application services; services enforce domain rules; repositories
perform course-scoped persistence. Telegram authentication and authorization
are backend responsibilities.

The canonical polling bot under `backend/app/bot_launcher.py` resolves the
Telegram sender directly, then calls `BotGradebook`; callback resource ids are
never treated as authorization evidence. Attendance checkbox changes live in
per-user bot state until Save commits the complete selection in one database
transaction. The bot and Mini App share SQLAlchemy models and persistence.
Multiline student input is normalized by trimming each line, ignores blank
lines, skips existing or repeated names, and inserts all new students in one
transaction.
Multiline lesson input uses `Название; тип; целый максимум`. Type is opaque
user data: the backend validates only that it is a non-empty bounded string and
does not infer rules from values such as `lecture` or `practice`. Every line is
validated before an atomic insert; the bot reports duplicates and the sum of
maximum scores in the submitted plan.
Course deletion resolves the course through the authenticated Telegram owner
before deleting it. SQLAlchemy cascades the confirmed operation to students,
lessons, grades, and attendance in one transaction.
Course summary generation resolves the same owned course, aggregates lesson
scores without changing data, and renders a UTF-8 Markdown document in memory.
Average score excludes missing grades; total score sums assigned grades.
Student statistics calculate attendance from explicit present/absent records;
unknown attendance is excluded from the denominator. Debtors for a selected
lesson are students with no score or a score below the teacher-provided passing
score. Lesson deletion rechecks ownership and cascades to its records.

Failure responses follow `docs/contracts/api.md`. No logs may contain bot
tokens, raw `initData`, grades, attendance payloads, callback academic data, or
unnecessary personal data. Backend quality requirements are in
`docs/testing.md`.
