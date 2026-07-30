#!/usr/bin/env python3
"""Audit graph-edge evidence anchor completeness without modifying graph claims."""
from __future__ import annotations
import argparse,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'; DOI=re.compile(r'^10\.\d{4,9}/\S+$',re.I)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--graph',required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.graph).resolve(strict=True);graph=json.loads(source.read_text(encoding='utf-8-sig'));edges=graph.get('edges')
  if not isinstance(edges,list):raise ValueError('graph must contain edges list')
  findings=[];summary={'edges':len(edges),'with_evidence':0,'with_page_or_section':0,'with_doi':0,'with_verification':0}
  for i,edge in enumerate(edges):
   evidence=edge.get('evidence') if isinstance(edge,dict) else None
   entries=evidence if isinstance(evidence,list) else [evidence] if isinstance(evidence,dict) else []
   if not entries:findings.append({'edge':i,'issue':'missing evidence anchor'});continue
   summary['with_evidence']+=1
   for j,item in enumerate(entries):
    if not isinstance(item,dict):findings.append({'edge':i,'anchor':j,'issue':'anchor is not an object'});continue
    if item.get('page') is not None or item.get('section'):summary['with_page_or_section']+=1
    else:findings.append({'edge':i,'anchor':j,'issue':'missing page and section'})
    raw=str(item.get('doi','')).strip().removeprefix('https://doi.org/').removeprefix('doi:')
    if raw and DOI.fullmatch(raw):summary['with_doi']+=1
    else:findings.append({'edge':i,'anchor':j,'issue':'missing or invalid DOI'})
    if item.get('verification'):summary['with_verification']+=1
    else:findings.append({'edge':i,'anchor':j,'issue':'missing verification/credibility state'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised audit')
  x={'schema_version':'1.0.0','artifact_type':'graph-evidence-anchor-audit','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'source_graph':str(source),'summary':summary,'findings':findings,'warnings':['Missing fields are audit findings, not evidence that a relation is false. This script does not verify DOI resolution, page truth, quote accuracy, or credibility.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
