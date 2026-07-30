#!/usr/bin/env python3
"""Create a protected biomedical study-planning artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--study',required=True);p.add_argument('--study-type',required=True,choices=('observational','interventional','diagnostic','translational','preclinical'));p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised biomedical plan')
  x={'schema_version':'1.0.0','artifact_type':'biomedical-study-plan','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'study':a.study,'study_type':a.study_type,'population_and_eligibility':{},'endpoints_and_estimands':[],'interventions_or_exposures':[],'specimen_and_assay_governance':[],'safety_and_monitoring':[],'consent_ethics_registration':[],'reporting_guidelines':[],'data_governance_artifacts':[],'warnings':['Planning artifact only. Obtain all applicable scientific, ethics, clinical, laboratory, and regulatory review from authorized bodies.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
