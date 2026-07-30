#!/usr/bin/env python3
"""Compute complete-case Cronbach's alpha from declared numeric survey item columns."""
from __future__ import annotations
import argparse,csv,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def variance(values):
 mean=sum(values)/len(values);return sum((x-mean)**2 for x in values)/(len(values)-1)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv');p.add_argument('--items',required=True,help='comma-separated item columns');p.add_argument('--reverse',default='',help='comma-separated reverse-scored item columns');p.add_argument('--max-score',type=float,help='required when --reverse is used; reverse value = max-score - value');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  src=Path(a.csv).resolve(strict=True);items=[x.strip() for x in a.items.split(',') if x.strip()];reverse=[x.strip() for x in a.reverse.split(',') if x.strip()]
  if len(items)<2 or len(set(items))!=len(items):raise ValueError('--items needs at least two distinct columns')
  if any(x not in items for x in reverse):raise ValueError('--reverse items must occur in --items')
  if reverse and a.max_score is None:raise ValueError('--max-score is required with --reverse')
  with src.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f));columns=set(rows[0]) if rows else set()
  missing=[x for x in items if x not in columns]
  if missing:raise ValueError('missing item columns: '+', '.join(missing))
  complete=[];dropped=0
  for row in rows:
   try:
    vals=[float(row[x]) for x in items]
    for i,key in enumerate(items):
     if key in reverse:vals[i]=a.max_score-vals[i]
    complete.append(vals)
   except (ValueError,TypeError):dropped+=1
  if len(complete)<2:raise ValueError('need at least two complete response rows')
  k=len(items);item_variances=[variance([row[i] for row in complete]) for i in range(k)];total_variance=variance([sum(row) for row in complete])
  if total_variance<=0:raise ValueError('total score variance must be positive')
  alpha=k/(k-1)*(1-sum(item_variances)/total_variance)
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised analysis')
  x={'schema_version':'1.0.0','artifact_type':'scale-reliability-result','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'source':str(src),'items':items,'reverse_items':reverse,'reverse_max_score':a.max_score,'missing_handling':'complete-case exclusion','n_input_rows':len(rows),'n_complete_rows':len(complete),'n_dropped_rows':dropped,'cronbach_alpha':alpha,'item_variances':dict(zip(items,item_variances)),'warnings':['Cronbach alpha measures internal consistency under its assumptions; it does not establish unidimensionality, validity, invariance, reliability for individual scores, or a universal adequacy threshold.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
