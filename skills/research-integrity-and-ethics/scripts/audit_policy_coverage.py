#!/usr/bin/env python3
"""Audit a disclosure record against a user-supplied policy field map.

Policy JSON requires ``policy_name``, ``source``, and ``required_fields`` (a
list of dotted disclosure-record paths). It checks that paths exist and have
non-empty values. It never fetches, interprets, or approves a policy.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
VERSION="0.1.0"

def value_at(data,path):
    current=data
    for key in path.split("."):
        if not isinstance(current,dict) or key not in current:return None
        current=current[key]
    return current

def filled(value):
    return bool(value.strip()) if isinstance(value,str) else bool(value)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("disclosures");p.add_argument("policy");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
    try:
        record=json.loads(Path(a.disclosures).read_text(encoding="utf-8"));policy=json.loads(Path(a.policy).read_text(encoding="utf-8"));fields=policy.get("required_fields")
        if not isinstance(record,dict) or record.get("artifact_type")!="research-disclosure-record":raise ValueError("disclosures must be a research-disclosure-record object")
        if not isinstance(fields,list) or not all(isinstance(x,str) and x for x in fields):raise ValueError("policy required_fields must be a list of non-empty dotted paths")
        findings=[]
        if not str(policy.get("policy_name","")).strip():findings.append({"severity":"warning","issue":"policy_name missing"})
        if not str(policy.get("source","")).strip():findings.append({"severity":"warning","issue":"policy source missing"})
        for path in fields:
            if not filled(value_at(record,path)):findings.append({"severity":"warning","field":path,"issue":"required disclosure field is empty or absent"})
        report={"schema_version":"1.0.0","artifact_type":"policy-coverage-audit","tool_version":VERSION,"disclosures":str(Path(a.disclosures).resolve()),"policy":{"name":policy.get("policy_name"),"source":policy.get("source")},"required_fields":fields,"findings":findings,"warnings":["Coverage audit only: it does not validate policy currency, interpret policy text, or grant ethics/institutional/journal approval."]}
        print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
    except (OSError,ValueError,json.JSONDecodeError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
