#!/usr/bin/env python3
"""Compare paper-claimed metric values against reproduced values.

Purpose
    Align paper-reported and reproduced metrics on the (model, dataset,
    metric) key and assign a verdict per row:
      match         both values present and relative error <= tolerance
                    (exactly-at-tolerance counts as match)
      mismatch      both present but relative error > tolerance
      missing_repro paper value exists, no reproduced value
      missing_paper reproduced value exists, no paper claim
    Relative error is abs(repro - paper) / abs(paper); when the paper value
    is 0, absolute error is used instead.

Dependencies
    Python 3 standard library only. No third-party packages. Fully
    deterministic (no randomness involved).

CLI
    python3 compare_results.py --paper claims.json --repro repro.json \
        [--tolerance 0.01] [--format md|json]

    Inline pairs (no files needed) — may be repeated:
    python3 compare_results.py --tolerance 0.01 \
        --pair "ResNet50:ImageNet:top1_acc:76.1:75.9" \
        --pair "ResNet50:ImageNet:top5_acc:92.8:"          # missing repro

    JSON file format (both files):
      [{"model": "ResNet50", "dataset": "ImageNet", "metric": "top1_acc",
        "value": 76.1, "source": "paper Table 2"}, ...]
    ("source" is optional but recommended; it is echoed into the report.)

    Multi-run input: a repro row's "value" may instead be a list of per-run
    numbers, e.g. "value": [75.8, 76.0, 75.9]. The report then shows
    mean ± std (n runs, spread) and judges the match on the mean. Paper
    values stay scalar; if the paper reports its own std, record it in
    "source" (e.g. "paper Table 2: 76.1±0.2").

Output
    --format md (default): a markdown comparison card with one row per
    metric plus a summary line. --format json: the same data as JSON.
"""

import argparse
import json
import math
import os
import random
import statistics
import sys


def _betainc(a, b, x, max_iter=200, eps=1e-12):
    """Regularized incomplete beta function I_x(a,b) via Lentz continued fraction.

    Reference: Numerical Recuits continued-fraction expansion of the incomplete
    beta function. Uses the symmetry I_x(a,b) = 1 - I_{1-x}(b,a) so the
    fraction converges for all x in (0, 1).
    """
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # Symmetry: evaluate the side that converges faster.
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betainc(b, a, 1.0 - x, max_iter, eps)
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1.0 - x) - lbeta) / a
    # Lentz continued fraction: f = 1/(1 + d1/(1 + d2/(1 + ...)))
    tiny = 1e-30
    f = 1.0
    c = 1.0
    d = 0.0
    for m in range(1, max_iter + 1):
        # even index term (2m)
        aa = m * (b - m) * x / ((a + 2 * m - 1.0) * (a + 2 * m))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        f *= c * d
        # odd index term (2m + 1)
        aa = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1.0))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < eps:
            break
    return front * f


def t_cdf(t, df):
    """Two-sided CDF of the Student t-distribution: P(T <= t)."""
    if df <= 0:
        raise ValueError("df must be positive")
    x = df / (df + t * t)
    ib = _betainc(df / 2.0, 0.5, x)
    return 1.0 - 0.5 * ib if t >= 0 else 0.5 * ib


