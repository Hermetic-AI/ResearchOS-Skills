"""Tests for graph_entity_merge.py (entity disambiguation + merge application)
and the new --apply-rewrites / --dry-run behavior of markdown_project_audit.py.

Covers the two remaining roadmap gaps:
  - "自动消歧和合并评分的人工验证/应用"  -> graph_entity_merge
  - "直接改写源文件的自动路径重写"        -> markdown_project_audit --apply-rewrites
"""
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGE = ROOT / "skills" / "knowledge-graph-builder" / "scripts" / "graph_entity_merge.py"
AUDIT = ROOT / "skills" / "knowledge-graph-builder" / "scripts" / "entity_identity_audit.py"
MD_AUDIT = ROOT / "skills" / "md2latex" / "scripts" / "markdown_project_audit.py"
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


def write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


# ------------------------------------------------ helper: build an identity audit

def make_same_label_graph(tmp_path: Path) -> Path:
    """Graph with two same-type/same-label nodes (concept:alpha/beta -> 'Foo'),
    a third distinct node, and edges referencing the to-be-merged pair."""
    graph = {
        "nodes": [
            {"id": "concept:alpha", "type": "method", "label": "Foo"},
            {"id": "concept:beta", "type": "method", "label": "Foo"},
            {"id": "concept:gamma", "type": "method", "label": "Bar"},
        ],
        "edges": [
            {"from": "concept:alpha", "to": "concept:gamma", "relation": "uses",
             "origin": "parser", "evidence": {"source": "a.md", "line": 1,
                                           "quote": "alpha uses gamma"}},
            {"from": "concept:beta", "to": "concept:gamma", "relation": "uses",
             "origin": "parser", "evidence": {"source": "a.md", "line": 2,
                                           "quote": "beta uses gamma"}},
        ],
    }
    return write_json(tmp_path, "graph.json", graph)


def make_similarity_graph(tmp_path: Path) -> Path:
    """Graph with two same-type, high token-overlap but differently-normalized
    labels so the audit emits a similarity candidate (6/7 token jaccard ~0.857)."""
    graph = {
        "nodes": [
            {"id": "concept:aaa", "type": "method",
             "label": "Multi Head Self Attention Feed Forward"},
            {"id": "concept:bbb", "type": "method",
             "label": "Multi Head Self Attention Feed Forward Network"},
        ],
        "edges": [
            {"from": "concept:aaa", "to": "concept:bbb", "relation": "extends",
             "origin": "parser", "evidence": {"source": "a.md", "line": 3,
                                           "quote": "aaa extends bbb"}},
        ],
    }
    return write_json(tmp_path, "graph.json", graph)


def build_audit(tmp_path: Path, graph_path: Path, *,
                similarity_threshold: float = 0.85) -> Path:
    audit_path = tmp_path / "audit.json"
    result = run_cli(AUDIT, "--graph", str(graph_path), "--out",
                     str(audit_path), "--similarity-threshold",
                     str(similarity_threshold))
    assert result.returncode == 0, result.stderr
    return audit_path


# -------------------------------------------- graph_entity_merge --auto-merge

def test_auto_merge_reduces_node_count(tmp_path: Path):
    graph_path = make_same_label_graph(tmp_path)
    audit_path = build_audit(tmp_path, graph_path)
    out = tmp_path / "merged.json"

    result = run_cli(MERGE, "--graph", str(graph_path),
                     "--identity-audit", str(audit_path),
                     "-o", str(out), "--auto-merge")
    assert result.returncode == 0, result.stderr

    merged = json.loads(out.read_text(encoding="utf-8"))
    ids = [n["id"] for n in merged["nodes"]]
    # Two 'Foo' nodes collapse into one canonical id; 'Bar' stays.
    assert len(ids) == 2
    assert "concept:alpha" in ids and "concept:gamma" in ids
    assert "concept:beta" not in ids
    # Input graph is untouched (read-only).
    original = json.loads(graph_path.read_text(encoding="utf-8"))
    assert len(original["nodes"]) == 3


def test_auto_merge_similarity_above_threshold(tmp_path: Path):
    graph_path = make_similarity_graph(tmp_path)
    audit_path = build_audit(tmp_path, graph_path)
    # Confirm the audit actually produced a similarity candidate.
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert len(audit["similarity_merge_candidates"]) >= 1
    out = tmp_path / "merged.json"

    result = run_cli(MERGE, "--graph", str(graph_path),
                     "--identity-audit", str(audit_path),
                     "-o", str(out), "--auto-merge",
                     "--similarity-threshold", "0.8")
    assert result.returncode == 0, result.stderr

    merged = json.loads(out.read_text(encoding="utf-8"))
    ids = [n["id"] for n in merged["nodes"]]
    assert len(ids) == 1
    assert ids[0] == "concept:aaa"  # lowest id wins as canonical


def test_merge_preserves_edges_no_dangling(tmp_path: Path):
    graph_path = make_same_label_graph(tmp_path)
    audit_path = build_audit(tmp_path, graph_path)
    out = tmp_path / "merged.json"

    result = run_cli(MERGE, "--graph", str(graph_path),
                     "--identity-audit", str(audit_path),
                     "-o", str(out), "--auto-merge")
    assert result.returncode == 0, result.stderr

    merged = json.loads(out.read_text(encoding="utf-8"))
    ids = {n["id"] for n in merged["nodes"]}
    for edge in merged["edges"]:
        assert edge["from"] in ids, f"dangling from: {edge}"
        assert edge["to"] in ids, f"dangling to: {edge}"
    # The beta->gamma edge was rewritten to the canonical id and both edges
    # survive (distinct evidence quotes), so we still have two edges.
    assert len(merged["edges"]) == 2


