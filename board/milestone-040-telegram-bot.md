# Milestone M040: Telegram Bot Gradebook

## Goal

Provide a tenant-isolated Telegram bot interface for routine gradebook work
without requiring a Mini App or public HTTPS endpoint.

## Tasks

### M040-001 Implement Bot Gradebook Workflows

Priority: P1
Status: `[x]`

Implement course and student navigation, lesson selection, paginated attendance
checkboxes, bulk attendance save, student add/remove, and score entry using
Telegram inline keyboards and long polling.

Acceptance notes:

- Every query and mutation is scoped by the Telegram user's application user.
- Attendance changes remain a draft until the user presses Save.
- Bulk attendance is committed atomically for the selected lesson.
- Empty courses, lessons, and student lists have explicit bot messages.
- Callback payloads contain stable ids and stay within Telegram limits.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest -q tests/backend/test_bot_service.py`
- Red confirmed: missing `backend.app.bot_service` during collection.
- Green: bot service/UI suite passed (`9 passed`).
- Full backend: `16 passed`, 88.70% coverage; Ruff format/lint, strict
  mypy, and Bandit passed.
- Frontend: `4 passed`; ESLint and production TypeScript/Vite build passed.
- Security: `pip-audit` and `npm audit --audit-level=high` found no known
  vulnerabilities.
- Docker Compose configuration and backend/frontend/bot image builds passed;
  database, backend, and frontend health checks passed.
- Live Telegram `getMe` could not be completed on 2026-07-20 because HTTPS
  connections to `api.telegram.org` timed out from both Windows and Docker.
  This is an external network gate, not treated as a passed runtime check.

Files changed:

- `backend/app/bot_launcher.py`, `backend/app/bot_service.py`,
  `backend/app/bot_ui.py`, `docker-compose.yml`
- `tests/backend/test_bot_service.py`, `tests/backend/test_bot_ui.py`
- `features/telegram_bot_gradebook.feature` and related architecture/runtime
  documentation

### M040-002 Add Students From A Multiline Message

Priority: P1
Status: `[x]`

Allow a teacher to paste one student name per line. Ignore empty lines, avoid
creating duplicates, commit the new students atomically, and report added and
skipped counts.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest -q tests/backend/test_bot_service.py -k multiline`
- Red confirmed: `BotGradebook.add_students` was absent.
- Green: targeted multiline test passed; bot service/UI suite passed (`10 passed`).
- Input blanks are ignored; existing and repeated names are skipped and
  reported; new names commit in one transaction after ownership validation.

### M040-003 Add Lessons From A Semicolon-Separated Message

Priority: P1
Status: `[x]`

Accept one lesson per line in `Название; тип; целый максимум` format, persist
the user-provided type without interpreting it, validate the complete message before writing, skip
exact duplicates, and report the total available score.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest -q tests/backend/test_bot_service.py -k lesson_batch`
- Red confirmed: `InvalidLessonBatch` and `BotGradebook.add_lessons` were absent.
- Green: the supplied 16-line plan imports 16 lessons and reports a maximum
  score total of exactly 100; malformed integer input rejects the full batch.
- User clarification applied: type is an opaque string and maximum is a
  user-provided non-negative integer; values such as `lecture` have no inferred
  behavior.
- Full backend: `19 passed`, 88.29% coverage; Ruff format/lint, strict mypy,
  Bandit, and synchronized skills passed.
- Frontend: `4 passed`; ESLint and production TypeScript/Vite build passed.
- Migration `0002_lesson_kind` passed SQLite upgrade/downgrade/upgrade and was
  applied to PostgreSQL (`head`).
- Backend, frontend, and bot images built; all Compose services including the
  recreated Telegram bot are running.

### M040-004 Delete A Course From The Bot

Priority: P1
Status: `[x]`

Add a destructive course button with explicit confirmation. Deletion must be
tenant-scoped and cascade to the course's students, lessons, grades, and
attendance.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest -q tests/backend/test_bot_service.py -k delete_course`
- Red confirmed: `BotGradebook.delete_course` was absent.
- Green: owner deletion cascades to students, lessons, and records; a second
  tenant receives `ResourceNotFound` and cannot delete the course.
- Course UI exposes `🗑 Удалить курс`, a separate warning, explicit
  confirmation, and cancellation back to the course.
- Full backend: `20 passed`, 88.41% coverage; Ruff format/lint, strict mypy,
  Bandit, and synchronized skills passed.
- Bot image rebuilt; backend, frontend, database, and recreated bot containers
  are running.

### M040-005 Download A Course Markdown Summary

Priority: P1
Status: `[x]`

Add a course button that returns a `.md` document containing a GitHub-flavored
Markdown grade table: students, every lesson, average score, total score, and
course maximums. Generate the document in memory and enforce tenant scope.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest -q tests/backend/test_bot_report.py`
- Red confirmed: `backend.app.bot_report` and the summary service contract were absent.
- Green: Markdown report covers every lesson/student, escapes user-controlled
  table characters, calculates assigned-score average and total, and includes
  per-lesson/course maximums. Foreign tenant access is denied.
- Report is uploaded from memory as `course-N-summary.md`; no temporary report
  file is written.
- Full backend: `21 passed`, 89.12% coverage; Ruff format/lint, strict mypy,
  Bandit, and synchronized skills passed.
- Bot image rebuilt; backend, frontend, database, and recreated bot containers
  are running.

### M040-006 Add Academic Analytics And Lesson Deletion

Priority: P1
Status: `[x]`

Implement debtors for a selected lesson, a per-student Markdown report with
attendance rate, and confirmed tenant-safe lesson deletion.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest -q tests/backend/test_bot_analytics.py`
  failed because the analytics report contracts were not implemented.
- Green: analytics, report, and bot UI suite passed (`10 passed`).
- Full backend: `24 passed`, 89.97% coverage; Ruff format/lint, strict mypy,
  Bandit, and synchronized skills passed.
- The bot image was rebuilt and the recreated bot container is running alongside
  healthy backend and database containers.

### M040-007 Remove Superseded Single-Tenant Prototype

Priority: P2
Status: `[x]`

Remove the unused root-level CLI/bot/JSON prototype, its seed data and obsolete
dependencies after the tenant-safe bot and Mini App have replaced it. Keep the
canonical backend, bot launcher, frontend, migrations, and agent tooling intact.

Validation:

- Baseline: full backend passed (`24 passed`, 89.97% coverage) before cleanup.
- Refactor verification: backend `24 passed` at 89.97% coverage; Ruff
  format/lint, strict mypy, Bandit, frontend `4 passed`, ESLint, TypeScript/Vite
  production build, skills synchronization, pip-audit, and npm audit passed.
- Docker backend and bot images rebuilt without Flask/requests; backend and
  database are healthy and the bot container is running.
- Generated caches and frontend build output were removed. `.test-tmp` remains
  Git-ignored because Windows denies deletion of two sandbox-owned subfolders;
  it is not repository content and does not affect builds or commits.
