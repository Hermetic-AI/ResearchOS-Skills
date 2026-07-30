import json
import math
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "experiment-designer" / "scripts" / "plan_sequential_design.py"
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))


def base_spec(**updates):
    payload = {
        "study_id": "s1",
        "family_alpha": 0.05,
        "sidedness": "two-sided",
        "multiplicity": {"method": "weighted-bonferroni"},
        "endpoints": [{"id": "primary", "weight": 3}, {"id": "secondary", "weight": 1}],
        "sequential": {"spending": "obrien-fleming", "information_fractions": [0.5, 1.0]},
        "stopping_rules": {"efficacy": {"decision_rule": "validated boundary", "authority": "DMC"}},
    }
    payload.update(updates)
    return payload


def run(tmp_path, payload, *extra):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "plan.json"
    result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--out", str(out), *extra], text=True, capture_output=True, encoding="utf-8")
    return result, source, out


def test_weighted_endpoints_and_spending_are_valid(tmp_path):
    result, _, out = run(tmp_path, base_spec())
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": "#/$defs/sequential_design_plan", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(artifact)
    assert math.isclose(artifact["endpoints"][0]["local_alpha"], 0.0375)
    assert math.isclose(artifact["endpoints"][1]["local_alpha"], 0.0125)
    for endpoint in artifact["endpoints"]:
        looks = endpoint["looks"]
        assert looks[0]["cumulative_alpha_budget"] < looks[1]["cumulative_alpha_budget"]
        assert math.isclose(looks[-1]["cumulative_alpha_budget"], endpoint["local_alpha"], rel_tol=1e-10)


def test_holm_reports_rank_thresholds_not_endpoint_alpha(tmp_path):
    payload = base_spec(multiplicity={"method": "holm"}, sequential={"spending": "none", "information_fractions": [1.0]})
    result, _, out = run(tmp_path, payload)
    assert result.returncode == 0
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["endpoints"][0]["local_alpha"] is None
    assert artifact["endpoints"][0]["holm_rank_thresholds"] == [0.025, 0.05]


def test_invalid_looks_and_incomplete_adaptation_fail_without_output(tmp_path):
    bad_looks = base_spec(sequential={"spending": "pocock", "information_fractions": [0.7, 0.5, 1.0]})
    result, _, out = run(tmp_path, bad_looks)
    assert result.returncode == 1
    assert "information fractions" in result.stderr
    assert not out.exists()
    incomplete = base_spec(adaptations=[{"id": "a1", "type": "sample size"}])
    result, _, out = run(tmp_path, incomplete)
    assert result.returncode == 1
    assert "missing prespecification" in result.stderr
    assert not out.exists()


def test_output_and_source_are_protected(tmp_path):
    result, source, out = run(tmp_path, base_spec())
    assert result.returncode == 0
    original = source.read_bytes()
    again = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--out", str(out)], text=True, capture_output=True, encoding="utf-8")
    assert again.returncode != 0 and "--force" in again.stderr
    replace_source = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--out", str(source), "--force"], text=True, capture_output=True, encoding="utf-8")
    assert replace_source.returncode != 0
    assert source.read_bytes() == original
