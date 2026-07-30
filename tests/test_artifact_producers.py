import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"}


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(ROOT / script), *map(str, args)],
        cwd=ROOT,
        env=ENV,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )


def assert_contract(path, definition):
    instance = json.loads(path.read_text(encoding="utf-8"))
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(instance)
    return instance


def test_cleaner_emits_manifest_and_never_replaces_raw_input(tmp_path):
    raw = tmp_path / "raw.csv"
    raw.write_text("id,value\n1,10\n1,10\n2,12\n", encoding="utf-8")
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"steps": [{"op": "dedupe", "columns": ["id"], "reason": "duplicate export"}]}), encoding="utf-8")
    clean = tmp_path / "clean.csv"
    manifest = tmp_path / "cleaning.json"
    result = run(
        "skills/data-analysis-assistant/scripts/clean_csv.py",
        raw, rules, "--out", clean, "--artifact-out", manifest, "--log-format", "json",
    )
    assert result.returncode == 0, result.stderr
    artifact = assert_contract(manifest, "cleaning_manifest")
    assert artifact["steps"][0]["affected"] == 1
    assert artifact["input"]["locator"] != artifact["output"]["locator"]

    destructive = run("skills/data-analysis-assistant/scripts/clean_csv.py", raw, rules, "--out", raw, "--force")
    assert destructive.returncode != 0
    assert "must not replace an input" in destructive.stderr
    assert raw.read_text(encoding="utf-8").startswith("id,value\n1,10")


def test_comparison_emits_reproduction_card_and_requires_commit(tmp_path):
    manifest = tmp_path / "reproduction.json"
    missing = run(
        "skills/reproduction-assistant/scripts/compare_results.py",
        "--pair", "model:data:accuracy:0.90:0.895",
        "--artifact-out", manifest,
        "--environment-json", '{"python":"3.12"}',
    )
    assert missing.returncode != 0
    assert "--repository-commit" in missing.stderr

    result = run(
        "skills/reproduction-assistant/scripts/compare_results.py",
        "--pair", "model:data:accuracy:0.90:0.895",
        "--artifact-out", manifest,
        "--repository-commit", "abc123",
        "--environment-json", '{"python":"3.12"}',
        "--format", "json",
    )
    assert result.returncode == 0, result.stderr
    artifact = assert_contract(manifest, "reproduction_card")
    assert artifact["repository_commit"] == "abc123"
    assert artifact["comparisons"][0]["verdict"] == "match"

    overwrite = run(
        "skills/reproduction-assistant/scripts/compare_results.py",
        "--pair", "model:data:accuracy:0.90:0.895",
        "--artifact-out", manifest,
        "--repository-commit", "abc123",
        "--environment-json", '{}',
    )
    assert overwrite.returncode != 0
    assert "use --force" in overwrite.stderr


def test_plotter_emits_figure_manifest_and_guards_outputs(tmp_path):
    pytest.importorskip("matplotlib")
    pytest.importorskip("numpy")
    data = tmp_path / "data.csv"
    data.write_text("group,value\nA,1\nA,2\nB,2\nB,3\n", encoding="utf-8")
    statistics = tmp_path / "statistics.json"
    statistics.write_text(json.dumps({
        "schema_version": "1.0.0",
        "artifact_type": "stat-results",
        "provenance": {"created_by": "test", "sources": [{"kind": "file", "locator": "data.csv"}]},
        "alpha": 0.05,
        "results": [{"id": "primary", "test": "Welch t", "statistic": 2.0, "p_value": 0.03,
                     "adjusted_p_value": 0.04, "effect_size": 0.5, "confidence_interval": [0.1, 0.9]}],
    }), encoding="utf-8")
    output = tmp_path / "figure"
    result = run(
        "skills/scientific-plot/scripts/plot_chart.py",
        data, "--template", "boxplot", "--x", "group", "--y", "value",
        "--formats", "svg", "--out", output,
        "--statistics-source", statistics, "--star-map", "A>B=primary",
    )
    assert result.returncode == 0, result.stderr
    artifact = assert_contract(tmp_path / "figure.manifest.json", "figure_manifest")
    assert artifact["figure_id"] == "figure"
    assert artifact["outputs"] == [str((tmp_path / "figure.svg").resolve())]
    stats = json.loads((tmp_path / "figure.stats.json").read_text(encoding="utf-8"))
    assert stats["stats"][0]["result_id"] == "primary"
    assert stats["stats"][0]["p_field"] == "adjusted_p_value"
    assert stats["stats"][0]["stars"] == "*"

    overwrite = run(
        "skills/scientific-plot/scripts/plot_chart.py",
        data, "--template", "boxplot", "--x", "group", "--y", "value",
        "--formats", "svg", "--out", output,
        "--statistics-source", statistics, "--star-map", "A>B=primary",
    )
    assert overwrite.returncode != 0
    assert "use --force" in overwrite.stderr
