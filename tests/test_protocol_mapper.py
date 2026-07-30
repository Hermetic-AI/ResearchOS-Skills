"""Tests for protocol-authoring/scripts/protocol_mapper.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "protocol-authoring" / "scripts" / "protocol_mapper.py"
INIT = ROOT / "skills" / "protocol-authoring" / "scripts" / "init_protocol.py"

PROTOCOL = {
    "schema_version": "1.0.0",
    "artifact_type": "research-protocol",
    "title": "Memory-Agent RCT",
    "design": "Randomized controlled trial",
    "objectives": ["Measure memory impact on reliability"],
    "hypotheses": ["Memory improves task completion"],
    "population_and_eligibility": {"domain": "long-horizon agents"},
    "outcomes_and_estimands": ["primary: completion rate"],
    "procedures": ["random allocation", "memory stream intervention"],
    "sample_size_evidence": ["power 0.8, alpha 0.05"],
    "analysis_artifacts": ["primary-analysis.R"],
    "monitoring_and_stopping": ["interim look at n=100"],
    "ethics_and_registration": ["IRB approved", "ClinicalTrials.gov"],
    "data_governance": ["de-identified logs"],
    "amendments_and_deviations": [],
    "warnings": [],
}


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def make_protocol(tmp_path: Path, data: dict | None = None) -> Path:
    path = tmp_path / "protocol.json"
    path.write_text(json.dumps(data or PROTOCOL, ensure_ascii=False), encoding="utf-8")
    return path


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_maps_randomized_trial_to_consort(tmp_path: Path):
    src = make_protocol(tmp_path)
    out = tmp_path / "mapping.json"
    result = run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert report["schema_version"] == "1.0.0"
    assert report["artifact_type"] == "protocol-guideline-mapping"
    assert report["tool_version"] == "0.1.0"
    assert "warnings" in report and report["warnings"]
    assert report["mapped_guideline"] == "consort"
    assert report["registry"] == "clinicaltrials.gov"


def test_checklist_items_each_have_status(tmp_path: Path):
    src = make_protocol(tmp_path)
    out = tmp_path / "mapping.json"
    result = run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", out)
    report = json.loads(result.stdout)
    assert report["checklist_items"] == len(report["checklist"])
    for row in report["checklist"]:
        assert row["status"] in {"satisfied", "partial", "missing"}
        assert "item" in row and "fields" in row


def test_populated_protocol_has_satisfied_items(tmp_path: Path):
    src = make_protocol(tmp_path)
    out = tmp_path / "mapping.json"
    result = run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", out)
    report = json.loads(result.stdout)
    assert any(row["status"] == "satisfied" for row in report["checklist"])
    assert report["missing_items"] < report["checklist_items"]


def test_empty_protocol_maps_but_all_missing(tmp_path: Path):
    empty = {
        "schema_version": "1.0.0", "artifact_type": "research-protocol",
        "title": "", "design": "",
    }
    src = make_protocol(tmp_path, empty)
    out = tmp_path / "mapping.json"
    result = run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert all(row["status"] == "missing" for row in report["checklist"])
    assert report["missing_items"] == report["checklist_items"]
    assert report["ready_for_human_review"] is False


def test_observational_design_maps_to_strobe(tmp_path: Path):
    data = dict(PROTOCOL)
    data["design"] = "Prospective cohort study"
    src = make_protocol(tmp_path, data)
    out = tmp_path / "mapping.json"
    result = run("--protocol", src, "--registry", "osf", "--out", out)
    report = json.loads(result.stdout)
    assert report["mapped_guideline"] == "strobe"


def test_systematic_review_maps_to_prisma(tmp_path: Path):
    data = dict(PROTOCOL)
    data["design"] = "Systematic review and meta-analysis"
    src = make_protocol(tmp_path, data)
    out = tmp_path / "mapping.json"
    result = run("--protocol", src, "--registry", "osf", "--out", out)
    report = json.loads(result.stdout)
    assert report["mapped_guideline"] == "prisma"


def test_registration_summary_differs_by_registry(tmp_path: Path):
    src = make_protocol(tmp_path)
    ct = tmp_path / "ct.json"
    osf = tmp_path / "osf.json"
    run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", ct)
    run("--protocol", src, "--registry", "osf", "--out", osf, "--force")
    ct_summary = json.loads(ct.read_text(encoding="utf-8"))["registration_summary"]
    osf_summary = json.loads(osf.read_text(encoding="utf-8"))["registration_summary"]
    assert ct_summary["registry_fields"]["study_type"] == "Interventional"
    assert "brief_title" in ct_summary["registry_fields"]
    assert osf_summary["registry_fields"]["category"] == "project"
    assert "title" in osf_summary["registry_fields"]


def test_output_protected_then_forced(tmp_path: Path):
    src = make_protocol(tmp_path)
    out = tmp_path / "mapping.json"
    out.write_text("keep", encoding="utf-8")
    protected = run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", out)
    assert protected.returncode != 0
    assert out.read_text(encoding="utf-8") == "keep"
    forced = run("--protocol", src, "--registry", "clinicaltrials.gov", "--out", out, "--force")
    assert forced.returncode == 0
    assert out.read_text(encoding="utf-8") != "keep"


def test_rejects_non_protocol_input(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"artifact_type": "other"}), encoding="utf-8")
    out = tmp_path / "mapping.json"
    result = run("--protocol", bad, "--registry", "clinicaltrials.gov", "--out", out)
    assert result.returncode != 0
    assert "research-protocol" in result.stderr


def test_init_then_mapping_round_trip(tmp_path: Path):
    proto = tmp_path / "protocol.json"
    init_result = subprocess.run(
        [sys.executable, str(INIT), "--out", proto, "--title", "Study",
         "--design", "Randomized trial"],
        capture_output=True, text=True, encoding="utf-8", check=False)
    assert init_result.returncode == 0, init_result.stderr
    out = tmp_path / "mapping.json"
    result = run("--protocol", proto, "--registry", "clinicaltrials.gov", "--out", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["mapped_guideline"] == "consort"
