# Testing And Quality Gates

## Required Test Levels

- Unit tests for grade, attendance, averages, debtors, and authorization rules.
- Integration tests against real SQLite and disposable PostgreSQL databases.
- API contract tests for authentication, validation, errors, and tenant scope.
- Alembic migration tests for upgrade and downgrade paths.
- Frontend component tests for forms, tables, loading, empty, and error states.
- End-to-end tests for Telegram authentication and the primary teacher flow.
- Regression tests for every fixed defect, especially cross-tenant access.
- Bot service tests for ownership, atomic batch updates, and score validation.
- Bot UI tests for draft transitions, pagination, and Telegram's callback size limit.
- Bot service tests for multiline student normalization, duplicate handling, and atomic insertion.
- Bot service tests for semicolon lesson parsing, opaque type preservation,
  integer score totals, duplicate handling, and all-or-nothing validation.
- Bot service/UI tests for confirmed course deletion, tenant denial, and
  cascading removal of all academic records.
- Bot report tests for tenant scope, Markdown table escaping, missing grades,
  averages, totals, maximums, and `.md` document content.
- Bot analytics tests for missing/below-threshold debtors, student totals,
  explicit attendance rates, tenant denial, and cascading lesson deletion.

## Approved Tooling

Backend: pytest, pytest-cov, Ruff, strict mypy, Bandit, and pip-audit.
Frontend: Vitest, Testing Library, Playwright, ESLint, Prettier, TypeScript
strict mode, and npm audit. Infrastructure: Docker build and Compose health
checks. CI must run all applicable checks without production secrets.

## Merge Gates

- All tests pass with no skipped critical security or tenant-isolation cases.
- Backend business and authorization code reaches at least 90% branch coverage;
  the repository-wide threshold starts at 80% and may only increase.
- Formatting, lint, and strict type checks pass.
- High/critical dependency vulnerabilities are resolved or explicitly accepted
  with owner, rationale, and expiry.
- Bandit reports no unresolved high-severity findings.
- Frontend production build and Docker images build successfully.
- Database migrations upgrade from the previous release and downgrade in CI.
- Documentation and behavior contracts match observable changes.

Exact commands become canonical in `AGENTS.md` when `M030` adds the relevant
configuration. Until then these are required outcomes, not claims of passing
automation.
