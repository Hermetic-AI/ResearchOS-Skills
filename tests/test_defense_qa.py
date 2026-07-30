"""Tests for thesis-defense-assistant/scripts/defense_qa.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "thesis-defense-assistant" / "scripts" / "defense_qa.py"
INIT = ROOT / "skills" / "thesis-defense-assistant" / "scripts" / "init_defense_brief.py"

BRIEF = {
    "schema_version": "1.0.0",
    "artifact_type": "thesis-defense-brief",
    "thesis_title": "Memory for Agents",
    "candidate": "A. Researcher",
    "research_question": "Does structured memory improve agent reliability?",
    "contributions": [
        {"title": "A memory-stream abstraction", "evidence": "chapter-3"},
        "An evaluation protocol",
    ],
    "evidence_ledger": [
        {"location": "chapter-3", "kind": "chapter"},
        {"location": "table-4", "kind": "table"},
    ],
    "limitations": ["small sample of domains", {"text": "single language"}],
    "anticipated_questions": [],
    "follow_up_actions": [],
    "warnings": [],
}


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def make_brief(tmp_path: Path, data: dict | None = None) -> Path:
    path = tmp_path / "brief.json"
    path.write_text(json.dumps(data or BRIEF, ensure_ascii=False), encoding="utf-8")
    return path


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_report_metadata_and_question_generation(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "20", "--minutes", "30", "--out", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == "1.0.0"
    assert report["artifact_type"] == "thesis-defense-qa"
    assert report["tool_version"] == "0.1.0"
    assert "warnings" in report and report["warnings"]
    # research question (2) + 2 contributions * 3 + 2 limitations * 2 = 12.
    assert report["question_count"] == 12
    topics = {q["topic"] for q in report["questions"]}
    assert {"research question", "contribution", "limitation"}.issubset(topics)


def test_simulated_qa_has_placeholder_answers(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "20", "--minutes", "30", "--out", out)
    report = json.loads(result.stdout)
    for q in report["questions"]:
        assert q["candidate_prepared_response"] is None
        assert q["status"] == "open"
        assert q["suggested_evidence_locations"] == ["chapter-3", "table-4"]


def test_timing_audit_flags_rushed_deck(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "60", "--minutes", "30", "--out", out)
    report = json.loads(result.stdout)
    assert report["timing"]["minutes_per_slide"] == 0.5
    assert any(f["check"] == "timing" for f in report["findings"])
    assert report["ready_for_human_review"] is False


def test_timing_audit_flags_sparse_deck(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "5", "--minutes", "60", "--out", out)
    report = json.loads(result.stdout)
    assert report["timing"]["minutes_per_slide"] == 12.0
    assert any(f["check"] == "timing" and "drag" in f["issue"] for f in report["findings"])


def test_timing_with_zero_slides_reports_finding(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "0", "--minutes", "30", "--out", out)
    report = json.loads(result.stdout)
    assert report["timing"]["minutes_per_slide"] is None
    assert any(f["check"] == "timing" for f in report["findings"])


def test_coverage_detects_uncovered_contribution(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "20", "--minutes", "30", "--out", out)
    report = json.loads(result.stdout)
    # "An evaluation protocol" is a plain string contribution with no evidence link.
    uncovered = [f for f in report["findings"] if f["check"] == "coverage"]
    assert uncovered
    assert any(f["contribution"] == "An evaluation protocol" for f in uncovered)


def test_max_difficulty_caps_question_set(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    all_q = run("--brief", src, "--slides", "20", "--minutes", "30",
                "--max-difficulty", "critical", "--out", out)
    found_q = run("--brief", src, "--slides", "20", "--minutes", "30",
                  "--max-difficulty", "foundational", "--out", out, "--force")
    all_count = json.loads(all_q.stdout)["question_count"]
    found_count = json.loads(found_q.stdout)["question_count"]
    assert found_count < all_count
    # Foundational cap excludes all methodological and critical questions.
    for q in json.loads(found_q.stdout)["questions"]:
        assert q["difficulty"] == "foundational"


def test_empty_brief_still_produces_report(tmp_path: Path):
    empty = {
        "schema_version": "1.0.0", "artifact_type": "thesis-defense-brief",
        "thesis_title": "T", "candidate": "C",
    }
    src = make_brief(tmp_path, empty)
    out = tmp_path / "qa.json"
    result = run("--brief", src, "--slides", "10", "--minutes", "20", "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["question_count"] == 0
    assert report["ready_for_human_review"] is True


def test_output_protected_then_forced(tmp_path: Path):
    src = make_brief(tmp_path)
    out = tmp_path / "qa.json"
    out.write_text("keep", encoding="utf-8")
    protected = run("--brief", src, "--slides", "20", "--minutes", "30", "--out", out)
    assert protected.returncode != 0
    assert out.read_text(encoding="utf-8") == "keep"
    forced = run("--brief", src, "--slides", "20", "--minutes", "30", "--out", out, "--force")
    assert forced.returncode == 0
    assert out.read_text(encoding="utf-8") != "keep"


def test_rejects_non_brief_input(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"artifact_type": "other"}), encoding="utf-8")
    out = tmp_path / "qa.json"
    result = run("--brief", bad, "--slides", "20", "--minutes", "30", "--out", out)
    assert result.returncode != 0
    assert "thesis-defense-brief" in result.stderr


def test_init_then_qa_round_trip(tmp_path: Path):
    brief = tmp_path / "brief.json"
    init_result = subprocess.run(
        [sys.executable, str(INIT), "--out", brief, "--thesis-title", "T",
         "--candidate", "C"],
        capture_output=True, text=True, encoding="utf-8", check=False)
    assert init_result.returncode == 0, init_result.stderr
    out = tmp_path / "qa.json"
    result = run("--brief", brief, "--slides", "15", "--minutes", "20", "--out", out)
    assert result.returncode == 0, result.stderr
    assert out.exists()
