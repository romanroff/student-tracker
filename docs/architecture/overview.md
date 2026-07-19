# Architecture Overview

## Purpose And Users

Student Tracker is a university gradebook for teachers. Its target interface is
a Telegram Mini App for managing courses, students, topics, grades,
attendance, averages, and debtors. Each teacher may own multiple courses and
may grant explicit course access to other users.

## Current Runtime

FastAPI, React, SQLAlchemy/Alembic, PostgreSQL/SQLite, and Docker implement the
tenant-isolated gradebook. The canonical Telegram bot uses long polling and
the same database services, so it can manage the journal locally without a
public Mini App URL. The Mini App remains the richer HTTPS interface.

## Request Identity

1. Telegram opens the React/TypeScript Mini App and supplies `initData`.
2. The frontend sends `initData` to FastAPI over HTTPS.
3. The backend validates its signature and freshness using the bot token.
4. The authenticated Telegram user is resolved to an application user.
5. Authorization scopes every operation to an owned course or course
   membership.
6. SQLAlchemy writes transactional data through repositories/services.
7. SQLite supports local development; PostgreSQL is authoritative in
   production.

For bot updates, Telegram supplies the authenticated sender id directly to the
bot process. The service resolves that id to an application user and still
checks course ownership for every callback resource id.

## Deployment

Frontend and backend are packaged as Docker workloads on a
university-managed server. Production requires HTTPS, PostgreSQL persistence,
secrets outside images and source control, health checks, logs, backups, and a
documented rollback procedure.

## Critical Constraints

- Telegram `initData` must be validated server-side; client identity is never
  trusted directly.
- Every student, topic, grade, and attendance record belongs to a course.
- Every course operation requires ownership or explicit membership.
- Cross-tenant reads and writes are security failures.
- Database migrations and backups must be reversible and tested.
- Personal and academic data must not be written to application logs.

Detailed boundaries live in `docs/contracts/` and decisions should be captured
as ADRs before implementation.
