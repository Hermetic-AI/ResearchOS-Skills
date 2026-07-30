#!/usr/bin/env python3
"""Run equivalence/noninferiority tests or deterministic missing-data sensitivity grids."""
from __future__ import annotations
import argparse,json,math,statistics,sys
from datetime import datetime,timezone

VERSION="0.1.0"
def vals(s,n):
 try:r=[float(x) for x in s.split(',') if x.strip()]
 except ValueError as e:raise ValueError(f'{n} must be comma-separated numbers') from e
 if len(r)<2:raise ValueError(f'{n} needs at least two values')
 return r
def prov(kind):return {"created_by":"data-analysis-assistant/inference_extensions.py","created_at":datetime.now(timezone.utc).isoformat(),"tool_version":VERSION,"command":" ".join(sys.argv),"seed":None,"sources":[{"kind":"user","locator":kind}],"warnings":[]}
def welch(a,b):
 va,vb=statistics.variance(a),statistics.variance(b); se=math.sqrt(va/len(a)+vb/len(b)); df=(va/len(a)+vb/len(b))**2/((va/len(a))**2/(len(a)-1)+(vb/len(b))**2/(len(b)-1));return statistics.fmean(a)-statistics.fmean(b),se,df
def equivalence(a):
 from statsmodels.stats.weightstats import ttost_ind
 x,y=vals(a.a,'--a'),vals(a.b,'--b')
 if not a.low<a.upp:raise ValueError('--low must be less than --upp')
 p,lower,upper=ttost_ind(x,y,a.low,a.upp,usevar='unequal'); diff,se,df=welch(x,y)
 return {"schema_version":"1.0.0","artifact_type":"stat-results","provenance":prov('equivalence'),"alpha":a.alpha,"results":[{"id":"equivalence-difference","test":"TOST equivalence (Welch)","statistic":diff/se,"p_value":float(p),"effect_size":diff,"confidence_interval":None,"adjusted_p_value":None,"equivalence_bounds":[a.low,a.upp],"lower_test":{"statistic":float(lower[0]),"p_value":float(lower[1]),"df":float(lower[2])},"upper_test":{"statistic":float(upper[0]),"p_value":float(upper[1]),"df":float(upper[2])}}],"warnings":["Equivalence is concluded only when both one-sided tests reject at alpha and the prespecified bounds are scientifically justified."]}
def noninferiority(a):
 from scipy.stats import t
 x,y=vals(a.a,'--a'),vals(a.b,'--b'); diff,se,df=welch(x,y)
 if a.margin<=0:raise ValueError('--margin must be positive; null boundary is difference <= -margin')
 statistic=(diff+a.margin)/se;p=float(t.sf(statistic,df))
 return {"schema_version":"1.0.0","artifact_type":"stat-results","provenance":prov('noninferiority'),"alpha":a.alpha,"results":[{"id":"noninferiority-difference","test":"Welch noninferiority t-test","statistic":statistic,"p_value":p,"effect_size":diff,"confidence_interval":None,"adjusted_p_value":None,"noninferiority_margin":a.margin,"df":df}],"warnings":["The margin is on the raw difference scale; justify it independently of observed data. A non-significant superiority test does not establish noninferiority."]}
def sensitivity(a):
 if not 0<=a.missing_fraction<=1 or a.steps<2:raise ValueError('missing fraction must be [0,1] and steps >= 2')
 ds=[a.delta_low+i*(a.delta_high-a.delta_low)/(a.steps-1) for i in range(a.steps)]
 rows=[{"delta":d,"adjusted_effect":a.observed_effect+a.missing_fraction*d,"standard_error":a.observed_se} for d in ds]
 return {"schema_version":"1.0.0","artifact_type":"sensitivity-analysis","provenance":prov('missing-data-delta'),"estimand":"effect shifted by missing_fraction × delta","observed_effect":a.observed_effect,"observed_standard_error":a.observed_se,"missing_fraction":a.missing_fraction,"scenarios":rows,"warnings":["This deterministic delta adjustment is a transparent sensitivity grid, not multiple imputation or proof of MAR/MNAR."]}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');s=p.add_subparsers(dest='mode',required=True)
 for name in ('equivalence','noninferiority'):
  q=s.add_parser(name);q.add_argument('--a',required=True);q.add_argument('--b',required=True);q.add_argument('--alpha',type=float,default=.05)
 e=s.choices['equivalence'];e.add_argument('--low',type=float,required=True);e.add_argument('--upp',type=float,required=True)
 n=s.choices['noninferiority'];n.add_argument('--margin',type=float,required=True)
 q=s.add_parser('missing-sensitivity');q.add_argument('--observed-effect',type=float,required=True);q.add_argument('--observed-se',type=float,required=True);q.add_argument('--missing-fraction',type=float,required=True);q.add_argument('--delta-low',type=float,required=True);q.add_argument('--delta-high',type=float,required=True);q.add_argument('--steps',type=int,default=11)
 a=p.parse_args(argv)
 try:r=equivalence(a) if a.mode=='equivalence' else noninferiority(a) if a.mode=='noninferiority' else sensitivity(a)
 except (RuntimeError,ValueError) as e:print(f'error: {e}',file=sys.stderr);return 1
 print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
