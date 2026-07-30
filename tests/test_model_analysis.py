import csv
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest


pytest.importorskip("pandas")
pytest.importorskip("statsmodels")
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "data-analysis-assistant" / "scripts" / "model_analysis.py"
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))


def dataset(path):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["subject", "time", "group", "baseline", "score", "count", "binary"])
        for subject in range(1, 41):
            group = subject % 2
            random_intercept = (subject % 5 - 2) * 0.3
            baseline = 8 + subject % 7
            for time in range(3):
                score = 2 + 0.4 * baseline + 1.2 * group + 0.5 * time + random_intercept + ((subject * 3 + time) % 4 - 1.5) * 0.1
                count = int(max(0, round(1 + 0.15 * baseline + group + time)))
                binary = int(score > 7.2)
                writer.writerow([subject, time, group, baseline, score, count, binary])


def run(data, *args):
    return subprocess.run([sys.executable, str(SCRIPT), str(data), *args], text=True, capture_output=True, encoding="utf-8")


def validate_artifact(value):
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": "#/$defs/stat_results", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(value)


@pytest.mark.parametrize("model,extra", [
    ("ols", []),
    ("ancova", []),
    ("glm", ["--family", "poisson"]),
])
def test_regression_glm_and_ancova_emit_stat_results(tmp_path, model, extra):
    data = tmp_path / "data.csv"
    dataset(data)
    formula = "count ~ group + baseline" if model == "glm" else "score ~ group + baseline"
    result = run(data, "--model", model, "--formula", formula, *extra)
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout)
    validate_artifact(artifact)
    assert artifact["model"]["nobs"] == 120
    assert any(item["term"] == "group" for item in artifact["results"])


@pytest.mark.parametrize("model", ["gee", "mixedlm"])
def test_repeated_and_mixed_models(tmp_path, model):
    data = tmp_path / "data.csv"
    dataset(data)
    result = run(data, "--model", model, "--formula", "score ~ group + time + baseline", "--groups", "subject")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout)
    validate_artifact(artifact)
    assert artifact["model"]["groups"] == "subject"
    assert artifact["results"]


def test_formula_restriction_plan_deviation_and_output_guards(tmp_path):
    data = tmp_path / "data.csv"
    dataset(data)
    unsafe = run(data, "--model", "ols", "--formula", "score ~ __import__(os)")
    assert unsafe.returncode != 0 and "disallowed" in unsafe.stderr
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"artifact_type": "analysis-plan", "planned_models": ["score ~ group"]}), encoding="utf-8")
    out = tmp_path / "result.json"
    result = run(data, "--model", "ols", "--formula", "score ~ group + baseline", "--analysis-plan", str(plan), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert any("DEVIATION" in item for item in artifact["provenance"]["warnings"])
    collision = run(data, "--model", "ols", "--formula", "score ~ group", "--out", str(data), "--force")
    assert collision.returncode != 0
