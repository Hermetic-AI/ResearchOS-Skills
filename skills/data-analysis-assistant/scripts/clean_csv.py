"""Declarative CSV cleaner for research data (zero-dependency, Python stdlib only).

Purpose:
    Apply an explicit, re-runnable list of cleaning rules to a CSV file and
    emit (1) a cleaned CSV and (2) a cleaning log recording every step with
    the number of rows/values affected and the stated reason — the log is
    meant to be quoted in the paper's Methods section. The raw file is never
    modified.

Dependencies:
    None (Python 3.8+ standard library only).

CLI usage:
    python3 clean_csv.py <input.csv> <rules.json> --out cleaned.csv
                        [--log cleaning_log.md] [--log-format md|json]
                        [--delimiter ,] [--encoding utf-8]

Rules file format (JSON):
    {"steps": [
      {"op": "dedupe", "columns": ["id"], "keep": "first",
       "reason": "re-export artifact"},
      {"op": "fill_missing", "column": "age", "strategy": "median",
       "reason": "MAR, 3% missing"},
      {"op": "drop_outliers", "column": "reaction_ms", "rule": "iqr",
       "reason": "pre-registered 1.5*IQR rule"},
      {"op": "convert_type", "column": "age", "type": "float",
       "on_error": "missing", "reason": "mixed encodings"}
    ]}

    Operations (applied in order):
      dedupe         remove duplicate rows. "columns" optional (default: all
                     columns = exact duplicates); "keep": "first" (default) or
                     "last" (keeps the last occurrence; original row order is
                     preserved).
      fill_missing   fill missing values in one column. strategy:
                     "mean"|"median"|"mode" (numeric stats ignore missing) or
                     "value" with "value": <string>.
      drop_outliers  drop rows where a numeric column is outside the rule:
                     "iqr" ([Q1-1.5*IQR, Q3+1.5*IQR]) or "zscore" (|z| > "z",
                     default z = 3.0).
      convert_type   cast a column: "float"|"int"|"str". on_error:
                     "missing" (bad values -> empty, default) or "drop_row".

    Every step SHOULD carry a "reason" string; it is copied into the log.
    See references/data-cleaning.md for when each operation is appropriate.

Output format:
    Cleaned CSV written to --out. Log (default: Markdown to stdout; --log
    writes a file, --log-format json switches to JSON) contains, per step:
    step index, op, column(s), reason, rows_before, rows_after,
    rows_affected, values_affected (for fill/convert), and a one-line
    citable summary. Exit code 0 on success, 1 on file/rule errors.
"""

import argparse
import csv
import json
import os
import sys

MISSING = {"", "na", "n/a", "nan", "null", "none", "-"}


def is_missing(v):
    return v.strip().lower() in MISSING


def percentile(sorted_vals, p):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def numeric_values(rows, ci):
    return [float(r[ci]) for r in rows if ci < len(r) and not is_missing(r[ci])
            and _is_float(r[ci])]


