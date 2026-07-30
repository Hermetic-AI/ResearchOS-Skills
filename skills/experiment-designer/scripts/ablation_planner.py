"""Ablation experiment matrix generator (mostly for ML/AI experiments).

An ablation study varies which COMPONENTS of a system are present while
holding everything else fixed, so the contribution of each component can be
attributed. This script generates the experiment matrix:

  loo  leave-one-out: the full system plus one run per component with ONLY
       that component removed. The metric drop of (full - loo[X]) is the
       marginal contribution of X GIVEN all other components — interactions
       between components are invisible to this design.
  all  all 2^k - 1 non-empty subsets. The only design that fully maps
       component interactions, but cost explodes (k=6 -> 63 training runs).
  add  cumulative add-one: start from the bare base and add components one
       at a time in a given (or seeded-random) order. Cheap, but strongly
       order-dependent: components added early absorb shared variance.

Each row is one training/evaluation run; a seeded run order decorrelates
config identity from queue position (thermal drift, cluster noise).

Dependencies: none (Python 3.8+ standard library only).

CLI usage:
    python ablation_planner.py --mode loo --components encoder,pretrain,augment --seed 42
    python ablation_planner.py --mode all --components a,b,c --format json
    python ablation_planner.py --mode add --components a,b,c --order a,c,b
    python ablation_planner.py --mode loo --components-file comps.txt --out matrix.csv
      # comps.txt: one component name per line

Output: CSV or JSON run matrix with columns run_id, config (label), one 0/1
column per component, n_components_active, and 'role' (full / base / loo:X /
subset / add-step). JSON embeds a meta block with mode, seed, and the
interpretation warning for the chosen mode.
"""

from __future__ import annotations

import argparse
import csv
import io
import itertools
import json
import os
import random
import sys


def load_components(args):
    if args.components_file:
        with open(args.components_file, encoding="utf-8") as f:
            comps = [line.strip() for line in f if line.strip()]
    else:
        comps = [c.strip() for c in (args.components or "").split(",") if c.strip()]
    if len(comps) < 2:
        raise SystemExit("need at least 2 components")
    if len(set(comps)) != len(comps):
        raise SystemExit("component names must be unique")
    if args.mode == "all" and len(comps) > 10:
        raise SystemExit(f"full ablation with {len(comps)} components = "
                         f"{2 ** len(comps) - 1} runs; use --mode loo or trim the list")
    return comps


def make_configs(mode, comps, order):
    """List of (role, active_set) pairs, always including the full system."""
    full = tuple(comps)
    if mode == "loo":
        cfgs = [("full", full)]
        cfgs += [(f"loo:{c}", tuple(x for x in comps if x != c)) for c in comps]
        return cfgs
    if mode == "all":
        cfgs = []
        for r in range(1, len(comps) + 1):
            for subset in itertools.combinations(comps, r):
                role = "full" if r == len(comps) else "subset"
                cfgs.append((role, subset))
        return cfgs
    # add: cumulative in the given order (default: component list order)
    seq = order or comps
    if sorted(seq) != sorted(comps):
        raise SystemExit("--order must be a permutation of the components")
    cfgs = [("base:add-nothing", ())]
    for i, c in enumerate(seq, 1):
        cfgs.append((f"add-step{i}:+{c}", tuple(seq[:i])))
    return cfgs


WARNINGS = {
    "loo": "leave-one-out attributes each component's contribution GIVEN all "
           "others; two components that only help together will BOTH look "
           "useless. Check suspicious pairs with a targeted 2x2.",
    "all": "full factorial over components; supports interaction analysis. "
           "Report a multiple-comparison strategy for the 2^k-1 contrasts.",
    "add": "cumulative add-one is ORDER-DEPENDENT: shared gains are credited "
           "to whichever component is added first. State and justify the order.",
}


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.add_argument("--mode", choices=["loo", "all", "add"], default="loo")
    p.add_argument("--components", default=None, help="comma-separated names")
    p.add_argument("--components-file", default=None,
                   help="file with one component name per line")
    p.add_argument("--order", default=None,
                   help="(add) comma-separated addition order; default = list order")
    p.add_argument("--seed", type=int, default=0,
                   help="seed for shuffling run order (0 = keep logical order)")
    p.add_argument("--no-shuffle", action="store_true",
                   help="keep logical order (full first, etc.)")
    p.add_argument("--format", choices=["csv", "json"], default="csv")
    p.add_argument("--out", default=None, help="output file (default stdout)")
    p.add_argument("--force", action="store_true", help="replace an existing --out file")
    args = p.parse_args(argv)
    if args.out and os.path.exists(args.out) and not args.force:
        raise SystemExit(f"output exists: {args.out}; use --force to replace it")

    comps = load_components(args)
    order = [c.strip() for c in args.order.split(",")] if args.order else None
    cfgs = make_configs(args.mode, comps, order)

    rows = []
    for i, (role, active) in enumerate(cfgs, 1):
        row = {"run_id": i, "config": "+".join(active) if active else "(base)",
               "role": role, "n_components_active": len(active)}
        row.update({c: int(c in active) for c in comps})
        rows.append(row)

    if args.seed and not args.no_shuffle:
        random.Random(args.seed).shuffle(rows)
        rows = [{**r, "run_id": i} for i, r in enumerate(rows, 1)]

    meta = {"mode": args.mode, "components": comps, "n_runs": len(rows),
            "seed": args.seed, "shuffled": bool(args.seed and not args.no_shuffle),
            "interpretation_warning": WARNINGS[args.mode]}
    if args.format == "json":
        text = json.dumps({"meta": meta, "runs": rows}, indent=2,
                          ensure_ascii=False)
    else:
        cols = ["run_id", "config", "role", "n_components_active"] + comps
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            w.writerow([r[c] for c in cols])
        text = buf.getvalue().rstrip("\n")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text)
    if args.format == "csv":
        print(json.dumps(meta, ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: force UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    main()
