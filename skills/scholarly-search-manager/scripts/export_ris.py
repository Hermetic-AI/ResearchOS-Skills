#!/usr/bin/env python3
"""Export local scholarly JSON records to a protected RIS file (offline)."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"
def line(tag,value):return f"{tag}  - {value}\n" if value not in (None,"",[]) else ""
def authors(value):return value if isinstance(value,list) else [value] if value else []
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("records");p.add_argument("--out",required=True);p.add_argument("--force",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  src=Path(a.records).resolve(strict=True);out=Path(a.out).resolve()
  if src==out:raise ValueError("--out must differ from input")
  if out.exists() and not a.force:raise ValueError("output exists; use --force only for a derived export")
  raw=json.loads(src.read_text(encoding="utf-8"));items=raw.get("items",raw) if isinstance(raw,dict) else raw
  if not isinstance(items,list):raise ValueError("input must be a JSON list or object with items list")
  chunks=[];warnings=[]
  for n,row in enumerate(items,1):
   if not isinstance(row,dict):raise ValueError(f"item {n} is not an object")
   if not row.get("title"):warnings.append(f"item {n} has no title")
   chunks.append("TY  - JOUR\n"+"".join(line("AU",x) for x in authors(row.get("authors")))+line("TI",row.get("title"))+line("PY",row.get("year"))+line("JO",row.get("journal") or row.get("container_title"))+line("DO",row.get("doi"))+line("UR",row.get("url"))+line("AB",row.get("abstract"))+"ER  - \n\n")
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text("".join(chunks),encoding="utf-8",newline="\n")
  print(json.dumps({"schema_version":"1.0.0","artifact_type":"ris-export","tool_version":VERSION,"input":str(src),"output":str(out),"records":len(items),"warnings":warnings+["Offline format conversion only: fields were not identifier-verified or normalized against a citation style."]},ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
