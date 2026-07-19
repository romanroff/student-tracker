"""Materialize canonical skills into Codex and Claude Code locations.

This is an optional maintenance tool, not a post-clone bootstrap step. The
template keeps `.agents/skills/` and `.claude/skills/` present so repo-local
skills work immediately after clone.

Usage:
    python tools/sync_skills.py
    python tools/sync_skills.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "agent-skills"
TARGETS = [
    ROOT / ".agents" / "skills",
    ROOT / ".claude" / "skills",
]


def directory_manifest(directory: Path) -> dict[str, str]:
    if not directory.exists() or not directory.is_dir():
        return {}

    manifest: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(directory).as_posix()
        manifest[relative_path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return manifest


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def sync_target(target: Path) -> None:
    remove_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize shared agent skills for Codex and Claude Code.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify generated copies without changing files.",
    )
    args = parser.parse_args()

    if not SOURCE.exists():
        print(f"Source directory does not exist: {SOURCE}", file=sys.stderr)
        return 1

    source_manifest = directory_manifest(SOURCE)

    if args.check:
        outdated = [
            target for target in TARGETS if directory_manifest(target) != source_manifest
        ]
        if outdated:
            print("Skills are out of sync:")
            for target in outdated:
                print(f"  - {target.relative_to(ROOT)}")
            print("Run: python tools/sync_skills.py")
            return 1
        print("Codex and Claude skills are synchronized.")
        return 0

    for target in TARGETS:
        sync_target(target)
        print(f"Synced: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
