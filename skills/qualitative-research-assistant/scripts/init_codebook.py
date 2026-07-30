#!/usr/bin/env python3
"""Create a draft qualitative codebook and audit-trail scaffold; not coded findings."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--study',required=True);p.add_argument('--approach',choices=['thematic-analysis','grounded-theory','framework-analysis','content-analysis'],required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived codebook')
  payload={'schema_version':'1.0.0','artifact_type':'qualitative-codebook','study':a.study,'approach':a.approach,'version':'0.1.0-draft','created_at':datetime.now(timezone.utc).isoformat(),'codes':[],'audit_trail':{'source_units':[],'coder_decisions':[],'disagreement_resolution':[],'codebook_changes':[]},'quality_plan':{'reflexivity':'open','negative_cases':'open','saturation_rationale':'open','agreement_method':'open'},'warnings':['This is a draft scaffold, not a coded dataset, saturation finding, agreement result, or participant-consent record.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
