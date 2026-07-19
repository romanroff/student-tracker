# Milestone M000: Project Bootstrap

## Goal

Define Student Tracker's product direction and operating conventions.

## Tasks

### M000-001 Define Project Identity

Priority: P0
Status: `[x]`

Ask the user:

- What is this project about?
- What category is it: website, backend, ML, AI agent, SQL/data, CLI, library,
  mobile, infrastructure, or other?
- Who is the user or operator?
- What is the first useful outcome?
- What constraints matter: security, privacy, cost, latency, compliance,
  offline use, deployment target, or integrations?

Acceptance notes:

- `README.md` names the project and describes its purpose.
- `AGENTS.md` no longer contains unresolved project identity placeholders.
- `BOARD.md` points to the right first milestones.

Validation:

- User confirmed Telegram Mini App as the target on 2026-07-19.
- Target users are university teachers managing isolated course rosters.

### M000-002 Define Stack And Commands

Priority: P0
Status: `[x]`

Capture the canonical stack and commands for install, run, test, targeted test,
lint, format, build, and type-check.

Acceptance notes:

- `AGENTS.md` command placeholders are replaced.
- `README.md` has a quick start.
- `.env.example` exists if configuration is needed.

Validation:

- Python 3.12 and the current prototype commands are documented.
- Target stack confirmed: React/TypeScript, FastAPI, SQLAlchemy/Alembic,
  SQLite/PostgreSQL, Docker on a university server.
- Full quality commands remain implementation work in `M030` and are not
  presented as currently available.

### M000-003 Build Documentation Map

Priority: P1
Status: `[x]`

Define the initial documentation navigation for the project.

Acceptance notes:

- `docs/README.md` describes what to read by task type.
- `docs/_map.yml` maps source paths to relevant docs.
- `docs/architecture/component-registry.md` includes initial components or a
  clear placeholder table.

Validation:

- `docs/_map.yml` maps current Python files and planned application roots.

### M000-004 Specialize Skills

Priority: P1
Status: `[x]`

Review generic skills and add project-specific skills only where they reduce
repeat mistakes or encode fragile process.

Acceptance notes:

- Generic skills are kept or removed deliberately.
- Project-specific skill descriptions contain clear trigger conditions.
- `.agents/skills/` and `.claude/skills/` match the intended skill set.

Validation:

- Generic engineering skills retained; AI eval skill marked outside current
  product scope.
- Run `python tools/sync_skills.py --check` after documentation bootstrap.
