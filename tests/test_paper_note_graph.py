import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "knowledge-graph-builder" / "scripts" / "build_graph.py"
ENVIRONMENT = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )


def paper_note() -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "paper-note",
        "paper": {
            "title": "Evidence-Aware Graphs",
            "doi": "10.1000/GRAPH.1",
            "year": 2025,
            "authors": ["Jane Smith", "Alex Lee"],
        },
        "research_question": "Can claims retain their evidence?",
        "method": "Typed graph ingestion",
        "contributions": ["Preserves anchors"],
        "limitations": ["One paper"],
        "claims": [
            {
                "id": "finding-primary",
                "claim_type": "finding",
                "text": "The graph preserves page-level evidence.",
                "support_level": "direct",
                "evidence": [
                    {
                        "source": "paper.pdf",
                        "page": 4,
                        "section": "Results",
                        "quote": "Page-level evidence was retained.",
                        "extraction_method": "native-text",
                        "verification": "exact-match",
                    },
                    {
                        "source": "paper.pdf",
                        "page": 5,
                        "section": "Discussion",
                        "quote": "The provenance remained available.",
                        "extraction_method": "native-text",
                        "verification": "human-verified",
                    },
                ],
            }
        ],
        "provenance": {
            "created_by": "literature-reader",
            "sources": [{"kind": "file", "locator": "paper.pdf"}],
        },
    }


def test_graph_ingests_paper_note_and_preserves_every_anchor(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    note = vault / "evidence.paper-note.json"
    note.write_text(json.dumps(paper_note()), encoding="utf-8")
    graph_path = tmp_path / "graph.json"

    result = run_cli(vault, "--out", graph_path, "--quiet")
    assert result.returncode == 0, result.stderr
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    paper = next(node for node in graph["nodes"] if node["type"] == "paper")
    claim = next(node for node in graph["nodes"] if node["type"] == "claim")
    assert paper["id"] == "paper:10.1000/graph.1"
    assert paper["artifact_type"] == "paper-note"
    assert paper["source_artifacts"] == ["evidence.paper-note.json"]
    assert claim["claim_id"] == "finding-primary"
    assert claim["paper"] == paper["id"]

    edges = [edge for edge in graph["edges"] if edge["origin"] == "paper-note"]
    assert len(edges) == 2
    assert {edge["evidence"]["page"] for edge in edges} == {4, 5}
    assert {edge["evidence"]["verification"] for edge in edges} == {
        "exact-match",
        "human-verified",
    }
    assert all(edge["from"] == paper["id"] and edge["to"] == claim["id"] for edge in edges)
    assert graph["stats"]["files"] == 1
    assert graph["stats"]["errors"] == 0


def test_invalid_paper_note_is_quarantined_as_graph_error(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    invalid = paper_note()
    invalid["claims"] = []
    (vault / "invalid.paper-note.json").write_text(json.dumps(invalid), encoding="utf-8")
    graph_path = tmp_path / "graph.json"
    warnings_path = tmp_path / "warnings.md"

    result = run_cli(vault, "--out", graph_path, "--warnings", warnings_path, "--quiet")
    assert result.returncode == 1
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert graph["stats"]["errors"] == 1
    assert graph["nodes"] == []
    assert "at least one claim" in warnings_path.read_text(encoding="utf-8")


def test_non_paper_json_is_ignored_without_warning(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "unrelated.json").write_text('{"artifact_type": "stat-results"}', encoding="utf-8")
    result = run_cli(vault, "--quiet")
    assert result.returncode == 0, result.stderr
    graph = json.loads(result.stdout)
    assert graph["stats"] == {"files": 0, "nodes": 0, "edges": 0, "errors": 0}
