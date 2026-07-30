import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run(script, *args, cwd=ROOT):
    return subprocess.run(
        [sys.executable, str(ROOT / script), *map(str, args)],
        cwd=cwd,
        env=ENV,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        check=True,
    )


def test_literature_metadata_and_seeded_triage(tmp_path):
    references = tmp_path / "refs.txt"
    references.write_text(
        "[1] Smith, J. Reproducible Research Workflows. Journal of Tests, 2024. https://doi.org/10.1234/example.1\n",
        encoding="utf-8",
    )
    metadata = json.loads(run("skills/literature-reader/scripts/extract_metadata.py", references).stdout)
    assert "10.1234/example.1" in json.dumps(metadata)

    scores = tmp_path / "scores.json"
    scores.write_text(json.dumps({"papers": [
        {"id": "a", "title": "A", "scores": {"relevance": 4, "novelty": 3, "quality": 4, "reproducibility": 5}},
        {"id": "b", "title": "B", "scores": {"relevance": 4, "novelty": 3, "quality": 4, "reproducibility": 5}},
    ]}), encoding="utf-8")
    first = run("skills/literature-reader/scripts/triage_score.py", scores, "--seed", "7").stdout
    second = run("skills/literature-reader/scripts/triage_score.py", scores, "--seed", "7").stdout
    assert first == second


def test_experiment_generators_are_seeded():
    args = ("complete", "--n", "8", "--arms", "treatment,control", "--seed", "42")
    first = run("skills/experiment-designer/scripts/randomization.py", *args).stdout
    second = run("skills/experiment-designer/scripts/randomization.py", *args).stdout
    assert first == second
    assert "treatment" in first and "control" in first

    matrix = run(
        "skills/experiment-designer/scripts/ablation_planner.py",
        "--mode", "loo", "--components", "encoder,decoder,augment", "--seed", "42", "--format", "json",
    ).stdout
    assert len(json.loads(matrix)["runs"]) == 4


def test_profile_and_clean_csv_without_overwriting_input(tmp_path):
    raw = tmp_path / "raw.csv"
    raw.write_text("id,group,score\n1,a,10\n1,a,10\n2,b,12\n", encoding="utf-8")
    profile = json.loads(run("skills/data-analysis-assistant/scripts/profile.py", raw, "--format", "json").stdout)
    assert profile["row_count"] == 3

    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"steps": [{"op": "dedupe", "columns": ["id"], "keep": "first", "rationale": "duplicate id"}]}), encoding="utf-8")
    clean = tmp_path / "clean.csv"
    run("skills/data-analysis-assistant/scripts/clean_csv.py", raw, rules, "--out", clean, "--log-format", "json")
    assert raw.read_text(encoding="utf-8").count("\n") == 4
    assert clean.read_text(encoding="utf-8").count("\n") == 3


def test_knowledge_graph_builds_json_and_dot(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "paper.md").write_text("# Paper\nUses [[Dataset A]] and cites @smith2024.\n", encoding="utf-8")
    graph = tmp_path / "graph.json"
    dot = tmp_path / "graph.dot"
    run("skills/knowledge-graph-builder/scripts/build_graph.py", notes, "--out", graph, "--dot", dot, "--quiet")
    payload = json.loads(graph.read_text(encoding="utf-8"))
    assert payload["nodes"] and dot.read_text(encoding="utf-8").startswith("digraph")


def test_markdown_conversion_and_citation_extraction(tmp_path):
    manuscript = tmp_path / "paper.md"
    manuscript.write_text("# Result\nEvidence supports this claim [1].\n\n# References\n[1] A. Author. A result. 2024.\n", encoding="utf-8")
    tex = tmp_path / "paper.tex"
    report = json.loads(run("skills/md2latex/scripts/md2latex.py", manuscript, "--out", tex).stdout)
    assert tex.is_file() and "Result" in tex.read_text(encoding="utf-8")
    assert report["output"] == str(tex)

    citations = json.loads(run("skills/paper-writing-assistant/scripts/md_text.py", manuscript, "--json").stdout)
    assert citations["cited_valid"] == [1]
    assert citations["uncited"] == []


def test_reproduction_probe_and_comparison(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    (repository / "README.md").write_text("```bash\npython train.py\n```\n", encoding="utf-8")
    (repository / "train.py").write_text("print('ok')\n", encoding="utf-8")
    probe = json.loads(run("skills/reproduction-assistant/scripts/repo_probe.py", repository).stdout)
    assert probe["entry_candidates"]

    comparison = json.loads(run(
        "skills/reproduction-assistant/scripts/compare_results.py",
        "--pair", "model:data:accuracy:0.90:0.895", "--format", "json",
    ).stdout)
    assert comparison["rows"][0]["verdict"] == "match"


def test_diagram_tools_create_reproducible_artifacts(tmp_path):
    mermaid = tmp_path / "flow.mmd"
    mermaid.write_text("flowchart LR\nA[Input] --> B[Output]\n", encoding="utf-8")
    checked = run("skills/scientific-plot/scripts/diagram_check.py", "--lang", "mermaid", "--in", mermaid)
    assert "mermaid-cli" in checked.stdout

    scene = tmp_path / "scene.json"
    scene.write_text(json.dumps({"nodes": [{"id": "a", "label": "Input"}, {"id": "b", "label": "Output"}], "edges": [{"from": "a", "to": "b"}]}), encoding="utf-8")
    first = tmp_path / "first.svg"
    second = tmp_path / "second.svg"
    run("skills/scientific-plot/scripts/excalidraw_gen.py", scene, "--out", first, "--seed", "9")
    run("skills/scientific-plot/scripts/excalidraw_gen.py", scene, "--out", second, "--seed", "9")
    assert first.read_bytes() == second.read_bytes()
