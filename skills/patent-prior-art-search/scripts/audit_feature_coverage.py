#!/usr/bin/env python3
"""Audit a manual technical-feature/prior-art evidence matrix (not legal analysis).

Input JSON is a list or ``{"features": [...]}``. Each row needs ``id`` and
``feature`` and may contain ``evidence`` entries with document ID and locator.
The tool reports feature rows without evidence locators; it never assesses
novelty, claim construction, family status, or legal relevance.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("matrix");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  raw=json.loads(Path(a.matrix).read_text(encoding="utf-8"));rows=raw.get("features") if isinstance(raw,dict) else raw
  if not isinstance(rows,list):raise ValueError("matrix must be a list or object with features list")
  ids=set();findings=[]
  for n,row in enumerate(rows,1):
   if not isinstance(row,dict):findings.append({"row":n,"severity":"error","issue":"feature row is not an object"});continue
   ident=str(row.get("id","")).strip()
   if not ident:findings.append({"row":n,"severity":"error","issue":"missing feature id"})
   elif ident in ids:findings.append({"row":n,"id":ident,"severity":"error","issue":"duplicate feature id"})
   ids.add(ident)
   if not str(row.get("feature","")).strip():findings.append({"row":n,"id":ident,"severity":"error","issue":"missing feature text"})
   evidence=row.get("evidence",[])
   if not isinstance(evidence,list) or not evidence:findings.append({"row":n,"id":ident,"severity":"warning","issue":"no prior-art evidence recorded"});continue
   for entry in evidence:
    if not isinstance(entry,dict) or not str(entry.get("document_id","")).strip() or not str(entry.get("locator","")).strip():findings.append({"row":n,"id":ident,"severity":"warning","issue":"evidence needs document_id and locator"})
  report={"schema_version":"1.0.0","artifact_type":"prior-art-feature-coverage-audit","tool_version":VERSION,"matrix":str(Path(a.matrix).resolve()),"features":len(rows),"findings":findings,"warnings":["Traceability audit only: evidence presence is not a novelty, obviousness, infringement, freedom-to-operate, or patentability conclusion."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
