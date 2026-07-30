#!/usr/bin/env python3
"""Create a protected authorship, conflict, AI-use, and availability disclosure record."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--manuscript',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised disclosure record')
  x={'schema_version':'1.0.0','artifact_type':'research-disclosure-record','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'manuscript_or_project':a.manuscript,'author_contributions':[],'conflicts_of_interest':[],'funding':[],'ai_use':{'tools':[],'tasks':[],'human_verification':[],'venue_policy_source':None},'data_availability':{'statement':None,'access_constraints':[],'repository_or_request_route':None},'code_availability':{'statement':None,'repository_or_archive':None,'version_or_commit':None},'approvals':[],'warnings':['Draft disclosure record only. Obtain contributor confirmations and verify applicable venue, funder, institutional, and legal requirements before submission.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
