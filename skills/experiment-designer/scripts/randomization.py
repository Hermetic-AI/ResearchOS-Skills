"""Reproducible randomization / allocation schedules for experiments.

Randomization licenses causal inference, but the *method* matters (complete
vs. blocked) and the schedule must be reproducible (seeded) and auditable.
This script produces unit -> arm allocation tables with a fixed seed so the
exact schedule can be regenerated, archived, and pre-registered.

Dependencies: none (Python 3.8+ standard library only).

CLI usage:
    # Complete (simple) randomization: independent draw per unit
    python randomization.py complete --n 60 --arms treatment,control --seed 42

    # Permuted-block randomization: balance maintained throughout enrollment
    python randomization.py block --n 60 --arms drug,placebo --ratio 2:1 \
        --block-size 6 --seed 42

    # Stratified randomization: independent balanced assignment WITHIN each
    # stratum of a covariate (sex, site, baseline severity), so every arm
    # stays balanced per stratum — not just overall
    python randomization.py stratified --strata male:30,female:30 \
        --arms treatment,control --seed 42
    python randomization.py stratified --units units.csv \
        --arms treatment,control --seed 42
    #   units.csv: columns unit_id,stratum (stratum column name via --stratum-col)

    # Common options:
    #   --format csv|json   output format (default csv)
    #   --out FILE          write to file instead of stdout
    #   --seed INT          fix the seed for reproducibility (default 0)

Output:
    CSV or JSON table with columns: unit_id, [block_id], arm.
    A JSON metadata header (method, arms, ratio, seed) is printed to stderr
    so the table itself stays machine-clean.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import random
import sys


def parse_ratio(arms, ratio_str):
    """Turn '2:1' into per-arm integer counts; default 1:1:..."""
    if ratio_str is None:
        return [1] * len(arms)
    parts = [int(p) for p in ratio_str.split(":")]
    if len(parts) != len(arms):
        raise SystemExit(f"ratio '{ratio_str}' must have one entry per arm ({len(arms)})")
    if any(p <= 0 for p in parts):
        raise SystemExit("ratio entries must be positive integers")
    return parts


def complete_randomization(n, arms, ratio, seed):
    """Independent random assignment per unit (like weighted coin flips).

    Simplest method; with small n it can yield noticeable arm-size imbalance.
    Fine for large n; prefer block randomization for n < ~100 or sequential
    enrollment.
    """
    rng = random.Random(seed)
    weights = [float(r) for r in ratio]
    return [{"unit_id": i + 1, "arm": rng.choices(arms, weights=weights)[0]}
            for i in range(n)]


def block_randomization(n, arms, ratio, block_size, seed):
    """Permuted-block randomization: every arm appears in the given ratio
    within each block; order inside a block is shuffled. Guarantees balance
    throughout enrollment. block_size must be a multiple of sum(ratio).
    """
    template = [arm for arm, r in zip(arms, ratio) for _ in range(r)]
    unit = len(template)
    if block_size is None:
        block_size = unit * 2
    if block_size % unit != 0:
        raise SystemExit(
            f"block_size ({block_size}) must be a multiple of sum(ratio)={unit}")
    reps = block_size // unit
    rng = random.Random(seed)
    rows, block_id = [], 0
    while len(rows) < n:
        block_id += 1
        block = template * reps
        rng.shuffle(block)
        for arm in block:
            if len(rows) >= n:
                break
            rows.append({"unit_id": len(rows) + 1, "block_id": block_id, "arm": arm})
    return rows


def _balanced_arms(m, arms, ratio):
    """Per-arm counts for m units, as balanced as the ratio allows
    (largest-remainder rounding), so imbalance never exceeds 1 per arm."""
    total = sum(ratio)
    raw = [m * r / total for r in ratio]
    counts = [int(x) for x in raw]
    for i in sorted(range(len(arms)), key=lambda i: raw[i] - counts[i],
                    reverse=True)[: m - sum(counts)]:
        counts[i] += 1
    return [arm for arm, c in zip(arms, counts) for _ in range(c)]


def stratified_randomization(strata, arms, ratio, seed):
    """Independent balanced randomization within each stratum.

    strata: list of (stratum_label, unit_id) pairs in enrollment order.
    Each stratum is shuffled with its own seeded RNG and assigned the most
    balanced arm counts possible for its size, so treatment arms are
    balanced on the stratification covariate BY CONSTRUCTION — a purely
    complete randomization only balances it in expectation.
    """
    by_stratum = {}
    for label, uid in strata:
        by_stratum.setdefault(label, []).append(uid)
    rows = []
    for label in sorted(by_stratum):
        uids = by_stratum[label]
        rng = random.Random(f"{seed}|{label}")
        pool = _balanced_arms(len(uids), arms, ratio)
        rng.shuffle(pool)
        shuffled = uids[:]
        rng.shuffle(shuffled)
        for uid, arm in zip(shuffled, pool):
            rows.append({"unit_id": uid, "stratum": label, "arm": arm})
    return rows


def load_strata(args):
    """Strata from inline 'male:30,female:30' counts or a units CSV file
    with unit_id and stratum columns."""
    if args.strata:
        strata = []
        for part in args.strata.split(","):
            label, _, count = part.partition(":")
            if not label or not count.isdigit() or int(count) < 1:
                raise SystemExit(f"bad stratum spec '{part}', expected 'label:count'")
            strata += [(label, f"{label}_{i + 1}") for i in range(int(count))]
        return strata
    if args.units:
        import csv
        with open(args.units, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "unit_id" not in reader.fieldnames or args.stratum_col not in reader.fieldnames:
                raise SystemExit(f"units file needs columns unit_id and "
                                 f"'{args.stratum_col}' (set --stratum-col)")
            return [(r[args.stratum_col], r["unit_id"]) for r in reader]
    raise SystemExit("stratified needs --strata label:count,... or --units FILE")


def emit(rows, fmt, out, meta):
    if fmt == "json":
        text = json.dumps({"meta": meta, "allocation": rows}, indent=2,
                          ensure_ascii=False)
    else:
        cols = list(rows[0].keys())
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            w.writerow([r[c] for c in cols])
        text = buf.getvalue().rstrip("\n")
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {out}", file=sys.stderr)
    else:
        print(text)
    if fmt == "csv":
        print(json.dumps(meta, ensure_ascii=False), file=sys.stderr)


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    sub = p.add_subparsers(dest="method", required=True)
    for name in ("complete", "block"):
        sp = sub.add_parser(name)
        sp.add_argument("--n", type=int, required=True, help="number of units")
        sp.add_argument("--arms", default="treatment,control",
                        help="comma-separated arm names")
        sp.add_argument("--ratio", default=None,
                        help="allocation ratio per arm, e.g. 2:1 (default equal)")
        sp.add_argument("--block-size", type=int, default=None,
                        help="(block only) units per block; must be a multiple "
                             "of sum(ratio); default 2x sum(ratio)")
        sp.add_argument("--seed", type=int, default=0)
        sp.add_argument("--format", choices=["csv", "json"], default="csv")
        sp.add_argument("--out", default=None, help="output file (default stdout)")
        sp.add_argument("--force", action="store_true", help="replace an existing --out file")
    sp = sub.add_parser("stratified",
                        help="balanced randomization within each stratum")
    sp.add_argument("--strata", default=None,
                    help="inline strata counts, e.g. 'male:30,female:30'")
    sp.add_argument("--units", default=None,
                    help="CSV file with unit_id and stratum columns")
    sp.add_argument("--stratum-col", default="stratum",
                    help="name of the stratum column in --units (default 'stratum')")
    sp.add_argument("--arms", default="treatment,control",
                    help="comma-separated arm names")
    sp.add_argument("--ratio", default=None,
                    help="allocation ratio per arm, e.g. 2:1 (default equal)")
    sp.add_argument("--seed", type=int, default=0)
    sp.add_argument("--format", choices=["csv", "json"], default="csv")
    sp.add_argument("--out", default=None, help="output file (default stdout)")
    sp.add_argument("--force", action="store_true", help="replace an existing --out file")
    args = p.parse_args(argv)
    if args.out:
        if getattr(args, "units", None) and os.path.abspath(args.out) == os.path.abspath(args.units):
            raise SystemExit("output must not replace the --units input file")
        if os.path.exists(args.out) and not args.force:
            raise SystemExit(f"output exists: {args.out}; use --force to replace it")

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    if len(arms) < 2:
        raise SystemExit("need at least 2 arms")
    ratio = parse_ratio(arms, args.ratio)

    if args.method == "complete":
        if args.block_size is not None:
            print("warning: --block-size is ignored for complete randomization",
                  file=sys.stderr)
        if args.n < 1:
            raise SystemExit("--n must be >= 1")
        rows = complete_randomization(args.n, arms, ratio, args.seed)
    elif args.method == "block":
        if args.n < 1:
            raise SystemExit("--n must be >= 1")
        rows = block_randomization(args.n, arms, ratio, args.block_size, args.seed)
    else:
        rows = stratified_randomization(load_strata(args), arms, ratio, args.seed)

    meta = {"method": args.method, "n": len(rows), "arms": arms, "ratio": ratio,
            "block_size": args.block_size if args.method == "block" else None,
            "seed": args.seed,
            "counts": {a: sum(1 for r in rows if r["arm"] == a) for a in arms}}
    if args.method == "stratified":
        meta["strata"] = sorted({r["stratum"] for r in rows})
        meta["counts_by_stratum"] = {
            s: {a: sum(1 for r in rows if r["stratum"] == s and r["arm"] == a)
                for a in arms}
            for s in meta["strata"]}
    emit(rows, args.format, args.out, meta)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: force UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    main()
