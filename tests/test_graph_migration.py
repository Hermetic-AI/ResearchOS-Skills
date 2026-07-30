import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATE = ROOT / "skills" / "knowledge-graph-builder" / "scripts" / "graph_version_migrate.py"
RESOLVE = ROOT / "skills" / "knowledge-graph-builder" / "scripts" / "graph_conflict_resolve.py"
ENVIRONMENT = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run_cli(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )


# ----------------------------------------------------------------- fixtures

def make_graph(tmp_path: Path, *, with_schema_version: bool = False) -> Path:
    graph = {
        "nodes": [
            {"id": "paper:1", "type": "paper", "label": "Paper One"},
            {"id": "method:1", "type": "method", "label": "Method"},
        ],
        "edges": [
            {"from": "paper:1", "to": "method:1", "relation": "uses",
             "origin": "parser", "evidence": {"source": "a.md", "line": 3,
                                           "quote": "uses method"}},
            {"from": "method:1", "to": "paper:1", "relation": "contradicts",
             "origin": "frontmatter", "evidence": {"source": "a.md", "line": 7,
                                                   "quote": "contradicts"}},
        ],
    }
    if with_schema_version:
        graph["schema_version"] = "1.0.0"
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    return path


def write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# ------------------------------------------------- graph_version_migrate.py

