#!/usr/bin/env python3
"""Create a human-review mock-review checklist; it does not judge a manuscript."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION="0.1.0"
QUESTIONS=[("scope","Is the research question and claimed contribution scoped and evidence-backed?","manuscript section and contribution-evidence locator"),("methods","Are design, sampling, variables, and analysis decisions reproducible?","protocol/design/analysis artifact"),("statistics","Are uncertainty, assumptions, multiplicity, and effect sizes reported appropriately?","stat-results and analysis-plan artifact"),("reproducibility","Can data/code/environment availability and limitations be traced?","reproduction or data-governance artifact"),("interpretation","Do conclusions stay within the design and observed evidence?","claim-evidence-citation matrix"),("ethics","Are approvals, consent, conflicts, funding, and AI-use disclosures present where applicable?","disclosure record/policy source")]
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--out",required=True);p.add_argument("--manuscript-version",required=True);p.add_argument("--force",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError("output exists; use --force only for a new mock-review checklist")
  data={"schema_version":"1.0.0","artifact_type":"mock-review-checklist","tool_version":VERSION,"created_at":datetime.now(timezone.utc).isoformat(),"manuscript_version":a.manuscript_version,"questions":[{"id":f"mock-{i+1}","category":c,"question":q,"evidence_expected":e,"reviewer_notes":None,"status":"unreviewed"} for i,(c,q,e) in enumerate(QUESTIONS)],"warnings":["Preparation template only: these are not actual reviewer comments, a peer-review report, or a prediction of editorial outcome."]}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(data,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
