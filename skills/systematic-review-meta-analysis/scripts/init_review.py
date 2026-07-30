#!/usr/bin/env python3
"""Create a protected draft systematic-review protocol with PICOS and PRISMA counters."""
from __future__ import annotations
import argparse,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--title',required=True);p.add_argument('--question',required=True);p.add_argument('--population',required=True);p.add_argument('--intervention',required=True);p.add_argument('--comparator',required=True);p.add_argument('--outcomes',required=True);p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  root=Path(a.root).resolve()
  if root.exists():raise ValueError('review root exists; refusing to merge or overwrite')
  root.mkdir(parents=True);(root/'screening').mkdir();(root/'extraction').mkdir();(root/'reports').mkdir()
  protocol={'schema_version':'1.0.0','artifact_type':'systematic-review-protocol','title':a.title,'question':a.question,'picos':{'population':a.population,'intervention':a.intervention,'comparator':a.comparator,'outcomes':[x.strip() for x in a.outcomes.split(';') if x.strip()],'study_designs':[]},'status':'draft','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'prisma_counts':{'identified':0,'deduplicated':0,'title_abstract_screened':0,'full_text_assessed':0,'included':0},'open_decisions':['Define information sources, search dates, eligibility criteria, screening reviewers, risk-of-bias tool, effect measures, synthesis model, and GRADE approach.'],'warnings':['This scaffold is not a registry submission, PRISMA compliance certificate, risk-of-bias assessment, or meta-analysis result.']}
  (root/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(protocol,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
