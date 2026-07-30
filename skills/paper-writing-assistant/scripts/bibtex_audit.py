#!/usr/bin/env python3
"""Audit BibTeX/BibLaTeX field completeness and DOI syntax offline."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
VERSION='0.1.0'; DOI=re.compile(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$',re.I)
def entries(text):
 out=[];start=0
 while True:
  match=re.search(r'@(\w+)\s*\{\s*([^,\s]+)\s*,',text[start:],re.I)
  if not match:break
  kind,key=match.group(1).lower(),match.group(2);pos=start+match.end();depth=1;end=pos
  while end<len(text) and depth:
   if text[end]=='{':depth+=1
   elif text[end]=='}':depth-=1
   end+=1
  if depth:raise ValueError(f'unclosed BibTeX entry {key}')
  body=text[pos:end-1];fields={m.group(1).lower():m.group(2).strip() for m in re.finditer(r'(\w+)\s*=\s*[\{"]([^}\"]*)[\}"]',body,re.S)}
  out.append((kind,key,fields));start=end
 return out
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('bib');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  source=Path(a.bib).resolve(strict=True);parsed=entries(source.read_text(encoding='utf-8-sig'))
  if not parsed:raise ValueError('no BibTeX entries found')
  result=[]
  for kind,key,fields in parsed:
   required=['author','title','year']+(['journal'] if kind=='article' else ['booktitle'] if kind in {'inproceedings','incollection'} else [])
   missing=[x for x in required if not fields.get(x)]
   doi=fields.get('doi','').strip().removeprefix('https://doi.org/').removeprefix('doi:')
   result.append({'key':key,'type':kind,'missing_required_fields':missing,'year':fields.get('year'),'venue':fields.get('journal') or fields.get('booktitle'),'pages':fields.get('pages'),'doi':doi or None,'doi_syntax_valid':None if not doi else bool(DOI.fullmatch(doi)),'warnings':['article has no pages field'] if kind=='article' and not fields.get('pages') else []})
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a revised audit')
  x={'schema_version':'1.0.0','artifact_type':'bibtex-field-audit','tool_version':VERSION,'source':str(source),'entries':result,'warnings':['Offline audit only: field presence and DOI syntax do not prove author, year, venue, page, or DOI truth. Use literature-reader audit_bibliography.py --online for explicit external verification.']}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(x,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
