#!/usr/bin/env python3
"""Collect read-only, structural quality evidence from a source repository.

Inventories common licensing, citation, dependency, CI, test, and documentation
files plus Git HEAD/status where available. It does not execute tests, install
dependencies, build artifacts, or declare release readiness.

Usage: python3 collect_repository_evidence.py repo_dir [--pretty]
"""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
VERSION="0.1.0"
NAMES={"license":["LICENSE","LICENSE.txt","COPYING"],"citation":["CITATION.cff","CITATION.bib"],"dependencies":["pyproject.toml","requirements.txt","environment.yml","package-lock.json","Cargo.lock","Project.toml"],"documentation":["README.md","CONTRIBUTING.md","CHANGELOG.md","CODE_OF_CONDUCT.md","SECURITY.md"],"tests":["pytest.ini","tox.ini","noxfile.py","tests"],"ci":[".github/workflows",".gitlab-ci.yml","azure-pipelines.yml"]}
def present(root,names):return [name for name in names if (root/name).exists()]
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("repo");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  root=Path(a.repo).resolve()
  if not root.is_dir():raise ValueError("repo must be a directory")
  git={"available":False}
  try:
   head=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],capture_output=True,text=True,timeout=5)
   status=subprocess.run(["git","-C",str(root),"status","--porcelain"],capture_output=True,text=True,timeout=5)
   if head.returncode==0:git={"available":True,"head":head.stdout.strip(),"dirty":bool(status.stdout.strip())}
  except (OSError,subprocess.TimeoutExpired):pass
  evidence={category:[str(path) for path in present(root,names)] for category,names in NAMES.items()}
  report={"schema_version":"1.0.0","artifact_type":"repository-quality-evidence","tool_version":VERSION,"repository":str(root),"evidence":evidence,"git":git,"warnings":["Structural inventory only: file presence does not prove license validity, test execution, CI success, scientific validation, security, or release readiness."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
