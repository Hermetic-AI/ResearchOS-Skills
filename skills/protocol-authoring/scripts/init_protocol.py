#!/usr/bin/env python3
"""Create a protected research-protocol planning artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION="0.1.0"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--title',required=True);p.add_argument('--design',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised protocol')
  x={'schema_version':'1.0.0','artifact_type':'research-protocol','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'title':a.title,'design':a.design,'objectives':[],'hypotheses':[],'population_and_eligibility':{},'outcomes_and_estimands':[],'procedures':[],'sample_size_evidence':[],'analysis_artifacts':[],'monitoring_and_stopping':[],'ethics_and_registration':[],'data_governance':[],'amendments_and_deviations':[],'warnings':['Planning artifact only. Obtain applicable ethical, regulatory, and registration decisions from authorized bodies.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
