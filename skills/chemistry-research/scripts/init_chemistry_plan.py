#!/usr/bin/env python3
"""Create a protected chemistry-research planning artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--objective',required=True);p.add_argument('--experiment-type',required=True,choices=('synthesis','formulation','analytical','catalysis','computational'));p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised chemistry plan')
  x={'schema_version':'1.0.0','artifact_type':'chemistry-experiment-plan','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'objective':a.objective,'experiment_type':a.experiment_type,'reagents_and_inputs':[],'conditions_and_controls':[],'sample_lineage':[],'analytical_evidence_plan':[],'calibration_and_uncertainty':[],'hazard_waste_and_sop_references':[],'data_provenance_artifacts':[],'warnings':['Planning artifact only. Follow authorized local SOPs and obtain qualified safety review; do not treat this plan as a procedure, hazard assessment, or experimental result.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
