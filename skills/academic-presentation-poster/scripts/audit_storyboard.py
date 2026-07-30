#!/usr/bin/env python3
"""Audit a presentation storyboard for declared evidence and accessibility planning."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--storyboard',required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  src=Path(a.storyboard).resolve(strict=True);x=json.loads(src.read_text(encoding='utf-8-sig'))
  if x.get('artifact_type')!='presentation-storyboard':raise ValueError('--storyboard must be a presentation-storyboard')
  findings=[];claims=x.get('claim_evidence_ledger') or [];visuals=x.get('visual_inventory') or [];access=x.get('accessibility_plan') or {}
  if not x.get('core_takeaway'):findings.append({'requirement':'core_takeaway','issue':'missing'})
  for i,item in enumerate(claims,1):
   if not isinstance(item,dict) or not item.get('claim') or not (item.get('source') or item.get('artifact')):findings.append({'claim':i,'issue':'claim needs text and source/artifact'})
  for key in ('reading_order','contrast_review','alt_text'):
   if visuals and not access.get(key):findings.append({'requirement':key,'issue':'visual inventory exists but accessibility plan is empty'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised audit')
  r={'schema_version':'1.0.0','artifact_type':'presentation-storyboard-audit','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'storyboard':str(src),'findings':findings,'ready_for_human_review':not findings,'warnings':['This checks declared planning fields only. It does not render a deck/poster, verify visual contrast, validate source claims, or certify accessibility.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
