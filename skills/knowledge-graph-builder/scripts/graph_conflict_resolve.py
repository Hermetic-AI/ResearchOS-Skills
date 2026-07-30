#!/usr/bin/env python3
"""Apply user-approved conflict resolutions to a ResearchOS knowledge graph.

Purpose
-------
``audit_temporal_conflicts.py`` reports temporal anomalies and contradictory
relation pairs, but it never modifies the graph. This script is the
apply-side counterpart: it takes a graph JSON and a resolutions JSON file
produced after the user inspects the audit findings, then either removes the
flagged edges or marks them as kept-with-evidence.

Each resolution matches edges by ``(from, to, relation)``:

  - ``action: "remove"`` drops every matching edge from the graph.
  - ``action: "keep"`` marks each matching edge with
    ``metadata.resolved = true`` (and ``metadata._note``), recording that the
    user verified the relation.

The input graph is never mutated in place; the resolved graph is written to
``-o`` (or stdout) and a JSON report is written to ``--report`` (or stdout
when neither ``-o`` nor ``--report`` is given). The report lists removed,
kept, and unmatched resolutions.

Dependencies: Python 3.8+ standard library only (no third-party packages).

CLI usage
---------
    python3 graph_conflict_resolve.py graph.json resolutions.json
                               [-o resolved.json] [--report report.json]
                               [--force] [--dry-run]

    graph.json        Input graph JSON (read-only).
    resolutions.json  Resolutions JSON (read-only), see format below.
    -o/--out          Write the resolved graph here (default: stdout).
    --report          Write the JSON resolution report here
                      (default: stdout, or omitted when -o is set).
    --force           Replace an existing output file.
    --dry-run         Report what would change without writing.
    --version         Print the tool version and exit.

Resolutions JSON format
-----------------------
    {
      "resolutions": [
        {
          "edge": {"from": "nodeA", "to": "nodeB", "relation": "contradicts"},
          "action": "remove",
          "note": "user confirmed this contradicts is spurious"
        },
        {
          "edge": {"from": "nodeA", "to": "nodeB", "relation": "improves-on"},
          "action": "keep",
          "note": "verified against paper"
        }
      ]
    }
"""

import argparse
import json
import sys
from pathlib import Path

VERSION = "0.1.0"


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to GBK
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Apply user-approved conflict resolutions to a graph.")
    parser.add_argument("graph", help="input graph JSON (read-only)")
    parser.add_argument("resolutions", help="resolutions JSON (read-only)")
    parser.add_argument("-o", "--out",
                        help="write resolved graph here (default: stdout)")
    parser.add_argument("--report",
                        help="write JSON resolution report here "
                             "(default: stdout)")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing output file")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(VERSION))
    args = parser.parse_args(argv)

    in_paths = {Path(args.graph).resolve(), Path(args.resolutions).resolve()}
    out_paths = [Path(p).resolve() for p in (args.out, args.report) if p]

    for path in out_paths:
        if path in in_paths:
            print("error: output must not replace an input file ({})"
                  .format(path), file=sys.stderr)
            return 2

    if len(set(out_paths)) != len(out_paths):
        print("error: --out and --report must be different files",
              file=sys.stderr)
        return 2

    existing = [str(p) for p in out_paths if p.exists()]
    if existing and not args.force:
        print("error: output exists: {}; use --force to replace it"
              .format(existing[0]), file=sys.stderr)
        return 2

    try:
        graph = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        print("error: cannot read {}: {}".format(args.graph, exc),
              file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("error: invalid JSON in {}: {}".format(args.graph, exc),
              file=sys.stderr)
        return 2

    if not isinstance(graph.get("nodes"), list) \
            or not isinstance(graph.get("edges"), list):
        print("error: graph must contain 'nodes' and 'edges' lists",
              file=sys.stderr)
        return 2

    try:
        res_data = json.loads(Path(args.resolutions).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        print("error: cannot read {}: {}".format(args.resolutions, exc),
              file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("error: invalid JSON in {}: {}".format(args.resolutions, exc),
              file=sys.stderr)
        return 2

    if not isinstance(res_data, dict) or not isinstance(res_data.get("resolutions"), list):
        print("error: resolutions JSON must be an object with a "
              "'resolutions' list", file=sys.stderr)
        return 2

    removed, kept, unmatched = [], [], []
    edges = graph["edges"]

    for index, item in enumerate(res_data["resolutions"]):
        if not isinstance(item, dict):
            print("error: resolution #{} is not an object".format(index),
                  file=sys.stderr)
            return 2
        edge_query = item.get("edge")
        action = item.get("action")
        note = item.get("note")
        if not isinstance(edge_query, dict):
            print("error: resolution #{} 'edge' is not an object".format(index),
                  file=sys.stderr)
            return 2
        if action not in ("remove", "keep"):
            print("error: resolution #{} action must be 'remove' or 'keep', "
                  "got '{}'".format(index, action), file=sys.stderr)
            return 2
        frm, to, relation = (str(edge_query.get("from", "")),
                             str(edge_query.get("to", "")),
                             str(edge_query.get("relation", "")))
        if not frm or not to or not relation:
            print("error: resolution #{} edge needs from/to/relation".format(index),
                  file=sys.stderr)
            return 2

        matches = [e for e in edges
                   if isinstance(e, dict)
                   and str(e.get("from")) == frm
                   and str(e.get("to")) == to
                   and str(e.get("relation")) == relation]

        if not matches:
            unmatched.append({
                "edge": {"from": frm, "to": to, "relation": relation},
                "action": action,
                "note": note,
                "reason": "no matching edge in graph",
            })
            continue

        signature = {"from": frm, "to": to, "relation": relation}

        if action == "remove":
            remove_ids = {id(e) for e in matches}
            graph["edges"] = [e for e in edges if id(e) not in remove_ids]
            edges = graph["edges"]
            removed.extend(signature for _ in matches)
        else:
            for edge in matches:
                metadata = edge.get("metadata")
                if not isinstance(metadata, dict):
                    metadata = {}
                    edge["metadata"] = metadata
                metadata["resolved"] = True
                metadata["resolution_note"] = note
            kept.extend(signature for _ in matches)

    report = {
        "schema_version": "1.0.0",
        "artifact_type": "graph-conflict-resolution",
        "tool_version": VERSION,
        "removed": removed,
        "kept": kept,
        "unmatched": unmatched,
        "warnings": [],
    }

    if not args.dry_run:
        graph_payload = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
        report_payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            Path(args.out).write_text(graph_payload, encoding="utf-8")
        else:
            print(graph_payload, end="")
        if args.report:
            Path(args.report).write_text(report_payload, encoding="utf-8")
        elif not args.out:
            print(report_payload, end="")

    print("resolved: {} removed, {} kept, {}{}".format(
        len(removed), len(kept),
        "{} unmatched".format(len(unmatched)) if unmatched else "0 unmatched",
        " [dry-run]" if args.dry_run else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
