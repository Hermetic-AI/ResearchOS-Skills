#!/usr/bin/env python3
"""Create a protected materials-research planning artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--material-system',required=True);p.add_argument('--target-property',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised materials plan')
  x={'schema_version':'1.0.0','artifact_type':'materials-experiment-plan','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'material_system':a.material_system,'target_property':a.target_property,'formulation_and_inputs':[],'process_variables':[],'sample_lineage':[],'characterization_plan':[],'property_test_protocol':[],'calibration_and_uncertainty':[],'safety_and_waste':[],'data_provenance_artifacts':[],'warnings':['Planning artifact only. Do not claim material identity, performance, stability, purity, or safety without appropriate measurements, calibration, and authorized review.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
