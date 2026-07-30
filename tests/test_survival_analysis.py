import csv
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest


pytest.importorskip("statsmodels")
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "data-analysis-assistant" / "scripts" / "survival_analysis.py"
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))


def data(path):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["time", "status", "x", "group"])
        for i in range(1, 61):
            writer.writerow([i / 3 + (i % 4), 0 if i % 5 == 0 else (2 if i % 7 == 0 else 1), i % 2, "a" if i % 2 else "b"])


def run(path, *args):
    return subprocess.run([sys.executable, str(SCRIPT), args[0], str(path), *args[1:]], text=True, capture_output=True, encoding="utf-8")


def validate(definition, value):
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(value)


def test_cox_emits_hazard_ratios(tmp_path):
    path = tmp_path / "survival.csv"; data(path)
    result = run(path, "cox", "--formula", "time ~ x", "--status", "status")
    assert result.returncode != 0  # cause codes are not valid binary event indicators
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for row in rows: row["status"] = "1" if row["status"] == "1" else "0"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    result = run(path, "cox", "--formula", "time ~ x", "--status", "status")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout); validate("stat_results", artifact)
    assert artifact["results"][0]["effect_size_metric"] == "hazard ratio"


def test_competing_risk_is_schema_valid_and_labeled_descriptive(tmp_path):
    path = tmp_path / "competing.csv"; data(path)
    result = run(path, "competing-risk", "--time", "time", "--status", "status", "--group", "group", "--at-times", "5", "10")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout); validate("competing_risk_estimate", artifact)
    assert artifact["causes"] == [1, 2]
    assert any("no Gray test" in warning for warning in artifact["warnings"])


def test_output_protection(tmp_path):
    path = tmp_path / "data.csv"; data(path); original = path.read_bytes()
    result = run(path, "competing-risk", "--time", "time", "--status", "status", "--out", str(path), "--force")
    assert result.returncode != 0 and path.read_bytes() == original
