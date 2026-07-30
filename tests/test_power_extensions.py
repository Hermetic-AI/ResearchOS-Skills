import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "experiment-designer" / "scripts" / "power_analysis.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, encoding="utf-8")


def test_noninferiority_and_equivalence_sample_sizes_respond_to_margin():
    ni = run("--test", "t_ind", "--solve", "n", "--hypothesis", "noninferiority", "--effect-size", "0", "--margin", "0.3", "--power", "0.8")
    eq = run("--test", "t_ind", "--solve", "n", "--hypothesis", "equivalence", "--effect-size", "0", "--margin", "0.3", "--power", "0.8")
    tighter = run("--test", "t_ind", "--solve", "n", "--hypothesis", "equivalence", "--effect-size", "0", "--margin", "0.2", "--power", "0.8")
    assert ni.returncode == eq.returncode == tighter.returncode == 0
    ni_data, eq_data, tight_data = map(lambda item: json.loads(item.stdout), (ni, eq, tighter))
    assert ni_data["hypothesis"] == "noninferiority"
    assert eq_data["n_per_group"] >= ni_data["n_per_group"]
    assert tight_data["n_per_group"] > eq_data["n_per_group"]


def test_cluster_and_dropout_inflation_rounds_to_whole_clusters():
    result = run("--test", "t_ind", "--solve", "n", "--effect-size", "0.5", "--power", "0.8", "--cluster-size", "12", "--icc", "0.05", "--cluster-cv", "0.4", "--dropout", "0.2")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    cluster = data["cluster_design"]
    assert cluster["design_effect"] > 1
    assert cluster["clusters_per_group"] >= 1
    assert cluster["enroll_per_group"] >= cluster["clusters_per_group"] * 12
    assert cluster["enroll_total"] == 2 * cluster["enroll_per_group"]


def test_cluster_power_uses_effective_sample_size():
    plain = run("--test", "t_ind", "--solve", "power", "--effect-size", "0.4", "--n", "100")
    clustered = run("--test", "t_ind", "--solve", "power", "--effect-size", "0.4", "--n", "100", "--cluster-size", "10", "--icc", "0.1")
    assert plain.returncode == clustered.returncode == 0
    assert json.loads(clustered.stdout)["power"] < json.loads(plain.stdout)["power"]


def test_invalid_margins_dropout_and_cluster_inputs_fail():
    cases = [
        ("--test", "t_ind", "--solve", "n", "--hypothesis", "equivalence", "--effect-size", "0.3", "--margin", "0.2"),
        ("--test", "t_ind", "--solve", "n", "--effect-size", "0.5", "--dropout", "1"),
        ("--test", "t_ind", "--solve", "n", "--effect-size", "0.5", "--cluster-size", "10"),
    ]
    for args in cases:
        result = run(*args)
        assert result.returncode != 0
        assert result.stderr
