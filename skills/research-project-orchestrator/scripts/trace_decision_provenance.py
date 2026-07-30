#!/usr/bin/env python3
"""Trace full-chain decision and input provenance in a ResearchOS project.

Records the inputs, decisions, and artifacts that flow into each project
update so the user can reconstruct why a given output was produced. Read-only:
it never changes the manifest.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
VERSION = "0.1.0"


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        r = getattr(s, "reconfigure", None)
        if r:
            r(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("project")
    p.add_argument("--pretty", action="store_true")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    a = p.parse_args(argv)
    try:
        root = Path(a.project).resolve(strict=True)
        manifest = json.loads((root / "project-manifest.json").read_text(encoding="utf-8"))
        if manifest.get("artifact_type") != "research-project-manifest":
            raise ValueError("not a research-project manifest")
        decisions = []
        for i, item in enumerate(manifest.get("decisions", []) or [], 1):
            if not isinstance(item, dict):
                decisions.append({"decision": i, "severity": "error", "issue": "not an object"})
                continue
            decisions.append({
                "decision": i, "type": item.get("type"), "rationale": item.get("rationale"),
                "inputs": item.get("inputs", []), "outputs": item.get("outputs", []),
                "timestamp": item.get("timestamp"),
                "warnings": [w for w in (["missing rationale"] if not item.get("rationale") else []) +
                             (["missing inputs"] if not item.get("inputs") else []) +
                             (["missing outputs"] if not item.get("outputs") else [])],
            })
        report = {
            "schema_version": "1.0.0", "artifact_type": "decision-provenance-trace",
            "tool_version": VERSION, "project": str(root),
            "decisions": decisions,
            "warnings": ["Trace only: records declared decision provenance without re-running or verifying computations."],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2 if a.pretty else None))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
