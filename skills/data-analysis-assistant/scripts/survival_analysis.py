#!/usr/bin/env python3
"""Fit Cox models or estimate competing-risk cumulative incidence."""

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
        import numpy as np
        import pandas as pd
        from statsmodels.duration.hazard_regression import PHReg
        from statsmodels.duration.survfunc import CumIncidenceRight
    except ImportError as exc:
        raise RuntimeError('install model dependencies with: python -m pip install -e ".[models]"') from exc
    return np, pd, PHReg, CumIncidenceRight


def safe_formula(formula, columns):
    if formula.count("~") != 1 or re.sub(r"[A-Za-z_]\w*|\d+(?:\.\d+)?|[~+*():,\-\s]", "", formula):
        raise ValueError("formula allows only columns, C(), numbers, and ~ + - * :")
    unknown = sorted(set(re.findall(r"[A-Za-z_]\w*", formula)) - set(columns) - {"C"})
    if unknown:
        raise ValueError("formula contains unknown/disallowed names: " + ", ".join(unknown))
    if formula.split("~", 1)[0].strip() not in columns:
        raise ValueError("formula response must be the duration column")


def provenance(path, warnings):
    return {
        "created_by": "data-analysis-assistant/survival_analysis.py",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool_version": VERSION,
        "command": " ".join(sys.argv),
        "seed": None,
        "sources": [{"kind": "file", "locator": str(path.resolve())}],
        "warnings": warnings,
    }


def cox(args, data, np, PHReg):
    safe_formula(args.formula, list(data.columns))
    duration = args.formula.split("~", 1)[0].strip()
    needed = [duration, args.status] + ([args.entry] if args.entry else []) + ([args.strata] if args.strata else [])
    missing = [name for name in needed if name not in data.columns]
    if missing:
        raise ValueError("columns not found: " + ", ".join(missing))
    complete = data.dropna(subset=needed)
    status = complete[args.status].astype(int)
    if not set(status.unique()).issubset({0, 1}) or status.sum() == 0:
        raise ValueError("Cox --status must be binary 0/1 with at least one event")
    model = PHReg.from_formula(
        args.formula, complete, status=status,
        entry=complete[args.entry] if args.entry else None,
        strata=complete[args.strata] if args.strata else None,
        ties=args.ties, missing="drop", eval_env=-1,
    )
    result = model.fit(groups=complete[args.cluster] if args.cluster else None)
    ci = result.conf_int(alpha=1 - args.ci)
    rows = []
    for index, term in enumerate(model.exog_names):
        if not math.isfinite(float(result.pvalues[index])):
            continue
        coefficient = float(result.params[index])
        rows.append({
            "id": "cox-" + re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-"),
            "term": term,
            "test": "Cox proportional hazards coefficient",
            "statistic": float(result.tvalues[index]),
            "p_value": float(result.pvalues[index]),
            "effect_size": math.exp(coefficient),
            "effect_size_metric": "hazard ratio",
            "log_hazard_coefficient": coefficient,
            "confidence_interval": [math.exp(float(ci[index, 0])), math.exp(float(ci[index, 1]))],
            "adjusted_p_value": None,
        })
    warnings = ["Proportional-hazards diagnostics are required before interpreting hazard ratios."]
    dropped = len(data) - len(complete)
    if dropped:
        warnings.append(f"removed {dropped} row(s) missing duration/status/entry/strata")
    return {
        "schema_version": "1.0.0", "artifact_type": "stat-results",
        "provenance": provenance(args.data, warnings), "alpha": args.alpha,
        "results": rows,
        "model": {"type": "cox-ph", "formula": args.formula, "ties": args.ties,
                  "nobs": int(len(complete)), "events": int(status.sum()),
                  "strata": args.strata, "cluster": args.cluster},
    }


def select_points(times, estimates, errors, requested):
    if not requested:
        indices = range(len(times))
    else:
        indices = []
        for point in requested:
            eligible = [i for i, time in enumerate(times) if time <= point]
            indices.append(eligible[-1] if eligible else 0)
        indices = sorted(set(indices))
    return [{"time": float(times[i]), "cumulative_incidence": float(estimates[i]),
             "standard_error": float(errors[i])} for i in indices]


def competing(args, data, np, CumIncidenceRight):
    for name in (args.time, args.status):
        if name not in data.columns:
            raise ValueError(f"column not found: {name}")
    if args.group and args.group not in data.columns:
        raise ValueError(f"group column not found: {args.group}")
    subset = [args.time, args.status] + ([args.group] if args.group else [])
    complete = data.dropna(subset=subset).copy()
    complete[args.status] = complete[args.status].astype(int)
    causes = sorted(int(item) for item in complete[args.status].unique() if item > 0)
    if not causes:
        raise ValueError("competing-risk status needs 0=censored and at least one positive cause code")
    groups = [("all", complete)] if not args.group else [(str(label), frame) for label, frame in complete.groupby(args.group, sort=True)]
    output = []
    for label, frame in groups:
        observed_causes = sorted(int(item) for item in frame[args.status].unique() if item > 0)
        estimate = CumIncidenceRight(frame[args.time].to_numpy(float), frame[args.status].to_numpy(int))
        for index, cause in enumerate(observed_causes):
            output.append({"group": label, "cause": cause,
                           "n": int(len(frame)), "events": int((frame[args.status] == cause).sum()),
                           "estimates": select_points(estimate.times, estimate.cinc[index], estimate.cinc_se[index], args.at_times)})
    warnings = [
        "Cumulative incidence is descriptive Aalen-Johansen estimation; no Gray test or Fine-Gray subdistribution model is claimed.",
        "Cause-specific Cox answers a different estimand and must not be relabeled as a subdistribution hazard model.",
    ]
    return {
        "schema_version": "1.0.0", "artifact_type": "competing-risk-estimate",
        "provenance": provenance(args.data, warnings), "time_column": args.time,
        "status_column": args.status, "group_column": args.group, "causes": causes,
        "groups": output, "warnings": warnings,
    }


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="mode", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("data", type=Path)
    common.add_argument("--out", type=Path)
    common.add_argument("--force", action="store_true")
    c = sub.add_parser("cox", parents=[common])
    c.add_argument("--formula", required=True)
    c.add_argument("--status", required=True)
    c.add_argument("--entry")
    c.add_argument("--strata")
    c.add_argument("--cluster")
    c.add_argument("--ties", choices=["breslow", "efron"], default="breslow")
    c.add_argument("--alpha", type=float, default=0.05)
    c.add_argument("--ci", type=float, default=0.95)
    cr = sub.add_parser("competing-risk", parents=[common])
    cr.add_argument("--time", required=True)
    cr.add_argument("--status", required=True)
    cr.add_argument("--group")
    cr.add_argument("--at-times", type=float, nargs="*")
    args = parser.parse_args(argv)
    if args.out and args.out.resolve() == args.data.resolve():
        parser.error("--out must not replace input data")
    if args.out and args.out.exists() and not args.force:
        parser.error(f"output exists: {args.out}; use --force to replace it")
    try:
        np, pd, PHReg, CIF = stack()
        data = pd.read_csv(args.data)
        artifact = cox(args, data, np, PHReg) if args.mode == "cox" else competing(args, data, np, CIF)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, RuntimeError) else 1
    text = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out:
        write(args.out, text); print(f"wrote {args.out}", file=sys.stderr)
    else: print(text, end="")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
