import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "experiment-designer" / "scripts" / "doe_designs.py"
pytest.importorskip("numpy")


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--format", "json", "--no-randomize"],
        text=True, capture_output=True, encoding="utf-8",
    )


def test_full_factorial_reports_full_rank_screening_model():
    result = run("--design", "full", "--factors-json", '{"A":[-1,1],"B":[-1,1],"C":[-1,1]}')
    assert result.returncode == 0, result.stderr
    meta = json.loads(result.stdout)["meta"]
    diagnostics = meta["design_diagnostics"]
    assert diagnostics["rank"] == diagnostics["n_parameters"] == 7
    assert diagnostics["non_estimable_terms"] == []
    assert diagnostics["d_efficiency_percent"] == pytest.approx(100)
    assert meta["alias_structure"]["resolution"] is None


def test_fractional_factorial_reports_resolution_and_aliases():
    result = run("--design", "frac2k", "--factors-json", '{"a":[-1,1],"b":[-1,1],"c":[-1,1]}', "--generators", "c=ab")
    assert result.returncode == 0, result.stderr
    meta = json.loads(result.stdout)["meta"]
    assert meta["alias_structure"]["resolution"] == 3
    groups = [set(item) for item in meta["alias_structure"]["groups"]]
    assert any("a" in group and "b:c" in group for group in groups)
    assert meta["design_diagnostics"]["non_estimable_terms"]


def test_response_surface_reports_quadratic_estimability():
    result = run("--design", "boxbehnken", "--factors-json", '{"A":[0,10],"B":[0,10],"C":[0,10]}', "--center-points", "3")
    assert result.returncode == 0, result.stderr
    diagnostics = json.loads(result.stdout)["meta"]["design_diagnostics"]
    assert diagnostics["rank"] == diagnostics["n_parameters"]
    assert all(f"quadratic({name})" in diagnostics["estimable_terms"] for name in "ABC")


def test_factor_source_cannot_be_overwritten_even_with_force(tmp_path):
    source = tmp_path / "factors.json"
    source.write_text('{"a":[-1,1],"b":[-1,1]}', encoding="utf-8")
    original = source.read_bytes()
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--design", "full", "--factors", str(source), "--out", str(source), "--force"],
        text=True, capture_output=True, encoding="utf-8",
    )
    assert result.returncode != 0
    assert source.read_bytes() == original
