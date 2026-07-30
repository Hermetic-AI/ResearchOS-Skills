#!/usr/bin/env python3
"""Preview or apply a guarded project-manifest status/artifact update."""
from __future__ import annotations
import argparse,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
TYPES={'paper-note':'knowledge-graph-builder','literature-matrix':'experiment-designer','research-gap':'experiment-designer','design-brief':'experiment-designer','analysis-plan':'data-analysis-assistant','cleaning-manifest':'data-analysis-assistant','stat-results':'scientific-plot','figure-manifest':'paper-writing-assistant','reproduction-card':'paper-writing-assistant'}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return 'sha256:'+h.hexdigest()
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('project');p.add_argument('--artifact');p.add_argument('--type',choices=sorted(TYPES));p.add_argument('--status',choices=['initialized','active','blocked','complete']);p.add_argument('--next-route');p.add_argument('--apply',action='store_true',help='write update; default previews only');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  root=Path(a.project).resolve(strict=True);manifest_path=root/'project-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
  if manifest.get('artifact_type')!='research-project-manifest':raise ValueError('not a research-project manifest')
  if a.artifact and not a.type:raise ValueError('--artifact requires --type')
  if a.type and not a.artifact:raise ValueError('--type requires --artifact')
  if a.artifact:
   path=Path(a.artifact).resolve(strict=True)
   if path==manifest_path:raise ValueError('project manifest cannot register itself as an artifact')
   payload=json.loads(path.read_text(encoding='utf-8'))
   if payload.get('artifact_type')!=a.type:raise ValueError(f"artifact_type must be {a.type!r}")
   item={'path':str(path),'artifact_type':a.type,'checksum':digest(path),'registered_at':datetime.now(timezone.utc).isoformat()}
   if item not in manifest['artifacts']:manifest['artifacts'].append(item)
   manifest['next_route']=a.next_route or TYPES[a.type]
  elif a.next_route:manifest['next_route']=a.next_route
  if a.status:manifest['status']=a.status
  manifest['updated_at']=datetime.now(timezone.utc).isoformat()
  manifest['last_update_provenance']={'created_by':'research-project-orchestrator/update_project.py','command':' '.join(sys.argv),'tool_version':VERSION}
  manifest['update_mode']='applied' if a.apply else 'preview'
  if a.apply:
   manifest.pop('update_mode');manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps(manifest,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
