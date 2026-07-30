#!/usr/bin/env python3
"""Compute two-coder nominal Cohen's kappa from a reviewed coding CSV.

CSV columns: item, coder, code. Each selected coder must have at most one code
per item; items missing either coder are reported and excluded. This calculates
agreement for the supplied unit/code scheme only; it does not validate coding,
interpretation, saturation, or qualitative validity.

Usage: python3 coding_agreement.py coding.csv --coder-a A --coder-b B [--pretty]
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
VERSION="0.1.0"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("coding");p.add_argument("--coder-a",required=True);p.add_argument("--coder-b",required=True);p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  if a.coder_a==a.coder_b:raise ValueError("--coder-a and --coder-b must differ")
  rows=list(csv.DictReader(Path(a.coding).open(encoding="utf-8",newline="")))
  if not rows or not {"item","coder","code"}.issubset(rows[0]):raise ValueError("CSV needs item,coder,code columns")
  judgments={};findings=[]
  for n,row in enumerate(rows,2):
   if row["coder"] not in {a.coder_a,a.coder_b}:continue
   key=(row["item"],row["coder"])
   if not row["item"].strip() or not row["code"].strip():findings.append({"row":n,"severity":"error","issue":"empty item or code"});continue
   if key in judgments:findings.append({"row":n,"severity":"error","issue":"multiple codes for same item/coder","item":row["item"],"coder":row["coder"]});continue
   judgments[key]=row["code"]
  items=sorted({item for item,_ in judgments});paired=[item for item in items if (item,a.coder_a) in judgments and (item,a.coder_b) in judgments];unpaired=[item for item in items if item not in paired]
  if not paired:raise ValueError("no paired items for the selected coders")
  cats=sorted({judgments[(item,coder)] for item in paired for coder in (a.coder_a,a.coder_b)});n=len(paired);observed=sum(judgments[(item,a.coder_a)]==judgments[(item,a.coder_b)] for item in paired)/n
  expected=sum((sum(judgments[(item,a.coder_a)]==cat for item in paired)/n)*(sum(judgments[(item,a.coder_b)]==cat for item in paired)/n) for cat in cats);kappa=(observed-expected)/(1-expected) if expected<1 else None
  report={"schema_version":"1.0.0","artifact_type":"coding-agreement","tool_version":VERSION,"coding":str(Path(a.coding).resolve()),"coders":[a.coder_a,a.coder_b],"paired_items":n,"unpaired_items":unpaired,"categories":cats,"observed_agreement":observed,"expected_agreement":expected,"cohens_kappa":kappa,"findings":findings,"warnings":["Cohen's kappa is for exactly one nominal code per item per selected coder; multi-label coding needs a prespecified alternative.","Agreement is not evidence of validity, saturation, reflexivity, or appropriate code definitions."]}
  print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except (OSError,ValueError) as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
