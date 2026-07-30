#!/usr/bin/env python3
"""Validate a manually curated claim-evidence-citation matrix (JSON).

Input is a JSON list or ``{"claims": [...]}``. Each row should contain
``id``, ``claim``, ``evidence`` and ``citation``. Evidence and citation may be
strings or objects, but must include a usable locator (e.g. page, section,
table, figure, DOI, or local artifact path). This checks traceability fields,
not factual correctness or entailment.

Usage: python3 evidence_matrix_audit.py matrix.json [--pretty]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VERSION = "0.1.0"
LOCATORS = ("page", "section", "table", "figure", "doi", "url", "path", "artifact")


def has_locator(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return isinstance(value, dict) and any(str(value.get(key, "")).strip() for key in LOCATORS)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)
    try:
        raw = json.loads(Path(args.matrix).read_text(encoding="utf-8"))
        rows = raw.get("claims") if isinstance(raw, dict) else raw
        if not isinstance(rows, list): raise ValueError("matrix must be a list or an object with a claims list")
        ids, findings = set(), []
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict): findings.append({"row":index,"severity":"error","issue":"row is not an object"}); continue
            identifier = str(row.get("id", "")).strip()
            if not identifier: findings.append({"row":index,"severity":"error","issue":"missing id"})
            elif identifier in ids: findings.append({"row":index,"id":identifier,"severity":"error","issue":"duplicate id"})
            ids.add(identifier)
            if not str(row.get("claim", "")).strip(): findings.append({"row":index,"id":identifier,"severity":"error","issue":"missing claim text"})
            if not has_locator(row.get("evidence")): findings.append({"row":index,"id":identifier,"severity":"warning","issue":"missing evidence or evidence locator"})
            if not has_locator(row.get("citation")): findings.append({"row":index,"id":identifier,"severity":"warning","issue":"missing citation or citation locator"})
        report = {"schema_version":"1.0.0","artifact_type":"claim-evidence-citation-audit","tool_version":VERSION,"matrix":str(Path(args.matrix).resolve()),"rows":len(rows),"findings":findings,"warnings":["Field-presence audit only: it does not establish that evidence entails a claim or that a citation is bibliographically correct."]}
        print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None)); return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
