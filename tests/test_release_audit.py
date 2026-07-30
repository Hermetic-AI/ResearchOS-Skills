"""Tests for research-software-quality/scripts/release_audit.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "research-software-quality" / "scripts" / "release_audit.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_version_flag():
    # --version needs a repo arg; pass a temp dir.
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_full_repo_passes_audit(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE", "Apache-2.0")
    write_file(repo / "README.md", "# Project")
    write_file(repo / "pyproject.toml", 'name = "pkg"\nversion = "1.2.0"\n')
    write_file(repo / "CHANGELOG.md", "# Changelog\n")
    write_file(repo / "CITATION.cff", "cff-version: 1.2.0\n")
    (repo / "tests").mkdir()
    write_file(repo / "tests" / "test_x.py", "def test_y(): pass\n")
    out = tmp_path / "audit.json"
    result = run(str(repo), "--out", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == "1.0.0"
    assert report["artifact_type"] == "software-release-audit"
    assert report["tool_version"] == "0.1.0"
    assert "warnings" in report and report["warnings"]
    assert report["release_version"] == "1.2.0"
    assert report["version_source"].endswith("pyproject.toml")
    assert report["missing_required"] == []
    assert report["ready_for_human_review"] is True
    for category in ("license", "readme", "tests"):
        assert report["inventory"][category]["present"] is True


def test_missing_required_artifacts_flagged(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    write_file(repo / "src" / "main.py", "print('hi')\n")
    out = tmp_path / "audit.json"
    result = run(str(repo), "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert set(report["missing_required"]) == {"license", "readme", "tests"}
    assert report["ready_for_human_review"] is False
    assert report["inventory"]["license"]["present"] is False


def test_version_resolution_order(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE")
    write_file(repo / "README.md")
    (repo / "tests").mkdir()
    # VERSION file takes precedence over pyproject.toml.
    write_file(repo / "VERSION", "9.9.9\n")
    write_file(repo / "pyproject.toml", 'version = "1.0.0"\n')
    out = tmp_path / "audit.json"
    result = run(str(repo), "--out", out)
    report = json.loads(result.stdout)
    assert report["release_version"] == "9.9.9"
    assert report["version_source"].endswith("VERSION")


def test_release_version_override(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE")
    write_file(repo / "README.md")
    (repo / "tests").mkdir()
    write_file(repo / "VERSION", "1.0.0\n")
    out = tmp_path / "audit.json"
    result = run(str(repo), "--release-version", "2.0.0-rc1", "--out", out)
    report = json.loads(result.stdout)
    assert report["release_version"] == "2.0.0-rc1"
    assert report["version_source"] == "command-line override"


def test_benchmark_command_runs_and_records_time(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE")
    write_file(repo / "README.md")
    (repo / "tests").mkdir()
    out = tmp_path / "audit.json"
    cmd = f"{sys.executable} -c \"import time; time.sleep(0.05); print('done')\""
    result = run(str(repo), "--benchmark", cmd, "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["benchmark"]["returncode"] == 0
    assert report["benchmark"]["wall_time_seconds"] >= 0.05
    assert report["benchmark"]["timed_out"] is False


def test_benchmark_respects_timeout(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE")
    write_file(repo / "README.md")
    (repo / "tests").mkdir()
    out = tmp_path / "audit.json"
    cmd = f"{sys.executable} -c \"import time; time.sleep(5)\""
    result = run(str(repo), "--benchmark", cmd, "--benchmark-timeout", "1", "--out", out)
    report = json.loads(result.stdout)
    assert report["benchmark"]["timed_out"] is True


def test_rejects_non_directory_repo(tmp_path: Path):
    not_a_dir = tmp_path / "file.txt"
    not_a_dir.write_text("x", encoding="utf-8")
    out = tmp_path / "audit.json"
    result = run(str(not_a_dir), "--out", out)
    assert result.returncode != 0
    assert "directory" in result.stderr.lower()


def test_output_protected_then_forced(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE")
    write_file(repo / "README.md")
    (repo / "tests").mkdir()
    out = tmp_path / "audit.json"
    out.write_text("keep", encoding="utf-8")
    protected = run(str(repo), "--out", out)
    assert protected.returncode != 0
    assert out.read_text(encoding="utf-8") == "keep"
    forced = run(str(repo), "--out", out, "--force")
    assert forced.returncode == 0
    assert out.read_text(encoding="utf-8") != "keep"


def test_report_written_to_disk_matches_stdout(tmp_path: Path):
    repo = tmp_path / "repo"
    write_file(repo / "LICENSE")
    write_file(repo / "README.md")
    (repo / "tests").mkdir()
    out = tmp_path / "audit.json"
    result = run(str(repo), "--out", out)
    assert result.returncode == 0
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    from_stdout = json.loads(result.stdout)
    assert on_disk == from_stdout
