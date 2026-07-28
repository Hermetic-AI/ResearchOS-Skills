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
import statistics
import sys


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


def verdict(paper, repro, tol):
    if paper is None:
        return "missing_paper", None
    if repro is None:
        return "missing_repro", None
    denom = abs(paper)
    err = abs(repro - paper) / denom if denom > 0 else abs(repro - paper)
    return ("match" if err <= tol else "mismatch"), err


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


def build_rows(paper_rows, repro_rows, tol):
    paper_map = {key_of(r): r for r in paper_rows}
    repro_map = {key_of(r): r for r in repro_rows}
    rows = []
    for key in sorted(set(paper_map) | set(repro_map)):
        p, r = paper_map.get(key), repro_map.get(key)
        pv = p.get("value") if p else None
        rv, rstats = summarize_runs(r.get("value")) if r else (None, None)
        v, err = verdict(pv, rv, tol)
        rows.append(
            {
                "model": key[0],
                "dataset": key[1],
                "metric": key[2],
                "paper_value": pv,
                "repro_value": rv,
                "repro_runs": rstats,
                "rel_error": round(err, 6) if err is not None else None,
                "tolerance": tol,
                "verdict": v,
                "paper_source": (p or {}).get("source"),
                "repro_source": (r or {}).get("source"),
            }
        )
    return rows


def to_markdown(rows, tol):
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
        err = "—" if r["rel_error"] is None else f"{r['rel_error']:.2%}"
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


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paper", help="JSON file with paper-claimed values")
    ap.add_argument("--repro", help="JSON file with reproduced values")
    ap.add_argument("--pair", action="append", default=[],
                    help="inline pair model:dataset:metric:paper:repro (repeatable)")
    ap.add_argument("--tolerance", type=float, default=0.01)
    ap.add_argument("--format", choices=("md", "json"), default="md")
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

    rows = build_rows(paper_rows, repro_rows, args.tolerance)
    # Windows consoles may default to GBK; force UTF-8 for box drawing etc.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.format == "json":
        print(json.dumps({"tolerance": args.tolerance, "rows": rows},
                         indent=2, ensure_ascii=False))
    else:
        print(to_markdown(rows, args.tolerance))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
