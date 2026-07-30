import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "causal-inference-assistant" / "scripts" / "causal_estimate.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def _rows(n=200, seed_effect=0.8):
    """Build a simple confounded dataset with a positive treatment effect."""
    rows = []
    for i in range(n):
        age = 20 + (i % 50)
        score = 5 + (i % 7)
        # higher score -> more likely treated; outcome depends on treatment + score
        treated = 1 if score >= 7 and i % 2 == 0 else (1 if i % 3 == 0 and score >= 6 else 0)
        outcome = 1.0 + seed_effect * treated + 0.1 * score + 0.05 * age
        rows.append({"treated": treated, "age": age, "score": score, "y": outcome})
    return rows


def test_psm_att_estimate(tmp_path):
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"rows": _rows()}), encoding="utf-8")
    out = tmp_path / "psm.json"
    result = run("--method", "psm", "--data", str(data), "--treatment", "treated",
                 "--outcome", "y", "--confounders", "age,score", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "causal-estimate"
    assert artifact["method"] == "propensity-score-matching"
    assert artifact["estimand"] == "ATT"
    assert artifact["n_matched_pairs"] > 0
    assert artifact["estimate"] > 0
    assert artifact["ci_low"] < artifact["estimate"] < artifact["ci_high"]
    # balance reported for each confounder
    assert "age" in artifact["balance"] and "score" in artifact["balance"]
    assert all(abs(v["std_mean_diff"]) < 2.0 for v in artifact["balance"].values())


def test_iptw_ate_estimate(tmp_path):
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"rows": _rows()}), encoding="utf-8")
    out = tmp_path / "iptw.json"
    result = run("--method", "iptw", "--data", str(data), "--treatment", "treated",
                 "--outcome", "y", "--confounders", "age,score", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["method"] == "inverse-probability-weighting"
    assert artifact["estimand"] == "ATE"
    assert artifact["estimate"] > 0
    assert artifact["weight_summary"]["mean"] == pytest.approx(1.0, abs=0.05)


def test_did_estimate(tmp_path):
    rows = []
    for g in ["treated", "control"]:
        for period in [0, 1]:
            for _ in range(30):
                base = 10.0
                treat_boost = 2.0 if g == "treated" and period == 1 else 0.0
                trend = 1.0 if period == 1 else 0.0
                rows.append({"treated": 1 if g == "treated" else 0, "post": period,
                             "y": base + treat_boost + trend})
    data = tmp_path / "did.json"
    data.write_text(json.dumps({"rows": rows}), encoding="utf-8")
    out = tmp_path / "did_out.json"
    result = run("--method", "did", "--data", str(data), "--treatment", "treated",
                 "--outcome", "y", "--time", "post", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["method"] == "difference-in-differences"
    # DiD = (treated_post - treated_pre) - (control_post - control_pre)
    #     = (13 - 10) - (11 - 10) = 3 - 1 = 2.0  (common trend nets out)
    assert artifact["estimate"] == pytest.approx(2.0, abs=0.01)
    assert artifact["se"] == pytest.approx(0.0, abs=0.01)


def test_rdd_estimate(tmp_path):
    rows = []
    for i in range(100):
        running = (i - 50) / 10.0
        jump = 3.0 if running >= 0 else 0.0
        y = 5.0 + 0.5 * running + jump
        rows.append({"running": running, "y": y})
    data = tmp_path / "rdd.json"
    data.write_text(json.dumps({"rows": rows}), encoding="utf-8")
    out = tmp_path / "rdd_out.json"
    result = run("--method", "rdd", "--data", str(data), "--running", "running",
                 "--outcome", "y", "--cutoff", "0.0", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["method"] == "regression-discontinuity"
    assert artifact["estimate"] == pytest.approx(3.0, abs=0.3)
    assert artifact["left"]["n"] > 0 and artifact["right"]["n"] > 0


def test_evalue_and_confidence_limit(tmp_path):
    out = tmp_path / "ev.json"
    result = run("--method", "evalue", "--risk-ratio", "2.1", "--confidence-limit", "1.3", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["method"] == "e-value"
    assert artifact["input_risk_ratio"] == 2.1
    # E-value = RR + sqrt(RR*(RR-1)) = 2.1 + sqrt(2.1*1.1) ~ 3.62
    assert artifact["e_value"] == pytest.approx(2.1 + (2.1 * 1.1) ** 0.5, abs=0.01)
    assert "confidence_limit" in artifact
    assert artifact["confidence_limit"]["e_value"] < artifact["e_value"]


def test_evalue_reciprocal_orientation(tmp_path):
    out = tmp_path / "ev.json"
    result = run("--method", "evalue", "--risk-ratio", "0.5", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["oriented_risk_ratio"] == pytest.approx(2.0, abs=0.001)
    assert artifact["e_value"] == pytest.approx(2.0 + (2.0 * 1.0) ** 0.5, abs=0.01)


def test_output_protected(tmp_path):
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"rows": _rows()}), encoding="utf-8")
    out = tmp_path / "psm.json"
    args = ["--method", "psm", "--data", str(data), "--treatment", "treated",
            "--outcome", "y", "--confounders", "age,score", "--out", str(out)]
    assert run(*args).returncode == 0
    assert run(*args).returncode == 1 and "--force" in run(*args).stderr


def test_missing_required_args(tmp_path):
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"rows": _rows()}), encoding="utf-8")
    out = tmp_path / "out.json"
    result = run("--method", "psm", "--data", str(data), "--outcome", "y",
                 "--confounders", "age,score", "--out", str(out))
    assert result.returncode == 1
    assert "treatment" in result.stderr


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
