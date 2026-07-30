#!/usr/bin/env python3
"""Migrate a ResearchOS knowledge-graph JSON from one schema version to another.

Purpose
-------
Graph schema versions evolve: new optional fields are added and node/edge
shapes change. This script applies a registered, idempotent migration to a
graph JSON so downstream tools can rely on the target schema. It never
mutates the input file; it writes the migrated graph to ``-o`` (or stdout)
and prints a migration report to stderr.

The initial concrete migration is ``1.0.0`` -> ``1.1.0``, which:

  - sets the top-level ``schema_version`` to ``"1.1.0"``
  - adds ``temporal: {year: null}`` to nodes that lack a ``temporal`` object
  - adds ``valid_from`` / ``valid_to`` (null) to edges that lack them
  - records a ``migrated`` provenance note (source version, tool version, UTC
    timestamp) — only when the graph was not already at the target version

Further migrations are added by registering a new ``(from, to)`` step in the
``MIGRATIONS`` registry; each step mutates the graph in place and returns the
number of nodes/edges it touched.

Dependencies: Python 3.8+ standard library only (no third-party packages).

CLI usage
---------
    python3 graph_version_migrate.py graph.json --from 1.0.0 --to 1.1.0
                               [-o migrated.json] [--force] [--dry-run]

    graph.json   Input graph JSON (read-only).
    --from       Source schema version. Defaults to the graph's own
                 ``schema_version`` (``"1.0.0"`` if absent). Must match the
                 detected version unless the graph is already at ``--to``.
    --to         Target schema version (required).
    -o/--out     Write the migrated graph here (default: stdout).
    --force      Replace an existing output file.
    --dry-run    Report what would change without writing.
    --version    Print the tool version and exit.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"


# ----------------------------------------------------------- migration steps

def migrate_1_0_0_to_1_1_0(graph):
    """Apply the 1.0.0 -> 1.1.0 migration in place.

    Returns ``(nodes_touched, edges_touched)``. Each sub-step is idempotent:
    fields already present are left untouched, so re-running on a 1.1.0 graph
    touches nothing.
    """
    nodes_touched = 0
    for node in graph.get("nodes", []):
        if isinstance(node, dict) and "temporal" not in node:
            node["temporal"] = {"year": None}
            nodes_touched += 1

    edges_touched = 0
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict):
            continue
        touched = False
        if "valid_from" not in edge:
            edge["valid_from"] = None
            touched = True
        if "valid_to" not in edge:
            edge["valid_to"] = None
            touched = True
        if touched:
            edges_touched += 1

    graph["schema_version"] = "1.1.0"
    return nodes_touched, edges_touched


MIGRATIONS = {
    ("1.0.0", "1.1.0"): migrate_1_0_0_to_1_1_0,
}


# --------------------------------------------------------------------- driver

def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to GBK
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Migrate a ResearchOS graph JSON between schema versions.")
    parser.add_argument("graph", help="input graph JSON (read-only)")
    parser.add_argument("--from", dest="from_version", default=None,
                        help="source schema version (default: auto-detect)")
    parser.add_argument("--to", dest="to_version", required=True,
                        help="target schema version")
    parser.add_argument("-o", "--out",
                        help="write migrated graph here (default: stdout)")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing output file")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(VERSION))
    args = parser.parse_args(argv)

    try:
        graph_path = Path(args.graph).resolve()
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
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

    if args.out:
        out_path = Path(args.out).resolve()
        if out_path == graph_path:
            print("error: output must not replace the input graph",
                  file=sys.stderr)
            return 2
        if out_path.exists() and not args.force:
            print("error: output exists: {}; use --force to replace it"
                  .format(out_path), file=sys.stderr)
            return 2
    else:
        out_path = None

    detected = graph.get("schema_version", "1.0.0")
    source = args.from_version if args.from_version is not None else detected
    key = (source, args.to_version)

    if key not in MIGRATIONS:
        supported = ", ".join("{} -> {}".format(a, b) for a, b in MIGRATIONS)
        print("error: unsupported migration '{}' -> '{}'; supported: {}"
              .format(source, args.to_version, supported), file=sys.stderr)
        return 2

    if detected == args.to_version:
        no_op = True
    elif args.from_version is not None and detected != args.from_version:
        print("error: graph schema_version is '{}', expected --from '{}'"
              .format(detected, args.from_version), file=sys.stderr)
        return 2
    else:
        no_op = False

    migrate_fn = MIGRATIONS[key]
    nodes_touched, edges_touched = migrate_fn(graph)

    if not no_op:
        graph["migrated"] = {
            "source_version": source,
            "tool_version": VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    if not args.dry_run:
        payload = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
        if out_path is not None:
            out_path.write_text(payload, encoding="utf-8")
        else:
            print(payload, end="")

    if no_op and nodes_touched == 0 and edges_touched == 0:
        status = "no-op (already at target version {})".format(args.to_version)
    else:
        status = "migrated {} -> {}".format(source, args.to_version)
    print("{}, {} node(s) and {} edge(s) touched".format(
        status, nodes_touched, edges_touched), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
