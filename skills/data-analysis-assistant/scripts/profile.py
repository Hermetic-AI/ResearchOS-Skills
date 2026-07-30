"""CSV data profiler for research data (zero-dependency, Python stdlib only).

Purpose:
    Profile a CSV file: per-column schema inference (numeric / categorical /
    datetime / text), descriptive statistics, missing-value counts, and
    suspected-outlier flags using IQR and z-score rules. Also detects constant
    columns and duplicate rows.

Dependencies:
    None (Python 3.8+ standard library only).

CLI usage:
    python3 profile.py <file.csv> [--format json|md|both] [--delimiter ,]
                        [--encoding utf-8] [--z-threshold 3.0] [--out report.md]

Output format:
    JSON (--format json, default) or Markdown (--format md) with:
      - row_count, column_count, duplicate_rows
      - schema: [{name, dtype, null_count, null_ratio, unique_count}]
      - stats:  {column: {count, mean, std, min, p25, p50, p75, max,
                skewness, kurtosis, normality_hint}}  (numeric only)
      - outliers: [{column, rule: iqr|zscore, count, indices (first 20 row indices)}]
      - anomalies: [{kind, detail}]  (high_null_ratio | constant | dup_rows)

    skewness is the sample skewness (Fisher g1) and kurtosis the sample excess
    kurtosis (g2). normality_hint is a quick screen only:
      "approximately normal" if |g1| <= 0.5 and |g2| <= 0.5,
      "mildly skewed"      if |g1| <= 1 and |g2| <= 1,
      "insufficient n (check with Shapiro-Wilk)" when n < 20 (or n < 3),
      "non-normal (check with Shapiro-Wilk)" otherwise.
    Always confirm with stat_test.py --test shapiro before choosing a test.

    --out writes the chosen format output to a file (UTF-8) instead of/ in
    addition to stdout. Use `--out report.md --format md` for a report file.

    All percentages are ratios in [0, 1]. Row indices are 0-based data rows
    (header excluded). Exit code 0 on success, 1 on file/parse errors.
"""

import argparse
import csv
import datetime
import json
import math
import os
import sys

MISSING = {"", "na", "n/a", "nan", "null", "none", "-"}

DT_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%m/%d/%Y",
)


def try_float(s):
    try:
        v = float(s)
        return None if math.isnan(v) or math.isinf(v) else v
    except ValueError:
        return None


def is_datetime(s):
    for fmt in DT_FORMATS:
        try:
            datetime.datetime.strptime(s, fmt)
            return True
        except ValueError:
            continue
    return False


def percentile(sorted_vals, p):
    """Linear-interpolation percentile on pre-sorted values."""
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def skewness_kurtosis(nums):
    """Sample skewness (g1) and excess kurtosis (g2). Returns (None, None) if n < 3."""
    n = len(nums)
    if n < 3:
        return None, None
    mean = sum(nums) / n
    m2 = sum((x - mean) ** 2 for x in nums) / n
    if m2 == 0:
        return 0.0, 0.0
    m3 = sum((x - mean) ** 3 for x in nums) / n
    m4 = sum((x - mean) ** 4 for x in nums) / n
    g1 = m3 / m2 ** 1.5
    g2 = m4 / m2 ** 2 - 3.0
    # small-sample bias corrections
    g1 *= math.sqrt(n * (n - 1)) / (n - 2) if n > 2 else 1.0
    g2 = ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3)) if n > 3 else g2
    return g1, g2


def normality_hint(g1, g2, n):
    if g1 is None or n < 20:
        return "insufficient n (check with Shapiro-Wilk)"
    if abs(g1) <= 0.5 and abs(g2) <= 0.5:
        return "approximately normal"
    if abs(g1) <= 1.0 and abs(g2) <= 1.0:
        return "mildly skewed"
    return "non-normal (check with Shapiro-Wilk)"


def infer_dtype(values_present):
    """Infer column dtype from non-missing values."""
    if not values_present:
        return "text"
    n_num = sum(1 for v in values_present if try_float(v) is not None)
    n_dt = sum(1 for v in values_present if is_datetime(v))
    total = len(values_present)
    if n_num / total >= 0.9:
        return "numeric"
    if n_dt / total >= 0.9:
        return "datetime"
    if len(set(values_present)) <= max(20, total * 0.05):
        return "categorical"
    return "text"


