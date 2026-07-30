import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "experiment-designer" / "scripts" / "create_preregistration.py"
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))


def spec(**updates):
    value = {
        "study_id": "study-001",
        "title": "Example experiment",
        "hypothesis": "Treatment improves score.",
        "experimental_unit": "participant",
        "variables": [{"name": "arm", "role": "treatment"}],
        "treatments": [{"name": "treatment"}, {"name": "control"}],
        "outcomes": [{"id": "score", "role": "primary", "timepoint": "week 8"}],
        "comparisons": [{"id": "primary", "contrast": "treatment-control"}],
        "planned_models": ["linear regression"],
        "alpha": 0.05,
        "open_questions": [],
    }
    value.update(updates)
    return value


def run(tmp_path, payload, *extra):
    source = tmp_path / "study.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "package"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(source), "--out-dir", str(out), *extra],
        text=True, capture_output=True, encoding="utf-8",
    )
    return result, source, out


def validate(name, payload):
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": f"#/$defs/{name}", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(payload)


def test_creates_schema_valid_draft_and_checksum_manifest(tmp_path):
    result, _, out = run(tmp_path, spec(hypothesis="_TODO_ pending pilot"))
    assert result.returncode == 0, result.stderr
    design = json.loads((out / "design-brief.json").read_text(encoding="utf-8"))
    plan = json.loads((out / "analysis-plan.json").read_text(encoding="utf-8"))
    manifest = json.loads((out / "preregistration-manifest.json").read_text(encoding="utf-8"))
    validate("design_brief", design)
    validate("analysis_plan", plan)
    validate("preregistration_manifest", manifest)
    assert manifest["registration_status"] == "draft"
    assert "$.hypothesis" in manifest["unresolved"]
    for item in manifest["files"]:
        assert hashlib.sha256((out / item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_freeze_rejects_todos_and_open_questions_without_partial_outputs(tmp_path):
    result, _, out = run(tmp_path, spec(open_questions=["Choose assay"]), "--freeze")
    assert result.returncode == 1
    assert "cannot freeze" in result.stderr
    assert not out.exists()


def test_freeze_writes_frozen_version(tmp_path):
    result, _, out = run(tmp_path, spec(), "--freeze", "--protocol-version", "1.0.0")
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "preregistration-manifest.json").read_text(encoding="utf-8"))
    assert manifest["registration_status"] == "frozen"
    assert manifest["protocol_version"] == "1.0.0"
    assert manifest["frozen_at"]


def test_existing_outputs_are_protected_and_input_is_unchanged(tmp_path):
    result, source, out = run(tmp_path, spec())
    assert result.returncode == 0
    original = source.read_bytes()
    second = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(source), "--out-dir", str(out)],
        text=True, capture_output=True, encoding="utf-8",
    )
    assert second.returncode == 1
    assert "--force" in second.stderr
    assert source.read_bytes() == original


def test_invalid_spec_fails_without_outputs(tmp_path):
    result, _, out = run(tmp_path, spec(alpha=2))
    assert result.returncode == 1
    assert "alpha" in result.stderr
    assert not out.exists()
