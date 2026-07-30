#!/usr/bin/env python3
"""Create a draft response matrix from reviewer-comment JSON; no replies are fabricated."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--comments',required=True,help='JSON list or {comments:[{reviewer,text,...}]}');p.add_argument('--out',required=True);p.add_argument('--manuscript-version',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.comments).resolve(strict=True);out=Path(a.out).resolve()
  if source==out:raise ValueError('--out must differ from comment input')
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived matrix')
  raw=json.loads(source.read_text(encoding='utf-8-sig'));comments=raw.get('comments',raw) if isinstance(raw,dict) else raw
  if not isinstance(comments,list):raise ValueError('comments must be a JSON list or object with comments list')
  rows=[]
  for i,item in enumerate(comments,1):
   if not isinstance(item,dict) or not str(item.get('text','')).strip():raise ValueError(f'comment {i} needs text')
   rows.append({'id':item.get('id',f'comment-{i}'),'reviewer':item.get('reviewer','unspecified'),'text':item['text'],'priority':item.get('priority','untriaged'),'category':item.get('category','untriaged'),'planned_action':'open','response_status':'open','evidence_or_location':None,'unresolved':[]})
  payload={'schema_version':'1.0.0','artifact_type':'peer-review-response-matrix','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'manuscript_version':a.manuscript_version,'source_comments':str(source),'rows':rows,'warnings':['This matrix is a plan, not a completed rebuttal. Attach verified manuscript locations or artifacts before claiming a comment is addressed.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
