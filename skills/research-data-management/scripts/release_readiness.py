#!/usr/bin/env python3
"""Screen a DMP for declared data-release prerequisites; never releases data."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dmp',required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  src=Path(a.dmp).resolve(strict=True);dmp=json.loads(src.read_text(encoding='utf-8-sig'))
  if dmp.get('artifact_type')!='data-management-plan':raise ValueError('--dmp must be a data-management-plan')
  sharing=dmp.get('sharing_and_preservation') or {};fair=dmp.get('metadata_and_fair') or {};constraints=dmp.get('approvals_and_constraints') or [];classification=dmp.get('classification') or {}
  findings=[]
  for key in ('repository','license','access_route'):
   if not sharing.get(key):findings.append({'requirement':key,'issue':'missing sharing/preservation decision'})
  for key in ('standards','documentation'):
   if not fair.get(key):findings.append({'requirement':key,'issue':'missing metadata/FAIR decision'})
  controlled=classification.get('controlled') or [];restricted=classification.get('restricted') or []
  if (controlled or restricted) and not constraints:findings.append({'requirement':'approvals_and_constraints','issue':'restricted/controlled classification needs documented release constraints'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised readiness screen')
  x={'schema_version':'1.0.0','artifact_type':'data-release-readiness-screen','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'dmp':str(src),'ready_for_human_review':not findings,'findings':findings,'warnings':['Passing this screen is not authorization to release data. Verify consent, contracts, de-identification, embargo, repository policy, jurisdictional rules, and approvals with authorized reviewers.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
