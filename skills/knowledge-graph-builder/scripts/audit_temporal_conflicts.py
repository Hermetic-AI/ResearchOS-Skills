#!/usr/bin/env python3
"""Audit temporal fields and conflicting relation declarations in a graph JSON.

Checks optional node ``year`` and edge ``valid_from``/``valid_to`` fields, and
flags lineage relations whose source is earlier than the target's stated year.
It also reports pairs containing ``contradicts`` plus another semantic relation.
No relation is removed or judged false.

Usage: python3 audit_temporal_conflicts.py graph.json [--pretty]
"""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
VERSION="0.1.0"; YEAR=re.compile(r"^\d{4}$"); LINEAGE={"improves-on","extends","outperforms"}
def year(value):
    text=str(value or "")
    return int(text) if YEAR.fullmatch(text) and 1000 <= int(text) <= 2999 else None
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("graph");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  graph=json.loads(Path(a.graph).read_text(encoding="utf-8"));nodes=graph.get("nodes");edges=graph.get("edges")
  if not isinstance(nodes,list) or not isinstance(edges,list):raise ValueError("graph must contain nodes and edges lists")
  years={str(n.get("id")):year(n.get("year")) for n in nodes if isinstance(n,dict)}; findings=[]; pairs={}
  for i,e in enumerate(edges,1):
   if not isinstance(e,dict):findings.append({"edge":i,"severity":"error","issue":"edge is not an object"});continue
   source,target,relation=str(e.get("from")),str(e.get("to")),str(e.get("relation"));pairs.setdefault((source,target),set()).add(relation)
   start,end=year(e.get("valid_from")),year(e.get("valid_to"))
   if e.get("valid_from") is not None and start is None:findings.append({"edge":i,"severity":"warning","issue":"invalid valid_from year"})
   if e.get("valid_to") is not None and end is None:findings.append({"edge":i,"severity":"warning","issue":"invalid valid_to year"})
   if start and end and start>end:findings.append({"edge":i,"severity":"error","issue":"valid_from is after valid_to"})
   if relation in LINEAGE and years.get(source) and years.get(target) and years[source]<years[target]:findings.append({"edge":i,"severity":"warning","issue":"lineage source predates target; verify relation/year evidence","from_year":years[source],"to_year":years[target]})
  for (source,target),relations in sorted(pairs.items()):
   if "contradicts" in relations and len(relations)>1:findings.append({"from":source,"to":target,"severity":"warning","issue":"contradicts coexists with other relation(s); retain evidence for both","relations":sorted(relations)})
  report={"schema_version":"1.0.0","artifact_type":"graph-temporal-conflict-audit","tool_version":VERSION,"graph":str(Path(a.graph).resolve()),"findings":findings,"warnings":["Audit only: temporal anomalies and contradictory relations can be legitimate; inspect evidence anchors before changing the graph.","Missing years and relation validity fields are not inferred."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
