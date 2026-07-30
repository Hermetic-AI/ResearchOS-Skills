import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "qualitative-research-assistant" / "scripts" / "saturation.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_saturation_curve_tracks_new_codes(tmp_path):
    log = tmp_path / "log.json"
    log.write_text(json.dumps({"entries": [
        {"source_id": "i1", "round": 1, "coder": "A", "code": "alpha"},
        {"source_id": "i2", "round": 1, "coder": "A", "code": "beta"},
        {"source_id": "i3", "round": 2, "coder": "A", "code": "alpha"},
        {"source_id": "i4", "round": 2, "coder": "A", "code": "gamma"},
        {"source_id": "i5", "round": 3, "coder": "A", "code": "alpha"},
        {"source_id": "i6", "round": 3, "coder": "A", "code": "beta"},
    ]}), encoding="utf-8")
    out = tmp_path / "sat.json"
    result = run("--mode", "saturation", "--log", str(log), "--threshold", "0.1", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "qualitative-saturation-curve"
    assert artifact["total_codes"] == 3
    curve = artifact["curve"]
    assert curve[0]["new_code_count"] == 2  # alpha, beta
    assert curve[1]["new_code_count"] == 1  # gamma
    assert curve[2]["new_code_count"] == 0  # no new codes
    assert curve[2]["new_code_rate"] == 0.0
    # threshold flag triggers once rate drops below 0.1 (after a non-empty round)
    assert artifact["below_threshold_from_round"] == 3
    assert any("does not establish saturation" in w for w in artifact["warnings"])


def test_saturation_without_round_field(tmp_path):
    log = tmp_path / "log.json"
    log.write_text(json.dumps([
        {"source_id": "i1", "coder": "A", "code": "alpha"},
        {"source_id": "i2", "coder": "A", "code": "beta"},
        {"source_id": "i3", "coder": "A", "code": "alpha"},
    ]), encoding="utf-8")
    out = tmp_path / "sat.json"
    result = run("--mode", "saturation", "--log", str(log), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["total_codes"] == 2
    assert artifact["curve"][0]["new_code_count"] == 1
    assert artifact["curve"][1]["new_code_count"] == 1
    assert artifact["curve"][2]["new_code_count"] == 0


def test_krippendorff_nominal_agreement(tmp_path):
    data = tmp_path / "alpha.json"
    data.write_text(json.dumps({
        "units": ["u1", "u2", "u3", "u4"],
        "coders": ["A", "B"],
        "values": {
            "A": {"u1": "red", "u2": "red", "u3": "blue", "u4": "blue"},
            "B": {"u1": "red", "u2": "red", "u3": "blue", "u4": "blue"},
        },
    }), encoding="utf-8")
    out = tmp_path / "alpha_out.json"
    result = run("--mode", "alpha", "--data", str(data), "--level", "nominal", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "krippendorff-alpha"
    assert artifact["alpha"] == pytest.approx(1.0, abs=0.001)
    assert artifact["observed_disagreement"] == pytest.approx(0.0, abs=0.001)
    assert artifact["n_units"] == 4 and artifact["n_coders"] == 2


def test_krippendorff_nominal_disagreement(tmp_path):
    data = tmp_path / "alpha.json"
    data.write_text(json.dumps({
        "units": ["u1", "u2", "u3", "u4"],
        "coders": ["A", "B"],
        "values": {
            "A": {"u1": "red", "u2": "red", "u3": "red", "u4": "red"},
            "B": {"u1": "blue", "u2": "blue", "u3": "blue", "u4": "blue"},
        },
    }), encoding="utf-8")
    out = tmp_path / "alpha_out.json"
    result = run("--mode", "alpha", "--data", str(data), "--level", "nominal", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["alpha"] == pytest.approx(-1.0, abs=0.001) or artifact["alpha"] <= 0.0


def test_krippendorff_with_missing_values(tmp_path):
    data = tmp_path / "alpha.json"
    data.write_text(json.dumps({
        "units": ["u1", "u2", "u3"],
        "coders": ["A", "B", "C"],
        "values": {
            "A": {"u1": "red", "u2": "blue"},
            "B": {"u1": "red", "u3": "blue"},
            "C": {"u2": "blue", "u3": "blue"},
        },
    }), encoding="utf-8")
    out = tmp_path / "alpha_out.json"
    result = run("--mode", "alpha", "--data", str(data), "--level", "nominal", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert -1.0 <= artifact["alpha"] <= 1.0
    assert artifact["n_coders"] == 3


def test_krippendorff_interval_level(tmp_path):
    data = tmp_path / "alpha.json"
    data.write_text(json.dumps({
        "units": ["u1", "u2", "u3"],
        "coders": ["A", "B"],
        "values": {
            "A": {"u1": 1, "u2": 2, "u3": 3},
            "B": {"u1": 1, "u2": 2, "u3": 3},
        },
    }), encoding="utf-8")
    out = tmp_path / "alpha_out.json"
    result = run("--mode", "alpha", "--data", str(data), "--level", "interval", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["alpha"] == pytest.approx(1.0, abs=0.001)


def test_output_protected(tmp_path):
    log = tmp_path / "log.json"
    log.write_text(json.dumps({"entries": [
        {"source_id": "i1", "round": 1, "coder": "A", "code": "alpha"},
    ]}), encoding="utf-8")
    out = tmp_path / "sat.json"
    args = ["--mode", "saturation", "--log", str(log), "--out", str(out)]
    assert run(*args).returncode == 0
    second = run(*args)
    assert second.returncode == 1 and "--force" in second.stderr


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
