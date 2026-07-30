#!/usr/bin/env python3
"""Run a read-only open-source release preflight; never grants release approval.

Checks required community files, CI configuration, the phase-audit wording,
and Git cleanliness. It does not inspect all dependency licenses, generated
artifacts, secrets, external terms, or provenance; human final review remains
mandatory.

Usage: python3 tools/release_preflight.py [repo_dir] [--pretty]
"""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
VERSION="0.1.0"
REQUIRED=["LICENSE","README.md","CONTRIBUTING.md","CODE_OF_CONDUCT.md","SECURITY.md","docs/OPEN_SOURCE_AUDIT.md"]
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("repo",nargs="?",default=".");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  root=Path(a.repo).resolve();
  if not root.is_dir():raise ValueError("repo must be a directory")
  findings=[]
  for name in REQUIRED:
   if not (root/name).is_file():findings.append({"severity":"error","item":name,"issue":"required release file is missing"})
  audit=root/"docs/OPEN_SOURCE_AUDIT.md"
  if audit.is_file() and "not release approval" not in audit.read_text(encoding="utf-8",errors="replace").lower():findings.append({"severity":"warning","item":"docs/OPEN_SOURCE_AUDIT.md","issue":"phase-audit/non-approval wording not found"})
  if not (root/".github/workflows").is_dir():findings.append({"severity":"warning","item":".github/workflows","issue":"no GitHub Actions workflow directory found"})
  git={"available":False}
  try:
   run=subprocess.run(["git","-C",str(root),"status","--porcelain"],capture_output=True,text=True,timeout=5)
   if run.returncode==0:
    changes=[line for line in run.stdout.splitlines() if line];git={"available":True,"clean":not changes,"changed_paths":changes}
    if changes:findings.append({"severity":"warning","item":"git worktree","issue":"worktree is not clean; review intended release contents"})
  except (OSError,subprocess.TimeoutExpired):pass
  report={"schema_version":"1.0.0","artifact_type":"open-source-release-preflight","tool_version":VERSION,"repository":str(root),"git":git,"findings":findings,"status":"needs-human-release-review","warnings":["This preflight is not release approval. Re-audit dependencies, provenance, secrets, generated artifacts, notices, distribution terms, and release tags before publishing."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
