import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "experiment-designer" / "scripts" / "validate_power_calculations.py"


def test_reference_grid_passes_when_validation_stack_is_installed():
    pytest.importorskip("statsmodels")
    pytest.importorskip("scipy")
    result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(result.stdout)
    assert report["status"] == "pass"
    assert report["case_count"] == 48
    assert report["maxima"]["max_absolute_n_error"] <= report["thresholds"]["max_absolute_n_error"]


def test_missing_dependency_message_or_report_is_machine_safe():
    result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True, encoding="utf-8")
    if result.returncode == 2:
        assert "[validation]" in result.stderr
        assert result.stdout == ""
    else:
        assert json.loads(result.stdout)["status"] in {"pass", "fail"}
