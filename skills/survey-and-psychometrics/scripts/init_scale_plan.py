#!/usr/bin/env python3
"""Create a draft survey and psychometric validation charter; not a validated scale."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--construct',required=True);p.add_argument('--population',required=True);p.add_argument('--use',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived charter')
  payload={'schema_version':'1.0.0','artifact_type':'psychometric-validation-charter','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'construct':a.construct,'target_population':a.population,'intended_use':a.use,'items':[],'required_decisions':['Define construct boundaries, content evidence, response scale, recall period, translation/accessibility, and intellectual-property permission.','Pre-specify pilot/cognitive testing, sampling, EFA/CFA split or replication, reliability estimands, factor model, invariance comparisons, and IRT/Rasch model if used.','Pre-specify missing-data, reverse-coding, local-dependence, differential-item-functioning, floor/ceiling, and reporting rules.'],'warnings':['This charter is not a validated instrument, reliability estimate, factor solution, invariance result, or permission to reproduce copyrighted items.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
