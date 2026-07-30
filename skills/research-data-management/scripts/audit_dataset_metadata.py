#!/usr/bin/env python3
"""Audit a declared dataset metadata record for FAIR/release review fields.

Input JSON is a list or ``{"datasets": [...]}``. Required review fields are
``id``, ``title``, ``version``, ``license_or_terms``, ``access_route``, and
``data_dictionary``. This checks field presence only; it never opens data.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"; FIELDS=("id","title","version","license_or_terms","access_route","data_dictionary")
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("metadata");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  raw=json.loads(Path(a.metadata).read_text(encoding="utf-8"));rows=raw.get("datasets") if isinstance(raw,dict) else raw
  if not isinstance(rows,list):raise ValueError("metadata must be a list or object with datasets list")
  ids=set();findings=[]
  for n,row in enumerate(rows,1):
   if not isinstance(row,dict):findings.append({"dataset":n,"severity":"error","issue":"dataset record is not an object"});continue
   ident=str(row.get("id","")).strip()
   if not ident:findings.append({"dataset":n,"severity":"error","issue":"missing id"})
   elif ident in ids:findings.append({"dataset":n,"id":ident,"severity":"error","issue":"duplicate id"})
   ids.add(ident)
   for field in FIELDS:
    if not str(row.get(field," ")).strip():findings.append({"dataset":n,"id":ident,"severity":"warning","field":field,"issue":"metadata/release review field missing"})
  report={"schema_version":"1.0.0","artifact_type":"dataset-metadata-audit","tool_version":VERSION,"metadata":str(Path(a.metadata).resolve()),"datasets":len(rows),"findings":findings,"warnings":["Field-presence audit only: it does not verify metadata accuracy, licensing, consent, anonymization, repository policy, FAIR compliance, or release permission."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
