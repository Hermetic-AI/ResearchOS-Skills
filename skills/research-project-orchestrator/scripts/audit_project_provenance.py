#!/usr/bin/env python3
"""Read-only provenance audit for a ResearchOS project manifest.

Verifies registered artifact paths and SHA-256 declarations where files remain
available. It reports absent provenance fields and never edits the manifest or
opens raw data beyond registered artifact files.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
VERSION="0.1.0"
def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return "sha256:"+h.hexdigest()
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("project");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  root=Path(a.project).resolve(strict=True);path=root/"project-manifest.json";m=json.loads(path.read_text(encoding="utf-8"))
  if m.get("artifact_type")!="research-project-manifest":raise ValueError("not a research-project manifest")
  findings=[]
  for n,item in enumerate(m.get("artifacts",[]),1):
   if not isinstance(item,dict):findings.append({"artifact":n,"severity":"error","issue":"artifact record is not an object"});continue
   artifact=Path(str(item.get("path", "")))
   if not artifact.is_file():findings.append({"artifact":n,"severity":"warning","path":str(artifact),"issue":"registered artifact is unavailable"});continue
   expected=item.get("checksum")
   if not expected:findings.append({"artifact":n,"path":str(artifact),"severity":"warning","issue":"missing checksum"})
   elif digest(artifact)!=expected:findings.append({"artifact":n,"path":str(artifact),"severity":"warning","issue":"artifact checksum differs from registration"})
  for field in ("last_update_provenance","updated_at","next_route","status"):
   if not m.get(field):findings.append({"severity":"warning","field":field,"issue":"manifest provenance/state field is missing"})
  report={"schema_version":"1.0.0","artifact_type":"project-provenance-audit","tool_version":VERSION,"project":str(root),"artifacts":len(m.get("artifacts",[])),"findings":findings,"warnings":["Audit only: checksum matching does not establish scientific validity, data permission, input provenance completeness, or decision quality."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
