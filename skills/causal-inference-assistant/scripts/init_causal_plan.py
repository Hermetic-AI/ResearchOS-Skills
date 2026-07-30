#!/usr/bin/env python3
"""Create a draft causal-analysis charter; it documents assumptions, not causal proof."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--treatment',required=True);p.add_argument('--outcome',required=True);p.add_argument('--estimand',choices=['ATE','ATT','ATC','CATE'],required=True);p.add_argument('--population',required=True);p.add_argument('--method',choices=['backdoor','matching','weighting','iv','did','rdd','synthetic-control'],default='backdoor');p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived plan')
  payload={'schema_version':'1.0.0','artifact_type':'causal-analysis-charter','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'treatment':a.treatment,'outcome':a.outcome,'estimand':a.estimand,'population':a.population,'proposed_method':a.method,'dag_variables':{'confounders':[],'mediators':[],'colliders':[],'instruments':[],'selection_variables':[]},'required_assumptions':['Define treatment/outcome temporal ordering and consistency.','Justify target-population exchangeability or the method-specific alternative.','Assess positivity/overlap and measurement quality.'],'diagnostics':['Pre-specify balance/overlap, model fit, and design-specific falsification checks.'],'sensitivity_analyses':['Pre-specify unmeasured-confounding, specification, and missing-data sensitivity analyses.'],'warnings':['This charter does not establish causal identification. Do not adjust for post-treatment variables, colliders, or instruments without a DAG-based rationale.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
