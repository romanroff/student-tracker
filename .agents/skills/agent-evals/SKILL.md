---
name: agent-evals
description: Design and run evaluations for prompts, models, retrieval, routing, tool use, structured outputs, and multi-step agent trajectories. Use when AI behavior changes or when failures should become regression datasets.
---

# Agent Evals

Evaluate both the result and the path that produced it. Prefer deterministic
graders for facts, schemas, and policy. Use model graders only for irreducibly
semantic criteria and calibrate them against human labels.

## Add An Eval

1. Define the objective and failure cost.
2. Choose an offline scripted suite by default. Mark provider-dependent cases as
   live.
3. Add representative, edge, adversarial, and historical failure data.
4. Include ground truth for expected route, permitted tool sequence, expected
   tool arguments, terminal state, citations or evidence, and structured output
   when applicable.
5. Grade deterministic fields exactly: schema validity, route, tool order,
   blocked unsafe calls, identifiers, numeric values, citations, and policy.
6. Grade trajectories, not only final answers.
7. Compare against the prior baseline and fail closed on safety, privacy,
   provenance, or contract regressions.

When an agent failure is found, save it as a regression case before changing
prompts, tools, retrieval, or orchestration.

Do not let a fluent final answer compensate for a wrong trajectory or missing
evidence.
