#!/usr/bin/env python3
"""Conservatively cluster local scholarly JSON records by DOI or title/year."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
VERSION='0.1.0'
def norm(value):
 value=re.sub(r'^https?://(?:dx\.)?doi\.org/','',str(value or '').strip().lower())
 value=re.sub(r'^doi:\s*','',value)
 return re.sub(r'[^a-z0-9]','',value)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('records');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.records).resolve(strict=True);out=Path(a.out).resolve()
  if source==out:raise ValueError('--out must differ from input')
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived library')
  payload=json.loads(source.read_text(encoding='utf-8'));items=payload.get('items',payload) if isinstance(payload,dict) else payload if isinstance(payload,list) else None
  if not isinstance(items,list):raise ValueError('input must be a JSON list or object with items list')
  buckets={}
  for i,item in enumerate(items):
   if not isinstance(item,dict):raise ValueError(f'item {i} is not an object')
   key='doi:'+norm(item.get('doi')) if norm(item.get('doi')) else 'title-year:'+norm(item.get('title'))+':'+str(item.get('year',''))
   if key in buckets and key.startswith('title-year:') and not norm(item.get('title')):key=f'unresolved:{i}'
   buckets.setdefault(key,[]).append((i,item))
  canonical=[];clusters=[]
  for key,members in buckets.items():
   best=max(members,key=lambda pair:sum(bool(pair[1].get(field)) for field in ('doi','title','authors','abstract','year')))[1]
   canonical.append(best)
   if len(members)>1:clusters.append({'key':key,'canonical_index':items.index(best),'member_indexes':[i for i,_ in members],'action':'review-and-merge-metadata; do-not-delete-automatically'})
  result={'schema_version':'1.0.0','artifact_type':'search-library','input':str(source),'items':canonical,'duplicate_clusters':clusters,'warnings':['Title/year clusters are candidates, not proof of duplicates. Review authors, version, and identifiers before merging.']}
  out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
