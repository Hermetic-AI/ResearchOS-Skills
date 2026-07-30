#!/usr/bin/env python3
"""Calculate an E-value for a supplied risk-ratio scale association.

Use only for a positive risk ratio or a ratio that can be reciprocated. The
optional confidence-limit is the bound closest to the null (1). E-values do
not establish causality, address bias other than unmeasured confounding, or
replace a causal design/diagnostic review.

Usage: python3 e_value.py --risk-ratio 2.1 [--confidence-limit 1.3]
"""
from __future__ import annotations
import argparse,json,math,sys
VERSION="0.1.0"
def evalue(ratio):
 if ratio<=0:raise ValueError("ratio must be positive")
 rr=ratio if ratio>=1 else 1/ratio
 return rr+math.sqrt(rr*(rr-1)),rr
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--risk-ratio",type=float,required=True);p.add_argument("--confidence-limit",type=float,help="confidence bound closest to 1, on risk-ratio scale");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
 try:
  value,oriented=evalue(a.risk_ratio);result={"schema_version":"1.0.0","artifact_type":"e-value-sensitivity","tool_version":VERSION,"input_risk_ratio":a.risk_ratio,"oriented_risk_ratio":oriented,"e_value":value,"warnings":["Applies to risk-ratio scale inputs only; odds/hazard ratios require justified approximation or conversion outside this tool.","An E-value quantifies one unmeasured-confounding strength benchmark; it does not prove identification, exchangeability, or causal validity."]}
  if a.confidence_limit is not None:
   bound,bound_oriented=evalue(a.confidence_limit);result["confidence_limit"]={"input":a.confidence_limit,"oriented":bound_oriented,"e_value":bound}
  print(json.dumps(result,ensure_ascii=False,indent=2 if a.pretty else None));return 0
 except ValueError as e:print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
