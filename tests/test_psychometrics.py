import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "survey-and-psychometrics" / "scripts" / "psychometrics.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def _correlated_items(n=60):
    """Generate responses where q1-q3 correlate and q4-q6 correlate (two factors)."""
    header = ["q1", "q2", "q3", "q4", "q5", "q6"]
    rows = []
    for i in range(n):
        f1 = (i % 5) + 1
        f2 = ((i * 3) % 5) + 1
        rows.append([f1, min(5, f1 + (i % 2)), max(1, f1 - (i % 2)),
                     f2, min(5, f2 + (i % 2)), max(1, f2 - (i % 2))])
    return header, rows


def test_efa_extracts_and_rotates(tmp_path):
    path = tmp_path / "items.csv"
    header, rows = _correlated_items()
    write_csv(path, header, rows)
    out = tmp_path / "efa.json"
    result = run("--mode", "efa", "--csv", str(path), "--items", ",".join(header),
                 "--factors", "2", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "psychometrics-efa"
    assert artifact["n_complete"] == 60
    assert artifact["factors"] == 2
    assert len(artifact["loadings"]) == 6
    assert len(artifact["eigenvalues"]) == 2
    assert all(0 <= entry["communalities"] <= 1 for entry in artifact["loadings"])
    # Two-factor structure: variance explained should be meaningfully > 0
    assert artifact["total_variance_explained"] > 0.3
    for entry in artifact["loadings"]:
        assert len(entry["loadings"]) == 2


def test_efa_single_factor(tmp_path):
    path = tmp_path / "items.csv"
    header = ["q1", "q2", "q3"]
    rows = []
    for i in range(40):
        v = (i % 5) + 1
        rows.append([v, min(5, v + 1), max(1, v - 1)])
    write_csv(path, header, rows)
    out = tmp_path / "efa.json"
    result = run("--mode", "efa", "--csv", str(path), "--items", "q1,q2,q3",
                 "--factors", "1", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert len(artifact["loadings"][0]["loadings"]) == 1


def test_reliability_alpha_and_item_total(tmp_path):
    path = tmp_path / "items.csv"
    header = ["q1", "q2", "q3", "q4"]
    rows = []
    for i in range(50):
        v = (i % 5) + 1
        rows.append([v, min(5, v + (i % 2)), max(1, v - (i % 2)), 6 - v])  # q4 reversed
    write_csv(path, header, rows)
    out = tmp_path / "rel.json"
    result = run("--mode", "reliability", "--csv", str(path), "--items", "q1,q2,q3,q4",
                 "--reverse", "q4", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "psychometrics-reliability"
    assert artifact["n_items"] == 4
    assert -1.0 <= artifact["cronbach_alpha"] <= 1.0
    assert set(artifact["item_total_correlations"].keys()) == set(header)
    assert set(artifact["alpha_if_item_deleted"].keys()) == set(header)
    # item-total correlations should be positive for a coherent scale
    assert all(v >= 0 for v in artifact["item_total_correlations"].values())


def test_rasch_fit(tmp_path):
    path = tmp_path / "rasch.csv"
    header = ["q1", "q2", "q3", "q4"]
    rows = []
    for i in range(80):
        ability = (i % 7) + 1
        rows.append([min(5, ability), min(5, ability + 1), max(1, ability - 1), min(5, ability + 2)])
    write_csv(path, header, rows)
    out = tmp_path / "rasch.json"
    result = run("--mode", "rasch", "--csv", str(path), "--items", ",".join(header), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "psychometrics-rasch"
    assert artifact["n_complete"] == 80
    assert artifact["n_items"] == 4
    assert set(artifact["item_difficulties"].keys()) == set(header)
    assert set(artifact["item_infit"].keys()) == set(header)
    assert isinstance(artifact["person_abilities_mean"], float)


def test_output_protected(tmp_path):
    path = tmp_path / "items.csv"
    header, rows = _correlated_items()
    write_csv(path, header, rows)
    out = tmp_path / "efa.json"
    args = ["--mode", "efa", "--csv", str(path), "--items", ",".join(header),
            "--factors", "2", "--out", str(out)]
    assert run(*args).returncode == 0
    second = run(*args)
    assert second.returncode == 1 and "--force" in second.stderr


def test_missing_item_column_rejected(tmp_path):
    path = tmp_path / "items.csv"
    write_csv(path, ["q1", "q2"], [[1, 2], [3, 4]])
    out = tmp_path / "efa.json"
    result = run("--mode", "efa", "--csv", str(path), "--items", "q1,q9",
                 "--factors", "1", "--out", str(out))
    assert result.returncode == 1
    assert "missing" in result.stderr


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
