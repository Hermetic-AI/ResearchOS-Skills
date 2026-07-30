#!/usr/bin/env python3
"""Fit regression, GLM, ANCOVA, GEE repeated-measure, or mixed models."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


VERSION = "0.1.0"
SAFE_TOKEN = re.compile(r"[A-Za-z_]\w*|\d+(?:\.\d+)?|[~+*():,\-\s]")


def require_stack():
    try:
        import pandas as pd
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
        from statsmodels.genmod.cov_struct import Autoregressive, Exchangeable, Independence
    except ImportError as exc:
        raise RuntimeError('install model dependencies with: python -m pip install -e ".[models]"') from exc
    return pd, sm, smf, {"independence": Independence, "exchangeable": Exchangeable, "ar1": Autoregressive}


def validate_formula(formula: str, columns: list[str]) -> None:
    if not formula or formula.count("~") != 1:
        raise ValueError("--formula must contain exactly one '~'")
    compact = "".join(SAFE_TOKEN.findall(formula))
    if re.sub(r"\s+", "", compact) != re.sub(r"\s+", "", formula):
        raise ValueError("formula contains unsupported characters; only columns, C(), numbers, and ~ + - * : are allowed")
    identifiers = re.findall(r"[A-Za-z_]\w*", formula)
    unknown = sorted(set(identifiers) - set(columns) - {"C"})
    if unknown:
        raise ValueError("formula contains unknown or disallowed names: " + ", ".join(unknown))
    response = formula.split("~", 1)[0].strip()
    if response not in columns:
        raise ValueError("formula response must be one untransformed column name")


def stable_id(term: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")[:40] or "term"
    return f"coef-{slug}-{hashlib.sha256(term.encode()).hexdigest()[:8]}"


def load_plan(path: Path | None, formula: str) -> tuple[list[dict], list[str]]:
    if path is None:
        return [], []
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read --analysis-plan: {exc}") from exc
    if plan.get("artifact_type") != "analysis-plan":
        raise ValueError("--analysis-plan must be an analysis-plan artifact")
    warnings = []
    planned = [str(item) for item in plan.get("planned_models", [])]
    if formula not in planned:
        warnings.append("DEVIATION: fitted formula is not an exact entry in analysis-plan.planned_models")
    return [{"kind": "file", "locator": str(path.resolve())}], warnings


def fit(args, data, sm, smf, covariances):
    if args.model in {"ols", "ancova"}:
        result = smf.ols(args.formula, data=data, missing="drop", eval_env=-1).fit(cov_type=args.cov_type)
        return result, "OLS" if args.model == "ols" else "ANCOVA via OLS"
    if args.model == "glm":
        families = {
            "gaussian": sm.families.Gaussian,
            "binomial": sm.families.Binomial,
            "poisson": sm.families.Poisson,
            "negative-binomial": sm.families.NegativeBinomial,
        }
        result = smf.glm(args.formula, data=data, family=families[args.family](), missing="drop", eval_env=-1).fit(cov_type=args.cov_type)
        return result, f"GLM ({args.family})"
    if not args.groups:
        raise ValueError(f"--model {args.model} requires --groups")
    if args.groups not in data.columns:
        raise ValueError(f"group column not found: {args.groups}")
    if args.model == "gee":
        covariance = covariances[args.cov_structure]()
        result = smf.gee(args.formula, groups=args.groups, data=data,
                         family=sm.families.Gaussian(), cov_struct=covariance,
                         missing="drop", eval_env=-1).fit()
        return result, f"GEE repeated measures ({args.cov_structure})"
    result = smf.mixedlm(args.formula, data=data, groups=data[args.groups],
                         re_formula=args.re_formula, missing="drop", eval_env=-1).fit(
                             reml=not args.ml, method="lbfgs", disp=False)
    return result, "linear mixed-effects model"


def artifact_from(args, data_path: Path, data, result, model_name: str, plan_sources, warnings):
    confidence = result.conf_int(alpha=1 - args.ci)
    values = result.params
    pvalues = result.pvalues
    statistics = getattr(result, "tvalues", None)
    rows = []
    fixed_names = list(getattr(result.model, "exog_names", []))
    for term in fixed_names:
        if term not in values.index or not math.isfinite(float(pvalues[term])):
            continue
        rows.append({
            "id": stable_id(term),
            "term": term,
            "test": f"{model_name} coefficient",
            "statistic": float(statistics[term]),
            "p_value": float(pvalues[term]),
            "effect_size": float(values[term]),
            "effect_size_metric": "unstandardized coefficient",
            "confidence_interval": [float(confidence.loc[term, 0]), float(confidence.loc[term, 1])],
            "adjusted_p_value": None,
        })
    nobs = int(result.nobs)
    dropped = int(len(data) - nobs)
    if dropped:
        warnings.append(f"complete-case/model-specific deletion removed {dropped} row(s)")
    if hasattr(result, "converged") and not bool(result.converged):
        warnings.append("model did not report convergence")
    return {
        "schema_version": "1.0.0",
        "artifact_type": "stat-results",
        "provenance": {
            "created_by": "data-analysis-assistant/model_analysis.py",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "command": " ".join(sys.argv),
            "seed": None,
            "sources": [{"kind": "file", "locator": str(data_path.resolve())}, *plan_sources],
            "warnings": warnings,
        },
        "alpha": args.alpha,
        "results": rows,
        "model": {
            "type": args.model,
            "name": model_name,
            "formula": args.formula,
            "family": args.family if args.model == "glm" else None,
            "groups": args.groups,
            "covariance": args.cov_structure if args.model == "gee" else None,
            "nobs": nobs,
            "rows_dropped": dropped,
            "converged": bool(result.converged) if hasattr(result, "converged") else None,
            "aic": float(result.aic) if hasattr(result, "aic") and math.isfinite(float(result.aic)) else None,
            "bic": float(result.bic) if hasattr(result, "bic") and math.isfinite(float(result.bic)) else None,
        },
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("data", type=Path, help="input CSV")
    parser.add_argument("--model", choices=["ols", "ancova", "glm", "gee", "mixedlm"], required=True)
    parser.add_argument("--formula", required=True, help="restricted Statsmodels formula")
    parser.add_argument("--family", choices=["gaussian", "binomial", "poisson", "negative-binomial"], default="gaussian")
    parser.add_argument("--groups", help="subject/cluster column for GEE or MixedLM")
    parser.add_argument("--cov-structure", choices=["independence", "exchangeable", "ar1"], default="exchangeable")
    parser.add_argument("--re-formula", default="1", help="MixedLM random-effects formula (default random intercept)")
    parser.add_argument("--ml", action="store_true", help="MixedLM maximum likelihood instead of REML")
    parser.add_argument("--cov-type", choices=["nonrobust", "HC0", "HC1", "HC2", "HC3"], default="nonrobust")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--ci", type=float, default=0.95)
    parser.add_argument("--analysis-plan", type=Path)
    parser.add_argument("--out", type=Path, help="write stat-results JSON instead of stdout")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.alpha < 1 or not 0 < args.ci < 1:
        parser.error("--alpha and --ci must be in (0, 1)")
    sources = [args.data.resolve()] + ([args.analysis_plan.resolve()] if args.analysis_plan else [])
    if args.out and args.out.resolve() in sources:
        parser.error("--out must not replace a source file")
    if args.out and args.out.exists() and not args.force:
        parser.error(f"output exists: {args.out}; use --force to replace it")
    try:
        pd, sm, smf, covariances = require_stack()
        data = pd.read_csv(args.data)
        validate_formula(args.formula, list(data.columns))
        plan_sources, warnings = load_plan(args.analysis_plan, args.formula)
        result, model_name = fit(args, data, sm, smf, covariances)
        artifact = artifact_from(args, args.data, data, result, model_name, plan_sources, warnings)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, RuntimeError) else 1
    text = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out:
        atomic_write(args.out, text)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
