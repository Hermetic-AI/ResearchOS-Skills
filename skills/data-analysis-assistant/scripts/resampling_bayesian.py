#!/usr/bin/env python3
"""Bootstrap, permutation, trimmed-mean, and beta-binomial analyses."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"


def numbers(value, name):
    try:
        result = [float(item) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise ValueError(f"{name} must be comma-separated numbers") from exc
    if not result: raise ValueError(f"{name} is empty")
    return result


def quantile(values, q):
    values = sorted(values); position = (len(values) - 1) * q; low, high = math.floor(position), math.ceil(position)
    return values[low] if low == high else values[low] + (values[high] - values[low]) * (position - low)


def stat_value(kind, values=None, a=None, b=None, x=None, y=None):
    if kind == "mean": return statistics.fmean(values)
    if kind == "median": return statistics.median(values)
    if kind == "difference": return statistics.fmean(a) - statistics.fmean(b)
    if kind == "correlation":
        mx, my = statistics.fmean(x), statistics.fmean(y)
        numerator = sum((u - mx) * (v - my) for u, v in zip(x, y))
        denominator = math.sqrt(sum((u - mx) ** 2 for u in x) * sum((v - my) ** 2 for v in y))
        if denominator == 0: raise ValueError("correlation needs non-constant x and y")
        return numerator / denominator
    raise ValueError("unknown statistic")


def inputs(args):
    if args.stat in {"mean", "median"}:
        if args.values is None: raise ValueError(f"--stat {args.stat} requires --values")
        return {"values": numbers(args.values, "--values")}
    if args.stat == "difference":
        if args.a is None or args.b is None: raise ValueError("--stat difference requires --a and --b")
        return {"a": numbers(args.a, "--a"), "b": numbers(args.b, "--b")}
    if args.x is None or args.y is None: raise ValueError("--stat correlation requires --x and --y")
    x, y = numbers(args.x, "--x"), numbers(args.y, "--y")
    if len(x) != len(y) or len(x) < 3: raise ValueError("correlation needs x/y of equal length >= 3")
    return {"x": x, "y": y}


def bootstrap(args):
    data = inputs(args); rng = random.Random(args.seed); observed = stat_value(args.stat, **data); sims = []
    for _ in range(args.reps):
        if args.stat in {"mean", "median"}: sample = [rng.choice(data["values"]) for _ in data["values"]]; sims.append(stat_value(args.stat, values=sample))
        elif args.stat == "difference":
            a, b = [rng.choice(data["a"]) for _ in data["a"]], [rng.choice(data["b"]) for _ in data["b"]]; sims.append(stat_value(args.stat, a=a, b=b))
        else:
            pairs = [rng.choice(list(zip(data["x"], data["y"]))) for _ in data["x"]]; x, y = zip(*pairs); sims.append(stat_value(args.stat, x=x, y=y))
    alpha = 1 - args.ci
    return {"schema_version": "1.0.0", "artifact_type": "resampling-estimate", "provenance": provenance("bootstrap", args.seed),
            "method": "nonparametric-bootstrap-percentile", "statistic": args.stat, "point_estimate": observed,
            "confidence_interval": [quantile(sims, alpha / 2), quantile(sims, 1 - alpha / 2)],
            "p_value": None, "n_resamples": args.reps, "seed": args.seed,
            "warnings": ["Percentile bootstrap interval; assess exchangeability/independence and use a design-aware resampling scheme for clustered, paired, or time-series data."]}


def permutation(args):
    data = inputs(args); rng = random.Random(args.seed); observed = stat_value(args.stat, **data); extreme = 0
    for _ in range(args.reps):
        if args.stat == "difference":
            pooled = data["a"] + data["b"]; rng.shuffle(pooled); simulated = stat_value("difference", a=pooled[:len(data["a"])], b=pooled[len(data["a"]):])
        elif args.stat == "correlation":
            y = data["y"][:]; rng.shuffle(y); simulated = stat_value("correlation", x=data["x"], y=y)
        else: raise ValueError("permutation supports difference or correlation")
        extreme += abs(simulated) >= abs(observed)
    p = (extreme + 1) / (args.reps + 1)
    return {"schema_version": "1.0.0", "artifact_type": "resampling-estimate", "provenance": provenance("permutation", args.seed),
            "method": "Monte-Carlo permutation (two-sided)", "statistic": args.stat, "point_estimate": observed,
            "confidence_interval": None, "p_value": p, "n_resamples": args.reps, "seed": args.seed,
            "warnings": ["Monte-Carlo p-value uses the +1 correction. Exchangeability under the null is required; preserve pairing, clustering, strata, or time blocks in the permutation scheme when applicable."]}


def robust(args):
    try:
        from scipy import stats
    except ImportError as exc: raise RuntimeError('install analysis dependencies with: python -m pip install -e ".[analysis]"') from exc
    a, b = numbers(args.a, "--a"), numbers(args.b, "--b")
    result = stats.ttest_ind(a, b, equal_var=False, trim=args.trim)
    return {"schema_version": "1.0.0", "artifact_type": "stat-results", "provenance": provenance("trimmed-mean", None), "alpha": args.alpha,
            "results": [{"id": "trimmed-mean-difference", "test": f"Yuen/Welch trimmed mean ({args.trim:.0%})", "statistic": float(result.statistic), "p_value": float(result.pvalue), "effect_size": statistics.fmean(a) - statistics.fmean(b), "confidence_interval": None, "adjusted_p_value": None}],
            "warnings": ["Effect estimate is the untrimmed mean difference; report trimmed means separately and justify the trimming proportion."]}


def bayes(args):
    for success, total, label in ((args.success_a, args.total_a, "a"), (args.success_b, args.total_b, "b")):
        if not 0 <= success <= total or total < 1: raise ValueError(f"invalid success/total for arm {label}")
    if args.prior_a <= 0 or args.prior_b <= 0: raise ValueError("Beta prior parameters must be > 0")
    rng = random.Random(args.seed); pa, pb = args.prior_a + args.success_a, args.prior_b + args.total_a - args.success_a
    qa, qb = args.prior_a + args.success_b, args.prior_b + args.total_b - args.success_b
    draws = [rng.betavariate(pa, pb) - rng.betavariate(qa, qb) for _ in range(args.reps)]
    alpha = 1 - args.ci
    return {"schema_version": "1.0.0", "artifact_type": "bayesian-estimate", "provenance": provenance("beta-binomial", args.seed),
            "model": "independent beta-binomial proportions", "prior": {"alpha": args.prior_a, "beta": args.prior_b},
            "arms": {"a": {"successes": args.success_a, "trials": args.total_a, "posterior": [pa, pb]}, "b": {"successes": args.success_b, "trials": args.total_b, "posterior": [qa, qb]}},
            "contrast": "p_a - p_b", "posterior_mean": statistics.fmean(draws), "credible_interval": [quantile(draws, alpha / 2), quantile(draws, 1 - alpha / 2)],
            "probability_greater_than_zero": sum(item > 0 for item in draws) / args.reps, "n_draws": args.reps, "seed": args.seed,
            "warnings": ["Posterior probabilities and credible intervals are not p-values or confidence intervals. Perform prior sensitivity analysis before confirmatory use."]}


def provenance(method, seed):
    return {"created_by": "data-analysis-assistant/resampling_bayesian.py", "created_at": datetime.now(timezone.utc).isoformat(), "tool_version": VERSION, "command": " ".join(sys.argv), "seed": seed, "sources": [{"kind": "user", "locator": method}], "warnings": []}


def write(path, text):
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
    sub = parser.add_subparsers(dest="mode", required=True)
    common = argparse.ArgumentParser(add_help=False); common.add_argument("--out", type=Path); common.add_argument("--force", action="store_true")
    rs = sub.add_parser("bootstrap", parents=[common]); pm = sub.add_parser("permutation", parents=[common])
    for item in (rs, pm):
        item.add_argument("--stat", choices=["mean", "median", "difference", "correlation"], required=True); item.add_argument("--values"); item.add_argument("--a"); item.add_argument("--b"); item.add_argument("--x"); item.add_argument("--y"); item.add_argument("--reps", type=int, default=5000); item.add_argument("--seed", type=int, default=0)
    rs.add_argument("--ci", type=float, default=0.95)
    rb = sub.add_parser("robust", parents=[common]); rb.add_argument("--a", required=True); rb.add_argument("--b", required=True); rb.add_argument("--trim", type=float, default=0.2); rb.add_argument("--alpha", type=float, default=0.05)
    by = sub.add_parser("bayes-binomial", parents=[common]); by.add_argument("--success-a", type=int, required=True); by.add_argument("--total-a", type=int, required=True); by.add_argument("--success-b", type=int, required=True); by.add_argument("--total-b", type=int, required=True); by.add_argument("--prior-a", type=float, default=1); by.add_argument("--prior-b", type=float, default=1); by.add_argument("--reps", type=int, default=10000); by.add_argument("--seed", type=int, default=0); by.add_argument("--ci", type=float, default=0.95)
    args = parser.parse_args(argv)
    if args.out and args.out.exists() and not args.force: parser.error(f"output exists: {args.out}; use --force to replace it")
    if args.mode in {"bootstrap", "permutation", "bayes-binomial"} and (args.reps < 100 or not 0 < args.ci < 1): parser.error("--reps must be >= 100 and --ci in (0, 1)")
    if args.mode == "robust" and not 0 <= args.trim < .5: parser.error("--trim must be in [0, .5)")
    try:
        artifact = bootstrap(args) if args.mode == "bootstrap" else permutation(args) if args.mode == "permutation" else robust(args) if args.mode == "robust" else bayes(args)
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2 if isinstance(exc, RuntimeError) else 1
    text = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out: write(args.out, text); print(f"wrote {args.out}", file=sys.stderr)
    else: print(text, end="")
    return 0

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
