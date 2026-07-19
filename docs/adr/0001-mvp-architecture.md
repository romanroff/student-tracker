# ADR 0001: Tenant-Isolated Telegram Mini App Architecture

Status: accepted — 2026-07-19

## Decision

The MVP uses a React/TypeScript Mini App, FastAPI, SQLAlchemy/Alembic, SQLite
for isolated local tests, PostgreSQL in Docker/production, and Telegram
`initData` signature validation. A user owns courses; students, lessons, and
lesson records are reachable only through an owned course.

Local browser development may use `X-Dev-Telegram-*` headers only when
`DEV_AUTH_ENABLED=true`. Every public deployment must set it to `false` and
provide `BOT_TOKEN`. The API returns 404 for another tenant's course resources
to avoid disclosing their existence.

Docker Compose is the canonical local full-stack runtime. The production target
is a university-managed HTTPS server with external secrets and persistent
PostgreSQL storage.

## Consequences

- The legacy global `Course`/JSON bot is not part of the production path.
- Every new query must demonstrate course ownership scoping in tests.
- Alembic migrations are required for schema changes.
- Telegram authentication can be tested deterministically without live calls.
- Course sharing/roles are deferred; MVP ownership is one user per course.
