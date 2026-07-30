#!/usr/bin/env python3
"""Install ResearchOS skills to a Claude Code skills directory.

Copies (or symlinks) every skill from the repository's `skills/` directory
into the target skills directory (default: ~/.claude/skills/), so each skill
becomes available as a slash command in Claude Code.

Usage:
    python tools/install_skills.py                # install to ~/.claude/skills/
    python tools/install_skills.py --scope user   # same as above (explicit)
    python tools/install_skills.py --scope project # install to .claude/skills/ in cwd
    python tools/install_skills.py --symlink      # symlink instead of copy (dev mode)
    python tools/install_skills.py --dry-run      # show what would happen
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_SRC = REPO_ROOT / "skills"


def discover_skills() -> list[Path]:
    """Return all installable skill directories from skills/."""
    skills = []
    for path in sorted(SKILLS_SRC.iterdir()):
        if path.is_dir() and (path / "SKILL.md").is_file():
            skills.append(path)
    return skills


def install(skills: list[Path], dest: Path, symlink: bool, dry_run: bool) -> dict[str, int]:
    dest.mkdir(parents=True, exist_ok=True)
    counts = {"copied": 0, "symlinked": 0, "skipped": 0, "overwritten": 0}
    for src in skills:
        name = src.name
        target = dest / name
        if target.exists() or target.is_symlink():
            if dry_run:
                counts["skipped"] += 1
                print(f"  [dry-run] would overwrite: {name}")
                continue
            if target.is_symlink():
                target.unlink()
            else:
                shutil.rmtree(target)
            counts["overwritten"] += 1
        else:
            counts["copied"] += 1
        if dry_run:
            action = "symlink" if symlink else "copy"
            print(f"  [dry-run] {action}: {name} -> {target}")
            continue
        if symlink:
            target.symlink_to(src.resolve(), target_is_directory=True)
            counts["symlinked"] += 1
            print(f"  symlinked: {name}")
        else:
            shutil.copytree(src, target)
            print(f"  installed: {name}")
    return counts


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scope", choices=("user", "project"), default="user",
                   help="user=~/.claude/skills/, project=./.claude/skills/")
    p.add_argument("--symlink", action="store_true",
                   help="symlink instead of copy (useful during development)")
    p.add_argument("--dry-run", action="store_true", help="show what would happen without writing")
    args = p.parse_args(argv)

    if args.scope == "user":
        dest = Path.home() / ".claude" / "skills"
    else:
        dest = Path.cwd() / ".claude" / "skills"

    skills = discover_skills()
    if not skills:
        print("error: no skills found to install", file=sys.stderr)
        return 1

    print(f"Installing {len(skills)} skills to {dest}")
    counts = install(skills, dest, args.symlink, args.dry_run)
    print(f"\nDone: {counts.get('copied', 0)} copied, {counts.get('symlinked', 0)} symlinked, "
          f"{counts.get('overwritten', 0)} overwritten, {counts.get('skipped', 0)} skipped.")
    print(f"\nRestart Claude Code. Skills are available as slash commands: /researchos, /literature-reader, etc.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
