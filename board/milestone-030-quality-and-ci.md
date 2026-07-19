# Milestone M030: Quality And CI

## Goal

Implement the senior-level gates approved in `docs/testing.md` and make them
mandatory in CI.

## Tasks

### M030-001 Configure Test Levels

Priority: P1
Status: `[x]`

Configure pytest/coverage, PostgreSQL integration and migration tests, Vitest,
Testing Library, and Playwright.

Acceptance notes:

- Test directories are documented in `AGENTS.md` or `docs/README.md`.
- Targeted and full test commands are known.

Validation:

- Run the configured targeted test command.

### M030-002 Configure Lint And Format

Priority: P1
Status: `[x]`

Configure Ruff for Python and ESLint/Prettier for TypeScript.

Acceptance notes:

- Commands are documented in `AGENTS.md`.
- Tool configuration files are committed when needed.

Validation:

- Run lint and format check commands.

### M030-003 Configure Build And Type Checks

Priority: P1
Status: `[x]`

Configure strict mypy, TypeScript strict mode, frontend production build,
Bandit, pip-audit, npm audit, and Docker build/health validation.

Acceptance notes:

- Build command is documented.
- Type-check command is documented if the stack supports it.
- Syntax checks are not mislabeled as type checks.

Validation:

- Run build and type-check commands.

### M030-004 Configure CI

Priority: P2
Status: `[R]`

Add required CI jobs for tests/coverage, lint/format, types, security,
migrations, frontend build, and Docker images without production secrets.

Acceptance notes:

- CI runs install, tests, lint, and build/type checks as applicable.
- CI avoids live secrets unless explicitly configured.

Validation:

- `.github/workflows/quality.yml` mirrors local backend/frontend/security,
  migration, and Docker build gates. First hosted CI run remains pending.
