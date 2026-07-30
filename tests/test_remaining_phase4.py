"""Tests for the remaining Phase 4 skill extensions."""
import json, os, subprocess, sys, csv
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=ENV, timeout=30, check=False)


# research-project-orchestrator: decision provenance trace
def test_decision_provenance_trace(tmp_path):
    manifest = {"artifact_type": "research-project-manifest", "decisions": [
        {"type": "route", "rationale": "next step", "inputs": ["a"], "outputs": ["b"]},
        {"type": "skip", "inputs": ["x"]},  # missing rationale
    ]}
    (tmp_path / "project-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    script = ROOT / "skills" / "research-project-orchestrator" / "scripts" / "trace_decision_provenance.py"
    r = run(script, str(tmp_path))
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    assert len(d["decisions"]) == 2
    assert "missing rationale" in d["decisions"][1]["warnings"]


# research-data-management: anonymization screen
def test_anonymize_screen_flags_direct_ids(tmp_path):
    f = tmp_path / "data.csv"
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "email", "zip", "score"])
        w.writerow(["Alice", "a@b.com", "12345", "10"])
        w.writerow(["Bob", "c@d.com", "12345", "20"])
    script = ROOT / "skills" / "research-data-management" / "scripts" / "anonymize_check.py"
    r = run(script, str(f), "--quasi", "zip")
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    assert "name" in d["direct_identifier_columns"]
    assert "email" in d["direct_identifier_columns"]
    assert d["quasi_identifier_risk"]["zip"]["risk"] == "low"  # same zip


def test_anonymize_high_uniqueness(tmp_path):
    f = tmp_path / "data.csv"
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "val"])
        for i in range(10):
            w.writerow([f"id{i}", str(i)])
    script = ROOT / "skills" / "research-data-management" / "scripts" / "anonymize_check.py"
    r = run(script, str(f), "--quasi", "id")
    d = json.loads(r.stdout)
    assert d["quasi_identifier_risk"]["id"]["risk"] == "high"
