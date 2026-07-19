# Milestone M010: Core Architecture

## Goal

Turn the approved Mini App target into implementable architecture decisions and
contracts without treating planned components as already available.

## Tasks

### M010-001 Define Runtime Flow

Priority: P1
Status: `[x]`

Finalize Telegram authentication, course authorization, request handling, and
transaction flow from Mini App to PostgreSQL.

Acceptance notes:

- `docs/runtime-flows/` contains the initial flow document.
- Entrypoints, consumers, external services, and failure modes are named.

Validation:

- Manual trace from entrypoint to consumer.

### M010-002 Define Component Registry

Priority: P1
Status: `[x]`

Keep component status current while prototype paths are replaced by the
FastAPI/React runtime.

Acceptance notes:

- Components are classified as `canonical`, `supporting`, `fallback`,
  `experimental`, `legacy`, `generated`, `test-only`, `unused`, or `unknown`.
- Canonical owner and consumer are clear for each core component.

Validation:

- Review against current source tree.

### M010-003 Define Contracts

Priority: P1
Status: `[x]`

Turn the initial API, UI, and data notes into versioned executable contracts.

Acceptance notes:

- `docs/contracts/` contains relevant contract notes.
- Tests or validators are identified for each critical contract.

Validation:

- Run contract tests if configured.

### M010-004 Capture Architecture Decisions

Priority: P2
Status: `[x]`

Record Telegram authentication, tenancy/roles, repository boundaries,
PostgreSQL deployment, and JSON migration decisions as ADRs.

Acceptance notes:

- `docs/adr/` contains initial ADRs for stack, storage, deployment, and major
  framework decisions when relevant.

Validation:

- `docs/adr/0001-mvp-architecture.md` records authentication, ownership,
  database, Docker, and legacy-path decisions.