def test_merge_records_provenance(tmp_path: Path):
    graph_path = make_same_label_graph(tmp_path)
    audit_path = build_audit(tmp_path, graph_path)
    report = tmp_path / "report.json"
    out = tmp_path / "merged.json"

    result = run_cli(MERGE, "--graph", str(graph_path),
                     "--identity-audit", str(audit_path),
                     "-o", str(out), "--report", str(report),
                     "--auto-merge")
    assert result.returncode == 0, result.stderr

    merged = json.loads(out.read_text(encoding="utf-8"))
    assert "merges" in merged and len(merged["merges"]) == 1
    record = merged["merges"][0]
    assert record["canonical_id"] == "concept:alpha"
    assert record["merged_ids"] == ["concept:beta"]
    assert record["source"] == "alias-proposal"
    assert record["node_type"] == "method"

    # Report carries the same provenance + summary counts.
    rpt = json.loads(report.read_text(encoding="utf-8"))
    assert rpt["artifact_type"] == "graph-entity-merge"
    assert rpt["merges_applied"] == 1
    assert rpt["node_count"] == 2 and rpt["edge_count"] == 2


def test_merge_protected_output_no_overwrite(tmp_path: Path):
    graph_path = make_same_label_graph(tmp_path)
    audit_path = build_audit(tmp_path, graph_path)
    out = tmp_path / "merged.json"

    assert run_cli(MERGE, "--graph", str(graph_path),
                   "--identity-audit", str(audit_path),
                   "-o", str(out), "--auto-merge").returncode == 0
    original = out.read_text(encoding="utf-8")

    # Second run without --force must refuse and leave the file intact.
    again = run_cli(MERGE, "--graph", str(graph_path),
                    "--identity-audit", str(audit_path),
                    "-o", str(out), "--auto-merge")
    assert again.returncode != 0
    assert "force" in again.stderr.lower()
    assert out.read_text(encoding="utf-8") == original


# -------------------------------------------- markdown_project_audit rewrites

def _make_md_project(tmp_path: Path) -> Path:
    """Create a project where a subdir .md links to sibling resources; the .tex
    output is flattened into an out-dir, so those links would break."""
    root = tmp_path / "project"
    sub = root / "sub"
    sub.mkdir(parents=True)
    (sub / "images").mkdir()
    (sub / "images" / "figure.png").write_bytes(b"\x89PNG")
    (sub / "other.md").write_text("# Other\n", encoding="utf-8")
    doc = sub / "doc.md"
    doc.write_text(
        "# Doc\n\n"
        "![fig](images/figure.png)\n\n"
        "See [other](other.md).\n",
        encoding="utf-8",
    )
    return root


def test_apply_rewrites_updates_paths(tmp_path: Path):
    root = _make_md_project(tmp_path)
    out_dir = "build"
    (root / out_dir).mkdir()

    result = run_cli(MD_AUDIT, str(root), "--rewrite-plan",
                     "--apply-rewrites", "--out-dir", out_dir)
    assert result.returncode == 0, result.stderr

    doc = root / "sub" / "doc.md"
    content = doc.read_text(encoding="utf-8")
    # Both sibling links were rewritten to traverse back from the flattened
    # output dir (build/doc.tex) to sub/.
    assert "../sub/images/figure.png" in content
    assert "../sub/other.md" in content
    # Original (now-broken) relative forms are gone.
    assert "](images/figure.png)" not in content
    assert "](other.md)" not in content


def test_dry_run_does_not_modify_files(tmp_path: Path):
    root = _make_md_project(tmp_path)
    out_dir = "build"
    (root / out_dir).mkdir()
    doc = root / "sub" / "doc.md"
    original = doc.read_text(encoding="utf-8")

    result = run_cli(MD_AUDIT, str(root), "--rewrite-plan",
                     "--apply-rewrites", "--dry-run", "--out-dir", out_dir)
    assert result.returncode == 0, result.stderr

    assert doc.read_text(encoding="utf-8") == original
    assert not (root / "sub" / "doc.md.bak").exists()

    # The report still records what would change.
    report = json.loads(result.stdout)
    assert report["dry_run"] is True
    assert len(report["files_modified"]) == 1
    assert report["backups_created"] == []


def test_backup_created_on_apply(tmp_path: Path):
    root = _make_md_project(tmp_path)
    out_dir = "build"
    (root / out_dir).mkdir()
    doc = root / "sub" / "doc.md"
    original = doc.read_text(encoding="utf-8")

    result = run_cli(MD_AUDIT, str(root), "--rewrite-plan",
                     "--apply-rewrites", "--out-dir", out_dir)
    assert result.returncode == 0, result.stderr

    backup = root / "sub" / "doc.md.bak"
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == original


def test_apply_rewrites_protected_backup(tmp_path: Path):
    root = _make_md_project(tmp_path)
    out_dir = "build"
    (root / out_dir).mkdir()
    doc = root / "sub" / "doc.md"

    # First apply: rewrites doc.md and writes doc.md.bak.
    assert run_cli(MD_AUDIT, str(root), "--rewrite-plan",
                   "--apply-rewrites", "--out-dir", out_dir).returncode == 0
    assert (root / "sub" / "doc.md.bak").exists()

    # Revert the source from the backup, keep the backup file, then re-run
    # without --force: the existing backup must be protected.
    backup = root / "sub" / "doc.md.bak"
    doc.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
    again = run_cli(MD_AUDIT, str(root), "--rewrite-plan",
                    "--apply-rewrites", "--out-dir", out_dir)
    assert again.returncode != 0
    assert "force" in again.stderr.lower()
