#!/usr/bin/env python3
"""Diagnose residuals, collinearity, influence, and GLM dispersion."""

from __future__ import annotations
import argparse, json, math, os, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

def stack():
    try:
        import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
        from statsmodels.stats.diagnostic import het_breuschpagan
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        from scipy import stats
    except ImportError as exc: raise RuntimeError('install model dependencies with: python -m pip install -e ".[models,analysis]"') from exc
    sys.path.insert(0, str(Path(__file__).resolve().parent)); from model_analysis import validate_formula
    return np, pd, sm, smf, het_breuschpagan, variance_inflation_factor, stats, validate_formula

def prov(path, warnings):
    return {"created_by":"data-analysis-assistant/model_diagnostics.py","created_at":datetime.now(timezone.utc).isoformat(),"tool_version":VERSION,"command":" ".join(sys.argv),"seed":None,"sources":[{"kind":"file","locator":str(path.resolve())}],"warnings":warnings}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}")
    p.add_argument("data",type=Path); p.add_argument("--formula",required=True); p.add_argument("--family",choices=["ols","poisson","binomial","negative-binomial"],default="ols"); p.add_argument("--top",type=int,default=10); p.add_argument("--out",type=Path); p.add_argument("--force",action="store_true")
    a=p.parse_args(argv)
    if a.out and a.out.resolve()==a.data.resolve(): p.error("--out must not replace input data")
    if a.out and a.out.exists() and not a.force: p.error(f"output exists: {a.out}; use --force to replace it")
    try:
        np,pd,sm,smf,bp,vif,stats,validate_formula=stack(); data=pd.read_csv(a.data); validate_formula(a.formula,list(data.columns))
        if a.family=="ols": result=smf.ols(a.formula,data=data,missing="drop",eval_env=-1).fit()
        else:
            family={"poisson":sm.families.Poisson,"binomial":sm.families.Binomial,"negative-binomial":sm.families.NegativeBinomial}[a.family]()
            result=smf.glm(a.formula,data=data,family=family,missing="drop",eval_env=-1).fit()
        exog=result.model.exog; names=result.model.exog_names
        vifs=[]
        for i,name in enumerate(names):
            if name.lower() not in {"intercept","const"}:
                value=float(vif(exog,i)); vifs.append({"term":name,"vif":value})
        residuals=np.asarray(result.resid if a.family=="ols" else result.resid_response); fitted=np.asarray(result.fittedvalues)
        influence=result.get_influence(); cooks=np.asarray(influence.cooks_distance[0]); leverage=np.asarray(getattr(influence,"hat_matrix_diag",np.full(len(cooks),np.nan)))
        flagged=sorted([{"row":int(i),"cooks_distance":float(cooks[i]),"leverage":float(leverage[i])} for i in range(len(cooks))],key=lambda x:x["cooks_distance"],reverse=True)[:a.top]
        warnings=["Diagnostics flag observations/assumptions for investigation; they do not authorize automatic deletion."]
        report={"schema_version":"1.0.0","artifact_type":"model-diagnostics","provenance":prov(a.data,warnings),"formula":a.formula,"family":a.family,"nobs":int(result.nobs),"vif":vifs,"influence":flagged,"warnings":warnings}
        if a.family=="ols":
            jb=stats.jarque_bera(residuals); bp_result=bp(residuals,exog)
            report["residuals"]={"mean":float(np.mean(residuals)),"standard_deviation":float(np.std(residuals,ddof=1)),"jarque_bera_statistic":float(jb.statistic),"jarque_bera_p_value":float(jb.pvalue),"durbin_watson":float(sm.stats.stattools.durbin_watson(residuals)),"breusch_pagan_lm":float(bp_result[0]),"breusch_pagan_p_value":float(bp_result[1])}
        else:
            dispersion=float(np.sum(np.asarray(result.resid_pearson)**2)/result.df_resid) if result.df_resid>0 else None
            report["dispersion"]={"pearson_chi2":float(np.sum(np.asarray(result.resid_pearson)**2)),"residual_df":float(result.df_resid),"pearson_dispersion":dispersion,"warning": "Poisson dispersion materially above 1 may indicate overdispersion; assess negative-binomial, quasi-likelihood, zero inflation, or dependence." if a.family=="poisson" and dispersion and dispersion>1.5 else None}
    except (OSError,RuntimeError,ValueError) as exc:
        print(f"error: {exc}",file=sys.stderr); return 2 if isinstance(exc,RuntimeError) else 1
    text=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=f".{a.out.name}.",suffix=".tmp",dir=a.out.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as h:h.write(text)
            os.replace(tmp,a.out)
        except Exception:
            try:os.unlink(tmp)
            except FileNotFoundError:pass
            raise
        print(f"wrote {a.out}",file=sys.stderr)
    else: print(text,end="")
    return 0

if __name__=="__main__":
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8");sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