def _is_float(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


def col_index(header, name):
    if name not in header:
        raise SystemExit(f"error: column '{name}' not found. Available: {header}")
    return header.index(name)


def op_dedupe(header, rows, step):
    cols = step.get("columns")
    idxs = [col_index(header, c) for c in cols] if cols else list(range(len(header)))
    keep = step.get("keep", "first")
    if keep not in ("first", "last"):
        raise SystemExit(f"error: dedupe \"keep\" must be 'first' or 'last', got '{keep}'")
    seen, kept = set(), []
    for r in (rows if keep == "first" else reversed(rows)):
        key = tuple(r[i] if i < len(r) else "" for i in idxs)
        if key in seen:
            continue
        seen.add(key)
        kept.append(r)
    if keep == "last":
        kept.reverse()
    return kept, {"rows_affected": len(rows) - len(kept)}


def op_fill_missing(header, rows, step):
    ci = col_index(header, step["column"])
    strategy = step.get("strategy", "value")
    if strategy == "value":
        if "value" not in step:
            raise SystemExit("error: fill_missing with strategy 'value' requires \"value\"")
        fill = str(step["value"])
    else:
        vals = numeric_values(rows, ci)
        strs = [r[ci].strip() for r in rows if ci < len(r) and not is_missing(r[ci])]
        if strategy == "mean":
            if not vals:
                raise SystemExit(f"error: no numeric values in '{step['column']}' for mean")
            fill = f"{sum(vals) / len(vals):.6g}"
        elif strategy == "median":
            if not vals:
                raise SystemExit(f"error: no numeric values in '{step['column']}' for median")
            fill = f"{percentile(sorted(vals), 0.5):.6g}"
        elif strategy == "mode":
            if not strs:
                raise SystemExit(f"error: no values in '{step['column']}' for mode")
            fill = max(set(strs), key=strs.count)
        else:
            raise SystemExit(f"error: unknown fill strategy '{strategy}'")
    n = 0
    for r in rows:
        if ci >= len(r):
            r.extend([""] * (ci + 1 - len(r)))
        if is_missing(r[ci]):
            r[ci] = fill
            n += 1
    return rows, {"values_affected": n, "fill_value": fill, "rows_affected": 0}


def op_drop_outliers(header, rows, step):
    ci = col_index(header, step["column"])
    rule = step.get("rule", "iqr")
    vals = numeric_values(rows, ci)
    if len(vals) < 4:
        raise SystemExit(f"error: not enough numeric values in '{step['column']}' for outlier rule")
    if rule == "iqr":
        sv = sorted(vals)
        q1, q3 = percentile(sv, 0.25), percentile(sv, 0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        detail = f"IQR bounds [{lo:.6g}, {hi:.6g}]"
    elif rule == "zscore":
        z = float(step.get("z", 3.0))
        mean = sum(vals) / len(vals)
        sd = (sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5
        if sd == 0:
            return rows, {"rows_affected": 0, "detail": "std = 0, nothing dropped"}
        lo, hi = mean - z * sd, mean + z * sd
        detail = f"z-score |z| > {z} (bounds [{lo:.6g}, {hi:.6g}])"
    else:
        raise SystemExit(f"error: unknown outlier rule '{rule}'")
    kept = [r for r in rows
            if ci >= len(r) or is_missing(r[ci]) or not _is_float(r[ci])
            or lo <= float(r[ci]) <= hi]
    return kept, {"rows_affected": len(rows) - len(kept), "detail": detail}


def op_convert_type(header, rows, step):
    ci = col_index(header, step["column"])
    ctype = step.get("type", "float")
    on_error = step.get("on_error", "missing")
    if on_error not in ("missing", "drop_row"):
        raise SystemExit(f"error: on_error must be 'missing' or 'drop_row', got '{on_error}'")
    n_ok = n_bad = 0
    kept = []
    for r in rows:
        if ci >= len(r) or is_missing(r[ci]):
            kept.append(r)
            continue
        v = r[ci].strip()
        try:
            if ctype == "float":
                r[ci] = f"{float(v):.6g}"
            elif ctype == "int":
                r[ci] = str(int(float(v)))
            elif ctype == "str":
                r[ci] = v
            else:
                raise SystemExit(f"error: unknown type '{ctype}'")
            n_ok += 1
            kept.append(r)
        except ValueError:
            n_bad += 1
            if on_error == "missing":
                r[ci] = ""
                kept.append(r)
    return kept, {"values_affected": n_ok, "invalid_values": n_bad,
                  "rows_affected": n_bad if on_error == "drop_row" else 0}


OPS = {
    "dedupe": op_dedupe,
    "fill_missing": op_fill_missing,
    "drop_outliers": op_drop_outliers,
    "convert_type": op_convert_type,
}


def clean(header, rows, steps):
    log = []
    for i, step in enumerate(steps, 1):
        op = step.get("op")
        if op not in OPS:
            raise SystemExit(f"error: step {i}: unknown op '{op}'. Available: {sorted(OPS)}")
        before = len(rows)
        rows, info = OPS[op](header, rows, step)
        entry = {
            "step": i,
            "op": op,
            "columns": step.get("columns") or ([step["column"]] if "column" in step else []),
            "reason": step.get("reason", "(no reason given)"),
            "rows_before": before,
            "rows_after": len(rows),
            **info,
        }
        changed = entry.get("rows_affected", 0) or entry.get("values_affected", 0)
        entry["summary"] = (f"Step {i} ({op} on {', '.join(entry['columns']) or 'all columns'}): "
                            f"{changed} rows/values affected; {entry['reason']}")
        log.append(entry)
    return rows, log


def log_to_markdown(log, input_path, out_path, n_before, n_after):
    lines = ["# Data Cleaning Log", "",
             f"- Input: `{input_path}` ({n_before} data rows)",
             f"- Output: `{out_path}` ({n_after} data rows)",
             f"- Rows removed overall: {n_before - n_after}", "",
             "| Step | Op | Column(s) | Rows before | Rows after | Rows affected | Values affected | Reason |",
             "|---|---|---|---|---|---|---|---|"]
    for e in log:
        lines.append(f"| {e['step']} | {e['op']} | {', '.join(e['columns']) or '(all)'} "
                     f"| {e['rows_before']} | {e['rows_after']} "
                     f"| {e.get('rows_affected', 0)} | {e.get('values_affected', '-')} "
                     f"| {e['reason']} |")
    lines += ["", "## Citable summary", ""]
    lines += [f"- {e['summary']}" for e in log]
    lines += ["", "在论文方法部分可引用本日志：初始 n → 各步剔除/修正及理由 → 最终 n。"]
    return "\n".join(lines)


def ensure_output_path(path, protected, force=False):
    """Reject raw-input aliases and accidental replacement of derived files."""
    resolved = os.path.abspath(path)
    if resolved in {os.path.abspath(item) for item in protected}:
        raise SystemExit(f"error: output path must not replace an input file: {path}")
    if os.path.exists(resolved) and not force:
        raise SystemExit(f"error: output exists: {path}; use --force to replace a derived artifact")


def cleaning_artifact(args, log):
    warnings = [f"step {entry['step']} has no explicit rationale"
                for entry in log if entry["reason"] == "(no reason given)"]
    return {
        "schema_version": "1.0.0",
        "artifact_type": "cleaning-manifest",
        "provenance": {
            "created_by": "data-analysis-assistant/clean_csv.py",
            "tool_version": "0.1.0",
            "command": " ".join(sys.argv),
            "seed": None,
            "sources": [
                {"kind": "file", "locator": os.path.abspath(args.file)},
                {"kind": "file", "locator": os.path.abspath(args.rules)},
            ],
            "warnings": warnings,
        },
        "input": {"kind": "file", "locator": os.path.abspath(args.file)},
        "output": {"kind": "file", "locator": os.path.abspath(args.out)},
        "steps": [{
            "action": entry["op"],
            "rationale": entry["reason"],
            "affected": int(entry.get("rows_affected", 0) or entry.get("values_affected", 0)),
            "columns": entry["columns"],
            "rows_before": entry["rows_before"],
            "rows_after": entry["rows_after"],
        } for entry in log],
    }


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Apply declarative cleaning rules to a CSV (stdlib only).")
    ap.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    ap.add_argument("file", help="input CSV (never modified)")
    ap.add_argument("rules", help="JSON rules file ({\"steps\": [...]})")
    ap.add_argument("--out", required=True, help="cleaned CSV output path")
    ap.add_argument("--log", help="cleaning log output path (default: stdout)")
    ap.add_argument("--log-format", choices=["md", "json"], default="md")
    ap.add_argument("--artifact-out", help="write a versioned cleaning-manifest JSON artifact")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs (never raw input)")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--encoding", default="utf-8")
    args = ap.parse_args(argv)

    protected = [args.file, args.rules]
    outputs = [args.out] + ([args.log] if args.log else []) + ([args.artifact_out] if args.artifact_out else [])
    if len({os.path.abspath(path) for path in outputs}) != len(outputs):
        raise SystemExit("error: --out, --log, and --artifact-out must be different files")
    for path in outputs:
        ensure_output_path(path, protected, args.force)

    with open(args.file, newline="", encoding=args.encoding) as f:
        rows = list(csv.reader(f, delimiter=args.delimiter))
    if len(rows) < 2:
        raise SystemExit("error: CSV needs a header row and at least one data row")
    header, data = rows[0], rows[1:]
    with open(args.rules, encoding="utf-8") as f:
        spec = json.load(f)
    steps = spec.get("steps")
    if not isinstance(steps, list) or not steps:
        raise SystemExit("error: rules file must contain a non-empty \"steps\" list")

    cleaned, log = clean(header, [list(r) for r in data], steps)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=args.delimiter)
        w.writerow(header)
        w.writerows(cleaned)

    text = (json.dumps({"input": args.file, "output": args.out,
                        "rows_before": len(data), "rows_after": len(cleaned),
                        "steps": log}, ensure_ascii=False, indent=2)
            if args.log_format == "json"
            else log_to_markdown(log, args.file, args.out, len(data), len(cleaned)))
    if args.log:
        with open(args.log, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        sys.stderr.write(f"written: {args.out} ({len(cleaned)} rows), log: {args.log}\n")
    else:
        print(text)
    if args.artifact_out:
        with open(args.artifact_out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cleaning_artifact(args, log), f, ensure_ascii=False, indent=2)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
