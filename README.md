# Student Tracker

Student Tracker is a multi-user electronic gradebook with a Telegram bot and
Telegram Mini App for university teachers. It tracks students, lessons, grades,
attendance, averages, and debtors while keeping every teacher's courses isolated.

## MVP Capabilities

- Telegram or explicit local developer authentication.
- A private set of courses for each authenticated user.
- Student creation and deletion inside a course.
- Lesson creation with date/time and maximum score.
- Per-lesson attendance and grades with score validation.
- Responsive React Mini App and versioned FastAPI API.
- Telegram bot menus for courses, students, lessons, batch attendance, and grades.
- PostgreSQL persistence and Alembic migrations in Docker.

## Architecture

- Telegram Mini App frontend built with React and TypeScript.
- FastAPI backend with SQLAlchemy and Alembic migrations.
- Telegram `initData` validation for authentication.
- SQLite for local development and PostgreSQL in production.
- Docker deployment on a university-managed server.
- Tenant isolation by Telegram user, course ownership, and explicit membership.

See `docs/architecture/overview.md` for runtime boundaries.

## Local Full-Stack Run

Copy `.env.example` to `.env`, keep `DEV_AUTH_ENABLED=true`, then run:

```powershell
docker compose up -d --build
```

Open `http://localhost:8080`. The local UI uses developer id `101`. Data is
stored in the `postgres_data` Docker volume.

The verified MVP supports per-user courses, students, lessons, attendance, and
grades. `DEV_AUTH_ENABLED=true` is strictly for localhost; disable it before
exposing the application to a network.

To stop the application without deleting data:

```powershell
docker compose down
```

## Local Python 3.12 Development

Requires Python 3.12.

```powershell
F:\soft\Python\Python312\python.exe -m venv .venv
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:DEV_AUTH_ENABLED = "true"
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Run the frontend separately:

```powershell
cd frontend
npm install
npm run dev
```

## Telegram Bot Setup

The bot works locally through long polling and does not require a domain,
public HTTPS URL, or Mini App. Put `BOT_TOKEN` in `.env`; `WEBAPP_URL` is
optional and only adds an extra Mini App button. Start the bot profile:

```powershell
docker compose --profile telegram up -d --build
```

`/start` opens an inline menu. A teacher can create courses and lessons, paste
several student names in one message (one name per line), manage students, mark a lesson's attendance in a paginated checkbox list, save all
attendance values atomically, and enter or clear scores. All bot operations
are scoped by the sender's Telegram id and use the same database as the Mini
App.

The course menu includes confirmed deletion. Confirmation removes the course
and its students, lessons, grades, and attendance; ownership is checked before
the destructive operation.

The `📊 Сводка (.md)` course button sends a generated Markdown document with
one column per lesson, one row per student, average and total scores, and a
maximum-score row. The report is generated in memory and tenant-scoped.

Selecting a student downloads a personal `.md` report with scores, average,
total, and attendance rate. A lesson menu can generate a debtors `.md` for an
entered passing score or delete the lesson after explicit confirmation.

Several lessons can be pasted in one message using
`Название; тип; целый максимум`. The type is stored exactly as supplied; the
bot does not infer scoring rules from it. The complete message is validated
before insertion and the response includes the sum of maximum scores.

The Mini App itself still requires a public HTTPS URL. When one is available,
set `DEV_AUTH_ENABLED=false` and `WEBAPP_URL=https://...`.

## Quality Commands

```powershell
.venv\Scripts\python.exe -m pytest -q --cov=backend
.venv\Scripts\python.exe -m ruff format --check backend tests
.venv\Scripts\python.exe -m ruff check backend tests
.venv\Scripts\python.exe -m mypy backend
.venv\Scripts\python.exe -m bandit -q -r backend
.venv\Scripts\python.exe -m pip_audit -r requirements.txt
cd frontend
npm test
npm run lint
npm run build
```

GitHub Actions repeats these gates, verifies Alembic upgrade/downgrade, and
builds the Docker images.

## Documentation

Start with `docs/README.md`. Work is tracked in `BOARD.md`.
