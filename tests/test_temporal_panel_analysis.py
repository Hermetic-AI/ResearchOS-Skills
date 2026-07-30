import csv
import json
import math
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest


pytest.importorskip("statsmodels")
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "data-analysis-assistant" / "scripts" / "temporal_panel_analysis.py"
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))


def run(mode, path, *args):
    return subprocess.run([sys.executable, str(SCRIPT), mode, str(path), *args], text=True, capture_output=True, encoding="utf-8")


def validate(definition, value):
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(value)


def test_sarimax_forecast_is_schema_valid(tmp_path):
    path = tmp_path / "series.csv"
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.writer(h); w.writerow(["date", "y"])
        for i in range(48): w.writerow([f"{2020 + i // 12}-{i % 12 + 1:02d}-01", 10 + 0.1 * i + math.sin(i / 3)])
    result = run("timeseries", path, "--date", "date", "--value", "y", "--order", "1,1,0", "--steps", "4")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout); validate("time_series_forecast", artifact)
    assert len(artifact["forecast"]) == 4 and artifact["frequency"] == "MS"


def test_panel_two_way_effects_and_cluster_metadata(tmp_path):
    path = tmp_path / "panel.csv"
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.writer(h); w.writerow(["firm", "year", "x", "y"])
        for firm in range(25):
            for year in range(5): w.writerow([firm, 2020 + year, firm % 3 + year / 4, 2 + 0.7 * (firm % 3 + year / 4) + firm * 0.1 + year * 0.2])
    result = run("panel", path, "--formula", "y ~ x", "--entity", "firm", "--time", "year")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout); validate("stat_results", artifact)
    assert artifact["model"]["effects"] == "two-way"
    assert artifact["model"]["entities"] == 25
    assert any(item["term"] == "x" for item in artifact["results"])


def test_irregular_series_and_source_overwrite_fail(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text("date,y\n2020-01-01,1\n2020-03-01,2\n2020-06-01,3\n", encoding="utf-8")
    irregular = run("timeseries", path, "--date", "date", "--value", "y")
    assert irregular.returncode != 0 and "frequency" in irregular.stderr
    original = path.read_bytes()
    overwrite = run("timeseries", path, "--date", "date", "--value", "y", "--out", str(path), "--force")
    assert overwrite.returncode != 0 and path.read_bytes() == original
