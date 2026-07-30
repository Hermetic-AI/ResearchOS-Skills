#!/usr/bin/env python3
"""Create a protected social-science study-planning artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--question',required=True);p.add_argument('--design',required=True,choices=('quantitative','qualitative','mixed-methods','experimental','observational'));p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised social-science plan')
  x={'schema_version':'1.0.0','artifact_type':'social-science-study-plan','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'question':a.question,'design':a.design,'theory_and_constructs':[],'population_sampling_and_generalization':[],'measurement_or_fieldwork':[],'consent_ethics_and_governance':[],'analysis_and_causal_boundaries':[],'preregistration_and_deviations':[],'reflexivity_and_reporting':[],'data_governance_artifacts':[],'warnings':['Planning artifact only. Do not treat declared plans as evidence of representativeness, consent, causal identification, validity, generalizability, or community approval.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
