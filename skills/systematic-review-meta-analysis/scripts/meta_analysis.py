#!/usr/bin/env python3
"""Compute effect sizes and inverse-variance meta-analysis (stdlib only).

Purpose:
    A zero-dependency statistical-synthesis helper for a systematic review. It
    (1) derives a common effect size from each study's 2x2 table or
    mean/SD arm data (SMD / Hedges' g, risk ratio, odds ratio, with
    log-scale standard errors and confidence intervals), and (2) pools the
    study-level effects with fixed-effect and DerSimonian-Laird random-effects
    inverse-variance meta-analysis, reporting heterogeneity (Q, I², tau²) and
    per-study forest-plot weights. It does not treat search results as included
    studies and does not replace a risk-of-bias or GRADE assessment.

Dependencies:
    None (Python 3.8+ standard library only; uses math for the normal CDF).

CLI usage:
    # Per-study effect sizes from a JSON study list.
    python3 meta_analysis.py --mode effects --studies studies.json --measure smd --out effects.json

    # Pooled meta-analysis from a precomputed effects JSON.
    python3 meta_analysis.py --mode pool --effects effects.json --model random --out meta.json

    Common options: --force  --version  --alpha 0.05

Study input format (for --mode effects):
    {"studies": [
      {"id": "s1", "measure": "smd",
       "n1": 30, "mean1": 10.0, "sd1": 2.0,
       "n2": 30, "mean2": 8.0,  "sd2": 2.0},
      {"id": "s2", "measure": "rr",
       "events1": 20, "n1": 100, "events2": 30, "n2": 100}
    ]}

    measure = smd | hedges_g | rr | or
    smd / hedges_g require n1/mean1/sd1 and n2/mean2/sd2
    rr / or require events1/n1 and events2/n2

Effects input format (for --mode pool):
    {"effects": [{"id": "s1", "estimate": 0.5, "se": 0.15}, ...]}

Output format:
    --mode effects -> effects.json with per-study estimate, se, ci_low, ci_high
    --mode pool    -> meta.json with pooled estimate, heterogeneity, forest data
    Every JSON artifact carries schema_version, artifact_type, tool_version,
    and warnings. Exit code 0 on success, 1 on bad input.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

VERSION = "0.1.0"

# --- Distribution helpers (pure stdlib) ---------------------------------------

def _norm_cdf(x):
    """Abramowitz & Stegun approximation of the standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p):
    """Beasley-Springer-Moro approximation of the normal quantile (inverse CDF)."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be in (0, 1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]
    p_low, p_high = 0.02425, 1.0 - 0.02425
    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
           ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)


def _ci(alpha):
    return _norm_ppf(1 - alpha / 2.0)


# --- Effect-size computation -------------------------------------------------

def _cohens_d(n1, mean1, sd1, n2, mean2, sd2):
    if n1 < 2 or n2 < 2:
        raise ValueError("each arm needs n >= 2")
    pooled_sd = math.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
    if pooled_sd <= 0:
        raise ValueError("pooled SD must be positive")
    d = (mean1 - mean2) / pooled_sd
    return d, pooled_sd


def _hedges_correction(d, n1, n2):
    df = n1 + n2 - 2
    if df <= 0:
        return 1.0
    # Exact J factor via gamma approximation.
    # J = Gamma(df/2) / (sqrt(df/2) * Gamma((df-1)/2))
    # Use log-gamma for stability.
    from math import lgamma, log, sqrt, exp
    log_j = lgamma(df / 2.0) - (log(df / 2.0) / 2.0) - lgamma((df - 1) / 2.0)
    return exp(log_j)


def effect_size_smd(n1, mean1, sd1, n2, mean2, sd2):
    d, _ = _cohens_d(n1, mean1, sd1, n2, mean2, sd2)
    se = math.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
    return d, se


def effect_size_hedges_g(n1, mean1, sd1, n2, mean2, sd2):
    d, _ = _cohens_d(n1, mean1, sd1, n2, mean2, sd2)
    j = _hedges_correction(d, n1, n2)
    g = d * j
    se = math.sqrt((n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2)))
    return g, se


def _log_ratio(events1, n1, events2, n2, zero_correction):
    if n1 <= 0 or n2 <= 0:
        raise ValueError("arm sizes must be positive")
    a, b = float(events1), float(n1 - events1)
    c, d = float(events2), float(n2 - events2)
    if zero_correction:
        if a == 0 or b == 0 or c == 0 or d == 0:
            a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    if a <= 0 or b <= 0 or c <= 0 or d <= 0:
        raise ValueError("cell counts must be positive (consider zero_correction)")
    return a, b, c, d


def effect_size_rr(events1, n1, events2, n2, zero_correction=True):
    a, b, c, d = _log_ratio(events1, n1, events2, n2, zero_correction)
    log_rr = math.log((a / (a + b)) / (c / (c + d)))
    se = math.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
    return log_rr, se


def effect_size_or(events1, n1, events2, n2, zero_correction=True):
    a, b, c, d = _log_ratio(events1, n1, events2, n2, zero_correction)
    log_or = math.log((a * d) / (b * c))
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return log_or, se


MEASURE_FUNCTIONS = {
    "smd": effect_size_smd,
    "hedges_g": effect_size_hedges_g,
    "rr": effect_size_rr,
    "or": effect_size_or,
}


def compute_effects(studies, measure, alpha=0.05):
    func = MEASURE_FUNCTIONS[measure]
    z = _ci(alpha)
    effects = []
    warnings = []
    for idx, study in enumerate(studies):
        sid = study.get("id", f"study-{idx + 1}")
        try:
            if measure in ("smd", "hedges_g"):
                estimate, se = func(study["n1"], study["mean1"], study["sd1"],
                                    study["n2"], study["mean2"], study["sd2"])
            else:
                estimate, se = func(study["events1"], study["n1"],
                                    study["events2"], study["n2"])
            effects.append({
                "id": sid,
                "estimate": estimate,
                "se": se,
                "ci_low": estimate - z * se,
                "ci_high": estimate + z * se,
            })
        except (KeyError, ValueError) as exc:
            warnings.append(f"{sid}: skipped ({exc})")
    if not effects:
        raise ValueError("no computable effect sizes; check study fields")
    return effects, warnings


# --- Meta-analysis pooling ---------------------------------------------------

def meta_analysis(effects, model="random", alpha=0.05):
    if len(effects) < 1:
        raise ValueError("need at least one effect")
    z = _ci(alpha)
    weights_fixed = [1.0 / (e["se"] ** 2) for e in effects]
    sum_w = sum(weights_fixed)
    fixed_effect = sum(w * e["estimate"] for w, e in zip(weights_fixed, effects)) / sum_w
    fixed_se = math.sqrt(1.0 / sum_w)

    # Heterogeneity (Cochran's Q).
    q = sum(w * (e["estimate"] - fixed_effect) ** 2 for w, e in zip(weights_fixed, effects))
    k = len(effects)
    df = k - 1
    if df > 0:
        i2 = max(0.0, (q - df) / q) if q > 0 else 0.0
    else:
        i2 = 0.0

    # DerSimonian-Laird tau^2.
    if df > 0 and q > df:
        c = sum(w for w in weights_fixed) - sum(w ** 2 for w in weights_fixed) / sum_w
        tau2 = (q - df) / c
    else:
        tau2 = 0.0

    if model == "fixed":
        pooled_estimate, pooled_se, model_used = fixed_effect, fixed_se, "fixed-effect"
        weights = weights_fixed
    else:
        model_used = "random-effects"
        weights = [1.0 / (e["se"] ** 2 + tau2) for e in effects]
        sum_wr = sum(weights)
        pooled_estimate = sum(w * e["estimate"] for w, e in zip(weights, effects)) / sum_wr
        pooled_se = math.sqrt(1.0 / sum_wr)

    forest = []
    for e, w in zip(effects, weights):
        forest.append({
            "id": e["id"],
            "estimate": e["estimate"],
            "se": e["se"],
            "weight": w,
            "ci_low": e["ci_low"],
            "ci_high": e["ci_high"],
        })

    return {
        "model": model_used,
        "k": k,
        "pooled_estimate": pooled_estimate,
        "pooled_se": pooled_se,
        "ci_low": pooled_estimate - z * pooled_se,
        "ci_high": pooled_estimate + z * pooled_se,
        "alpha": alpha,
        "heterogeneity": {
            "Q": q,
            "df": df,
            "I_squared": i2,
            "tau_squared": tau2,
        },
        "forest": forest,
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
    ap.add_argument("--mode", choices=["effects", "pool"], required=True)
    ap.add_argument("--studies", help="studies.json (for --mode effects)")
    ap.add_argument("--effects", help="effects.json (for --mode pool)")
    ap.add_argument("--measure", choices=["smd", "hedges_g", "rr", "or"], default="smd")
    ap.add_argument("--model", choices=["fixed", "random"], default="random")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs")
    args = ap.parse_args(argv)

    try:
        if not 0 < args.alpha < 1:
            raise ValueError("alpha must be in (0, 1)")

        if args.mode == "effects":
            if not args.studies:
                raise ValueError("--studies is required for --mode effects")
            source = Path(args.studies).resolve(strict=True)
            payload = json.loads(source.read_text(encoding="utf-8"))
            studies = payload.get("studies") or (payload if isinstance(payload, list) else None)
            if not isinstance(studies, list):
                raise ValueError("studies input must be a list or an object with a 'studies' list")
            effects, warnings = compute_effects(studies, args.measure, args.alpha)
            ensure_output_path(args.out, [str(source)], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "meta-analysis-effects",
                "tool_version": VERSION,
                "source": str(source),
                "measure": args.measure,
                "alpha": args.alpha,
                "effects": effects,
                "warnings": warnings + [
                    "Effect sizes are computed from supplied summary data only; they do not replace study-level risk-of-bias or GRADE assessment.",
                ],
            }
            write_json(args.out, artifact)
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

        # pool
        if not args.effects:
            raise ValueError("--effects is required for --mode pool")
        source = Path(args.effects).resolve(strict=True)
        payload = json.loads(source.read_text(encoding="utf-8"))
        effects = payload.get("effects") or (payload if isinstance(payload, list) else None)
        if not isinstance(effects, list):
            raise ValueError("effects input must be a list or an object with an 'effects' list")
        result = meta_analysis(effects, model=args.model, alpha=args.alpha)
        ensure_output_path(args.out, [str(source)], args.force)
        artifact = {
            "schema_version": "1.0.0",
            "artifact_type": "meta-analysis-pooled",
            "tool_version": VERSION,
            "source": str(source),
            **result,
            "warnings": [
                "Pooling assumes compatible estimands, populations, timepoints, and effect measures across studies.",
                "I² describes observed heterogeneity magnitude; it does not establish its cause or justify subgroup claims without pre-specification.",
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
