#!/usr/bin/env python3
"""Audit a proposal charter's human-entered budget assumptions (no cost approval)."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("charter");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  data=json.loads(Path(a.charter).read_text(encoding="utf-8"))
  if data.get("artifact_type")!="research-proposal-charter":raise ValueError("input must be a research-proposal-charter")
  items=data.get("budget_assumptions",[]);findings=[]
  if not isinstance(items,list):raise ValueError("budget_assumptions must be a list")
  for n,item in enumerate(items,1):
   if not isinstance(item,dict):findings.append({"item":n,"severity":"error","issue":"budget item is not an object"});continue
   for key in ("category","amount","rationale","source_or_rule"):
    if item.get(key) in (None,""):findings.append({"item":n,"severity":"warning","field":key,"issue":"budget assumption field is missing"})
   if item.get("amount") is not None:
    try:
     if float(item["amount"])<0:findings.append({"item":n,"severity":"error","field":"amount","issue":"amount must be non-negative"})
    except (TypeError,ValueError):findings.append({"item":n,"severity":"error","field":"amount","issue":"amount must be numeric"})
  report={"schema_version":"1.0.0","artifact_type":"budget-assumptions-audit","tool_version":VERSION,"charter":str(Path(a.charter).resolve()),"items":len(items),"findings":findings,"warnings":["Completeness audit only: it does not interpret funder rules, validate rates, currencies, eligibility, indirect costs, or approve a budget."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
