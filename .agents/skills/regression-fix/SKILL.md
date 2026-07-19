---
name: regression-fix
description: Diagnose and fix defects with a permanent reproducer. Use for bug reports, broken behavior, incorrect outputs, unsafe tool behavior, failed integrations, data errors, prompt failures, or any issue that must not recur.
---

# Regression Fix

1. Select one board task id and capture the smallest failing input.
2. Remove secrets and unrelated production data.
3. Classify the boundary: unit, integration, contract, behavior, eval, or live
   provider.
4. Add one regression test named for the wrong behavior and expected correction.
5. Run it against unchanged implementation. Require the expected assertion
   failure. Environment or import errors are not valid Red.
6. Identify the first incorrect state transition, transform, policy decision, or
   external boundary assumption.
7. Apply the smallest fix at the owner of the defect.
8. Rerun the regression, owning module tests, and relevant eval or integration
   suite.
9. Keep the regression permanently.

For agent failures, inspect route, ordered tool calls, tool arguments, evidence,
policy decisions, and terminal state, not only final text.

Record root cause, Red command/result, Green command/result, changed files, and
unavailable live services in the active board task.
