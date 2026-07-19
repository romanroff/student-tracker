# Project Board

This board is the task index for Student Tracker. The repository is migrating
from a single-course Python prototype to a multi-user Telegram Mini App.

## Protocol

- Work on one task id at a time.
- Keep changes scoped to the selected task.
- Add or update tests for behavior changes.
- Run the smallest relevant validation command first.
- Update the task with status, files changed, validation results, and blockers.
- When a milestone is fully complete and accepted, move its entire
  `board/milestone*.md` file into `board/archive/` and update this index.

## Status

- `[ ]` todo
- `[~]` in_progress
- `[?]` blocked
- `[R]` needs_review
- `[x]` done
- `[-]` deferred

## Priority

- P0 production, correctness, or security blocker
- P1 core product or architecture work
- P2 quality, scale, developer productivity
- P3 nice-to-have

## Index

| Milestone | Active | Purpose |
| --- | ---: | --- |
| [M000 Bootstrap](board/milestone-000-bootstrap.md) | 0 | Project identity, target stack, documentation map, and skills selected |
| [M010 Core Architecture](board/milestone-010-core-architecture.md) | 0 | Runtime shape, boundaries, contracts, and ADR established |
| [M020 Mini App Slice](board/milestone-020-first-feature.md) | 0 | Authenticated tenant-isolated MVP implemented and verified |
| [M030 Quality And CI](board/milestone-030-quality-and-ci.md) | 1 | Local gates configured; first hosted CI run pending |
| [M040 Telegram Bot Gradebook](board/milestone-040-telegram-bot.md) | 0 | Tenant-safe Telegram gradebook delivered; superseded prototype removed |
| [Archive](board/archive/) | 0 | Completed milestone files |
