#!/usr/bin/env python3
"""Create a protected ResearchOS project scaffold and provenance manifest."""
from __future__ import annotations
import argparse,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--title',required=True);p.add_argument('--project-id');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  root=Path(a.root).resolve()
  if root.exists():raise ValueError('project root already exists; refusing to merge or overwrite')
  project_id=a.project_id or re.sub(r'[^a-z0-9]+','-',a.title.lower()).strip('-')
  if not project_id:raise ValueError('title/project id must contain letters or digits')
  for name in ('inputs','artifacts','reports','logs','patches'): (root/name).mkdir(parents=True,exist_ok=True)
  manifest={'schema_version':'1.0.0','artifact_type':'research-project-manifest','project_id':project_id,'title':a.title,'created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'status':'initialized','artifacts':[],'next_route':'literature-reader','open_decisions':['Define research question, target population, primary estimand, data permissions, and protocol version.'],'warnings':['Manifest stores paths and provenance only; do not put raw restricted data, credentials, or participant identifiers here.']}
  (root/'project-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
