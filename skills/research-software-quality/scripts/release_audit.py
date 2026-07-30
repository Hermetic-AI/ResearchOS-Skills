#!/usr/bin/env python3
"""Audit a repository for release readiness and run an optional benchmark harness.

Combines two checks into one release-audit report:

1. **Release-readiness inventory** — scans a repository for the artifacts a
   release normally requires: a LICENSE, a README, a resolvable version, a
   changelog, a test entry point or test directory, and a CITATION.cff. Each
   item is reported present/absent with the path found.
2. **Benchmark harness** — runs a user-supplied command (or a tiny built-in
   probe) via subprocess and measures wall-clock time and, where the platform
   exposes it, peak resident memory. Results are recorded alongside the
   inventory so a release can cite a known performance baseline.

The script writes a JSON release-audit report to ``--out`` and prints it to
stdout. It does not execute the project's own test suite, publish a release,
or authorize distribution.

Dependencies: none (Python 3.8+ standard library only).

CLI usage:
    python release_audit.py repo_dir --out release-audit.json

    # With a real benchmark command and explicit version:
    python release_audit.py repo_dir --version 1.2.0 \\
        --benchmark "python -m pytest tests/ -q" --out release-audit.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

# Release artifacts to look for, with candidate names per category.
RELEASE_ARTIFACTS = {
    "license": ["LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "COPYING"],
    "readme": ["README.md", "README.rst", "README.txt", "README"],
    "changelog": ["CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "NEWS.md", "CHANGES.md"],
    "citation": ["CITATION.cff", "CITATION.bib", "CITATION"],
    "contributing": ["CONTRIBUTING.md", "CONTRIBUTING.rst"],
    "code_of_conduct": ["CODE_OF_CONDUCT.md"],
}

# Files that imply a test harness exists in the repository.
TEST_CANDIDATES = [
    "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml",
    "Makefile", "noxfile.py", ".github/workflows",
]


def _first_existing(root, names):
    """Return the first candidate path that exists under ``root``, or None."""
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def inventory_release(root):
    """Scan ``root`` for release artifacts; return per-category findings."""
    findings = {}
    present = 0
    for category, names in RELEASE_ARTIFACTS.items():
        path = _first_existing(root, names)
        findings[category] = {"present": path is not None,
                              "path": str(path) if path else None}
        if path is not None:
            present += 1

    test_path = _first_existing(root, TEST_CANDIDATES)
    tests_dir = root / "tests"
    if test_path is None and tests_dir.is_dir():
        test_path = tests_dir
    findings["tests"] = {"present": test_path is not None,
                         "path": str(test_path) if test_path else None}
    if test_path is not None:
        present += 1

    return findings, present


def resolve_version(root, override):
    """Resolve a release version from override, then common version files."""
    if override:
        return override, "command-line override"
    direct = root / "VERSION"
    if direct.is_file():
        return direct.read_text(encoding="utf-8").strip(), str(direct)
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("version"):
                _, _, value = line.partition("=")
                value = value.strip().strip('"').strip("'")
                if value:
                    return value, str(pyproject)
    init = root / "src" / "__init__.py"
    if not init.is_file():
        init = root / "__init__.py"
    if init.is_file():
        for line in init.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("__version__"):
                _, _, value = line.partition("=")
                value = value.strip().strip('"').strip("'")
                if value:
                    return value, str(init)
    return None, None


def run_benchmark(command, cwd, timeout):
    """Run ``command`` in ``cwd``; return time/memory metrics and any error.

    Memory is only reported on platforms that expose ``/proc`` status or the
    ``resource`` module; otherwise ``peak_memory_kb`` is null with a note.
    """
    metrics = {
        "command": command,
        "timeout_seconds": timeout,
        "returncode": None,
        "wall_time_seconds": None,
        "peak_memory_kb": None,
        "timed_out": False,
        "error": None,
        "memory_note": None,
    }
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            command, shell=True, cwd=str(cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        metrics["returncode"] = proc.returncode
    except subprocess.TimeoutExpired:
        metrics["timed_out"] = True
    except (OSError, ValueError) as exc:
        metrics["error"] = str(exc)
    metrics["wall_time_seconds"] = round(time.perf_counter() - start, 3)

    metrics["peak_memory_kb"] = _peak_memory_kb()
    if metrics["peak_memory_kb"] is None:
        metrics["memory_note"] = "peak memory unavailable on this platform"
    return metrics


def _peak_memory_kb():
    """Best-effort peak resident memory of the current process in KB."""
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux reports KB; macOS reports bytes. Normalize to KB.
        return usage if usage < 1024 * 1024 else usage // 1024
    except ImportError:
        pass
    status = Path("/proc/self/status")
    if status.is_file():
        for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("repo", help="path to the repository root to audit")
    p.add_argument("--release-version", default=None, help="override the release version")
    p.add_argument("--benchmark", default=None,
                   help="command to run as a benchmark probe (default: a tiny built-in probe)")
    p.add_argument("--benchmark-timeout", type=int, default=30,
                   help="benchmark timeout in seconds (default 30)")
    p.add_argument("--out", required=True, help="output release-audit report")
    p.add_argument("--force", action="store_true", help="replace an existing --out file")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = p.parse_args(argv)

    try:
        root = Path(args.repo).resolve()
        out = Path(args.out).resolve()
        if not root.is_dir():
            raise ValueError("repo must be a directory")
        if out.exists() and not args.force:
            raise ValueError("output exists; use --force only for a revised audit")

        findings, present_count = inventory_release(root)
        version, version_source = resolve_version(root, args.release_version)

        if args.benchmark:
            command = args.benchmark
        else:
            command = (sys.executable
                       + " -c 'import math; print(sum(math.sqrt(i) for i in range(10**6)))'")
        benchmark = run_benchmark(command, root, args.benchmark_timeout)

        required = ["license", "readme", "tests"]
        missing_required = [cat for cat in required if not findings[cat]["present"]]
        ready = not missing_required and version is not None

        report = {
            "schema_version": "1.0.0",
            "artifact_type": "software-release-audit",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "repository": str(root),
            "release_version": version,
            "version_source": version_source,
            "inventory": findings,
            "artifacts_present": present_count,
            "missing_required": missing_required,
            "benchmark": benchmark,
            "ready_for_human_review": ready,
            "warnings": [
                "Release audit only: it inventories files and runs one benchmark command. "
                "It does not execute the project's test suite, publish a release, verify "
                "license validity, or authorize distribution.",
            ],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: force UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
