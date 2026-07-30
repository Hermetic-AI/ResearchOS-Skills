import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = {
    **os.environ,
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUTF8": "1",
    "MPLBACKEND": "Agg",
}


def run_cli(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=20,
        check=False,
    )


def assert_protected_then_forced(script: str, args: list[str], output: Path) -> None:
    sentinel = "do-not-overwrite\n"
    output.write_text(sentinel, encoding="utf-8")

    protected = run_cli(script, *args)
    assert protected.returncode != 0
    assert protected.stderr.strip()
    assert output.read_text(encoding="utf-8") == sentinel

    forced = run_cli(script, *args, "--force")
    assert forced.returncode == 0, forced.stderr
    assert output.read_text(encoding="utf-8") != sentinel


def test_profile_output_requires_force(tmp_path: Path):
    source = tmp_path / "data.csv"
    source.write_text("group,value\nA,1\nB,2\n", encoding="utf-8")
    output = tmp_path / "profile.json"
    assert_protected_then_forced(
        "skills/data-analysis-assistant/scripts/profile.py",
        [str(source), "--out", str(output)],
        output,
    )


def test_randomization_output_requires_force(tmp_path: Path):
    output = tmp_path / "allocation.csv"
    assert_protected_then_forced(
        "skills/experiment-designer/scripts/randomization.py",
        ["complete", "--n", "4", "--seed", "7", "--out", str(output)],
        output,
    )


def test_graph_output_requires_force(tmp_path: Path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "paper.md").write_text("# Paper\n\n## Concepts\n- memory\n", encoding="utf-8")
    output = tmp_path / "graph.json"
    assert_protected_then_forced(
        "skills/knowledge-graph-builder/scripts/build_graph.py",
        [str(notes), "--out", str(output), "--quiet"],
        output,
    )


def test_md2latex_output_requires_force(tmp_path: Path):
    source = tmp_path / "paper.md"
    source.write_text("# Result\n\nEvidence.\n", encoding="utf-8")
    output = tmp_path / "paper.tex"
    assert_protected_then_forced(
        "skills/md2latex/scripts/md2latex.py",
        [str(source), "--out", str(output)],
        output,
    )


def test_diagram_output_requires_force(tmp_path: Path):
    source = tmp_path / "flow.mmd"
    source.write_text("flowchart TD\nA --> B\n", encoding="utf-8")
    output = tmp_path / "checked.mmd"
    assert_protected_then_forced(
        "skills/scientific-plot/scripts/diagram_check.py",
        ["--lang", "mermaid", "--in", str(source), "--out", str(output)],
        output,
    )


def test_excalidraw_output_requires_force(tmp_path: Path):
    source = tmp_path / "scene.json"
    source.write_text(
        json.dumps({"nodes": [{"id": "a", "label": "Input"}], "edges": []}),
        encoding="utf-8",
    )
    output = tmp_path / "scene.svg"
    assert_protected_then_forced(
        "skills/scientific-plot/scripts/excalidraw_gen.py",
        [str(source), "--out", str(output)],
        output,
    )


def test_dependency_export_requires_force(tmp_path: Path):
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "requirements.txt").write_text("numpy>=2\n", encoding="utf-8")
    output = tmp_path / "frozen.txt"
    assert_protected_then_forced(
        "skills/reproduction-assistant/scripts/parse_deps.py",
        [str(repository), "--export", str(output)],
        output,
    )


def test_dependency_export_never_replaces_source_even_with_force(tmp_path: Path):
    repository = tmp_path / "repository"
    repository.mkdir()
    source = repository / "requirements.txt"
    original = "numpy>=2\n"
    source.write_text(original, encoding="utf-8")

    result = run_cli(
        "skills/reproduction-assistant/scripts/parse_deps.py",
        str(repository),
        "--export",
        str(source),
        "--force",
    )

    assert result.returncode != 0
    assert "source" in result.stderr.lower()
    assert source.read_text(encoding="utf-8") == original
