#!/usr/bin/env python3
"""Screen a research-software quality plan for declared release evidence."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  src=Path(a.plan).resolve(strict=True);x=json.loads(src.read_text(encoding='utf-8-sig'))
  if x.get('artifact_type')!='research-software-quality-plan':raise ValueError('--plan must be a research-software-quality-plan')
  findings=[]
  for key in ('environment','test_evidence','scientific_validation','ci_evidence','release_checklist'):
   if not x.get(key):findings.append({'requirement':key,'issue':'no declared evidence'})
  lic=x.get('license_and_citation') or {}
  if not lic.get('license'):findings.append({'requirement':'license','issue':'missing declared software license'})
  if not lic.get('citation'):findings.append({'requirement':'citation','issue':'missing declared citation metadata'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised readiness screen')
  r={'schema_version':'1.0.0','artifact_type':'research-software-release-readiness','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'plan':str(src),'ready_for_human_review':not findings,'findings':findings,'warnings':['This checks declarations in a plan only. It does not execute tests, inspect a release, verify licenses/citations, assess security, or authorize publication.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