def profile(path, delimiter, encoding, z_threshold):
    with open(path, newline="", encoding=encoding) as f:
        rows = list(csv.reader(f, delimiter=delimiter))
    if not rows:
        raise SystemExit("error: empty CSV file")
    header = rows[0]
    data = [r + [""] * (len(header) - len(r)) for r in rows[1:] if any(r)]

    result = {
        "file": path,
        "row_count": len(data),
        "column_count": len(header),
        "duplicate_rows": len(data) - len({tuple(r) for r in data}),
        "schema": [],
        "stats": {},
        "outliers": [],
        "anomalies": [],
    }

    for ci, name in enumerate(header):
        col = [r[ci].strip() for r in data]
        missing = [v for v in col if v.lower() in MISSING]
        present = [v for v in col if v.lower() not in MISSING]
        dtype = infer_dtype(present)
        null_ratio = len(missing) / len(col) if col else 0.0
        result["schema"].append({
            "name": name,
            "dtype": dtype,
            "null_count": len(missing),
            "null_ratio": round(null_ratio, 4),
            "unique_count": len(set(present)),
        })
        if null_ratio > 0.3:
            result["anomalies"].append({
                "kind": "high_null_ratio",
                "detail": f"column '{name}' has {null_ratio:.1%} missing values",
            })
        if len(set(present)) <= 1 and present:
            result["anomalies"].append({
                "kind": "constant",
                "detail": f"column '{name}' is constant (value: {present[0]!r})",
            })
        if dtype != "numeric":
            continue
        nums = []
        idx_map = []
        for ri, v in enumerate(col):
            fv = try_float(v) if v.lower() not in MISSING else None
            if fv is not None:
                nums.append(fv)
                idx_map.append(ri)
        nums_sorted = sorted(nums)
        n = len(nums)
        mean = sum(nums) / n
        std = math.sqrt(sum((x - mean) ** 2 for x in nums) / (n - 1)) if n > 1 else 0.0
        q1, med, q3 = (percentile(nums_sorted, p) for p in (0.25, 0.5, 0.75))
        g1, g2 = skewness_kurtosis(nums)
        result["stats"][name] = {
            "count": n, "mean": round(mean, 6), "std": round(std, 6),
            "min": nums_sorted[0], "p25": q1, "p50": med, "p75": q3,
            "max": nums_sorted[-1],
            "skewness": round(g1, 4) if g1 is not None else None,
            "kurtosis": round(g2, 4) if g2 is not None else None,
            "normality_hint": normality_hint(g1, g2, n),
        }
        # IQR rule: outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        iqr_hits = [idx_map[i] for i, x in enumerate(nums) if x < lo or x > hi]
        if iqr_hits:
            result["outliers"].append({
                "column": name, "rule": "iqr", "count": len(iqr_hits),
                "bounds": [lo, hi], "indices": iqr_hits[:20],
            })
        # z-score rule: |z| > threshold
        if std > 0:
            z_hits = [idx_map[i] for i, x in enumerate(nums)
                      if abs((x - mean) / std) > z_threshold]
            if z_hits:
                result["outliers"].append({
                    "column": name, "rule": "zscore", "count": len(z_hits),
                    "threshold": z_threshold, "indices": z_hits[:20],
                })

    if result["duplicate_rows"]:
        result["anomalies"].append({
            "kind": "dup_rows",
            "detail": f"{result['duplicate_rows']} fully duplicated data rows",
        })
    return result


def to_markdown(r):
    lines = [f"# Data Profile: `{r['file']}`", "",
             f"- Rows: {r['row_count']} | Columns: {r['column_count']} | "
             f"Duplicate rows: {r['duplicate_rows']}", "",
             "## Schema", "",
             "| Column | Type | Missing | Null ratio | Unique |",
             "|---|---|---|---|---|"]
    for c in r["schema"]:
        lines.append(f"| {c['name']} | {c['dtype']} | {c['null_count']} "
                     f"| {c['null_ratio']:.1%} | {c['unique_count']} |")
    if r["stats"]:
        lines += ["", "## Descriptive statistics (numeric)", "",
                  "| Column | n | Mean | Std | Min | P25 | P50 | P75 | Max | Skew | Kurtosis | Normality hint |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, s in r["stats"].items():
            skew = f"{s['skewness']:.3g}" if s["skewness"] is not None else "n/a"
            kurt = f"{s['kurtosis']:.3g}" if s["kurtosis"] is not None else "n/a"
            lines.append(f"| {name} | {s['count']} | {s['mean']:.4g} | {s['std']:.4g} "
                         f"| {s['min']:.4g} | {s['p25']:.4g} | {s['p50']:.4g} "
                         f"| {s['p75']:.4g} | {s['max']:.4g} | {skew} | {kurt} "
                         f"| {s['normality_hint']} |")
    if r["outliers"]:
        lines += ["", "## Suspected outliers", ""]
        for o in r["outliers"]:
            lines.append(f"- `{o['column']}` ({o['rule']}): {o['count']} value(s), "
                         f"row indices {o['indices']}")
    if r["anomalies"]:
        lines += ["", "## Anomalies / cleaning hints", ""]
        for a in r["anomalies"]:
            lines.append(f"- [{a['kind']}] {a['detail']}")
    return "\n".join(lines)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Profile a CSV file (stdlib only).")
    ap.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    ap.add_argument("file")
    ap.add_argument("--format", choices=["json", "md", "both"], default="json")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--encoding", default="utf-8")
    ap.add_argument("--z-threshold", type=float, default=3.0)
    ap.add_argument("--out", help="also write output to this file (UTF-8); "
                                "with --format both, writes both blocks")
    ap.add_argument("--force", action="store_true", help="replace an existing --out file")
    args = ap.parse_args(argv)
    if args.out:
        if os.path.abspath(args.out) == os.path.abspath(args.file):
            raise SystemExit("error: --out must not replace the input CSV")
        if os.path.exists(args.out) and not args.force:
            raise SystemExit(f"error: output exists: {args.out}; use --force to replace it")
    r = profile(args.file, args.delimiter, args.encoding, args.z_threshold)
    blocks = []
    if args.format in ("json", "both"):
        blocks.append(json.dumps(r, ensure_ascii=False, indent=2))
    if args.format in ("md", "both"):
        blocks.append(to_markdown(r))
    text = "\n\n---\n\n".join(blocks)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        sys.stderr.write(f"written: {args.out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
