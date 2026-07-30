#!/usr/bin/env python3
"""Audit a Markdown or LaTeX manuscript outline without modifying source files."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
VERSION='0.1.0'
CANONICAL=['abstract','introduction','methods','results','discussion','conclusion','references']
ALIASES={'abstract':'abstract|摘要','introduction':'introduction|引言|绪论','methods':'methods?|materials and methods|方法','results':'results?|结果','discussion':'discussion|讨论','conclusion':'conclusions?|结论','references':'references|bibliography|参考文献'}
def headings(text, suffix):
 if suffix=='.tex': return [(m.group(1).lower(),m.group(2).strip()) for m in re.finditer(r'\\(?:section|chapter)\*?\{([^}]*)\}',text) for _ in [0] for m in [m]]
 return [(m.group(1).lower(),m.group(2).strip()) for m in re.finditer(r'^(#{1,2})\s+(.+?)\s*#*$',text,re.M)]
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('manuscript');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  path=Path(a.manuscript); text=path.read_text(encoding='utf-8'); raw=headings(text,path.suffix.lower())
  if not raw: raise ValueError('no Markdown #/## or LaTeX section/chapter headings found')
  found=[]
  for _, title in raw:
   key=next((name for name, pattern in ALIASES.items() if re.fullmatch(pattern,title,re.I)),None)
   found.append({'title':title,'canonical':key})
  order=[item['canonical'] for item in found if item['canonical']]; positions={name:order.index(name) for name in set(order)}
  missing=[name for name in CANONICAL if name not in positions and name!='conclusion']
  duplicate=sorted({name for name in order if order.count(name)>1})
  inversions=[{'before':CANONICAL[i],'after':CANONICAL[i+1]} for i in range(len(CANONICAL)-1) if CANONICAL[i] in positions and CANONICAL[i+1] in positions and positions[CANONICAL[i]]>positions[CANONICAL[i+1]]]
  report={'manuscript':str(path),'format':path.suffix.lower(),'headings':found,'canonical_order':order,'missing_core_sections':missing,'duplicate_core_sections':duplicate,'order_issues':inversions,'warnings':['This is an outline screen, not a disciplinary or journal-specific completeness review.','A missing heading may be intentional for a short communication, review, thesis, or journal template.']}
  print(json.dumps(report,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e: print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
