#!/usr/bin/env python3
"""Create a protected thesis-defense preparation brief."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
VERSION = "0.1.0"
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--out", required=True); p.add_argument("--thesis-title", required=True); p.add_argument("--candidate", required=True); p.add_argument("--force", action="store_true"); p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}"); a=p.parse_args(argv)
    try:
        out=Path(a.out).resolve()
        if out.exists() and not a.force: raise ValueError("output exists; use --force only for a revised defense brief")
        x={"schema_version":"1.0.0","artifact_type":"thesis-defense-brief","created_at":datetime.now(timezone.utc).isoformat(),"tool_version":VERSION,"thesis_title":a.thesis_title,"candidate":a.candidate,"research_question":None,"contributions":[],"evidence_ledger":[],"limitations":[],"anticipated_questions":[],"follow_up_actions":[],"warnings":["Preparation artifact only. Verify requirements and evidence with the candidate, institution, and thesis materials."]}
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError) as e: print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
