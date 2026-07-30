#!/usr/bin/env python3
"""Create a protected machine-learning experiment planning artifact."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--task',required=True);p.add_argument('--primary-metric',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised ML plan')
  x={'schema_version':'1.0.0','artifact_type':'ml-experiment-plan','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'task':a.task,'primary_metric':a.primary_metric,'intended_use':None,'prohibited_uses':[],'data_and_splits':{'unit_of_split':None,'leakage_controls':[],'dataset_evidence':[]},'baselines':[],'metrics_and_thresholds':[],'ablations':[],'compute_budget':{},'evaluation_protocol':{},'model_card_evidence':[],'reproducibility_artifacts':[],'risks_and_limitations':[],'warnings':['Planning artifact only. Attach executed run artifacts and protocol evidence before making performance, fairness, safety, or reproducibility claims.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