def welch_ttest(mean1, std1, n1, mean2, std2, n2):
    """Welch's t-test between two independent samples.

    Returns (t_statistic, df, p_value_two_sided). std1/std2 are the sample
    standard deviations; n1/n2 the sample sizes.
    """
    if n1 < 2 or n2 < 2:
        return 0.0, 0.0, 1.0
    v1 = std1 * std1
    v2 = std2 * std2
    se = math.sqrt(v1 / n1 + v2 / n2)
    if se == 0.0:
        return (0.0, 1.0, 1.0) if mean1 == mean2 else (math.copysign(1e30, mean1 - mean2), 1.0, 0.0)
    t = (mean1 - mean2) / se
    num = (v1 / n1 + v2 / n2) ** 2
    den = (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    df = num / den if den > 0 else 1.0
    p = 2.0 * (1.0 - t_cdf(abs(t), df))
    return t, df, p


def bootstrap_ci(runs, level, seed, n_boot=10000):
    """Percentile bootstrap confidence interval for the mean of runs.

    Deterministic given (runs, level, seed). Returns (ci_low, ci_high).
    """
    rng = random.Random(seed)
    n = len(runs)
    means = []
    for _ in range(n_boot):
        s = 0.0
        for _ in range(n):
            s += runs[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    alpha = 1.0 - level
    lower_idx = int(math.floor(alpha / 2.0 * n_boot))
    upper_idx = int(math.ceil((1.0 - alpha / 2.0) * n_boot)) - 1
    lower_idx = max(0, min(lower_idx, n_boot - 1))
    upper_idx = max(0, min(upper_idx, n_boot - 1))
    if lower_idx > upper_idx:
        lower_idx = upper_idx
    return means[lower_idx], means[upper_idx]


def _paper_dist(row):
    """Extract optional (mean, std, n) from a paper row, or None."""
    if row is None:
        return None
    if "std" not in row or "n" not in row:
        return None
    try:
        std = float(row["std"])
        n = int(row["n"])
        mean = float(row["value"])
    except (TypeError, ValueError, KeyError):
        return None
    if n < 2 or std < 0:
        return None
    return mean, std, n


def _uncertainty_verdict(paper_value, paper_dist, repro_runs, repro_ci):
    """Compute uncertainty-aware verdict. Returns dict of extra stats to merge
    into repro_runs, or {} when there is nothing to add.

    Cases:
      - paper has std+n and repro has multiple runs: Welch's t-test.
      - only repro has multiple runs: check if paper scalar falls in repro CI.
    """
    extras = {}
    if repro_runs is None:
        return extras
    n = repro_runs.get("n", 0)
    if n < 2:
        return extras
    mean = repro_runs["mean"]
    std = repro_runs["std"]

    ci_low = ci_high = None
    if repro_ci is not None:
        ci_low, ci_high, ci_level = repro_ci
        extras["ci_low"] = round(ci_low, 6)
        extras["ci_high"] = round(ci_high, 6)
        extras["ci_level"] = ci_level

    if paper_dist is not None:
        pmean, pstd, pn = paper_dist
        t, df, p = welch_ttest(pmean, pstd, pn, mean, std, n)
        extras["t_statistic"] = round(t, 6)
        extras["df"] = round(df, 4)
        extras["p_value"] = round(p, 6)
        if repro_ci is not None:
            in_ci = ci_low <= pmean <= ci_high
        else:
            in_ci = None
        if in_ci is True:
            extras["uncertainty_verdict"] = "consistent"
        elif in_ci is False and p < 0.05:
            extras["uncertainty_verdict"] = "inconsistent"
        elif p >= 0.05:
            extras["uncertainty_verdict"] = "consistent"
        else:
            extras["uncertainty_verdict"] = "uncertain"
        return extras

    # Only repro has a distribution; paper is a scalar.
    if repro_ci is not None and paper_value is not None:
        in_ci = ci_low <= paper_value <= ci_high
        if in_ci:
            extras["uncertainty_verdict"] = "consistent"
        else:
            # Without a paper std+n we cannot run a t-test; mark uncertain.
            extras["uncertainty_verdict"] = "uncertain"
    return extras


def summarize_runs(value):
    """Normalize a repro 'value' to (scalar, stats).

    scalar is the number used for the verdict (the mean for multi-run input).
    stats is None for scalar input, else {n, mean, std, min, max}.
    """
    if isinstance(value, list):
        runs = [float(v) for v in value]
        if not runs:
            return None, None
        mean = statistics.fmean(runs)
        stats = {
            "n": len(runs),
            "mean": round(mean, 6),
            "std": round(statistics.stdev(runs), 6) if len(runs) > 1 else 0.0,
            "min": min(runs),
            "max": max(runs),
        }
        return mean, stats
    return (float(value) if value is not None else None), None


def verdict(paper, repro, tol, abs_tol=None):
    if paper is None:
        return "missing_paper", None, None
    if repro is None:
        return "missing_repro", None, None
    absolute_error = abs(repro - paper)
    if abs_tol is not None:
        return ("match" if absolute_error <= abs_tol else "mismatch"), absolute_error, "absolute"
    denom = abs(paper)
    err = absolute_error / denom if denom > 0 else absolute_error
    return ("match" if err <= tol else "mismatch"), err, "relative" if denom > 0 else "absolute_zero_baseline"


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise SystemExit(f"error: {path} must contain a JSON list")
    return data


def key_of(row):
    return (row.get("model", ""), row.get("dataset", ""), row.get("metric", ""))


def parse_pair(spec):
    parts = spec.split(":")
    if len(parts) != 5:
        raise SystemExit(f"error: --pair expects model:dataset:metric:paper:repro, got {spec!r}")
    model, dataset, metric, p, r = parts
    return (model, dataset, metric,
            float(p) if p else None,
            float(r) if r else None)


def build_rows(paper_rows, repro_rows, tol, abs_tol=None, direction="neutral",
               bootstrap_ci_level=None, seed=None, uncertainty=False):
    paper_map = {key_of(r): r for r in paper_rows}
    repro_map = {key_of(r): r for r in repro_rows}
    rows = []
    for key in sorted(set(paper_map) | set(repro_map)):
        p, r = paper_map.get(key), repro_map.get(key)
        pv = p.get("value") if p else None
        if pv is not None and not isinstance(pv, (int, float)):
            try:
                pv = float(pv)
            except (TypeError, ValueError):
                raise SystemExit(
                    f"error: paper value for {key[0]}/{key[1]}/{key[2]} "
                    f"is not numeric: {pv!r}")
        rv, rstats = summarize_runs(r.get("value")) if r else (None, None)
        v, err, error_kind = verdict(pv, rv, tol, abs_tol)
        change = None
        if pv is not None and rv is not None:
            delta = rv - pv
            change = "same" if delta == 0 else ("improved" if (delta > 0) == (direction == "higher") else "worse") if direction != "neutral" else "different"
        row = {
            "model": key[0],
            "dataset": key[1],
            "metric": key[2],
            "paper_value": pv,
            "repro_value": rv,
            "repro_runs": rstats,
            "error": round(err, 6) if err is not None else None,
            "error_kind": error_kind if err is not None else None,
            "rel_error": round(err, 6) if error_kind == "relative" else None,
            "tolerance": abs_tol if abs_tol is not None else tol,
            "direction": direction, "directional_change": change,
            "verdict": v,
            "paper_source": (p or {}).get("source"),
            "repro_source": (r or {}).get("source"),
        }
        # Distribution-level statistics (additive; only when requested).
        repro_ci = None
        if bootstrap_ci_level is not None and rstats is not None and rstats["n"] > 1:
            runs = [float(x) for x in r.get("value")]
            ci_low, ci_high = bootstrap_ci(runs, bootstrap_ci_level, seed)
            repro_ci = (ci_low, ci_high, bootstrap_ci_level)
            rstats["ci_low"] = round(ci_low, 6)
            rstats["ci_high"] = round(ci_high, 6)
            rstats["ci_level"] = bootstrap_ci_level
        if uncertainty and rstats is not None and rstats["n"] > 1:
            paper_dist = _paper_dist(p)
            extras = _uncertainty_verdict(pv, paper_dist, rstats, repro_ci)
            rstats.update(extras)
        rows.append(row)
    return rows


def to_markdown(rows, tol, abs_tol=None):
    def fmt(x):
        return "—" if x is None else (f"{x:.6g}" if isinstance(x, float) else str(x))

    def fmt_repro(r):
        if r["repro_runs"] is None:
            return fmt(r["repro_value"])
        s = r["repro_runs"]
        return f"{s['mean']:.4g}±{s['std']:.3g} (n={s['n']}, {s['min']:.4g}–{s['max']:.4g})"

    lines = [
        "# Reproduction Comparison Card",
        "",
        f"Tolerance: relative error ≤ {tol:g} ⇒ match",
        "",
        "| Model | Dataset | Metric | Paper | Reproduced | Rel. err | Verdict | Sources |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        err = "—" if r["error"] is None else (f"{r['error']:.6g}" if r["error_kind"] != "relative" else f"{r['error']:.2%}")
        srcs = "; ".join(s for s in (r["paper_source"], r["repro_source"]) if s) or "—"
        lines.append(
            f"| {r['model']} | {r['dataset']} | {r['metric']} "
            f"| {fmt(r['paper_value'])} | {fmt_repro(r)} | {err} "
            f"| {r['verdict']} | {srcs} |"
        )
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    lines += ["", f"Summary ({len(rows)} metrics): {summary}", ""]
    return "\n".join(lines)


def load_environment(spec):
    if not spec:
        raise SystemExit("error: --artifact-out requires --environment-json (JSON object or file)")
    try:
        if os.path.isfile(spec):
            with open(spec, encoding="utf-8") as handle:
                value = json.load(handle)
        else:
            value = json.loads(spec)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: cannot read --environment-json: {exc}")
    if not isinstance(value, dict):
        raise SystemExit("error: --environment-json must resolve to a JSON object")
    return value


def reproduction_artifact(args, rows):
    if not args.repository_commit:
        raise SystemExit("error: --artifact-out requires --repository-commit")
    environment = load_environment(args.environment_json)
    sources = []
    if args.paper:
        sources.append({"kind": "file", "locator": os.path.abspath(args.paper)})
    if args.repro:
        sources.append({"kind": "file", "locator": os.path.abspath(args.repro)})
    if args.pair:
        sources.append({"kind": "user", "locator": "inline --pair values"})
    verdict_map = {"missing_repro": "missing-repro", "missing_paper": "missing-paper"}
    warnings = []
    for row in rows:
        if not row.get("paper_source"):
            warnings.append(f"missing paper evidence locator for {row['model']}/{row['dataset']}/{row['metric']}")
        if not row.get("repro_source"):
            warnings.append(f"missing reproduced artifact locator for {row['model']}/{row['dataset']}/{row['metric']}")
    return {
        "schema_version": "1.0.0",
        "artifact_type": "reproduction-card",
        "provenance": {
            "created_by": "reproduction-assistant/compare_results.py",
            "tool_version": "0.1.0",
            "command": " ".join(sys.argv),
            "seed": None,
            "sources": sources,
            "warnings": warnings,
        },
        "repository_commit": args.repository_commit,
        "environment": environment,
        "tolerance": args.tolerance,
        "comparisons": [{
            "metric": row["metric"],
            "model": row["model"],
            "dataset": row["dataset"],
            "paper_value": row["paper_value"],
            "reproduced_value": row["repro_value"],
            "verdict": verdict_map.get(row["verdict"], row["verdict"]),
            "paper_source": row["paper_source"],
            "repro_source": row["repro_source"],
        } for row in rows],
    }


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    ap.add_argument("--paper", help="JSON file with paper-claimed values")
    ap.add_argument("--repro", help="JSON file with reproduced values")
    ap.add_argument("--pair", action="append", default=[],
                    help="inline pair model:dataset:metric:paper:repro (repeatable)")
    ap.add_argument("--tolerance", type=float, default=0.01, help="relative-error tolerance (default 0.01)")
    ap.add_argument("--abs-tolerance", type=float, help="use absolute-error tolerance instead of --tolerance")
    ap.add_argument("--direction", choices=("higher", "lower", "neutral"), default="neutral", help="metric direction for descriptive change labels; does not alter tolerance verdict")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--artifact-out", help="write a versioned reproduction-card JSON artifact")
    ap.add_argument("--repository-commit", help="exact reproduced repository commit (required for artifact)")
    ap.add_argument("--environment-json", help="environment JSON object or path (required for artifact)")
    ap.add_argument("--force", action="store_true", help="replace an existing --artifact-out file")
    ap.add_argument("--bootstrap-ci", type=float,
                    help="emit bootstrap CI at this level for multi-run repro means (e.g. 0.95); requires --seed")
    ap.add_argument("--seed", type=int, help="RNG seed for deterministic bootstrap")
    ap.add_argument("--uncertainty", action="store_true",
                    help="enable uncertainty-aware verdicts (CI overlap / Welch t-test)")
    args = ap.parse_args(argv[1:])

    paper_rows = load(args.paper) if args.paper else []
    repro_rows = load(args.repro) if args.repro else []
    for spec in args.pair:
        model, dataset, metric, pv, rv = parse_pair(spec)
        row = {"model": model, "dataset": dataset, "metric": metric}
        if pv is not None:
            paper_rows.append({**row, "value": pv, "source": "inline --pair"})
        if rv is not None:
            repro_rows.append({**row, "value": rv, "source": "inline --pair"})
    if not paper_rows and not repro_rows:
        ap.error("provide --paper/--repro files or at least one --pair")

    if args.tolerance < 0 or args.abs_tolerance is not None and args.abs_tolerance < 0:
        ap.error("tolerances must be non-negative")
    if args.bootstrap_ci is not None:
        if args.seed is None:
            ap.error("--bootstrap-ci requires --seed for deterministic output")
        if not (0.0 < args.bootstrap_ci < 1.0):
            ap.error("--bootstrap-ci must be between 0 and 1 (exclusive)")
    rows = build_rows(paper_rows, repro_rows, args.tolerance, args.abs_tolerance, args.direction,
                      bootstrap_ci_level=args.bootstrap_ci, seed=args.seed,
                      uncertainty=args.uncertainty)
    if args.artifact_out:
        artifact = reproduction_artifact(args, rows)
        if os.path.exists(args.artifact_out) and not args.force:
            raise SystemExit(f"error: artifact output exists: {args.artifact_out}; use --force to replace it")
        with open(args.artifact_out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(artifact, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    # Windows consoles may default to GBK; force UTF-8 for box drawing etc.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.format == "json":
        print(json.dumps({"tolerance": args.abs_tolerance if args.abs_tolerance is not None else args.tolerance,
                          "tolerance_kind": "absolute" if args.abs_tolerance is not None else "relative",
                          "direction": args.direction, "rows": rows},
                         indent=2, ensure_ascii=False))
    else:
        print(to_markdown(rows, args.tolerance, args.abs_tolerance))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
