#!/usr/bin/env python3
"""Create a defense-question coverage checklist from declared contributions and limitations."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
AREAS=['research question and scope','methods and assumptions','evidence and robustness','novelty and alternatives','limitations and follow-up']
def text(item):return item if isinstance(item,str) else item.get('title') or item.get('text') or item.get('id') if isinstance(item,dict) else str(item)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--brief',required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  src=Path(a.brief).resolve(strict=True);brief=json.loads(src.read_text(encoding='utf-8-sig'))
  if brief.get('artifact_type')!='thesis-defense-brief':raise ValueError('--brief must be a thesis-defense-brief')
  contributions=[text(x) for x in brief.get('contributions',[])];limitations=[text(x) for x in brief.get('limitations',[])]
  rows=[{'focus':'overall','area':area,'prepared_response':None,'evidence_or_location':None,'status':'open'} for area in AREAS]
  rows += [{'focus':item,'area':'contribution evidence and novelty','prepared_response':None,'evidence_or_location':None,'status':'open'} for item in contributions if item]
  rows += [{'focus':item,'area':'limitation and mitigation','prepared_response':None,'evidence_or_location':None,'status':'open'} for item in limitations if item]
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised question checklist')
  x={'schema_version':'1.0.0','artifact_type':'thesis-defense-question-coverage','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'brief':str(src),'rows':rows,'warnings':['Preparation prompts only; they do not predict examiner questions or supply answers. Attach verified thesis locations/evidence before treating an answer as prepared.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
