#!/usr/bin/env python3
"""Compute deterministic graph components, degree centrality, and optional graph diffs."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION='0.1.0'
def load(path):
 data=json.loads(Path(path).read_text(encoding='utf-8'))
 if not isinstance(data.get('nodes'),list) or not isinstance(data.get('edges'),list):raise ValueError('graph must contain nodes and edges lists')
 return data
def edge_key(edge):return (str(edge.get('from')),str(edge.get('to')),str(edge.get('relation')))
def analyze(data):
 ids=sorted(str(n['id']) for n in data['nodes']);neighbors={x:set() for x in ids};incoming={x:0 for x in ids};outgoing={x:0 for x in ids}
 for edge in data['edges']:
  a,b=str(edge.get('from')),str(edge.get('to'))
  if a in neighbors and b in neighbors:neighbors[a].add(b);neighbors[b].add(a);outgoing[a]+=1;incoming[b]+=1
 seen=set();components=[]
 for seed in ids:
  if seed in seen:continue
  stack=[seed];seen.add(seed);part=[]
  while stack:
   node=stack.pop();part.append(node)
   for nxt in neighbors[node]:
    if nxt not in seen:seen.add(nxt);stack.append(nxt)
  components.append(sorted(part))
 centrality=sorted([{'id':node,'degree':len(neighbors[node]),'in_degree':incoming[node],'out_degree':outgoing[node]} for node in ids],key=lambda x:(-x['degree'],x['id']))
 return {'node_count':len(ids),'edge_count':len(data['edges']),'components':[{'id':f'component-{i+1}','nodes':part,'size':len(part)} for i,part in enumerate(sorted(components,key=lambda x:(-len(x),x)))],'degree_centrality':centrality}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('graph');p.add_argument('--compare',help='optional previous graph JSON');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  current=load(a.graph);result={'graph':str(a.graph),'analysis':analyze(current)}
  if a.compare:
   old=load(a.compare);old_nodes={str(n['id']) for n in old['nodes']};new_nodes={str(n['id']) for n in current['nodes']};old_edges={edge_key(e) for e in old['edges']};new_edges={edge_key(e) for e in current['edges']}
   result['diff']={'added_nodes':sorted(new_nodes-old_nodes),'removed_nodes':sorted(old_nodes-new_nodes),'added_edges':[list(x) for x in sorted(new_edges-old_edges)],'removed_edges':[list(x) for x in sorted(old_edges-new_edges)]}
  print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError,KeyError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
