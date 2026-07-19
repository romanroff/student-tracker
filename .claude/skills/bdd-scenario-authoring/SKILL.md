---
name: bdd-scenario-authoring
description: Author executable Given-When-Then behavior contracts for observable product, API, CLI, data, ML, or agent behavior. Use when acceptance criteria need examples or when behavior changes should be described before implementation.
---

# BDD Scenario Authoring

Write behavior in domain language before implementation.

## Author A Scenario

1. Name the observable capability, not an internal function.
2. Write `Given` as known state, input data, permissions, configuration, or
   external context.
3. Write `When` as one user or system action. Hide implementation details.
4. Write `Then` as externally visible, testable outcomes.
5. Add fixtures and expected structured results when useful.
6. Bind the scenario to an automated test unless the project deliberately uses
   manual acceptance for that behavior.

## Quality Gate

Reject scenarios that name private methods in `When`, assert only call counts,
omit important input state, use vague outcomes such as "works", or require live
services for deterministic behavior.

Use Scenario Outline only when all rows share the same rule and remain readable.
