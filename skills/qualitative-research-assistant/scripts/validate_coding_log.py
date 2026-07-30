#!/usr/bin/env python3
"""Validate a human-authored qualitative coding log against a codebook inventory."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def items(raw,key):return raw.get(key,raw) if isinstance(raw,dict) else raw
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--codebook',required=True);p.add_argument('--log',required=True,help='JSON list or {entries:[{source_id,location,code,coder,rationale}]}');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  cb=json.loads(Path(a.codebook).read_text(encoding='utf-8-sig'));codes=items(cb,'codes')
  if not isinstance(codes,list):raise ValueError('codebook must contain codes list')
  known={str(x.get('id',x.get('code',''))) for x in codes if isinstance(x,dict)}
  if not known or '' in known:raise ValueError('codebook codes need non-empty id or code')
  entries=items(json.loads(Path(a.log).read_text(encoding='utf-8-sig')),'entries')
  if not isinstance(entries,list):raise ValueError('log must be a JSON list or object with entries list')
  findings=[]
  for index,row in enumerate(entries,1):
   if not isinstance(row,dict):raise ValueError(f'entry {index} must be an object')
   missing=[key for key in ('source_id','location','code','coder','rationale') if not str(row.get(key,'')).strip()]
   if missing:findings.append({'entry':index,'issue':'missing required audit fields','fields':missing})
   if str(row.get('code','')) not in known:findings.append({'entry':index,'issue':'code not found in codebook','code':row.get('code')})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised coding audit')
  x={'schema_version':'1.0.0','artifact_type':'qualitative-coding-log-audit','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'codebook':str(Path(a.codebook).resolve()),'entries':len(entries),'findings':findings,'valid':not findings,'warnings':['This validates record completeness and declared code membership only. It does not assess interpretation, agreement, saturation, consent, de-identification, or thematic validity.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
