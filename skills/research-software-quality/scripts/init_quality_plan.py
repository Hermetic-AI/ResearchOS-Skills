#!/usr/bin/env python3
"""Create a protected research-software quality-plan artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--project',required=True);p.add_argument('--version-label',dest='label',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised quality plan')
  x={'schema_version':'1.0.0','artifact_type':'research-software-quality-plan','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'project':a.project,'release_version':a.label,'environment':{},'test_evidence':[],'scientific_validation':[],'ci_evidence':[],'benchmark_protocols':[],'release_checklist':[],'license_and_citation':{},'known_limitations':[],'warnings':['Planning artifact only. Attach executed commands and outcomes before making quality or release-readiness claims.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
