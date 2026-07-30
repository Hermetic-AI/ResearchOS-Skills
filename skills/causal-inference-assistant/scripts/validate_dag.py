#!/usr/bin/env python3
"""Validate a declared causal DAG inventory; it does not identify an adjustment set."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"; ROLES={"treatment","outcome","confounder","mediator","collider","instrument","prognostic","unmeasured","other"}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dag',required=True,help='JSON {nodes:[{id,role}],edges:[{source,target}]}');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.dag).resolve(strict=True);raw=json.loads(source.read_text(encoding='utf-8-sig'));nodes=raw.get('nodes');edges=raw.get('edges')
  if not isinstance(nodes,list) or not isinstance(edges,list):raise ValueError('DAG requires nodes and edges lists')
  by_id={str(n.get('id','')):n for n in nodes if isinstance(n,dict)}
  if len(by_id)!=len(nodes) or not by_id or '' in by_id:raise ValueError('nodes need unique non-empty ids')
  bad={nid:n.get('role') for nid,n in by_id.items() if n.get('role') not in ROLES}
  if bad:raise ValueError(f'unsupported node roles: {bad}')
  pairs=[]
  for e in edges:
   if not isinstance(e,dict) or e.get('source') not in by_id or e.get('target') not in by_id:raise ValueError('every edge needs known source and target')
   if e['source']==e['target']:raise ValueError('self edges are not allowed')
   pairs.append((e['source'],e['target']))
  if len(set(pairs))!=len(pairs):raise ValueError('duplicate edges are not allowed')
  adjacency={nid:[] for nid in by_id}
  for s,t in pairs:adjacency[s].append(t)
  visiting=set();visited=set();cycles=[]
  def walk(node, trail):
   if node in visiting: cycles.append(trail[trail.index(node):]+[node]);return
   if node in visited:return
   visiting.add(node)
   for nxt in adjacency[node]:walk(nxt,trail+[nxt])
   visiting.remove(node);visited.add(node)
  for node in by_id:walk(node,[node])
  treatment=[nid for nid,n in by_id.items() if n['role']=='treatment'];outcome=[nid for nid,n in by_id.items() if n['role']=='outcome']
  if len(treatment)!=1 or len(outcome)!=1:raise ValueError('DAG needs exactly one treatment and one outcome node')
  parents={nid:[] for nid in by_id}
  for s,t in pairs:parents[t].append(s)
  tx,oy=treatment[0],outcome[0]; flags=[]
  for nid,n in by_id.items():
   if n['role']=='confounder' and not (nid in parents[tx] and nid in parents[oy]):flags.append({'node':nid,'issue':'declared confounder is not a direct parent of both treatment and outcome; confirm its role/path explicitly'})
   if n['role'] in {'mediator','collider'} and nid in parents[tx]:flags.append({'node':nid,'issue':'post-treatment or collider role has a treatment parent; do not adjust without a design-specific rationale'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised DAG audit')
  result={'schema_version':'1.0.0','artifact_type':'causal-dag-audit','tool_version':VERSION,'source_dag':str(source),'nodes':len(nodes),'edges':len(edges),'treatment':tx,'outcome':oy,'cycles':cycles,'role_flags':flags,'warnings':['Acyclicity and declared-role checks do not establish causal identification, sufficient adjustment, temporal validity, or any causal claim.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
