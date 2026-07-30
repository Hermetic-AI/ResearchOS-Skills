#!/usr/bin/env python3
"""Interactively (or automatically) apply entity-merge proposals to a graph.

Purpose
-------
``entity_identity_audit.py`` is read-only: it proposes same-label alias merges
and same-type similarity candidates, but never edits a graph. This script is
the apply-side counterpart. It loads a graph JSON and the audit JSON, then for
each proposal either:

  - asks the user to approve / reject / skip (interactive mode), or
  - auto-approves same-label groups and, when ``--auto-merge`` is set, similarity
    candidates whose score meets ``--similarity-threshold`` (automatic mode).

On approval the graph is rewritten so every node in the group shares one
canonical id (the lowest id in the group, deterministically), their edges are
merged and deduped, the removed nodes are dropped, and the merge is recorded in
a ``merges`` provenance array on the output graph. The input graph is never
mutated; the merged graph is written to ``-o``.

Dependencies: Python 3.8+ standard library only (no third-party packages).

CLI usage
---------
    python3 graph_entity_merge.py --graph graph.json --identity-audit audit.json
        [-o merged.json] [--auto-merge] [--similarity-threshold 0.9]
        [--force] [--report report.json] [--quiet]

    --graph              input graph JSON (read-only).
    --identity-audit     audit JSON produced by entity_identity_audit.py.
    -o/--out             write the merged graph here (default: stdout).
    --auto-merge         auto-approve same-label groups; similarity candidates
                         are auto-approved only when their score >= threshold.
    --similarity-threshold  score cutoff for auto-merging similarity candidates
                         in automatic mode (default 0.9).
    --force              replace an existing output file.
    --report             write a JSON merge report here.
    --quiet              suppress the stderr summary.
    --version            print the tool version and exit.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"


# ----------------------------------------------------------------- merging --


def _edge_key(edge):
    """Deterministic dedup key for an edge (relation + full evidence)."""
    evidence = edge.get("evidence") or {}
    return (
        edge.get("from"), edge.get("to"), edge.get("relation"),
        json.dumps(evidence, ensure_ascii=False, sort_keys=True),
    )


def _merge_node_group(nodes_by_id, group_ids):
    """Collapse *group_ids* into the lowest id. Returns (canonical_id, merged_node,
    removed_ids, merge_record_fragment)."""
    ordered = sorted(group_ids)
    canonical_id = ordered[0]
    canonical = dict(nodes_by_id[canonical_id])
    removed_ids = ordered[1:]

    aliases = list(canonical.get("aliases") or [])
    merged_labels = []
    merged_stable = []
    for nid in ordered:
        node = nodes_by_id.get(nid) or {}
        stable = node.get("stable_entity_id")
        if stable and stable not in merged_stable:
            merged_stable.append(stable)
        label = node.get("label")
        if label and label != canonical.get("label") and label not in merged_labels:
            merged_labels.append(label)
        for alias in node.get("aliases") or []:
            if alias not in aliases:
                aliases.append(alias)
        # Preserve a file path if the canonical node has none.
        if not canonical.get("path") and node.get("path"):
            canonical["path"] = node["path"]

    if merged_labels:
        for label in merged_labels:
            if label not in aliases:
                aliases.append(label)
    if aliases:
        canonical["aliases"] = aliases
    return canonical_id, canonical, removed_ids, merged_labels, merged_stable


def _apply_merge(graph, group_ids, proposal, stable_map):
    """Apply one approved merge in-memory. Returns the merge provenance record."""
    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    canonical_id, canonical, removed_ids, merged_labels, merged_stable = (
        _merge_node_group(nodes_by_id, group_ids)
    )

    # Rewrite edges: map removed ids -> canonical, drop self-loops, dedup.
    id_map = {rid: canonical_id for rid in removed_ids}
    new_edges = []
    seen_keys = set()
    for edge in graph.get("edges") or []:
        frm = id_map.get(edge.get("from"), edge.get("from"))
        to = id_map.get(edge.get("to"), edge.get("to"))
        if frm == to:
            continue
        new = {**edge, "from": frm, "to": to}
        key = _edge_key(new)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        new_edges.append(new)

    # Drop removed nodes, replace canonical.
    new_nodes = []
    for node in graph.get("nodes") or []:
        nid = node.get("id")
        if nid in id_map:
            continue
        new_nodes.append(canonical if nid == canonical_id else node)

    graph["nodes"] = sorted(new_nodes, key=lambda n: n["id"])
    graph["edges"] = sorted(new_edges, key=lambda e: (e["from"], e["to"], e["relation"]))

    stable_for_group = [stable_map[nid] for nid in group_ids if nid in stable_map]
    return {
        "canonical_id": canonical_id,
        "merged_ids": sorted(removed_ids),
        "stable_entity_ids": sorted(set(stable_for_group)) if stable_for_group else sorted(set(merged_stable)),
        "labels": [nodes_by_id[nid].get("label") for nid in group_ids if nid in nodes_by_id],
        "node_type": proposal.get("node_type"),
        "normalized_label": proposal.get("normalized_label"),
        "score": proposal.get("score"),
        "reason": proposal.get("reason"),
        "source": proposal.get("source"),
    }


# ------------------------------------------------------------- interactive --


def _prompt(proposal, index, total):
    """Ask the user to approve/reject/skip one proposal. Returns the verb."""
    print(f"\n[{index}/{total}] Merge group ({proposal.get('node_type')}): "
          f"{proposal.get('normalized_label') or proposal.get('labels')}", file=sys.stderr)
    for nid in proposal["node_ids"]:
        print(f"      id: {nid}", file=sys.stderr)
    if proposal.get("score") is not None:
        print(f"   score: {proposal['score']}", file=sys.stderr)
    print(f"  reason: {proposal.get('reason')}", file=sys.stderr)
    while True:
        try:
            ans = input("  approve / reject / skip? [a/r/s]: ").strip().lower()
        except EOFError:
            return "skip"
        if ans in ("a", "approve", "y", "yes"):
            return "approve"
        if ans in ("r", "reject", "n", "no"):
            return "reject"
        if ans in ("s", "skip", ""):
            return "skip"
        print("  please answer a (approve), r (reject) or s (skip)", file=sys.stderr)


def _decide(proposal, index, total, auto_merge, threshold):
    """Decide the verb for one proposal. In automatic mode same-label groups are
    always approved; similarity candidates require score >= threshold."""
    if auto_merge:
        if proposal.get("source") == "similarity-candidate":
            return "approve" if (proposal.get("score") or 0) >= threshold else "skip"
        return "approve"
    if not sys.stdin.isatty():
        print("warning: no interactive terminal and --auto-merge not set; "
              "skipping remaining proposals", file=sys.stderr)
        return "skip"
    return _prompt(proposal, index, total)


# --------------------------------------------------------------------- main --


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to GBK
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Apply entity-merge proposals from an identity audit to a graph.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--graph", required=True, help="input graph JSON (read-only)")
    parser.add_argument("--identity-audit", required=True,
                        help="audit JSON from entity_identity_audit.py")
    parser.add_argument("-o", "--out", help="write merged graph here (default: stdout)")
    parser.add_argument("--auto-merge", action="store_true",
                        help="auto-approve same-label groups and qualifying similarity "
                             "candidates without prompting")
    parser.add_argument("--similarity-threshold", type=float, default=0.9,
                        help="score cutoff for auto-merging similarity candidates "
                             "(default: 0.9)")
    parser.add_argument("--report", help="write a JSON merge report here")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing output/report file")
    parser.add_argument("--quiet", action="store_true",
                        help="suppress the stderr summary")
    args = parser.parse_args(argv)

    outputs = [path for path in (args.out, args.report) if path]
    if len({str(Path(path).resolve()) for path in outputs}) != len(outputs):
        print("error: --out and --report must be different files", file=sys.stderr)
        return 2
    for path in outputs:
        if Path(path).resolve() == Path(args.graph).resolve():
            print("error: output must not replace the input graph", file=sys.stderr)
            return 2
        if Path(path).resolve() == Path(args.identity_audit).resolve():
            print("error: output must not replace the identity audit", file=sys.stderr)
            return 2
    existing = [path for path in outputs if Path(path).exists()]
    if existing and not args.force:
        print(f"error: output exists: {existing[0]}; use --force to replace it",
              file=sys.stderr)
        return 2
    if not 0 < args.similarity_threshold <= 1:
        print("error: --similarity-threshold must be in (0,1]", file=sys.stderr)
        return 2

    try:
        graph = json.loads(Path(args.graph).read_text(encoding="utf-8-sig"))
        audit = json.loads(Path(args.identity_audit).read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(graph.get("nodes"), list):
        print("error: graph must contain a nodes list", file=sys.stderr)
        return 2

    stable_map = {
        e["node_id"]: e.get("stable_entity_id") for e in audit.get("entities", [])
        if e.get("node_id") and e.get("stable_entity_id")
    }

    proposals = []
    for p in audit.get("alias_merge_proposals", []):
        proposals.append({**p, "source": "alias-proposal"})
    for p in audit.get("similarity_merge_candidates", []):
        proposals.append({**p, "source": "similarity-candidate"})

    # Work on a deep copy so the input object is never mutated.
    out_graph = json.loads(json.dumps(graph))
    merges = []
    applied = 0
    skipped = 0
    for index, proposal in enumerate(proposals, 1):
        verb = _decide(proposal, index, len(proposals),
                       args.auto_merge, args.similarity_threshold)
        if verb == "approve":
            record = _apply_merge(out_graph, proposal["node_ids"], proposal, stable_map)
            merges.append(record)
            applied += 1
        else:
            skipped += 1
        if verb == "skip" and not args.auto_merge and not sys.stdin.isatty():
            # Non-interactive warning path already skipped the rest.
            skipped += len(proposals) - index
            break

    out_graph.setdefault("merges", [])
    out_graph["merges"].extend(merges)

    node_count = len(out_graph.get("nodes") or [])
    edge_count = len(out_graph.get("edges") or [])
    report = {
        "schema_version": "1.0.0",
        "artifact_type": "graph-entity-merge",
        "tool_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_graph": str(Path(args.graph).resolve()),
        "identity_audit": str(Path(args.identity_audit).resolve()),
        "auto_merge": args.auto_merge,
        "similarity_threshold": args.similarity_threshold,
        "merges_applied": applied,
        "merges_skipped": skipped,
        "node_count": node_count,
        "edge_count": edge_count,
        "merges": merges,
        "warnings": [
            "Merged nodes share the lowest group id as their canonical id. "
            "Edges to/from removed ids were rewritten to the canonical id; "
            "resulting self-loops were dropped and duplicate edges deduped.",
        ],
    }

    payload = json.dumps(out_graph, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")

    if args.report:
        Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")

    if not args.quiet:
        print(f"merge complete: {applied} applied, {skipped} skipped; "
              f"{node_count} nodes, {edge_count} edges", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
