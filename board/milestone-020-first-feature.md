# Milestone M020: Authenticated Course Roster Slice

## Goal

Deliver authentication, course ownership, roster display, and student creation
through the Mini App with tenant isolation.

## Tasks

### M020-001 Define First Vertical Slice

Priority: P0
Status: `[x]`

Define: a Telegram-authenticated teacher creates/selects a course, views its
student roster, and adds a student.

Acceptance notes:

- The behavior is described in user or operator language.
- Inputs, outputs, and success criteria are explicit.
- Test boundary is selected.

Validation:

- Scope confirmed by the user on 2026-07-19: each authenticated teacher owns
  their students and lessons and manages grades and attendance in the Mini App.

### M020-002 Add Behavior Contract

Priority: P1
Status: `[x]`

Add happy-path, validation, forged/expired authentication, and cross-tenant
Given-When-Then scenarios.

Acceptance notes:

- Scenario lives under `features/`.
- Fixture and expected result are identified when useful.
- Automated test binding exists or is deliberately deferred.

Validation:

- `features/mvp_gradebook.feature` covers record management, forged identity,
  course listing, and cross-tenant access. Automated bindings are implemented
  in backend API tests under M020-003.

### M020-003 Implement First Slice

Priority: P0
Status: `[x]`

Implement the React -> FastAPI -> SQLAlchemy slice with migrations and TDD.

Acceptance notes:

- Red and Green commands are recorded.
- Targeted validation passes.
- Docs are updated for changed behavior.

Validation:

- Red: `.venv\Scripts\python.exe -m pytest tests/backend/test_mvp_api.py -q`
  failed with three expected 404 responses before API implementation.
- Green: 7 backend tests pass with 85% branch coverage; 4 frontend tests,
  ESLint, strict TypeScript production build, Ruff, mypy, Bandit, and dependency
  audit pass.
- Docker smoke: PostgreSQL, FastAPI, and React/Nginx containers build and report
  healthy. Alembic revision `0001_mvp_gradebook` is applied.
- Tenant smoke: two dev-auth teachers list only their own course; cross-tenant
  student reads and writes both return 404; attendance `true` and score `9/10`
  persist through the register API and backend restart.
- Browser smoke: desktop and 390x844 Mini App flows create a course, student,
  lesson, and save attendance with score `8.5/10`.
- Regression fixes: bootstrap always leaves loading state after API failure;
  developer display names are header-safe; async forms retain a stable form
  reference through API awaits. Permanent Vitest coverage was added.

### M020-004 Review Developer Experience

Priority: P2
Status: `[x]`

Check whether install, run, and test flow is clear for a new contributor.

Acceptance notes:

- README quick start works or blockers are documented.
- Common local failure modes are documented.

Validation:

- README documents Python 3.12 `.venv`, Docker, local browser, Telegram, quality,
  and environment setup.
