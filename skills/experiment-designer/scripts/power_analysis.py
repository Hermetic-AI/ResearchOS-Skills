"""A priori power / sample-size / MDE estimation (normal approximation).

Solves the "fix three, solve the fourth" relationship among sample size,
effect size, alpha, and power for five common tests:

  t_ind     two independent means, effect size = Cohen's d
            (or give --means M1 M2 plus --sd for a raw difference)
  t_one     one mean vs. a fixed value; d = |mu - mu0| / sd
  t_paired  paired means (pre/post, matched); d = mean_diff / sd_diff —
            --sd must be the SD of the DIFFERENCE scores, not of either
            measurement; sd_diff = sd * sqrt(2(1-r)), so a paired design
            gains power exactly in proportion to the pairing correlation
  two_prop  two independent proportions (give --p1 --p2; uses Cohen's h)
  corr      Pearson correlation vs. 0; effect size = r (Fisher z transform)

For each test you can solve for:
  n       required sample size (per group for two-sample tests; total
          otherwise), given effect size, alpha, power
  power   achieved power, given n and effect size
  mde     minimum detectable effect size, given n and power

Method: two-sided (default) or one-sided normal approximation, equal
allocation. This is the standard a priori approximation; it ignores the
t-distribution's heavier tails, so results can be optimistic at small/moderate
n or stringent alpha. Use the optional reference validation before sign-off.

For standardized mean tests, ``--hypothesis noninferiority`` and
``--hypothesis equivalence`` use a positive standardized ``--margin``.
Cluster-randomized inflation uses ``--cluster-size``, ``--icc``, and optional
``--cluster-cv``; dropout is applied after the design effect and allocation is
rounded to complete clusters.

Dependencies: none (Python 3.8+ standard library; uses statistics.NormalDist).

CLI usage:
    python power_analysis.py --test t_ind    --solve n --effect-size 0.5 --power 0.8
    python power_analysis.py --test t_one    --solve n --effect-size 0.3
    python power_analysis.py --test t_paired --solve n --effect-size 0.5 --power 0.9
    python power_analysis.py --test corr     --solve n --effect-size 0.3 --power 0.8
    python power_analysis.py --test corr     --solve power --effect-size 0.3 --n 84
    python power_analysis.py --test two_prop --solve n --p1 0.40 --p2 0.55 --power 0.8
    python power_analysis.py --test t_ind    --solve mde --n 30 --power 0.8
    python power_analysis.py --test t_ind    --solve n --means 105 100 --sd 15 \
        --power 0.9 --alpha 0.01 --sides 2

Output: JSON object to stdout with the inputs, the solved quantity, the
dropout-inflated enrollment size (when solving n), and method notes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from statistics import NormalDist

Z = NormalDist()


def zcrit(alpha, sides):
    """Critical z for the type-I error rate."""
    return Z.inv_cdf(1 - alpha / 2) if sides == 2 else Z.inv_cdf(1 - alpha)


def effect_from_args(args, test):
    """Effect size d (t-tests), h (two_prop), or r (corr)."""
    if args.effect_size is not None:
        return args.effect_size
    if test == "two_prop":
        if args.p1 is None or args.p2 is None:
            raise SystemExit("two_prop needs --p1 and --p2 (or --effect-size h)")
        return abs(2 * math.asin(math.sqrt(args.p1)) - 2 * math.asin(math.sqrt(args.p2)))
    if args.means and args.sd:
        return abs(args.means[0] - args.means[1]) / args.sd
    raise SystemExit(f"{test} needs --effect-size, or --means M1 M2 --sd SD"
                     + (" (r in (-1,1))" if test == "corr" else ""))


def signed_mean_effect(args):
    if args.effect_size is not None:
        return args.effect_size
    if args.means and args.sd:
        return (args.means[0] - args.means[1]) / args.sd
    raise SystemExit("noninferiority/equivalence needs --effect-size, or --means M1 M2 --sd SD")


# Non-centrality / inversion formulas per test family.
# Each returns (n_from_d, power_from_d_n, mde_from_n). n is per group for
# t_ind/two_prop, total for t_one/t_paired/corr.

def formulas(test):
    """Power model: ncp = d * f(n). Solve by inverting f."""
    if test in ("t_ind", "two_prop"):
        f = lambda n: math.sqrt(n / 2)
        finv = lambda x: 2 * x ** 2
        dmin = lambda n: math.sqrt(2 / n)
    elif test in ("t_one", "t_paired"):
        f = lambda n: math.sqrt(n)
        finv = lambda x: x ** 2
        dmin = lambda n: 1 / math.sqrt(n)
    else:  # corr, Fisher z
        f = lambda n: math.sqrt(n - 3)
        finv = lambda x: x ** 2 + 3
        dmin = lambda n: 1 / math.sqrt(n - 3)

    def n_from_d(d, alpha, power, sides):
        za, zb = zcrit(alpha, sides), Z.inv_cdf(power)
        return math.ceil(finv((za + zb) / d))

    def power_from(d, n, alpha, sides):
        ncp = d * f(n)
        za = zcrit(alpha, sides)
        p = 1 - Z.cdf(za - ncp)
        if sides == 2:
            p += Z.cdf(-za - ncp)
        return min(max(p, 0.0), 1.0)

    def mde_from(n, alpha, power, sides):
        d = (zcrit(alpha, sides) + Z.inv_cdf(power)) * dmin(n)
        return math.tanh(d) if test == "corr" else d

    return n_from_d, power_from, mde_from


def equivalence_power(effect, margin, n, alpha, f):
    """Normal-approximation TOST power for symmetric standardized margins."""
    se = 1 / f(n)
    za = zcrit(alpha, 1)
    lower = -margin + za * se
    upper = margin - za * se
    if lower >= upper:
        return 0.0
    return max(0.0, Z.cdf((upper - effect) / se) - Z.cdf((lower - effect) / se))


def alternative_power(hypothesis, effect, margin, n, alpha, f):
    if hypothesis == "noninferiority":
        return 1 - Z.cdf(zcrit(alpha, 1) - (effect + margin) * f(n))
    return equivalence_power(effect, margin, n, alpha, f)


def solve_alternative_n(hypothesis, effect, margin, alpha, target, f, minimum=2):
    low, high = minimum - 1, minimum
    while high <= 10_000_000 and alternative_power(hypothesis, effect, margin, high, alpha, f) < target:
        low, high = high, high * 2
    if high > 10_000_000:
        high = 10_000_000
        if alternative_power(hypothesis, effect, margin, high, alpha, f) < target:
            raise SystemExit("required n exceeds 10,000,000; inspect margin and assumptions")
    while high - low > 1:
        middle = (low + high) // 2
        if alternative_power(hypothesis, effect, margin, middle, alpha, f) >= target:
            high = middle
        else:
            low = middle
    return high


def design_effect(cluster_size, icc, cluster_cv):
    """Approximate variance inflation for equal/unequal cluster sizes."""
    return 1 + (cluster_size * (1 + cluster_cv ** 2) - 1) * icc


EFFECT_METRIC = {"t_ind": "Cohen's d", "t_one": "Cohen's d",
                 "t_paired": "Cohen's d (SD of difference scores)",
                 "two_prop": "Cohen's h", "corr": "Pearson r (Fisher z)"}
N_LABEL = {"t_ind": "n_per_group", "two_prop": "n_per_group",
           "t_one": "n_total", "t_paired": "n_pairs", "corr": "n_total"}


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.add_argument("--test", choices=list(EFFECT_METRIC), required=True)
    p.add_argument("--solve", choices=["n", "power", "mde"], required=True)
    p.add_argument("--effect-size", type=float, default=None,
                   help="Cohen's d (t tests), Cohen's h (two_prop), or r (corr)")
    p.add_argument("--means", type=float, nargs=2, default=None,
                   help="means M1 M2 (with --sd) instead of --effect-size")
    p.add_argument("--sd", type=float, default=None,
                   help="pooled SD; for t_paired, the SD of DIFFERENCE scores")
    p.add_argument("--p1", type=float, default=None, help="proportion in group 1")
    p.add_argument("--p2", type=float, default=None, help="proportion in group 2")
    p.add_argument("--n", type=int, default=None,
                   help="sample size (per group for two-sample tests)")
    p.add_argument("--power", type=float, default=0.80)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--sides", type=int, choices=[1, 2], default=2)
    p.add_argument("--hypothesis", choices=["superiority", "noninferiority", "equivalence"],
                   default="superiority", help="confirmatory hypothesis type")
    p.add_argument("--margin", type=float, default=None,
                   help="positive standardized noninferiority/equivalence margin")
    p.add_argument("--dropout", type=float, default=0.0,
                   help="expected dropout/attrition rate, e.g. 0.2 (used when "
                        "solving n to give the enrollment size)")
    p.add_argument("--cluster-size", type=float, default=None,
                   help="anticipated mean analyzable units per randomized cluster")
    p.add_argument("--icc", type=float, default=None,
                   help="intracluster correlation in [0, 1)")
    p.add_argument("--cluster-cv", type=float, default=0.0,
                   help="coefficient of variation of cluster size (default 0)")
    args = p.parse_args(argv)

    if not 0 < args.alpha < 1:
        raise SystemExit("--alpha must be in (0, 1)")
    if not 0 < args.power < 1:
        raise SystemExit("--power must be in (0, 1)")
    if not 0 <= args.dropout < 1:
        raise SystemExit("--dropout must be in [0, 1)")
    cluster_requested = args.cluster_size is not None or args.icc is not None or args.cluster_cv != 0
    if cluster_requested:
        if args.cluster_size is None or args.icc is None:
            raise SystemExit("cluster inflation needs both --cluster-size and --icc")
        if args.cluster_size <= 1:
            raise SystemExit("--cluster-size must be > 1")
        if not 0 <= args.icc < 1:
            raise SystemExit("--icc must be in [0, 1)")
        if args.cluster_cv < 0:
            raise SystemExit("--cluster-cv must be >= 0")
    if args.hypothesis != "superiority":
        if args.test not in ("t_ind", "t_one", "t_paired"):
            raise SystemExit("noninferiority/equivalence currently support standardized mean tests only")
        if args.solve == "mde":
            raise SystemExit("--solve mde is not defined here for noninferiority/equivalence; vary --margin explicitly")
        if args.margin is None or args.margin <= 0:
            raise SystemExit("noninferiority/equivalence require --margin > 0 in standardized effect units")
        if args.sides != 2:
            raise SystemExit("do not set --sides for noninferiority/equivalence; their one-sided tests are handled internally")
    if args.n is not None:
        if args.n < 1:
            raise SystemExit("--n must be >= 1")
        if args.test == "corr" and args.n <= 3:
            raise SystemExit("corr needs --n > 3 (the Fisher z model uses n - 3)")
    if (args.means is not None or args.sd is not None) and \
            args.test not in ("t_ind", "t_one", "t_paired"):
        raise SystemExit(f"--means/--sd only apply to t tests; for {args.test} "
                         "use --effect-size (or --p1/--p2 for two_prop)")

    n_from_d, power_from, mde_from = formulas(args.test)
    if args.test in ("t_ind", "two_prop"):
        f = lambda n: math.sqrt(n / 2)
    elif args.test in ("t_one", "t_paired"):
        f = lambda n: math.sqrt(n)
    else:
        f = lambda n: math.sqrt(n - 3)

    d = None
    if args.solve in ("n", "power"):
        d = signed_mean_effect(args) if args.hypothesis != "superiority" else effect_from_args(args, args.test)
        if args.hypothesis == "superiority" and d <= 0:
            raise SystemExit("effect size must be > 0")
        if args.hypothesis == "noninferiority" and d <= -args.margin:
            raise SystemExit("expected effect must exceed the noninferiority null boundary (-margin)")
        if args.hypothesis == "equivalence" and abs(d) >= args.margin:
            raise SystemExit("expected effect must lie strictly inside the equivalence margins")
        if args.test == "corr" and d >= 1:
            raise SystemExit("corr effect size is |r|, must be < 1")
        if args.test == "corr":
            d = math.atanh(d)  # work in Fisher-z units; convert back for output
    result = {"test": args.test, "solve": args.solve, "alpha": args.alpha,
              "sides": args.sides,
              "hypothesis": args.hypothesis,
              "method": "normal approximation, equal allocation"
                        if args.test in ("t_ind", "two_prop")
                        else "normal approximation"}
    if d is not None:
        result["effect_size"] = round(math.tanh(d) if args.test == "corr" else d, 6)
    if args.margin is not None:
        result["standardized_margin"] = args.margin
    if args.test == "two_prop":
        result["proportions"] = [args.p1, args.p2]
    result["effect_size_metric"] = EFFECT_METRIC[args.test]
    n_label = N_LABEL[args.test]
    per_group = args.test in ("t_ind", "two_prop")

    if args.solve == "n":
        n = (n_from_d(d, args.alpha, args.power, args.sides)
             if args.hypothesis == "superiority"
             else solve_alternative_n(args.hypothesis, d, args.margin, args.alpha, args.power, f))
        result["target_power"] = args.power
        result[n_label] = n
        if per_group:
            result["n_total"] = 2 * n
        if cluster_requested:
            de = design_effect(args.cluster_size, args.icc, args.cluster_cv)
            inflated = math.ceil(n * de)
            clusters = math.ceil(inflated / args.cluster_size)
            enroll = math.ceil(clusters * args.cluster_size / (1 - args.dropout))
            result["cluster_design"] = {
                "mean_cluster_size": args.cluster_size, "icc": args.icc,
                "cluster_size_cv": args.cluster_cv, "design_effect": round(de, 6),
                "clusters_" + ("per_group" if per_group else "total"): clusters,
                "enroll_" + ("per_group" if per_group else "total"): enroll,
            }
            if per_group:
                result["cluster_design"]["clusters_total"] = 2 * clusters
                result["cluster_design"]["enroll_total"] = 2 * enroll
        elif args.dropout > 0:
            enroll = math.ceil(n / (1 - args.dropout))
            result["dropout_rate"] = args.dropout
            result["enroll_" + ("per_group" if per_group else "total")] = enroll
            if per_group:
                result["enroll_total"] = 2 * enroll
    elif args.solve == "power":
        if not args.n:
            raise SystemExit("--solve power needs --n")
        effective_n = args.n / design_effect(args.cluster_size, args.icc, args.cluster_cv) if cluster_requested else args.n
        result[n_label] = args.n
        result["effective_" + n_label] = round(effective_n, 4) if cluster_requested else args.n
        achieved = (power_from(d, effective_n, args.alpha, args.sides)
                    if args.hypothesis == "superiority"
                    else alternative_power(args.hypothesis, d, args.margin, effective_n, args.alpha, f))
        result["power"] = round(achieved, 4)
        if cluster_requested:
            result["cluster_design"] = {"mean_cluster_size": args.cluster_size, "icc": args.icc, "cluster_size_cv": args.cluster_cv, "design_effect": round(design_effect(args.cluster_size, args.icc, args.cluster_cv), 6)}
    else:
        if not args.n:
            raise SystemExit("--solve mde needs --n")
        result[n_label] = args.n
        result["target_power"] = args.power
        result["mde"] = round(mde_from(args.n, args.alpha, args.power, args.sides), 4)
        result["mde_metric"] = result["effect_size_metric"]

    notes = [
        "normal approximation; can be optimistic at small/moderate n or stringent alpha",
        "report a sensitivity range over plausible effect sizes, not a single n",
        "avoid post-hoc ('observed') power — it is a deterministic function "
        "of the p-value and uninformative",
    ]
    if args.test == "t_paired":
        notes.append("d for t_paired uses the SD of difference scores; the "
                     "stronger the within-unit correlation, the smaller the "
                     "required n — pairing is a variance-reduction device")
    if args.test == "corr":
        notes.append("Fisher z approximation; test is H0: r = 0")
    if args.hypothesis == "noninferiority":
        notes.append("margin is standardized and positive; H0 is effect <= -margin, with larger effects favorable")
    if args.hypothesis == "equivalence":
        notes.append("normal-approximation TOST power for symmetric standardized margins")
    if cluster_requested:
        notes.append("cluster inflation is approximate; power depends on the number of independent clusters, cluster-size distribution, and planned cluster-aware analysis")
    result["notes"] = notes
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: force UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    main()
