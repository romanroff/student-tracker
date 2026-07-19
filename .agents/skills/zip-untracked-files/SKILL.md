---
name: zip-untracked-files
description: Create a U-files.zip archive containing only Git untracked files. Use when the user asks to zip U files, untracked files, Git status U/?? files, "сделай zip из U файлов", "архив U файлов", or similar requests to package newly created files without staged, modified, deleted, ignored, or tracked files.
---

# Zip Untracked Files

Use this skill to package the current repository's untracked Git files into `U-files.zip` for handoff or review.

## Workflow

1. Confirm the current directory is inside the target Git repository.
2. Run `git status --porcelain=v1 -z --untracked-files=all` or use `scripts/create_untracked_zip.py`.
3. Include only records with the `??` status. Do not include staged, modified, deleted, renamed, ignored, or tracked files.
4. Preserve paths relative to the repository root inside the archive.
5. Exclude the output archive itself, even if `U-files.zip` already appears as untracked.
6. Report the archive path and the number of included files. If no untracked files exist, say that no archive was created.

Prefer the bundled script because it handles NUL-delimited Git output, spaces in filenames, repository-root normalization, and output exclusion:

```powershell
.\.venv\Scripts\python.exe agent-skills\zip-untracked-files\scripts\create_untracked_zip.py
```

If the project venv is unavailable, use any Python 3 interpreter:

```powershell
python agent-skills\zip-untracked-files\scripts\create_untracked_zip.py
```

Use `--output <path>` only when the user asks for a custom archive name or location.

## Constraints

- Do not stage or commit files.
- Do not include ignored files unless the user explicitly asks for ignored files too.
- Do not delete, move, or rewrite repository files.
- Do not use ad hoc parsing of human-readable `git status`; use porcelain output or the bundled script.
