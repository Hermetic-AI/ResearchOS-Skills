#!/usr/bin/env python3
"""Audit a proposal charter's declared Specific Aims for planning completeness."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--charter',required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  src=Path(a.charter).resolve(strict=True);x=json.loads(src.read_text(encoding='utf-8-sig'))
  if x.get('artifact_type')!='proposal-charter' or not isinstance(x.get('aims'),list):raise ValueError('--charter must be a proposal-charter with aims list')
  findings=[]
  for i,aim in enumerate(x['aims'],1):
   if not isinstance(aim,dict):findings.append({'aim':i,'issue':'aim must be an object'});continue
   missing=[key for key in ('title','objective','approach','expected_deliverable') if not str(aim.get(key,'')).strip()]
   if missing:findings.append({'aim':i,'issue':'missing planning fields','fields':missing})
   if not aim.get('evidence_ids') and not aim.get('feasibility_rationale'):findings.append({'aim':i,'issue':'missing feasibility evidence or explicit rationale'})
  if not x['aims']:findings.append({'issue':'no aims declared'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised audit')
  r={'schema_version':'1.0.0','artifact_type':'specific-aims-audit','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'charter':str(src),'aim_count':len(x['aims']),'findings':findings,'ready_for_human_review':not findings,'warnings':['This checks declared planning fields only. It does not evaluate scientific merit, innovation, fundability, budget realism, feasibility, or compliance.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
