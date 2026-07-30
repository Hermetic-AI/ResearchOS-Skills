#!/usr/bin/env python3
"""Validate a human-assessed risk-of-bias ledger without assigning judgments.

Input JSON is a list or ``{"assessments": [...]}``. Each assessment requires
``study_id``, ``tool``, ``domain``, ``judgment`` (low|some_concerns|high|unclear)
and a non-empty ``rationale``. Duplicate study/tool/domain entries are flagged.

Usage: python3 audit_risk_of_bias.py rob-ledger.json [--pretty]
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"; JUDGMENTS={"low","some_concerns","high","unclear"}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("ledger");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  raw=json.loads(Path(a.ledger).read_text(encoding="utf-8"));rows=raw.get("assessments") if isinstance(raw,dict) else raw
  if not isinstance(rows,list):raise ValueError("ledger must be a list or object with assessments list")
  seen=set();findings=[]
  for n,row in enumerate(rows,1):
   if not isinstance(row,dict):findings.append({"row":n,"severity":"error","issue":"assessment is not an object"});continue
   key=tuple(str(row.get(k,"")).strip() for k in ("study_id","tool","domain"))
   if any(not x for x in key):findings.append({"row":n,"severity":"error","issue":"study_id, tool, and domain are required"})
   elif key in seen:findings.append({"row":n,"severity":"error","issue":"duplicate study/tool/domain assessment","key":key})
   seen.add(key)
   if str(row.get("judgment","")) not in JUDGMENTS:findings.append({"row":n,"severity":"error","issue":"judgment must be low, some_concerns, high, or unclear"})
   if not str(row.get("rationale","")).strip():findings.append({"row":n,"severity":"warning","issue":"missing rationale/evidence locator"})
  report={"schema_version":"1.0.0","artifact_type":"risk-of-bias-ledger-audit","tool_version":VERSION,"ledger":str(Path(a.ledger).resolve()),"assessments":len(rows),"findings":findings,"warnings":["Structure audit only: it does not select a RoB tool, assess study methods, or determine an overall study judgment."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
