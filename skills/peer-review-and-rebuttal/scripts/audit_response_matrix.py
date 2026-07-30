#!/usr/bin/env python3
"""Audit whether completed reviewer responses include verifiable revision evidence."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'; DONE={'addressed','complete','completed'}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--matrix',required=True);p.add_argument('--manuscript',help='optional .md/.tex text to check text: evidence');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.matrix).resolve(strict=True);matrix=json.loads(source.read_text(encoding='utf-8-sig'))
  if matrix.get('artifact_type')!='peer-review-response-matrix' or not isinstance(matrix.get('rows'),list):raise ValueError('--matrix must be a peer-review-response-matrix')
  manuscript=Path(a.manuscript).resolve(strict=True) if a.manuscript else None;text=manuscript.read_text(encoding='utf-8-sig') if manuscript else None
  findings=[]
  for row in matrix['rows']:
   status=str(row.get('response_status','')).casefold();evidence=row.get('evidence_or_location')
   if status in DONE:
    if not isinstance(evidence,str) or not evidence.strip():findings.append({'id':row.get('id'),'issue':'completed response lacks evidence_or_location'});continue
    if evidence.startswith('text:'):
     phrase=evidence[5:].strip()
     if not text:findings.append({'id':row.get('id'),'issue':'text evidence needs --manuscript'});
     elif phrase not in text:findings.append({'id':row.get('id'),'issue':'text evidence not found in manuscript','phrase':phrase})
    elif evidence.startswith('artifact:') and not Path(evidence[9:].strip()).is_file():findings.append({'id':row.get('id'),'issue':'artifact evidence path not found','path':evidence[9:].strip()})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised audit')
  x={'schema_version':'1.0.0','artifact_type':'peer-review-response-audit','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'matrix':str(source),'manuscript':str(manuscript) if manuscript else None,'findings':findings,'valid':not findings,'warnings':['Only text: and artifact: evidence locations are mechanically checked. A valid location does not prove that the response adequately addresses the reviewer comment.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
