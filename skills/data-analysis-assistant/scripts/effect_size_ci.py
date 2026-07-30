#!/usr/bin/env python3
"""Bootstrap confidence intervals for effect sizes used by stat_test.py.

Resampling is row-wise and is therefore unsuitable for clustered, paired, or serially
dependent data unless rows are already the scientific resampling unit.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone


VERSION = "0.1.0"
MISSING = {"", "na", "n/a", "nan", "null", "none", "-"}


def rows(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str, column: str) -> float:
    if value.strip().lower() in MISSING:
        raise ValueError(f"missing numeric value in {column}")
    return float(value)


def d_independent(data, value, group):
    groups = {}
    for row in data:
        groups.setdefault(row[group], []).append(number(row[value], value))
    if len(groups) != 2:
        raise ValueError("Cohen's d requires exactly two complete groups")
    a, b = groups.values()
    if len(a) < 2 or len(b) < 2:
        raise ValueError("Cohen's d requires at least two observations per group")
    import numpy as np
    pooled = np.sqrt(((len(a)-1)*np.var(a, ddof=1)+(len(b)-1)*np.var(b, ddof=1))/(len(a)+len(b)-2))
    return 0.0 if pooled == 0 else float((np.mean(a)-np.mean(b))/pooled)


def rank_biserial(data, value, group):
    from scipy.stats import mannwhitneyu
    groups = {}
    for row in data:
        groups.setdefault(row[group], []).append(number(row[value], value))
    if len(groups) != 2:
        raise ValueError("rank-biserial r requires exactly two complete groups")
    a, b = groups.values()
    if not a or not b:
        raise ValueError("rank-biserial r requires observations in both groups")
    return float(1 - 2 * mannwhitneyu(a, b, alternative="two-sided").statistic / (len(a) * len(b)))


def eta_squared(data, value, group):
    import numpy as np
    groups = {}
    for row in data:
        groups.setdefault(row[group], []).append(number(row[value], value))
    if len(groups) < 2:
        raise ValueError("eta squared requires at least two complete groups")
    all_values = np.array([item for values in groups.values() for item in values])
    total = float(((all_values - all_values.mean()) ** 2).sum())
    return 0.0 if total == 0 else float(sum(len(v) * (np.mean(v) - all_values.mean()) ** 2 for v in groups.values()) / total)


def correlation(data, x, y, method):
    from scipy.stats import pearsonr, spearmanr
    xv, yv = [number(row[x], x) for row in data], [number(row[y], y) for row in data]
    value = float((pearsonr if method == "pearson" else spearmanr)(xv, yv).statistic)
    if not math.isfinite(value):
        raise ValueError("correlation is undefined for a constant bootstrap sample")
    return value


def cramers_v(data, col1, col2):
    import numpy as np
    from scipy.stats import chi2_contingency
    left, right = sorted({row[col1] for row in data}), sorted({row[col2] for row in data})
    if len(left) < 2 or len(right) < 2:
        raise ValueError("Cramer's V requires at least two levels in each column")
    table = np.zeros((len(left), len(right)), dtype=int)
    for row in data:
        table[left.index(row[col1]), right.index(row[col2])] += 1
    statistic = chi2_contingency(table).statistic
    return float((statistic / (table.sum() * (min(table.shape) - 1))) ** 0.5)


def complete_data(all_rows, args):
    required = [args.value, args.group] if args.metric in {"cohens-d", "rank-biserial", "eta-squared"} else [args.x, args.y] if args.metric in {"pearson", "spearman"} else [args.col1, args.col2]
    if any(not column for column in required):
        raise ValueError(f"{args.metric} requires its documented column options")
    if any(column not in all_rows[0] for column in required):
        raise ValueError("one or more requested columns are not present")
    return [row for row in all_rows if all(row[column].strip().lower() not in MISSING for column in required)]


def measure(data, args):
    if args.metric == "cohens-d": return d_independent(data, args.value, args.group)
    if args.metric == "rank-biserial": return rank_biserial(data, args.value, args.group)
    if args.metric == "eta-squared": return eta_squared(data, args.value, args.group)
    if args.metric in {"pearson", "spearman"}: return correlation(data, args.x, args.y, args.metric)
    return cramers_v(data, args.col1, args.col2)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", help="CSV input")
    parser.add_argument("--metric", required=True, choices=["cohens-d", "rank-biserial", "eta-squared", "cramers-v", "pearson", "spearman"])
    parser.add_argument("--value"); parser.add_argument("--group")
    parser.add_argument("--x"); parser.add_argument("--y")
    parser.add_argument("--col1"); parser.add_argument("--col2")
    parser.add_argument("--reps", type=int, default=2000)
    parser.add_argument("--ci", type=float, default=.95)
    parser.add_argument("--seed", type=int, default=20260729)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)
    try:
        if args.reps < 100 or not 0 < args.ci < 1:
            raise ValueError("--reps must be at least 100 and --ci must be between 0 and 1")
        import numpy as np
        data = complete_data(rows(args.data), args)
        if len(data) < 4:
            raise ValueError("need at least four complete rows")
        point = measure(data, args)
        rng = np.random.default_rng(args.seed); values = []
        for _ in range(args.reps):
            sample = [data[i] for i in rng.integers(0, len(data), len(data))]
            try:
                estimate = measure(sample, args)
                if math.isfinite(estimate): values.append(estimate)
            except (ValueError, ZeroDivisionError): pass
        if len(values) < args.reps * .9:
            raise ValueError("too many degenerate bootstrap samples; collect more data or simplify the metric")
        low, high = np.quantile(values, [(1-args.ci)/2, 1-(1-args.ci)/2])
        artifact = {"schema_version":"1.0.0", "artifact_type":"stat-results", "provenance":{"created_by":"data-analysis-assistant/effect_size_ci.py", "created_at":datetime.now(timezone.utc).isoformat(), "tool_version":VERSION, "command":" ".join(sys.argv), "seed":args.seed, "sources":[{"kind":"file","locator":args.data}], "warnings":[]}, "alpha":1-args.ci, "results":[{"id":"effect-size", "test":f"bootstrap CI for {args.metric}", "statistic":None, "p_value":1.0, "effect_size":point, "confidence_interval":[float(low),float(high)], "adjusted_p_value":None}], "warnings":["Percentile bootstrap CI; it does not account for clustering, pairing, serial dependence, or a design-aware resampling scheme."]}
        print(json.dumps(artifact, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError, ImportError) as error:
        print(f"error: {error}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
