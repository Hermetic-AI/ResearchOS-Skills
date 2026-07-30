#!/usr/bin/env python3
"""Audit questionnaire item-response completeness and declared score ranges.

Usage: python3 audit_item_responses.py responses.csv --items q1,q2 --min-score 1 --max-score 5 [--reverse q2]

This is a data-quality screen only. It does not estimate factors, reliability,
validity, invariance, IRT, or respondent-level construct scores.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
VERSION="0.1.0"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("responses");p.add_argument("--items",required=True);p.add_argument("--min-score",type=float,required=True);p.add_argument("--max-score",type=float,required=True);p.add_argument("--reverse",default="");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  items=[x.strip() for x in a.items.split(",") if x.strip()];reverse=[x.strip() for x in a.reverse.split(",") if x.strip()]
  if not items or a.min_score>=a.max_score:raise ValueError("items required and min-score must be less than max-score")
  rows=list(csv.DictReader(Path(a.responses).open(encoding="utf-8",newline="")))
  if not rows or any(x not in rows[0] for x in items):raise ValueError("all --items must be CSV columns")
  if any(x not in items for x in reverse):raise ValueError("--reverse items must be among --items")
  report_items=[]
  for item in items:
   missing=invalid=0;values=[]
   for row in rows:
    raw=(row.get(item) or "").strip()
    if not raw:missing+=1;continue
    try:value=float(raw)
    except ValueError:invalid+=1;continue
    if not a.min_score<=value<=a.max_score:invalid+=1
    else:values.append(value)
   report_items.append({"item":item,"reverse_scored_declared":item in reverse,"n_valid":len(values),"n_missing":missing,"n_invalid_or_out_of_range":invalid,"min_observed":min(values) if values else None,"max_observed":max(values) if values else None})
  report={"schema_version":"1.0.0","artifact_type":"item-response-audit","tool_version":VERSION,"responses":str(Path(a.responses).resolve()),"n_rows":len(rows),"declared_range":[a.min_score,a.max_score],"items":report_items,"warnings":["Range and missingness audit only: inspect wording, response process, distribution, permissions, and psychometric model assumptions separately."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
