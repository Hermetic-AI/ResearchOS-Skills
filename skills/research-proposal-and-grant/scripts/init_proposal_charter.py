#!/usr/bin/env python3
"""Create a protected, evidence-aware proposal-planning charter."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--funder", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)
    try:
        out = Path(args.out).resolve()
        if out.exists() and not args.force:
            raise ValueError("output exists; use --force only for a derived charter")
        payload = {
            "schema_version": "1.0.0", "artifact_type": "proposal-charter",
            "created_at": datetime.now(timezone.utc).isoformat(), "tool_version": VERSION,
            "title": args.title, "research_question": args.question, "funder_or_call": args.funder,
            "call_evidence": {"url_or_document": None, "deadline": None, "eligibility": [], "required_sections": []},
            "aims": [], "innovation": [], "approach": [],
            "milestones": [], "budget_assumptions": [], "risks_and_fallbacks": [],
            "evidence_ledger": [], "compliance_decisions": [],
            "warnings": ["Planning artifact only. Verify funder rules, costs, eligibility, and approvals against primary sources before submission."],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
