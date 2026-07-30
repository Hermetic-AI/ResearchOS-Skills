#!/usr/bin/env python3
"""Validate ResearchOS skill structure without third-party dependencies."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_RE = re.compile(r"`((?:scripts|references|assets)/[^`\s]+)`")
YAML_VALUE_RE = re.compile(r'^\s{2}([a-z_]+):\s+"(.*)"\s*$')


@dataclass(frozen=True)
class Finding:
    level: str
    path: Path
    message: str

    def render(self, root: Path) -> str:
        try:
            location = self.path.relative_to(root)
        except ValueError:
            location = self.path
        return f"{self.level}: {location}: {self.message}"


def skill_directories(root: Path) -> list[Path]:
    """Return skill directories. Skills live under skills/; fall back to the
    repository root for backward compatibility with single-skill checkouts."""
    skills_root = root / "skills"
    if skills_root.is_dir():
        return sorted(path.parent for path in skills_root.glob("*/SKILL.md"))
    return sorted(path.parent for path in root.glob("*/SKILL.md"))


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("SKILL.md frontmatter is not closed") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, "\n".join(lines[end + 1 :])


def validate_openai_yaml(skill_dir: Path, name: str) -> list[Finding]:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        return [Finding("ERROR", path, "missing agents/openai.yaml")]
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = YAML_VALUE_RE.match(line)
        if match:
            values[match.group(1)] = match.group(2)
    findings = []
    for key in ("display_name", "short_description", "default_prompt"):
        if not values.get(key):
            findings.append(Finding("ERROR", path, f"missing quoted interface.{key}"))
    short = values.get("short_description", "")
    if short and not 25 <= len(short) <= 64:
        findings.append(Finding("ERROR", path, "short_description must be 25-64 characters"))
    prompt = values.get("default_prompt", "")
    if prompt and f"${name}" not in prompt:
        findings.append(Finding("ERROR", path, f"default_prompt must mention ${name}"))
    return findings


def validate_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_file = skill_dir / "SKILL.md"
    try:
        metadata, body = parse_frontmatter(skill_file)
    except (OSError, UnicodeError, ValueError) as exc:
        return [Finding("ERROR", skill_file, str(exc))]

    if set(metadata) != {"name", "description"}:
        findings.append(
            Finding("ERROR", skill_file, "frontmatter must contain only name and description")
        )
    name = metadata.get("name", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        findings.append(Finding("ERROR", skill_file, "invalid skill name"))
    if name != skill_dir.name:
        findings.append(Finding("ERROR", skill_file, "name must match directory name"))
    if not metadata.get("description"):
        findings.append(Finding("ERROR", skill_file, "description must not be empty"))
    if len(metadata.get("description", "")) > 1024:
        findings.append(Finding("ERROR", skill_file, "description exceeds 1024 characters"))
    if len(body.splitlines()) > 500:
        findings.append(Finding("ERROR", skill_file, "body exceeds 500 lines"))

    for relative in RESOURCE_RE.findall(body):
        if not (skill_dir / relative).exists():
            findings.append(Finding("ERROR", skill_file, f"missing referenced resource: {relative}"))

    for script in sorted((skill_dir / "scripts").glob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except (OSError, UnicodeError, SyntaxError) as exc:
            findings.append(Finding("ERROR", script, f"Python syntax/read failure: {exc}"))

    findings.extend(validate_openai_yaml(skill_dir, name))
    return findings


def validate_repository(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    skills = skill_directories(root)
    if not skills:
        return [Finding("ERROR", root, "no skill directories found")]
    for skill in skills:
        findings.extend(validate_skill(skill))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    root = args.root.resolve()
    findings = validate_repository(root)
    for finding in findings:
        print(finding.render(root))
    errors = sum(f.level == "ERROR" for f in findings)
    if errors:
        print(f"Validation failed: {errors} error(s).", file=sys.stderr)
        return 1
    print(f"Validated {len(skill_directories(root))} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
