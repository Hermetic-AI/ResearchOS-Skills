#!/usr/bin/env python3
"""Generate deterministic entity identity keys and alias-merge proposals without editing a graph."""
from __future__ import annotations
import argparse,hashlib,json,re,sys,unicodedata
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def norm(value):
 value=unicodedata.normalize('NFKC',str(value)).casefold().strip()
 return re.sub(r'[^\w]+',' ',value).strip()
def similarity(left,right):
 a,b=set(norm(left).split()),set(norm(right).split())
 return len(a&b)/len(a|b) if a or b else 0.0
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--graph',required=True);p.add_argument('--out',required=True);p.add_argument('--similarity-threshold',type=float,default=.85,help='same-type token Jaccard threshold for review-only alias candidates');p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.graph).resolve(strict=True);raw=json.loads(source.read_text(encoding='utf-8-sig'));nodes=raw.get('nodes')
  if not isinstance(nodes,list):raise ValueError('graph must contain nodes list')
  if not 0<a.similarity_threshold<=1:raise ValueError('--similarity-threshold must be in (0,1]')
  output=[];groups={};typed=[]
  for i,node in enumerate(nodes,1):
   if not isinstance(node,dict):raise ValueError(f'node {i} must be an object')
   nid=str(node.get('id','')).strip();label=str(node.get('label',nid)).strip();kind=str(node.get('type','other')).strip()
   if not nid or not label:raise ValueError(f'node {i} needs id and label')
   identifiers=node.get('identifiers',{}) if isinstance(node.get('identifiers',{}),dict) else {}
   doi=str(identifiers.get('doi',node.get('doi',''))).strip().lower().removeprefix('https://doi.org/').removeprefix('doi:')
   citekey=str(identifiers.get('citekey',node.get('citekey',''))).strip().casefold()
   basis=('doi:'+doi) if doi else ('citekey:'+citekey if citekey else 'label:'+norm(label))
   stable='entity:'+hashlib.sha256((kind+'|'+basis).encode('utf-8')).hexdigest()[:16]
   output.append({'node_id':nid,'node_type':kind,'label':label,'stable_entity_id':stable,'identity_basis':basis})
   typed.append((nid,kind,label))
   groups.setdefault((kind,norm(label)),[]).append(nid)
  proposals=[{'node_type':kind,'normalized_label':label,'node_ids':ids,'reason':'same type and normalized label; requires human merge approval'} for (kind,label),ids in groups.items() if len(ids)>1]
  scored=[]
  for i,(left_id,kind,left_label) in enumerate(typed):
   for right_id,right_kind,right_label in typed[i+1:]:
    score=similarity(left_label,right_label)
    if kind==right_kind and score>=a.similarity_threshold and norm(left_label)!=norm(right_label):scored.append({'node_type':kind,'node_ids':[left_id,right_id],'labels':[left_label,right_label],'score':round(score,6),'method':'token-jaccard on normalized labels','reason':'review-only similarity candidate; requires human merge approval'})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised audit')
  x={'schema_version':'1.0.0','artifact_type':'graph-entity-identity-audit','created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'source_graph':str(source),'entities':output,'alias_merge_proposals':proposals,'similarity_merge_candidates':scored,'similarity_threshold':a.similarity_threshold,'warnings':['Stable IDs are derived from declared identifiers or normalized labels. Matching labels and similarity scores are merge proposals only; no node is changed, merged, or treated as semantically identical.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
