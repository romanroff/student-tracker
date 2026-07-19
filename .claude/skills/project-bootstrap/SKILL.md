---
name: project-bootstrap
description: Initialize a cloned template repository for a concrete project. Use when the repository still contains template placeholders, the project purpose or stack is unclear, the user asks to fill AGENTS.md/README/BOARD/docs, or a new project is being started from this template.
---

# Project Bootstrap

Use this skill before broad implementation when the repository still looks like
a template.

## Workflow

1. Read `AGENTS.md`, `BOARD.md`, and `board/milestone-000-bootstrap.md`.
2. Ask only the missing project questions needed to remove placeholders:
   project purpose, project type, stack, runtime, package manager, database,
   deployment target, canonical commands, and quality gates.
3. Propose the project shape before creating broad scaffolding.
4. After confirmation, update the operational files:
   `README.md`, `AGENTS.md`, `BOARD.md`, `docs/README.md`, `docs/_map.yml`,
   and `docs/architecture/component-registry.md`.
5. Add project-specific folders only when they follow from the confirmed stack.
6. Replace template language with project facts. Do not preserve generic
   placeholders as if they were decisions.

## Output Standards

- Keep `AGENTS.md` concise and operational.
- Put long procedures in `docs/agent_playbooks/` or a skill.
- Put active work in `BOARD.md` and `board/`.
- Put architecture facts in `docs/`.
- Use exact commands. Mark unknown commands as unresolved rather than guessing.
- Do not add framework, cloud, database, or CI dependencies without user
  confirmation.
