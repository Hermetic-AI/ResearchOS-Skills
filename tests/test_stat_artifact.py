import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest


pytest.importorskip("numpy")
pytest.importorskip("scipy")

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))


def test_adjust_writes_valid_artifact_and_refuses_overwrite(tmp_path):
    artifact = tmp_path / "adjusted.json"
    command = [
        sys.executable,
        str(ROOT / "skills" / "data-analysis-assistant" / "scripts" / "stat_test.py"),
        "--test", "adjust",
        "--method", "holm",
        "--pvalues", "0.01,0.04,0.20",
        "--labels", "primary,secondary,exploratory",
        "--artifact-out", str(artifact),
    ]
    environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    first = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    assert first.returncode == 0, first.stderr

    instance = json.loads(artifact.read_text(encoding="utf-8"))
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": "#/$defs/stat_results", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(instance)
    assert instance["results"][0]["adjusted_p_value"] == pytest.approx(0.03)
    assert instance["results"][0]["statistic"] is None

    second = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    assert second.returncode != 0
    assert "use --force" in second.stderr
