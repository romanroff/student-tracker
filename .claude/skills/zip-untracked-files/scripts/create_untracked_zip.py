"""Create U-files.zip from Git untracked files only."""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result.stdout


def repo_root(cwd: Path) -> Path:
    return Path(run_git(["rev-parse", "--show-toplevel"], cwd).strip()).resolve()


def untracked_files(root: Path) -> list[Path]:
    status = run_git(
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        root,
    )
    files: list[Path] = []
    for entry in status.split("\0"):
        if not entry.startswith("?? "):
            continue
        relative = Path(entry[3:])
        absolute = (root / relative).resolve()
        if absolute.is_file():
            files.append(absolute)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def create_zip(root: Path, output: Path, files: list[Path]) -> int:
    output = output.resolve()
    selected = [path for path in files if path.resolve() != output]
    if not selected:
        print("No untracked files found; no archive created.")
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in selected:
            archive.write(path, path.relative_to(root).as_posix())

    print(f"Created {output} with {len(selected)} untracked file(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a zip archive containing Git untracked files only.",
    )
    parser.add_argument(
        "--output",
        default="U-files.zip",
        help="Archive path. Relative paths are resolved from the repository root.",
    )
    args = parser.parse_args()

    try:
        root = repo_root(Path.cwd())
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        return create_zip(root, output, untracked_files(root))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
