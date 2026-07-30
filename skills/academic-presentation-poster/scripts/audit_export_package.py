#!/usr/bin/env python3
"""Audit declared final presentation export files against a storyboard (read-only)."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"; TYPES={"slides":{".pptx",".pdf"},"poster":{".pdf",".png",".tiff"}}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--storyboard",required=True);p.add_argument("--export",action="append",required=True);p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  story=json.loads(Path(a.storyboard).read_text(encoding="utf-8"));fmt=story.get("format");allowed=TYPES.get(fmt,set());findings=[];files=[]
  for raw in a.export:
   path=Path(raw).resolve()
   if not path.is_file():findings.append({"severity":"error","path":str(path),"issue":"declared export file is missing"});continue
   files.append({"path":str(path),"bytes":path.stat().st_size,"suffix":path.suffix.lower()})
   if allowed and path.suffix.lower() not in allowed:findings.append({"severity":"warning","path":str(path),"issue":f"unusual extension for storyboard format {fmt}"})
  if not story.get("accessibility"):findings.append({"severity":"warning","issue":"storyboard has no accessibility declaration to carry into export review"})
  report={"schema_version":"1.0.0","artifact_type":"presentation-export-audit","tool_version":VERSION,"storyboard":str(Path(a.storyboard).resolve()),"exports":files,"findings":findings,"warnings":["File inventory only: it does not render slides/posters, inspect visual contrast, read alt text, verify fonts, or certify accessibility."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
