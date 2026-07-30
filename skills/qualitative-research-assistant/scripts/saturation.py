#!/usr/bin/env python3
"""Track team saturation curves and compute Krippendorff's alpha (stdlib only).

Purpose:
    A zero-dependency helper for the analytic phase of qualitative research. It
    (1) tracks new-code accumulation across coders and analytic rounds, computes
    a cumulative saturation curve, and reports when the new-code rate drops
    below a pre-specified threshold (descriptive only — it never declares
    saturation), and (2) computes Krippendorff's alpha for nominal, ordinal,
    interval, or ratio data across multiple coders and units, handling missing
    values and chance-corrected agreement. It does not replace human judgment,
    reflexivity, or an audit trail.

Dependencies:
    None (Python 3.8+ standard library only).

CLI usage:
    # Saturation curve from a coding log.
    python3 saturation.py --mode saturation --log coding-log.json --rounds 3 \\
        --threshold 0.05 --out saturation.json

    # Krippendorff's alpha from a units x coders matrix.
    python3 saturation.py --mode alpha --data data.json --level nominal --out alpha.json

    Common options: --force  --version

Coding-log format (for --mode saturation):
    {"entries": [
      {"source_id": "i1", "round": 1, "coder": "A", "code": "theme-x"},
      ...
    ]}

Alpha data format (for --mode alpha):
    {"units": ["u1", "u2", ...],
     "coders": ["A", "B", ...],
     "values": {"A": {"u1": "red", "u2": "blue", ...},
                 "B": {"u1": "red", "u2": "green", ...}}}
    Missing values should be omitted from the inner dicts.

Output format:
    --mode saturation -> saturation.json with per-round new-code counts, rates,
                         cumulative curve, and a descriptive threshold flag.
    --mode alpha      -> alpha.json with alpha, coincidence matrices, and Do/De.
    Every JSON artifact carries schema_version, artifact_type, tool_version,
    and warnings. Exit code 0 on success, 1 on bad input.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

VERSION = "0.1.0"

# --- Saturation curve --------------------------------------------------------

def saturation_curve(entries, rounds=None, threshold=0.05):
    if not isinstance(entries, list) or not entries:
        raise ValueError("entries must be a non-empty list")
    for n, row in enumerate(entries, 1):
        if not isinstance(row, dict) or "code" not in row:
            raise ValueError(f"entry {n} needs at least a 'code'")

    # Determine round ordering: explicit round field, else source order.
    has_rounds = all(isinstance(row.get("round"), int) for row in entries)
    if has_rounds:
        round_ids = sorted({row["round"] for row in entries})
        if rounds is not None:
            round_ids = [r for r in round_ids if r in set(rounds)] if isinstance(rounds, list) else round_ids
        def round_of(row):
            return row["round"]
    else:
        source_order = []
        seen = set()
        for row in entries:
            src = row.get("source_id")
            if src not in seen:
                seen.add(src)
                source_order.append(src)
        round_ids = list(range(1, len(source_order) + 1))
        source_to_round = {src: i + 1 for i, src in enumerate(source_order)}
        def round_of(row):
            return source_to_round.get(row.get("source_id"), len(round_ids))

    by_round = {r: [] for r in round_ids}
    for row in entries:
        r = round_of(row)
        if r in by_round:
            by_round[r].append(row["code"])

    seen = set()
    curve = []
    total_new = 0
    below_threshold_from = None
    for r in round_ids:
        codes = [c for c in by_round[r] if isinstance(c, str) and c.strip()]
        new = sorted(set(codes) - seen)
        seen.update(codes)
        total_new += len(new)
        rate = len(new) / max(1, len(codes)) if codes else 0.0
        if rate < threshold and below_threshold_from is None and len(curve) > 0:
            below_threshold_from = r
        curve.append({
            "round": r,
            "entries_in_round": len(codes),
            "new_codes": new,
            "new_code_count": len(new),
            "new_code_rate": rate,
            "cumulative_codes": len(seen),
        })

    return {
        "rounds": round_ids,
        "threshold": threshold,
        "curve": curve,
        "total_codes": len(seen),
        "below_threshold_from_round": below_threshold_from,
    }


# --- Krippendorff's alpha ----------------------------------------------------

_NOMINAL = lambda a, b: 0.0 if a == b else 1.0
_ORDINAL = lambda a, b, n: ((a - b) / max(1, n - 1)) ** 2
_INTERVAL = lambda a, b: (a - b) ** 2
_RATIO = lambda a, b: ((a - b) / (a + b)) ** 2 if (a + b) != 0 else 0.0


def krippendorff_alpha(values, coders, units, level="nominal"):
    """Compute Krippendorff's alpha for the given coincidence data.

    values: {coder: {unit: value}}; missing pairs are simply absent.
    """
    if level not in {"nominal", "ordinal", "interval", "ratio"}:
        raise ValueError("level must be nominal|ordinal|interval|ratio")

    # Collect all observed categories for ordinal ranking.
    all_categories = set()
    for coder in coders:
        for unit in units:
            if unit in values.get(coder, {}):
                all_categories.add(values[coder][unit])

    if level == "ordinal":
        ordered = sorted(all_categories)
        rank = {cat: i for i, cat in enumerate(ordered)}
        n_cat = len(ordered)

    def _ratio_distance(a, b):
        return ((a - b) / (a + b)) ** 2 if (a + b) != 0 else 0.0

    def distance(a, b):
        if level == "nominal":
            return _NOMINAL(a, b)
        if level == "ordinal":
            return _ORDINAL(rank[a], rank[b], n_cat)
        if level == "interval":
            return _INTERVAL(float(a), float(b))
        return _ratio_distance(float(a), float(b))

    # Build coincidence matrix over observed pairs within each unit.
    categories = sorted(all_categories)
    cat_index = {cat: i for i, cat in enumerate(categories)}
    m = len(categories)
    coincidence = [[0.0] * m for _ in range(m)]
    total_pairs = 0.0

    for unit in units:
        unit_coders = [c for c in coders if unit in values.get(c, {})]
        n_coders = len(unit_coders)
        if n_coders < 2:
            continue
        # Number of pairable values for this unit.
        et = n_coders * (n_coders - 1)
        for i in range(n_coders):
            for j in range(n_coders):
                if i == j:
                    continue
                ci, cj = unit_coders[i], unit_coders[j]
                vi, vj = values[ci][unit], values[cj][unit]
                weight = 1.0 / (n_coders - 1)
                coincidence[cat_index[vi]][cat_index[vj]] += weight
                total_pairs += weight

    if total_pairs == 0:
        raise ValueError("no pairable values across coders; check for missing overlap")

    # Observed disagreement Do.
    do = 0.0
    for i in range(m):
        for j in range(m):
            if coincidence[i][j] == 0:
                continue
            do += coincidence[i][j] * distance(categories[i], categories[j])
    do /= total_pairs

    # Expected disagreement De from category marginals.
    marginals = [sum(coincidence[i][j] for j in range(m)) for i in range(m)]
    de = 0.0
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            de += marginals[i] * marginals[j] * distance(categories[i], categories[j])
    de /= (total_pairs * (total_pairs - 1)) if total_pairs > 1 else 1.0

    alpha = 1.0 - do / de if de > 0 else 1.0
    return {
        "alpha": alpha,
        "observed_disagreement": do,
        "expected_disagreement": de,
        "categories": categories,
        "n_units": len(units),
        "n_coders": len(coders),
        "level": level,
    }


# --- I/O helpers -------------------------------------------------------------

def ensure_output_path(path, protected, force=False):
    resolved = os.path.abspath(path)
    if resolved in {os.path.abspath(item) for item in protected}:
        raise SystemExit(f"error: output path must not replace an input file: {path}")
    if os.path.exists(resolved) and not force:
        raise SystemExit(f"error: output exists: {path}; use --force to replace a derived artifact")


def write_json(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --- Main --------------------------------------------------------------------

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    ap.add_argument("--mode", choices=["saturation", "alpha"], required=True)
    ap.add_argument("--log", help="coding-log.json (for --mode saturation)")
    ap.add_argument("--data", help="data.json (for --mode alpha)")
    ap.add_argument("--rounds", help="comma-separated round ids to include (saturation)")
    ap.add_argument("--threshold", type=float, default=0.05, help="new-code rate threshold")
    ap.add_argument("--level", choices=["nominal", "ordinal", "interval", "ratio"],
                    default="nominal", help="Krippendorff alpha metric level")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs")
    args = ap.parse_args(argv)

    try:
        if args.mode == "saturation":
            if not args.log:
                raise ValueError("--log is required for --mode saturation")
            source = Path(args.log).resolve(strict=True)
            payload = json.loads(source.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("entries"), list):
                entries = payload["entries"]
            elif isinstance(payload, list):
                entries = payload
            else:
                entries = None
            if not isinstance(entries, list):
                raise ValueError("log must be a list or an object with an 'entries' list")
            rounds = [int(r) for r in args.rounds.split(",") if r.strip()] if args.rounds else None
            result = saturation_curve(entries, rounds=rounds, threshold=args.threshold)
            ensure_output_path(args.out, [str(source)], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "qualitative-saturation-curve",
                "tool_version": VERSION,
                "source": str(source),
                **result,
                "warnings": [
                    "Descriptive curve only: a new-code rate below threshold does not establish saturation.",
                    "Assess information power, sampling, negative cases, code granularity, and reflexivity with the research team.",
                ],
            }
            write_json(args.out, artifact)
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

        # alpha
        if not args.data:
            raise ValueError("--data is required for --mode alpha")
        source = Path(args.data).resolve(strict=True)
        payload = json.loads(source.read_text(encoding="utf-8"))
        units = payload.get("units")
        coders = payload.get("coders")
        values = payload.get("values")
        if not (isinstance(units, list) and isinstance(coders, list) and isinstance(values, dict)):
            raise ValueError("alpha data needs 'units', 'coders', and 'values' fields")
        result = krippendorff_alpha(values, coders, units, level=args.level)
        ensure_output_path(args.out, [str(source)], args.force)
        artifact = {
            "schema_version": "1.0.0",
            "artifact_type": "krippendorff-alpha",
            "tool_version": VERSION,
            "source": str(source),
            **result,
            "warnings": [
                "Alpha measures coder agreement under its metric assumptions; it does not establish validity, interpretation quality, or saturation.",
            ],
        }
        write_json(args.out, artifact)
        print(json.dumps(artifact, ensure_ascii=False, indent=2))
        return 0

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
