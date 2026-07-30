#!/usr/bin/env python3
"""Export a ResearchOS graph JSON to GraphML, GEXF, or JSON-LD without changing it."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from xml.sax.saxutils import escape
from urllib.parse import quote
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('graph');p.add_argument('--format',choices=['graphml','gexf','jsonld','turtle'],required=True);p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  graph=Path(a.graph).resolve(strict=True);out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived export')
  data=json.loads(graph.read_text(encoding='utf-8'));nodes=data.get('nodes',[]);edges=data.get('edges',[])
  if not isinstance(nodes,list) or not isinstance(edges,list):raise ValueError('graph must contain nodes and edges lists')
  if a.format=='jsonld':
   payload={'@context':{'id':'@id','type':'@type','label':'https://schema.org/name','relation':'https://schema.org/relation'},'@graph':[{'@id':n['id'],'@type':n.get('type','Concept'),'label':n.get('label',n['id'])} for n in nodes]+[{'@id':f"edge:{i}",'@type':'Relation','source':e.get('from'),'target':e.get('to'),'relation':e.get('relation'),'evidence':e.get('evidence')} for i,e in enumerate(edges)]}
   text=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
  elif a.format=='turtle':
   uri=lambda value:'<urn:researchos:node:'+quote(str(value),safe='')+'>'
   literal=lambda value:json.dumps(str(value),ensure_ascii=False)
   text='@prefix ros: <https://researchos.example/schema#> .\n\n'+''.join(f'{uri(n["id"])} a ros:{quote(str(n.get("type","Concept")),safe="")} ; ros:label {literal(n.get("label",n["id"]))} .\n' for n in nodes)+''.join(f'{uri(e.get("from"))} ros:{quote(str(e.get("relation","relatedTo")),safe="")} {uri(e.get("to"))} .\n' for e in edges)
  elif a.format=='graphml':
   text='<?xml version="1.0" encoding="UTF-8"?>\n<graphml xmlns="http://graphml.graphdrawing.org/xmlns"><graph id="ResearchOS" edgedefault="directed">\n'+''.join(f'<node id="{escape(str(n["id"]))}"><data key="label">{escape(str(n.get("label",n["id"])))}</data><data key="type">{escape(str(n.get("type","")))}</data></node>\n' for n in nodes)+''.join(f'<edge id="e{i}" source="{escape(str(e.get("from","")))}" target="{escape(str(e.get("to","")))}"><data key="relation">{escape(str(e.get("relation","")))}</data></edge>\n' for i,e in enumerate(edges))+'</graph></graphml>\n'
  else:
   text='<?xml version="1.0" encoding="UTF-8"?>\n<gexf version="1.2"><graph mode="static" defaultedgetype="directed"><nodes>\n'+''.join(f'<node id="{escape(str(n["id"]))}" label="{escape(str(n.get("label",n["id"]))) }"/>\n' for n in nodes)+'</nodes><edges>\n'+''.join(f'<edge id="{i}" source="{escape(str(e.get("from","")))}" target="{escape(str(e.get("to","")))}" label="{escape(str(e.get("relation",""))) }"/>\n' for i,e in enumerate(edges))+'</edges></graph></gexf>\n'
  out.write_text(text,encoding='utf-8');print(f'wrote {out} ({len(nodes)} nodes, {len(edges)} edges)');return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
