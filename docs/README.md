# Student Tracker Documentation

Use `docs/_map.yml` to resolve source paths to the documents that govern them.

## Read By Task

- Product shape and security constraints: `docs/architecture/overview.md`
- Runtime ownership and migration status:
  `docs/architecture/component-registry.md`
- Telegram/backend work: `docs/domains/backend.md`, API contract, runtime flow
- Mini App work: `docs/domains/frontend.md`, UI and API contracts
- Database work: `docs/domains/data.md`, data-model contract
- Docker/CI/server work: `docs/domains/devops.md`, testing policy
- Behavior changes: `docs/behavior-contracts.md`, then `features/`
- Architecture decisions: `docs/adr/`

## Current Versus Target State

Documentation distinguishes implemented canonical runtime paths from future
product work. A target component is not canonical until its implementation and
validation exist.

## Update Rules

Update contracts when observable behavior or schemas change. Update runtime
flows when request, authorization, persistence, or failure paths change. Record
costly or hard-to-reverse decisions as ADRs.
