#!/usr/bin/env python3
"""Record repository, environment, command, and dataset checksums for a reproduction run."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def sha256_text(value):return hashlib.sha256(value.encode('utf-8')).hexdigest()
def git(repo,*args):
 r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf-8',errors='replace')
 return r.stdout.strip() if r.returncode==0 else None
def nvidia():
 try:
  r=subprocess.run(['nvidia-smi','--query-gpu=name,driver_version,cuda_version','--format=csv,noheader'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=10)
  return {'available':r.returncode==0,'gpus':[line.strip() for line in r.stdout.splitlines() if line.strip()]} if r.returncode==0 else {'available':False}
 except (OSError,subprocess.TimeoutExpired):return {'available':False}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('repo');p.add_argument('--command',required=True);p.add_argument('--data',action='append',default=[]);p.add_argument('--config',action='append',default=[]);p.add_argument('--seed',type=int);p.add_argument('--env',action='append',default=[]);p.add_argument('--include-env-values',action='store_true');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  repo=Path(a.repo).resolve(strict=True);out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived snapshot')
  files=[]
  for raw in a.data:
   path=Path(raw).resolve(strict=True)
   if not path.is_file():raise ValueError(f'--data must be a file: {path}')
   files.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha256(path)})
  configs=[]
  for raw in a.config:
   path=Path(raw).resolve(strict=True)
   if not path.is_file():raise ValueError(f'--config must be a file: {path}')
   configs.append({'path':str(path),'sha256':sha256(path)})
  selected_env={}
  for name in a.env:
   if not name or '=' in name:raise ValueError('--env expects a variable name')
   value=os.environ.get(name)
   selected_env[name]=None if value is None else (value if a.include_env_values else {'sha256':sha256_text(value),'present':True})
  payload={'schema_version':'1.0.0','artifact_type':'reproduction-provenance','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'repository':str(repo),'repository_commit':git(repo,'rev-parse','HEAD'),'repository_dirty':bool(git(repo,'status','--porcelain')),'git_diff':git(repo,'diff','--stat'),'command':a.command,'seed':a.seed,'environment':{'python':sys.version.split()[0],'platform':platform.platform(),'machine':platform.machine(),'selected_variables':selected_env,'gpu':nvidia()},'datasets':files,'config_files':configs,'warnings':['Snapshot records local state only and selected environment values are hashed unless --include-env-values is explicit. It does not verify dataset licenses, remote release/tag provenance, container image digest, or that a command will reproduce a result.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
