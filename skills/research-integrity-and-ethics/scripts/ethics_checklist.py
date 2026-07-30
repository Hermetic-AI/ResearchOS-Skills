#!/usr/bin/env python3
"""Create a research ethics and integrity readiness checklist; not an approval decision."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
VERSION='0.1.0'
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--study',required=True);p.add_argument('--human-data',action='store_true');p.add_argument('--animal-data',action='store_true');p.add_argument('--sensitive-data',action='store_true');p.add_argument('--ai-use',action='store_true');p.add_argument('--out',required=True);p.add_argument('--force',action='store_true');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  out=Path(a.out).resolve()
  if out.exists() and not a.force:raise ValueError('output exists; use --force only for a derived checklist')
  items=[{'area':'authorship','required':'Record contribution roles, approvals, conflicts, and corresponding-author responsibility.','status':'open'},{'area':'integrity','required':'Preserve provenance, negative results, corrections, and citation verification evidence.','status':'open'},{'area':'reporting','required':'Select the applicable reporting guideline and preregistration/disclosure requirements.','status':'open'}]
  if a.human_data:items.append({'area':'human-participants','required':'Document ethics approval/exemption, consent basis, protocol version, recruitment, risk/benefit, and adverse-event handling before collection.','status':'open'})
  if a.animal_data:items.append({'area':'animals','required':'Document animal-care approval, humane endpoints, welfare monitoring, and reporting requirements.','status':'open'})
  if a.sensitive_data or a.human_data:items.append({'area':'privacy','required':'Document data minimization, identifiers, access controls, retention, sharing basis, re-identification risk, and breach response.','status':'open'})
  if a.ai_use:items.append({'area':'ai-disclosure','required':'Document tools, material use, human verification, data-sharing restrictions, and venue-specific disclosure language.','status':'open'})
  payload={'schema_version':'1.0.0','artifact_type':'ethics-integrity-checklist','study':a.study,'created_at':datetime.now(timezone.utc).isoformat(),'tool_version':VERSION,'items':items,'warnings':['This checklist is not institutional ethics approval, legal advice, consent, a data-processing agreement, or a determination of regulatory compliance.']}
  out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
