import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "experiment-designer" / "scripts" / "longitudinal_power.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, encoding="utf-8")


def test_repeated_measure_efficiency_and_dropout():
    low = run("repeated-mean", "--effect-size", "0.4", "--measurements", "4", "--correlation", "0.2", "--dropout", "0.1")
    high = run("repeated-mean", "--effect-size", "0.4", "--measurements", "4", "--correlation", "0.8")
    assert low.returncode == high.returncode == 0
    low_data, high_data = json.loads(low.stdout), json.loads(high.stdout)
    assert low_data["n_analyzable_per_group"] < high_data["n_analyzable_per_group"]
    assert low_data["n_enroll_per_group"] > low_data["n_analyzable_per_group"]


def test_longitudinal_slope_uses_timing_information():
    compact = run("longitudinal-slope", "--slope-effect", "0.1", "--times", "0,1,2", "--correlation", "0.5")
    spread = run("longitudinal-slope", "--slope-effect", "0.1", "--times", "0,2,4", "--correlation", "0.5")
    assert compact.returncode == spread.returncode == 0
    assert json.loads(spread.stdout)["n_analyzable_per_group"] < json.loads(compact.stdout)["n_analyzable_per_group"]


def test_survival_event_count_and_enrollment():
    result = run("survival", "--hazard-ratio", "0.7", "--event-probability", "0.6", "--power", "0.9", "--dropout", "0.1")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["required_events"] > 0
    assert data["n_enroll_total"] > data["required_events"]
    assert abs(data["n_enroll_treatment"] - data["n_enroll_control"]) <= 1


def test_invalid_assumptions_and_output_collision_fail(tmp_path):
    invalid = run("survival", "--hazard-ratio", "1", "--event-probability", "0.5")
    assert invalid.returncode != 0 and "hazard-ratio" in invalid.stderr
    invalid_times = run("longitudinal-slope", "--slope-effect", "0.2", "--times", "0,2,1", "--correlation", "0.5")
    assert invalid_times.returncode != 0
    out = tmp_path / "result.json"
    out.write_text("keep", encoding="utf-8")
    collision = run("survival", "--hazard-ratio", "0.7", "--event-probability", "0.5", "--out", str(out))
    assert collision.returncode != 0 and out.read_text(encoding="utf-8") == "keep"
