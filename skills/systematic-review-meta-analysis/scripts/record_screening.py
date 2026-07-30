#!/usr/bin/env python3
"""Validate and record human-supplied systematic-review screening decisions."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION="0.1.0"; STATES={"include","exclude","pending","duplicate"}
def load(path): return json.loads(Path(path).read_text(encoding="utf-8-sig"))
def items(raw, key): return raw.get(key,raw) if isinstance(raw,dict) else raw
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--records',required=True,help='JSON list or {records:[{id,...}]}');p.add_argument('--decisions',required=True,help='JSON list or {decisions:[{record_id,decision,reason}]}');p.add_argument('--stage',choices=('title_abstract','full_text'),required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  records=items(load(a.records),'records'); decisions=items(load(a.decisions),'decisions')
  if not isinstance(records,list) or not isinstance(decisions,list):raise ValueError('records and decisions must each be JSON lists')
  ids=[str(row.get('id','')) for row in records if isinstance(row,dict)]
  if len(ids)!=len(records) or not all(ids) or len(set(ids))!=len(ids):raise ValueError('every record needs a unique non-empty id')
  by_id={str(row.get('record_id','')):row for row in decisions if isinstance(row,dict)}
  if len(by_id)!=len(decisions) or set(by_id)!=set(ids):raise ValueError('decisions must contain exactly one record_id for every input record')
  rows=[]
  for rid in ids:
   d=by_id[rid];state=str(d.get('decision','')).lower()
   if state not in STATES:raise ValueError(f'{rid}: decision must be one of {sorted(STATES)}')
   reason=str(d.get('reason','')).strip()
   if state in {'exclude','duplicate'} and not reason:raise ValueError(f'{rid}: {state} requires a human-supplied reason')
   rows.append({'record_id':rid,'stage':a.stage,'decision':state,'reason':reason or None,'reviewer':d.get('reviewer'),'decision_source':d.get('decision_source')})
  counts={state:sum(row['decision']==state for row in rows) for state in sorted(STATES)}
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised decision log')
  result={'schema_version':'1.0.0','artifact_type':'review-screening-log','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'stage':a.stage,'source_records':str(Path(a.records).resolve()),'rows':rows,'counts':counts,'warnings':['Decisions are recorded exactly as supplied; this script does not judge relevance, duplicate status, eligibility, or risk of bias.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
