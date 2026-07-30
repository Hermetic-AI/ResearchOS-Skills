#!/usr/bin/env python3
"""Fit univariate SARIMAX forecasts or fixed-effects panel regressions."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


VERSION = "0.1.0"


def stack():
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except ImportError as exc:
        raise RuntimeError('install model dependencies with: python -m pip install -e ".[models]"') from exc
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from model_analysis import stable_id, validate_formula
    return pd, smf, SARIMAX, stable_id, validate_formula


def parse_tuple(value, length, name):
    try: result = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc: raise ValueError(f"{name} must be comma-separated integers") from exc
    if len(result) != length or any(item < 0 for item in result):
        raise ValueError(f"{name} needs {length} nonnegative integers")
    if length == 4 and result[3] == 1:
        raise ValueError("seasonal period must be 0 or >= 2")
    return result


def prov(path, warnings):
    return {"created_by": "data-analysis-assistant/temporal_panel_analysis.py",
            "created_at": datetime.now(timezone.utc).isoformat(), "tool_version": VERSION,
            "command": " ".join(sys.argv), "seed": None,
            "sources": [{"kind": "file", "locator": str(path.resolve())}], "warnings": warnings}


def timeseries(args, data, pd, SARIMAX, stable_id):
    for name in (args.date, args.value):
        if name not in data.columns: raise ValueError(f"column not found: {name}")
    frame = data[[args.date, args.value]].copy()
    frame[args.date] = pd.to_datetime(frame[args.date], errors="raise")
    if frame[args.date].duplicated().any(): raise ValueError("time index contains duplicates")
    frame = frame.sort_values(args.date).set_index(args.date)
    frequency = args.freq or pd.infer_freq(frame.index)
    if not frequency: raise ValueError("cannot infer regular frequency; provide --freq after defining an aggregation/alignment rule")
    series = pd.to_numeric(frame[args.value], errors="raise").asfreq(frequency)
    missing = int(series.isna().sum())
    if missing and not args.allow_missing: raise ValueError(f"regularized series contains {missing} missing observation(s); use --allow-missing only with a justified state-space missingness assumption")
    order = parse_tuple(args.order, 3, "--order")
    seasonal = parse_tuple(args.seasonal_order, 4, "--seasonal-order")
    result = SARIMAX(series, order=order, seasonal_order=seasonal, trend=args.trend,
                     enforce_stationarity=not args.no_enforce_stationarity,
                     enforce_invertibility=not args.no_enforce_invertibility,
                     missing="none").fit(disp=False, maxiter=args.maxiter)
    ci = result.conf_int(alpha=1 - args.ci)
    coefficients = []
    for term, estimate, statistic, pvalue in zip(result.param_names, result.params, result.zvalues, result.pvalues):
        if math.isfinite(float(pvalue)):
            coefficients.append({"id": stable_id(term), "term": term, "estimate": float(estimate),
                                 "statistic": float(statistic), "p_value": float(pvalue),
                                 "confidence_interval": [float(ci.loc[term].iloc[0]), float(ci.loc[term].iloc[1])]})
    forecast = []
    if args.steps:
        prediction = result.get_forecast(steps=args.steps)
        bounds = prediction.conf_int(alpha=1 - args.ci)
        for index, mean, (_, row) in zip(prediction.predicted_mean.index, prediction.predicted_mean, bounds.iterrows()):
            forecast.append({"time": str(index), "mean": float(mean), "lower": float(row.iloc[0]), "upper": float(row.iloc[1])})
    warnings = ["Inspect residual autocorrelation, stability/invertibility, structural breaks, and out-of-sample performance before using forecasts."]
    if missing: warnings.append(f"state-space likelihood handled {missing} missing observation(s)")
    if not result.mle_retvals.get("converged", True): warnings.append("optimizer did not report convergence")
    return {"schema_version": "1.0.0", "artifact_type": "time-series-forecast", "provenance": prov(args.data, warnings),
            "date_column": args.date, "value_column": args.value, "frequency": frequency,
            "order": list(order), "seasonal_order": list(seasonal), "trend": args.trend,
            "nobs": int(result.nobs), "missing": missing, "converged": bool(result.mle_retvals.get("converged", True)),
            "aic": float(result.aic), "bic": float(result.bic), "coefficients": coefficients,
            "forecast": forecast, "warnings": warnings}


def panel(args, data, smf, stable_id, validate_formula):
    validate_formula(args.formula, list(data.columns))
    for name in (args.entity, args.time):
        if name not in data.columns: raise ValueError(f"column not found: {name}")
    identifiers = set(re.findall(r"[A-Za-z_]\w*", args.formula)) - {"C"}
    complete = data.dropna(subset=sorted(identifiers | {args.entity, args.time})).copy()
    entity_levels, time_levels = complete[args.entity].nunique(), complete[args.time].nunique()
    if entity_levels < 2 or time_levels < 2: raise ValueError("panel needs at least two entities and two time periods")
    additions = []
    if args.effects in {"entity", "two-way"}: additions.append(f"C({args.entity})")
    if args.effects in {"time", "two-way"}: additions.append(f"C({args.time})")
    formula = args.formula + (" + " + " + ".join(additions) if additions else "")
    cluster = args.cluster or args.entity
    if cluster not in complete.columns: raise ValueError(f"cluster column not found: {cluster}")
    result = smf.ols(formula, data=complete, eval_env=-1).fit(cov_type="cluster", cov_kwds={"groups": complete[cluster]})
    ci = result.conf_int(alpha=1 - args.ci)
    absorbed_prefixes = tuple(f"C({name})[" for name in (args.entity, args.time))
    rows = []
    for term in result.params.index:
        if term.startswith(absorbed_prefixes): continue
        pvalue = float(result.pvalues[term])
        if not math.isfinite(pvalue): continue
        rows.append({"id": stable_id(term), "term": term, "test": "panel fixed-effects coefficient",
                     "statistic": float(result.tvalues[term]), "p_value": pvalue,
                     "effect_size": float(result.params[term]), "effect_size_metric": "within-model unstandardized coefficient",
                     "confidence_interval": [float(ci.loc[term, 0]), float(ci.loc[term, 1])], "adjusted_p_value": None})
    warnings = ["Cluster-robust inference can be unreliable with few clusters; report cluster count and use an appropriate small-sample method when needed."]
    if len(complete) < len(data): warnings.append(f"complete-case deletion removed {len(data) - len(complete)} row(s)")
    return {"schema_version": "1.0.0", "artifact_type": "stat-results", "provenance": prov(args.data, warnings),
            "alpha": args.alpha, "results": rows,
            "model": {"type": "panel-fixed-effects", "formula": args.formula, "fitted_formula": formula,
                      "effects": args.effects, "entity": args.entity, "time": args.time, "cluster": cluster,
                      "nobs": int(result.nobs), "entities": int(entity_levels), "periods": int(time_levels),
                      "r_squared": float(result.rsquared)}}


def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True); fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as h: h.write(text)
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="mode", required=True); common = argparse.ArgumentParser(add_help=False)
    common.add_argument("data", type=Path); common.add_argument("--out", type=Path); common.add_argument("--force", action="store_true")
    ts = sub.add_parser("timeseries", parents=[common]); ts.add_argument("--date", required=True); ts.add_argument("--value", required=True)
    ts.add_argument("--freq"); ts.add_argument("--order", default="1,0,0"); ts.add_argument("--seasonal-order", default="0,0,0,0")
    ts.add_argument("--trend", choices=["n", "c", "t", "ct"], default="c"); ts.add_argument("--steps", type=int, default=0)
    ts.add_argument("--ci", type=float, default=0.95); ts.add_argument("--allow-missing", action="store_true")
    ts.add_argument("--no-enforce-stationarity", action="store_true"); ts.add_argument("--no-enforce-invertibility", action="store_true"); ts.add_argument("--maxiter", type=int, default=200)
    pn = sub.add_parser("panel", parents=[common]); pn.add_argument("--formula", required=True); pn.add_argument("--entity", required=True); pn.add_argument("--time", required=True)
    pn.add_argument("--effects", choices=["none", "entity", "time", "two-way"], default="two-way"); pn.add_argument("--cluster")
    pn.add_argument("--alpha", type=float, default=0.05); pn.add_argument("--ci", type=float, default=0.95)
    args = parser.parse_args(argv)
    if args.out and args.out.resolve() == args.data.resolve(): parser.error("--out must not replace input data")
    if args.out and args.out.exists() and not args.force: parser.error(f"output exists: {args.out}; use --force to replace it")
    if getattr(args, "steps", 0) < 0 or not 0 < args.ci < 1 or (hasattr(args, "alpha") and not 0 < args.alpha < 1): parser.error("steps must be nonnegative and alpha/ci in (0,1)")
    try:
        pd, smf, SARIMAX, stable_id, validate_formula = stack(); data = pd.read_csv(args.data)
        artifact = timeseries(args, data, pd, SARIMAX, stable_id) if args.mode == "timeseries" else panel(args, data, smf, stable_id, validate_formula)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2 if isinstance(exc, RuntimeError) else 1
    text = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out: atomic(args.out, text); print(f"wrote {args.out}", file=sys.stderr)
    else: print(text, end="")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
