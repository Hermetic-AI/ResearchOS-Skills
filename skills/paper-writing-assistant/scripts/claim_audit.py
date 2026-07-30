#!/usr/bin/env python3
"""Screen Markdown/LaTeX prose for strong claims lacking nearby numeric citations."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
VERSION='0.1.0'
PATTERN=re.compile(r'\b(prove[sd]?|demonstrate[sd]?|cause[sd]?|lead(?:s|ing)? to|result(?:s|ed)? in|establish(?:es|ed)?|significant(?:ly)?)\b|证明|导致|因果|显著',re.I)
CITE=re.compile(r'\[\d[\d,;\-\s]*\]|\\cite\w*\{[^}]+\}')
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('manuscript');p.add_argument('--paper-note',help='validated paper-note JSON used as an evidence ledger');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  path=Path(a.manuscript); findings=[]
  for line_no,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
   if PATTERN.search(line) and not CITE.search(line) and not line.lstrip().startswith(('#','%','```')):
    findings.append({'line':line_no,'text':line.strip()[:300],'issue':'strong-claim-without-nearby-citation','suggestion':'Verify evidence and add a citation, a qualified scope, or move the claim to results supported by a validated artifact.'})
  ledger=[]
  if a.paper_note:
   note=json.loads(Path(a.paper_note).read_text(encoding='utf-8'))
   if note.get('artifact_type')!='paper-note': raise ValueError('--paper-note must be a paper-note artifact')
   for claim in note.get('claims',[]):
    anchors=claim.get('evidence',[])
    ledger.append({'id':claim.get('id'),'support_level':claim.get('support_level'),'anchor_count':len(anchors),'anchors':[{'source':x.get('source'),'page':x.get('page'),'section':x.get('section'),'verification':x.get('verification')} for x in anchors]})
  print(json.dumps({'manuscript':str(path),'findings':findings,'evidence_ledger':ledger,'warnings':['Heuristic only: a citation may validly appear in a neighboring sentence, figure caption, or paragraph.','The ledger preserves paper-note evidence anchors but cannot prove semantic entailment between manuscript prose and a source.']},ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e: print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
