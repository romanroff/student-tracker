---
name: tdd-workflow
description: Enforce test-first development for deterministic logic, behavior changes, refactors, and implementation tasks. Use when adding or changing code behavior, fixing a defect, or implementing a board task that needs Red, verified failure, minimal Green, verified success, and safe refactoring.
---

# TDD Workflow

Work on one board task and one vertical slice at a time.

## Execute One Slice

1. State one observable behavior and the smallest relevant test command.
2. Red: add one test through a public interface where practical.
3. Verify Red: run only that test. Confirm it fails for the missing behavior,
   not for import, fixture, environment, or syntax problems.
4. Green: implement the minimum code needed for that behavior.
5. Verify Green: rerun the targeted test, then the nearest affected suite when
   available.
6. Refactor only while green. Rerun affected tests after refactoring.
7. Repeat for the next behavior.

## Test Boundary

- Unit tests: pure logic, models, transforms, validators.
- Integration tests: storage, network, service, filesystem, and framework
  boundaries.
- Contract tests: schemas, payloads, public APIs, file formats, and CLI output.
- Behavior tests: user-visible workflows.
- Evals: prompts, models, tools, retrieval, routing, and agent trajectories.

Prefer real project code over mocks. Mock external services when needed, but
preserve the consumed response shape.

## Finish

Record Red and Green commands, results, changed files, and remaining risk in the
active board task.