def test_migrate_adds_schema_version_temporal_and_validity(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    out = tmp_path / "migrated.json"

    result = run_cli(MIGRATE, str(graph_path), "--from", "1.0.0", "--to", "1.1.0",
                     "-o", str(out))
    assert result.returncode == 0, result.stderr

    migrated = json.loads(out.read_text(encoding="utf-8"))
    assert migrated["schema_version"] == "1.1.0"
    for node in migrated["nodes"]:
        assert node["temporal"] == {"year": None}
    for edge in migrated["edges"]:
        assert "valid_from" in edge and edge["valid_from"] is None
        assert "valid_to" in edge and edge["valid_to"] is None
    assert migrated["migrated"]["source_version"] == "1.0.0"
    # Input stays read-only.
    assert "schema_version" not in json.loads(
        graph_path.read_text(encoding="utf-8"))


def test_migrate_idempotent_on_already_migrated_graph(tmp_path: Path):
    graph = {
        "schema_version": "1.1.0",
        "nodes": [{"id": "paper:1", "type": "paper", "label": "P",
                   "temporal": {"year": 2024}}],
        "edges": [{"from": "paper:1", "to": "paper:1", "relation": "uses",
                   "origin": "parser", "evidence": {"source": "a.md"},
                   "valid_from": 2024, "valid_to": None}],
        "migrated": {"source_version": "1.0.0", "tool_version": "0.1.0",
                     "timestamp": "2000-01-01T00:00:00+00:00"},
    }
    graph_path = write_json(tmp_path, "graph.json", graph)
    out = tmp_path / "migrated.json"

    result = run_cli(MIGRATE, str(graph_path), "--from", "1.0.0", "--to", "1.1.0",
                     "-o", str(out))
    assert result.returncode == 0, result.stderr
    assert "no-op" in result.stderr

    migrated = json.loads(out.read_text(encoding="utf-8"))
    assert migrated["schema_version"] == "1.1.0"
    # Existing values preserved, no duplication, no overwrite of migrated note.
    assert migrated["nodes"][0]["temporal"] == {"year": 2024}
    assert migrated["edges"][0]["valid_from"] == 2024
    assert migrated["migrated"]["timestamp"] == "2000-01-01T00:00:00+00:00"
    assert "no-op" in result.stderr


def test_migrate_dry_run_does_not_write(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    out = tmp_path / "migrated.json"

    result = run_cli(MIGRATE, str(graph_path), "--from", "1.0.0", "--to", "1.1.0",
                     "-o", str(out), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert not out.exists()
    assert "migrated" in result.stderr


def test_migrate_refuses_to_overwrite_input(tmp_path: Path):
    graph_path = make_graph(tmp_path)

    result = run_cli(MIGRATE, str(graph_path), "--from", "1.0.0", "--to", "1.1.0",
                     "-o", str(graph_path))
    assert result.returncode != 0
    assert "input" in result.stderr.lower()
    # Input is untouched.
    assert "schema_version" not in json.loads(
        graph_path.read_text(encoding="utf-8"))


def test_migrate_unsupported_version_pair_errors(tmp_path: Path):
    graph_path = make_graph(tmp_path)

    result = run_cli(MIGRATE, str(graph_path), "--from", "1.0.0", "--to", "9.9.9")
    assert result.returncode != 0
    assert "unsupported" in result.stderr.lower()


def test_migrate_invalid_graph_errors(tmp_path: Path):
    graph_path = write_json(tmp_path, "graph.json", {"nodes": []})

    result = run_cli(MIGRATE, str(graph_path), "--from", "1.0.0", "--to", "1.1.0")
    assert result.returncode != 0
    assert "edges" in result.stderr.lower()


# ----------------------------------------------- graph_conflict_resolve.py

def make_resolutions(*items: dict) -> dict:
    return {"resolutions": list(items)}


def test_resolve_remove_drops_edge(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    resolutions = make_resolutions({
        "edge": {"from": "method:1", "to": "paper:1", "relation": "contradicts"},
        "action": "remove",
        "note": "user confirmed this contradicts is spurious",
    })
    res_path = write_json(tmp_path, "resolutions.json", resolutions)
    out = tmp_path / "resolved.json"
    report_path = tmp_path / "report.json"

    result = run_cli(RESOLVE, str(graph_path), str(res_path), "-o", str(out),
                     "--report", str(report_path))
    assert result.returncode == 0, result.stderr

    resolved = json.loads(out.read_text(encoding="utf-8"))
    assert len(resolved["edges"]) == 1
    assert all(e["relation"] != "contradicts" for e in resolved["edges"])

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["artifact_type"] == "graph-conflict-resolution"
    assert len(report["removed"]) == 1
    assert report["kept"] == []
    assert report["unmatched"] == []


def test_resolve_keep_adds_metadata(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    resolutions = make_resolutions({
        "edge": {"from": "paper:1", "to": "method:1", "relation": "uses"},
        "action": "keep",
        "note": "verified against paper",
    })
    res_path = write_json(tmp_path, "resolutions.json", resolutions)
    out = tmp_path / "resolved.json"

    result = run_cli(RESOLVE, str(graph_path), str(res_path), "-o", str(out))
    assert result.returncode == 0, result.stderr

    resolved = json.loads(out.read_text(encoding="utf-8"))
    kept = next(e for e in resolved["edges"] if e["relation"] == "uses")
    assert kept["metadata"]["resolved"] is True
    assert kept["metadata"]["resolution_note"] == "verified against paper"
    # Other edge untouched.
    other = next(e for e in resolved["edges"]
                 if e["relation"] == "contradicts")
    assert "metadata" not in other


def test_resolve_dry_run_does_not_write(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    resolutions = make_resolutions({
        "edge": {"from": "method:1", "to": "paper:1", "relation": "contradicts"},
        "action": "remove",
    })
    res_path = write_json(tmp_path, "resolutions.json", resolutions)
    out = tmp_path / "resolved.json"
    report_path = tmp_path / "report.json"

    result = run_cli(RESOLVE, str(graph_path), str(res_path), "-o", str(out),
                     "--report", str(report_path), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert not out.exists()
    assert not report_path.exists()
    assert "dry-run" in result.stderr


def test_resolve_unmatched_reported_without_error(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    resolutions = make_resolutions({
        "edge": {"from": "ghost", "to": "gone", "relation": "cites"},
        "action": "remove",
    })
    res_path = write_json(tmp_path, "resolutions.json", resolutions)
    out = tmp_path / "resolved.json"
    report_path = tmp_path / "report.json"

    result = run_cli(RESOLVE, str(graph_path), str(res_path), "-o", str(out),
                     "--report", str(report_path))
    assert result.returncode == 0, result.stderr

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert len(report["unmatched"]) == 1
    assert report["unmatched"][0]["reason"] == "no matching edge in graph"
    # Graph unchanged.
    resolved = json.loads(out.read_text(encoding="utf-8"))
    assert len(resolved["edges"]) == 2


def test_resolve_protected_output_no_overwrite_without_force(tmp_path: Path):
    graph_path = make_graph(tmp_path)
    resolutions = make_resolutions({
        "edge": {"from": "method:1", "to": "paper:1", "relation": "contradicts"},
        "action": "remove",
    })
    res_path = write_json(tmp_path, "resolutions.json", resolutions)
    out = tmp_path / "resolved.json"

    assert run_cli(RESOLVE, str(graph_path), str(res_path),
                  "-o", str(out)).returncode == 0
    original = out.read_text(encoding="utf-8")

    protected = run_cli(RESOLVE, str(graph_path), str(res_path),
                        "-o", str(out))
    assert protected.returncode != 0
    assert out.read_text(encoding="utf-8") == original

    forced = run_cli(RESOLVE, str(graph_path), str(res_path),
                     "-o", str(out), "--force")
    assert forced.returncode == 0, forced.stderr
