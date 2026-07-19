# Data Domain

SQLite is the local development database and PostgreSQL is the production
system of record. SQLAlchemy models and Alembic migrations are the canonical
schema path. No JSON or text-file persistence participates in the runtime.

All academic records are course-owned and all access paths are tenant-scoped.
Use stable identifiers, foreign keys, uniqueness constraints, transactions,
timestamps, and indexed ownership relationships. Migration CI must exercise
upgrade and downgrade. Production operation requires encrypted transport,
least-privilege credentials, backups, restore drills, and defined retention.

See `docs/contracts/data-model.md` for entity invariants.
