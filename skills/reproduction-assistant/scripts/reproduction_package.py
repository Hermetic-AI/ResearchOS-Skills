#!/usr/bin/env python3
"""Create a reviewed reproduction-package manifest and optional protected ZIP archive."""
from __future__ import annotations
import argparse,hashlib,json,sys,zipfile
from pathlib import Path
VERSION='0.1.0'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('run_dir');p.add_argument('--level',choices=['environment-only','reduced-scale','full-claimed-config','full-verified-match'],required=True);p.add_argument('--out',required=True);p.add_argument('--archive',help='explicit ZIP archive path; optional and never implied');p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  root=Path(a.run_dir).resolve(strict=True);out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived manifest')
  if out.is_relative_to(root):raise ValueError('--out must be outside run_dir to avoid self-inclusion')
  excluded={'.git','__pycache__','.pytest_cache','.mypy_cache'}
  secret_names={'.env','id_rsa','id_ed25519','credentials.json','service-account.json'}
  skipped=[];candidates=[]
  for path in root.rglob('*'):
   if not path.is_file():continue
   rel=path.relative_to(root)
   if any(part in excluded for part in rel.parts):skipped.append({'path':str(rel),'reason':'cache_or_vcs'});continue
   if path.name.lower() in secret_names or path.suffix.lower() in {'.pem','.key','.pfx','.p12'}:skipped.append({'path':str(rel),'reason':'sensitive_filename'});continue
   candidates.append(path)
  files=[{'path':str(path.relative_to(root)),'bytes':path.stat().st_size,'sha256':digest(path)} for path in sorted(candidates, key=str)]
  archive=None
  if a.archive:
   archive_path=Path(a.archive).resolve()
   if archive_path.is_relative_to(root):raise ValueError('--archive must be outside run_dir to avoid self-inclusion')
   if archive_path.exists() and not a.force:raise ValueError('archive exists; use --force only for a reviewed derived archive')
   archive_path.parent.mkdir(parents=True,exist_ok=True)
   with zipfile.ZipFile(archive_path,'w',compression=zipfile.ZIP_DEFLATED) as zf:
    for path in candidates:zf.write(path,path.relative_to(root).as_posix())
   archive={'path':str(archive_path),'sha256':digest(archive_path),'files_archived':len(files)}
  payload={'schema_version':'1.0.0','artifact_type':'reproduction-package-manifest','run_dir':str(root),'reproduction_level':a.level,'files':files,'skipped_files':skipped,'archive':archive,'warnings':['Heuristic filename exclusion cannot prove absence of secrets, proprietary material, licensing restrictions, or controlled data. Review every file and obtain distribution permission before sharing.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
