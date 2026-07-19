Always mention the name of the user.

# AGENTS.md

## Project

Student Tracker is a multi-user university gradebook whose target interface is
a Telegram Mini App, with a tenant-safe Telegram bot as an additional interface.
The stack is React/TypeScript, FastAPI, SQLAlchemy/Alembic, SQLite locally,
PostgreSQL in production, and Docker on a university-managed server.

Every production data path must be scoped by authenticated user and course.

## Repository Navigation

Before implementation:

1. Read `BOARD.md` and select one task id.
2. Read `docs/README.md` and resolve the changed path through `docs/_map.yml`.
3. Trace the active implementation from entrypoint to persistence/output.
4. Use the component classifications in
   `docs/architecture/component-registry.md`.
5. Update related contracts and architecture docs when behavior changes.

## Canonical Commands

```powershell
# Install backend and quality tools in Python 3.12 .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# Run backend locally
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload

# Full backend validation
.venv\Scripts\python.exe -m pytest -q --cov=backend
.venv\Scripts\python.exe -m ruff format --check backend tests
.venv\Scripts\python.exe -m ruff check backend tests
.venv\Scripts\python.exe -m mypy backend
.venv\Scripts\python.exe -m bandit -q -r backend
.venv\Scripts\python.exe -m pip_audit -r requirements.txt

# Frontend validation (run from frontend/)
npm test
npm run lint
npm run build

# Full-stack local runtime
docker compose up -d --build

# Validate synchronized repository skills
python tools/sync_skills.py --check
```

Use only `.venv\Scripts\python.exe` for project Python commands. The approved
gate set and thresholds are recorded in `docs/testing.md`.

## Work Protocol

- Work on one board task at a time and keep changes scoped.
- Prefer project conventions and canonical runtime paths.
- Use Red -> Verify Red -> Green -> Verify Green -> Refactor for behavior work.
- Add a durable regression test for every defect.
- Write Given-When-Then scenarios for new user-visible behavior.
- Run the smallest relevant check first, then the nearest affected suite.
- Record files, validation, blockers, and acceptance notes in the active task.
- Never weaken assertions, validation, authorization, or tenant isolation to
  make a check pass.

## Quality Gates

The production target requires:

- unit, integration, API contract, migration, and end-to-end tests;
- coverage thresholds on critical backend business and authorization logic;
- Ruff lint/format and strict mypy for Python;
- ESLint, Prettier, TypeScript strict mode, and frontend tests;
- Bandit, pip-audit, and npm dependency audit;
- Docker image build and health checks;
- secret-free CI with all gates required before merge;
- documentation updates for changed commands, contracts, architecture, or flow.

Unavailable gates must be reported explicitly; they must not be silently
treated as passed.

## Skills

Canonical skills live in `agent-skills/`. Generated copies live in
`.agents/skills/` and `.claude/skills/`. Edit the canonical source first, then
run `python tools/sync_skills.py` and verify with `--check`.

- `$project-bootstrap` — repository identity and operational documentation.
- `$tdd-workflow` — deterministic behavior changes and refactors.
- `$bdd-scenario-authoring` — observable acceptance behavior.
- `$regression-fix` — defects requiring a permanent reproducer.
- `$agent-evals` — AI/agent behavior only; currently outside product scope.
- `$zip-untracked-files` — package Git-untracked files on request.
