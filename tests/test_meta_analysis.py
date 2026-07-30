import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "systematic-review-meta-analysis" / "scripts" / "meta_analysis.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_smd_effects_with_ci(tmp_path):
    studies = tmp_path / "studies.json"
    studies.write_text(json.dumps({"studies": [
        {"id": "s1", "measure": "smd", "n1": 30, "mean1": 10.0, "sd1": 2.0, "n2": 30, "mean2": 8.0, "sd2": 2.0},
        {"id": "s2", "measure": "smd", "n1": 50, "mean1": 5.0, "sd1": 1.5, "n2": 50, "mean2": 4.5, "sd2": 1.5},
    ]}), encoding="utf-8")
    out = tmp_path / "effects.json"
    result = run("--mode", "effects", "--studies", str(studies), "--measure", "smd", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "meta-analysis-effects"
    assert artifact["measure"] == "smd"
    assert len(artifact["effects"]) == 2
    s1 = artifact["effects"][0]
    assert s1["id"] == "s1"
    # Cohen's d = (10-8)/pooled_sd; pooled_sd ~ 2.0 -> d ~ 1.0
    assert s1["estimate"] == pytest.approx(1.0, abs=0.05)
    assert s1["ci_low"] < s1["estimate"] < s1["ci_high"]
    assert s1["se"] > 0


def test_hedges_g_applies_correction(tmp_path):
    studies = tmp_path / "studies.json"
    studies.write_text(json.dumps({"studies": [
        {"id": "s1", "measure": "hedges_g", "n1": 10, "mean1": 10.0, "sd1": 2.0, "n2": 10, "mean2": 8.0, "sd2": 2.0},
    ]}), encoding="utf-8")
    out = tmp_path / "effects.json"
    result = run("--mode", "effects", "--studies", str(studies), "--measure", "hedges_g", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    g = artifact["effects"][0]["estimate"]
    # Hedges' g is slightly smaller in magnitude than Cohen's d for small n.
    assert abs(g) < 1.05
    assert g > 0


def test_rr_and_or_with_zero_correction(tmp_path):
    studies = tmp_path / "studies.json"
    studies.write_text(json.dumps({"studies": [
        {"id": "s1", "measure": "rr", "events1": 20, "n1": 100, "events2": 30, "n2": 100},
        {"id": "s2", "measure": "or", "events1": 0, "n1": 50, "events2": 10, "n2": 50},
    ]}), encoding="utf-8")
    out = tmp_path / "effects.json"
    result = run("--mode", "effects", "--studies", str(studies), "--measure", "rr", "--out", str(out))
    assert result.returncode == 0, result.stderr
    rr_artifact = json.loads(out.read_text(encoding="utf-8"))
    assert rr_artifact["effects"][0]["estimate"] < 0  # log(RR) < 0 since risk1 < risk2

    out2 = tmp_path / "or.json"
    result = run("--mode", "effects", "--studies", str(studies), "--measure", "or", "--out", str(out2))
    assert result.returncode == 0, result.stderr
    or_artifact = json.loads(out2.read_text(encoding="utf-8"))
    # zero-cell correction allows computation without error
    assert isinstance(or_artifact["effects"][0]["estimate"], float)


def test_random_effects_pooling(tmp_path):
    effects = tmp_path / "effects.json"
    effects.write_text(json.dumps({"effects": [
        {"id": "s1", "estimate": 0.5, "se": 0.1, "ci_low": 0.3, "ci_high": 0.7},
        {"id": "s2", "estimate": 0.6, "se": 0.1, "ci_low": 0.4, "ci_high": 0.8},
        {"id": "s3", "estimate": 0.4, "se": 0.1, "ci_low": 0.2, "ci_high": 0.6},
    ]}), encoding="utf-8")
    out = tmp_path / "meta.json"
    result = run("--mode", "pool", "--effects", str(effects), "--model", "random", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "meta-analysis-pooled"
    assert artifact["model"] == "random-effects"
    assert artifact["k"] == 3
    assert 0.3 < artifact["pooled_estimate"] < 0.7
    assert artifact["pooled_se"] > 0
    assert artifact["ci_low"] < artifact["pooled_estimate"] < artifact["ci_high"]
    assert artifact["heterogeneity"]["I_squared"] == pytest.approx(0.0, abs=0.01)
    assert len(artifact["forest"]) == 3
    assert all("weight" in entry for entry in artifact["forest"])


def test_fixed_effect_pooling(tmp_path):
    effects = tmp_path / "effects.json"
    effects.write_text(json.dumps({"effects": [
        {"id": "s1", "estimate": 0.5, "se": 0.1, "ci_low": 0.3, "ci_high": 0.7},
        {"id": "s2", "estimate": 0.7, "se": 0.2, "ci_low": 0.3, "ci_high": 1.1},
    ]}), encoding="utf-8")
    out = tmp_path / "meta.json"
    result = run("--mode", "pool", "--effects", str(effects), "--model", "fixed", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["model"] == "fixed-effect"
    # Fixed-effect weights by 1/se^2: s1 weight 100, s2 weight 25 -> pooled ~ (0.5*100+0.7*25)/125 = 0.54
    assert artifact["pooled_estimate"] == pytest.approx(0.54, abs=0.01)


def test_heterogeneity_flag(tmp_path):
    effects = tmp_path / "effects.json"
    effects.write_text(json.dumps({"effects": [
        {"id": "s1", "estimate": 0.1, "se": 0.05, "ci_low": 0.0, "ci_high": 0.2},
        {"id": "s2", "estimate": 0.9, "se": 0.05, "ci_low": 0.8, "ci_high": 1.0},
    ]}), encoding="utf-8")
    out = tmp_path / "meta.json"
    result = run("--mode", "pool", "--effects", str(effects), "--model", "random", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["heterogeneity"]["Q"] > 0
    assert artifact["heterogeneity"]["I_squared"] > 0.5
    assert artifact["heterogeneity"]["tau_squared"] > 0


def test_output_protected(tmp_path):
    effects = tmp_path / "effects.json"
    effects.write_text(json.dumps({"effects": [
        {"id": "s1", "estimate": 0.5, "se": 0.1, "ci_low": 0.3, "ci_high": 0.7},
    ]}), encoding="utf-8")
    out = tmp_path / "meta.json"
    assert run("--mode", "pool", "--effects", str(effects), "--model", "fixed", "--out", str(out)).returncode == 0
    second = run("--mode", "pool", "--effects", str(effects), "--model", "fixed", "--out", str(out))
    assert second.returncode == 1
    assert "--force" in second.stderr


def test_invalid_alpha_rejected(tmp_path):
    effects = tmp_path / "effects.json"
    effects.write_text(json.dumps({"effects": [
        {"id": "s1", "estimate": 0.5, "se": 0.1, "ci_low": 0.3, "ci_high": 0.7},
    ]}), encoding="utf-8")
    out = tmp_path / "meta.json"
    result = run("--mode", "pool", "--effects", str(effects), "--model", "fixed", "--alpha", "1.5", "--out", str(out))
    assert result.returncode == 1
    assert "alpha" in result.stderr


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
