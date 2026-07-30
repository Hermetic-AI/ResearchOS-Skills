#!/usr/bin/env python3
"""Create a protected data-management-plan artifact without handling research data."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--owner", required=True, help="Role, not personal contact details")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)
    try:
        out = Path(args.out).resolve()
        if out.exists() and not args.force:
            raise ValueError("output exists; use --force only for a revised DMP")
        payload = {
            "schema_version": "1.0.0", "artifact_type": "data-management-plan",
            "created_at": datetime.now(timezone.utc).isoformat(), "tool_version": VERSION,
            "project": args.project, "responsible_role": args.owner,
            "data_inventory": [],
            "classification": {"public": [], "internal": [], "restricted": [], "controlled": [], "decision_basis": []},
            "metadata_and_fair": {"standards": [], "persistent_identifiers": [], "documentation": [], "interoperability": []},
            "storage_and_security": {"approved_locations": [], "backup": [], "access_controls": [], "encryption": []},
            "retention_and_disposal": {"policy_sources": [], "retention_period": None, "disposal_method": None},
            "sharing_and_preservation": {"repository": None, "license": None, "access_route": None, "embargo": None},
            "approvals_and_constraints": [],
            "warnings": ["This is a governance plan, not an approval or data release. Do not publish or transform sensitive data without authorized review."],
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
