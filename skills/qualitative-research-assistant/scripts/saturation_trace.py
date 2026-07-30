#!/usr/bin/env python3
"""Create a descriptive new-code saturation trace from a human coding log.

The caller supplies source order explicitly. The script reports codes first
observed in each source and a cumulative curve; it never declares saturation.

Usage: python3 saturation_trace.py coding-log.json --source-order i1,i2,i3 [--pretty]
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("log");p.add_argument("--source-order",required=True,help="comma-separated reviewed source IDs in analytic order");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  raw=json.loads(Path(a.log).read_text(encoding="utf-8"));entries=raw.get("entries",raw) if isinstance(raw,dict) else raw
  order=[x.strip() for x in a.source_order.split(",") if x.strip()]
  if not isinstance(entries,list) or not order or len(set(order))!=len(order):raise ValueError("log must be a list/entries list and source order must contain unique IDs")
  by={source:[] for source in order};outside=[]
  for n,row in enumerate(entries,1):
   if not isinstance(row,dict) or not str(row.get("source_id","")).strip() or not str(row.get("code","")).strip():raise ValueError(f"entry {n} needs source_id and code")
   (by[row["source_id"]] if row["source_id"] in by else outside).append(row["code"])
  seen=set();trace=[]
  for source in order:
   codes=sorted(set(by[source]));new=sorted(set(codes)-seen);seen.update(codes);trace.append({"source_id":source,"coded_entries":len(by[source]),"codes_observed":codes,"new_codes":new,"new_code_count":len(new),"cumulative_codes":len(seen)})
  report={"schema_version":"1.0.0","artifact_type":"qualitative-saturation-trace","tool_version":VERSION,"log":str(Path(a.log).resolve()),"source_order":order,"trace":trace,"entries_outside_order":len(outside),"warnings":["Descriptive trace only: zero new codes does not establish saturation. Assess information power, sampling, negative cases, code granularity, and reflexivity with the research team."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
