"""Tests for patent-prior-art-search/scripts/patent_family.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "patent-prior-art-search" / "scripts" / "patent_family.py"
INIT = ROOT / "skills" / "patent-prior-art-search" / "scripts" / "init_search_ledger.py"

LEDGER = {
    "schema_version": "1.0.0",
    "artifact_type": "prior-art-search-ledger",
    "subject": "widget with lever and spring",
    "cutoff_date": "2024-01-01",
    "patent_records": [
        {"pub_number": "US100A", "title": "Widget", "filing_date": "2020-01-15",
         "priority_date": "2019-06-01", "publication_date": "2021-03-01",
         "jurisdiction": "US", "status": "granted",
         "claims": ["a widget comprising a lever and a spring"]},
        {"pub_number": "EP200B", "title": "Widget", "filing_date": "2020-07-20",
         "priority_date": "2019-06-01", "jurisdiction": "EP", "status": "pending",
         "claims": ["widget with lever spring and hinge"]},
        {"pub_number": "JP300C", "title": "Old Widget", "filing_date": "2018-01-01",
         "priority_date": "2017-01-01", "jurisdiction": "JP", "status": "expired",
         "claims": ["a device with a lever"]},
        {"pub_number": "US999FUTURE", "title": "New Widget", "filing_date": "2024-06-01",
         "priority_date": "2024-02-01", "jurisdiction": "US", "status": "pending",
         "claims": ["widget with lever spring and hinge"]},
    ],
    "family_links": [
        {"family_id": "F1", "members": ["US100A", "EP200B"]},
    ],
    "feature_matrix": [],
    "query_log": [],
    "non_patent_records": [],
    "scope_limitations": [],
    "counsel_review": None,
    "warnings": [],
}

TARGET_CLAIMS = ["a widget comprising a lever and a spring mechanism"]


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def make_ledger(tmp_path: Path, data: dict | None = None) -> Path:
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(data or LEDGER, ensure_ascii=False), encoding="utf-8")
    return path


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_report_metadata(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--out", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == "1.0.0"
    assert report["artifact_type"] == "patent-family-analysis"
    assert report["tool_version"] == "0.1.0"
    assert "warnings" in report and report["warnings"]


def test_family_grouping_and_singletons(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--out", out)
    report = json.loads(result.stdout)
    # F1 (US100A, EP200B) + JP300C singleton + US999FUTURE singleton = 3 families, 4 members.
    assert report["family_count"] == 3
    assert report["member_count"] == 4


def test_timelines_computed_per_family(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--out", out)
    report = json.loads(result.stdout)
    assert len(report["timelines"]) == report["family_count"]
    f1 = next(t for t in report["timelines"] if t["family_id"] == "F1")
    assert f1["member_count"] == 2
    assert f1["earliest_priority"] == "2019-06-01"
    assert set(f1["jurisdictions"]) == {"EP", "US"}


def test_prior_art_ranking_excludes_post_cutoff(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--target-claims", str(_write_claims(tmp_path)),
                 "--cutoff-date", "2024-01-01", "--out", out)
    report = json.loads(result.stdout)
    # US999FUTURE (priority 2024-02-01) is after the 2024-01-01 cutoff and must be excluded.
    ranked_numbers = [r["pub_number"] for r in report["prior_art_ranking"]]
    assert "US999FUTURE" not in ranked_numbers
    assert set(ranked_numbers) == {"US100A", "EP200B", "JP300C"}


def _write_claims(tmp_path: Path) -> Path:
    path = tmp_path / "target.json"
    path.write_text(json.dumps(TARGET_CLAIMS, ensure_ascii=False), encoding="utf-8")
    return path


def test_closest_prior_art_is_scored_with_overlap(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--target-claims", str(_write_claims(tmp_path)),
                 "--cutoff-date", "2024-01-01", "--out", out)
    report = json.loads(result.stdout)
    assert report["closest_prior_art"] is not None
    # US100A shares the most claim tokens with the target, so it should lead.
    assert report["closest_prior_art"]["pub_number"] == "US100A"
    assert report["closest_prior_art"]["claims_overlap"] > 0.5


def test_ranking_sorts_descending_by_score(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--target-claims", str(_write_claims(tmp_path)),
                 "--cutoff-date", "2024-01-01", "--out", out)
    scores = [r["score"] for r in json.loads(result.stdout)["prior_art_ranking"]]
    assert scores == sorted(scores, reverse=True)


def test_family_tree_text_rendering(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    result = run("--ledger", src, "--out", out)
    report = json.loads(result.stdout)
    tree = report["family_tree"]
    assert "Family: F1" in tree
    assert "US100A" in tree and "EP200B" in tree and "JP300C" in tree


def test_mermaid_output_written(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    mermaid = tmp_path / "tree.mmd"
    result = run("--ledger", src, "--mermaid-out", mermaid, "--out", out)
    assert result.returncode == 0, result.stderr
    content = mermaid.read_text(encoding="utf-8")
    assert content.startswith("flowchart TD")
    assert "US100A" in content


def test_mermaid_output_protected_then_forced(tmp_path: Path):
    src = make_ledger(tmp_path)
    out = tmp_path / "report.json"
    mermaid = tmp_path / "tree.mmd"
    # First run writes both outputs.
    first = run("--ledger", src, "--mermaid-out", mermaid, "--out", out)
    assert first.returncode == 0, first.stderr
    mermaid_content = mermaid.read_text(encoding="utf-8")
    assert mermaid_content.startswith("flowchart TD")
    # Second run without --force is blocked on the existing --out file.
    second = run("--ledger", src, "--mermaid-out", mermaid, "--out", out)
    assert second.returncode != 0
    # With --force, mermaid output is replaced.
    third = run("--ledger", src, "--mermaid-out", mermaid, "--out", out, "--force")
    assert third.returncode == 0
    assert mermaid.read_text(encoding="utf-8").startswith("flowchart TD")


def test_handles_dedicated_family_file(tmp_path: Path):
    family_file = tmp_path / "families.json"
    family_file.write_text(json.dumps({"families": [
        {"family_id": "X1", "members": [
            {"pub_number": "AA111", "filing_date": "2019-05-01",
             "priority_date": "2019-01-01", "claims": ["lever"]},
        ]},
    ]}), encoding="utf-8")
    out = tmp_path / "report.json"
    result = run("--family-file", family_file, "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["family_count"] == 1
    assert report["member_count"] == 1


def test_rejects_missing_input_source(tmp_path: Path):
    out = tmp_path / "report.json"
    result = run("--out", out)
    assert result.returncode != 0


def test_init_then_family_round_trip(tmp_path: Path):
    ledger = tmp_path / "ledger.json"
    init_result = subprocess.run(
        [sys.executable, str(INIT), "--out", ledger, "--subject", "Invention",
         "--cutoff-date", "2024-01-01"],
        capture_output=True, text=True, encoding="utf-8", check=False)
    assert init_result.returncode == 0, init_result.stderr
    out = tmp_path / "report.json"
    result = run("--ledger", ledger, "--out", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["artifact_type"] == "patent-family-analysis"
