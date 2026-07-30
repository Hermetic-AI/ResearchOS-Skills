#!/usr/bin/env python3
"""Create a protected prior-art search ledger; no legal conclusion is produced."""
from __future__ import annotations
import argparse,json,sys
from datetime import date,datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--subject',required=True);p.add_argument('--cutoff-date',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  date.fromisoformat(a.cutoff_date);out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised ledger')
  x={'schema_version':'1.0.0','artifact_type':'prior-art-search-ledger','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'subject':a.subject,'cutoff_date':a.cutoff_date,'feature_matrix':[],'query_log':[],'patent_records':[],'non_patent_records':[],'family_links':[],'scope_limitations':[],'counsel_review':None,'warnings':['Research-support artifact only; it is not a legal opinion, freedom-to-operate analysis, or completeness guarantee.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
