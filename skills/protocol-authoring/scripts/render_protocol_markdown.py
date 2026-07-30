#!/usr/bin/env python3
"""Render a structured research-protocol JSON charter to protected Markdown.

The renderer preserves empty sections as explicit placeholders. It does not
map reporting standards, assess completeness, register a study, or submit data.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"
SECTIONS=[("objectives","Objectives"),("hypotheses","Hypotheses"),("population_and_eligibility","Population and eligibility"),("outcomes_and_estimands","Outcomes and estimands"),("procedures","Procedures"),("sample_size_evidence","Sample-size evidence"),("analysis_artifacts","Analysis artifacts"),("monitoring_and_stopping","Monitoring and stopping"),("ethics_and_registration","Ethics and registration"),("data_governance","Data governance"),("amendments_and_deviations","Amendments and deviations")]
def show(value):
 if isinstance(value,list):return "\n".join(f"- {x}" if not isinstance(x,dict) else "- `"+json.dumps(x,ensure_ascii=False)+"`" for x in value) or "- _To be specified_"
 if isinstance(value,dict):return "- `"+json.dumps(value,ensure_ascii=False)+"`" if value else "- _To be specified_"
 return f"- {value}" if value else "- _To be specified_"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("protocol");p.add_argument("--out",required=True);p.add_argument("--force",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  src=Path(a.protocol).resolve(strict=True);out=Path(a.out).resolve()
  if src==out:raise ValueError("--out must differ from protocol input")
  if out.exists() and not a.force:raise ValueError("output exists; use --force only for a derived rendering")
  data=json.loads(src.read_text(encoding="utf-8"))
  if data.get("artifact_type")!="research-protocol":raise ValueError("input must be a research-protocol artifact")
  lines=[f"# {data.get('title','Untitled protocol')}","",f"**Design:** {data.get('design','To be specified')}",""]
  for key,label in SECTIONS:lines+= [f"## {label}",show(data.get(key)),""]
  lines += ["## Planning status","- This rendered document is a planning artifact, not ethical approval, registration, or a regulatory submission.",""]
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text("\n".join(lines),encoding="utf-8")
  print(json.dumps({"input":str(src),"output":str(out),"sections":len(SECTIONS),"warnings":["Rendering only: review every placeholder and governing requirement before use."]},ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
