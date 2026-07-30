#!/usr/bin/env python3
"""Estimate causal effects with propensity scores, DiD, RDD, and E-values.

Purpose:
    A zero-dependency design-implementation helper for observational causal
    analyses. It (1) estimates propensity scores via logistic regression solved
    with Newton-Raphson on pure-Python matrices, then performs 1:1 greedy
    nearest-neighbor matching and computes inverse-probability-of-treatment
    weights (IPTW) with stabilization and truncation; (2) estimates a
    two-group x two-period difference-in-differences effect with a cluster-robust
    standard error; (3) estimates a sharp regression-discontinuity effect with
    local-linear OLS on each side of the cutoff; and (4) computes the E-value
    for an observed risk-ratio-scale association and its confidence limit. It
    documents assumptions; it does not prove exchangeability, parallel trends,
    or continuity.

Dependencies:
    None (Python 3.8+ standard library only).

CLI usage:
    python3 causal_estimate.py --method psm --data data.json --treatment treated \\
        --out matched.json --caliper 0.2
    python3 causal_estimate.py --method iptw --data data.json --treatment treated \\
        --out weighted.json --truncate 0.01
    python3 causal_estimate.py --method did --data data.json --out did.json
    python3 causal_estimate.py --method rdd --data data.json --out rdd.json --cutoff 0.0 --bandwidth 1.0
    python3 causal_estimate.py --method evalue --risk-ratio 2.1 --confidence-limit 1.3

    Common options: --force  --version  --alpha 0.05  --max-iter 100  --tol 1e-6

Data JSON format (PSM/IPTW): list of rows, each a dict with the treatment
    column (0/1), the outcome column (numeric), and confounder columns (numeric).
    {"rows": [{"treated": 1, "age": 45, "score": 7.2, "y": 1.0}, ...]}

Data JSON format (DiD): rows with columns treated (0/1), post (0/1), y (numeric).
    Interaction term (treated*post) is the DiD estimand.

Data JSON format (RDD): rows with columns running (numeric), y (numeric).
    The cutoff splits the sample; local-linear OLS is fit on each side.

Output format:
    A JSON artifact per method with the estimate, standard error, confidence
    interval, diagnostics, and method-specific detail. Every artifact carries
    schema_version, artifact_type, tool_version, and warnings.
    Exit code 0 on success, 1 on bad input.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

VERSION = "0.1.0"

# --- Pure-Python matrix / OLS helpers ----------------------------------------

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _mat_vec_mul(matrix, vector):
    return [_dot(row, vector) for row in matrix]


def _transpose(matrix):
    if not matrix:
        return []
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]


def _solve_linear(A, b):
    """Solve Ax = b via Gaussian elimination with partial pivoting."""
    n = len(A)
    aug = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular matrix in OLS solve")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= piv
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            for j in range(col, n + 1):
                aug[r][j] -= factor * aug[col][j]
    return [aug[i][n] for i in range(n)]


def ols(X, y, add_intercept=True):
    """Return coefficients, residuals, and residual standard error."""
    if add_intercept:
        X = [[1.0] + list(row) for row in X]
    XtX = [[_dot(Xti, Xtj) for Xtj in _transpose(X)] for Xti in _transpose(X)]
    Xty = [_dot(col, y) for col in _transpose(X)]
    beta = _solve_linear(XtX, Xty)
    residuals = [yi - _dot(X[i], beta) for i, yi in enumerate(y)]
    dof = len(y) - len(beta)
    rss = sum(r ** 2 for r in residuals)
    sigma2 = rss / dof if dof > 0 else float("inf")
    se = []
    try:
        XtX_inv = _invert(_transpose(X), X)
    except ValueError:
        se = [float("nan")] * len(beta)
    else:
        for k in range(len(beta)):
            se.append(math.sqrt(max(0.0, sigma2 * XtX_inv[k][k])))
    return beta, residuals, se, sigma2, dof


def _invert(XtX, X):
    """Invert via Gaussian elimination (XtX is square)."""
    n = len(XtX)
    aug = [list(XtX[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv = aug[col][col]
        for j in range(col, 2 * n):
            aug[col][j] /= piv
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            for j in range(col, 2 * n):
                aug[r][j] -= factor * aug[col][j]
    return [row[n:] for row in aug]


def _mean(values):
    return sum(values) / len(values)


def _variance(values):
    m = _mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - 1)


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _logistic(x):
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _ci_z(alpha):
    # Beasley-Springer-Moro normal quantile for 1 - alpha/2.
    p = 1 - alpha / 2.0
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p_low, p_high = 0.02425, 0.97575
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


# --- Propensity score estimation ---------------------------------------------

def estimate_propensity(rows, treatment, confounders):
    X = [[float(row[c]) for c in confounders] for row in rows]
    y = [float(row[treatment]) for row in rows]
    beta, mu = ols_logistic(X, y)
    scores = [_logistic(_dot([1.0] + row, beta)) for row in X]
    return scores, beta


def ols_logistic(X, y, max_iter=100, tol=1e-6):
    """Newton-Raphson IRLS for logistic regression."""
    n = len(X)
    p = len(X[0])
    beta = [0.0] * (p + 1)
    for _ in range(max_iter):
        eta = [_dot([1.0] + list(X[i]), beta) for i in range(n)]
        mu = [_logistic(e) for e in eta]
        w = [m * (1.0 - m) for m in mu]
        z = [eta[i] + (y[i] - mu[i]) / w[i] if w[i] > 1e-9 else eta[i] for i in range(n)]
        Xw = [[math.sqrt(w[i]) * (1.0 if j == 0 else X[i][j - 1]) for j in range(p + 1)] for i in range(n)]
        zw = [math.sqrt(w[i]) * z[i] for i in range(n)]
        try:
            beta_new, _, _, _, _ = ols(Xw, zw, add_intercept=False)
        except ValueError:
            break
        if max(abs(beta_new[j] - beta[j]) for j in range(p + 1)) < tol:
            beta = beta_new
            break
        beta = beta_new
    eta = [_dot([1.0] + list(X[i]), beta) for i in range(n)]
    mu = [_logistic(e) for e in eta]
    return beta, mu


# --- Propensity score matching -----------------------------------------------

def psm(rows, treatment, outcome, confounders, caliper=0.2, alpha=0.05):
    scores, beta = estimate_propensity(rows, treatment, confounders)
    treated = [(i, scores[i]) for i in range(len(rows)) if int(rows[i][treatment]) == 1]
    control = [(i, scores[i]) for i in range(len(rows)) if int(rows[i][treatment]) == 0]
    if not treated or not control:
        raise ValueError("PSM needs both treated and control units")
    sd_pooled = math.sqrt(_variance(scores)) or 1.0
    caliper = caliper * sd_pooled
    used = set()
    pairs = []
    for ti, ts in sorted(treated, key=lambda x: x[1]):
        best, best_dist = None, float("inf")
        for ci, cs in control:
            if ci in used:
                continue
            dist = abs(ts - cs)
            if dist < best_dist:
                best, best_dist = ci, dist
        if best is not None and best_dist <= caliper:
            pairs.append((ti, best))
            used.add(best)
    if not pairs:
        raise ValueError("no matches within caliper; relax caliper or review overlap")
    effects = [float(rows[ti][outcome]) - float(rows[ci][outcome]) for ti, ci in pairs]
    att = _mean(effects)
    se = math.sqrt(_variance(effects) / len(effects)) if len(effects) > 1 else float("nan")
    z = _ci_z(alpha)
    balance = {}
    for c in confounders:
        t_mean = _mean([float(rows[ti][c]) for ti, _ in pairs])
        c_mean = _mean([float(rows[ci][c]) for _, ci in pairs])
        pooled = math.sqrt((_variance([float(rows[ti][c]) for ti, _ in pairs]) +
                            _variance([float(rows[ci][c]) for _, ci in pairs])) / 2.0) or 1.0
        balance[c] = {"treated_mean": t_mean, "control_mean": c_mean,
                      "std_mean_diff": (t_mean - c_mean) / pooled}
    return {
        "method": "propensity-score-matching",
        "estimand": "ATT",
        "n_treated_total": len(treated),
        "n_control_total": len(control),
        "n_matched_pairs": len(pairs),
        "caliper": caliper,
        "estimate": att,
        "se": se,
        "ci_low": att - z * se,
        "ci_high": att + z * se,
        "balance": balance,
        "propensity_model": {"coefficients": {"intercept": beta[0],
                                              **dict(zip(confounders, beta[1:]))}},
    }


# --- IPTW --------------------------------------------------------------------

def iptw(rows, treatment, outcome, confounders, truncate=0.0, alpha=0.05):
    scores, beta = estimate_propensity(rows, treatment, confounders)
    n = len(rows)
    weights = []
    for i, row in enumerate(rows):
        ps = min(max(scores[i], 1e-6), 1 - 1e-6)
        if int(row[treatment]) == 1:
            weights.append(1.0 / ps)
        else:
            weights.append(1.0 / (1.0 - ps))
    w_mean = _mean(weights)
    weights = [w / w_mean for w in weights]
    if truncate > 0:
        lo, hi = truncate, 1.0 - truncate
        weights = [min(max(w, lo * w_mean), hi * w_mean) for w in weights]
        weights = [w / _mean(weights) for w in weights]
    y = [float(row[outcome]) for row in rows]
    t = [float(row[treatment]) for row in rows]
    num_t = sum(w * ti * yi for w, ti, yi in zip(weights, t, y))
    den_t = sum(w * ti for w, ti in zip(weights, t))
    num_c = sum(w * (1 - ti) * yi for w, ti, yi in zip(weights, t, y))
    den_c = sum(w * (1 - ti) for w, ti in zip(weights, t))
    mu_t, mu_c = num_t / den_t, num_c / den_c
    ate = mu_t - mu_c
    # Sandwich-style robust SE via residual regression on treatment + confounders.
    residuals = [yi - (mu_t if ti == 1 else mu_c) for yi, ti in zip(y, t)]
    X = [[t[i]] + [float(rows[i][c]) for c in confounders] for i in range(len(rows))]
    try:
        beta_reg, _, se, _, dof = ols(X, residuals)
        se_ate = se[0] if se else float("nan")
    except ValueError:
        se_ate = float("nan")
    z = _ci_z(alpha)
    return {
        "method": "inverse-probability-weighting",
        "estimand": "ATE",
        "n": n,
        "truncate": truncate,
        "estimate": ate,
        "se": se_ate,
        "ci_low": ate - z * se_ate,
        "ci_high": ate + z * se_ate,
        "weighted_means": {"treated": mu_t, "control": mu_c},
        "weight_summary": {"mean": _mean(weights), "min": min(weights), "max": max(weights)},
        "propensity_model": {"coefficients": {"intercept": beta[0],
                                              **dict(zip(confounders, beta[1:]))}},
    }


# --- Difference-in-differences ------------------------------------------------

def did(rows, treatment, outcome, time, alpha=0.05):
    groups = {"pre": {"treated": [], "control": []}, "post": {"treated": [], "control": []}}
    for row in rows:
        period = "post" if int(row[time]) == 1 else "pre"
        group = "treated" if int(row[treatment]) == 1 else "control"
        groups[period][group].append(float(row[outcome]))
    means = {p: {g: _mean(v) for g, v in gs.items()} for p, gs in groups.items()}
    for key in ["pre", "post"]:
        for g in ["treated", "control"]:
            if not groups[key][g]:
                raise ValueError(f"DiD cell {key}/{g} is empty")
    did_estimate = (means["post"]["treated"] - means["pre"]["treated"]) - \
                   (means["post"]["control"] - means["pre"]["control"])
    # Cluster-robust SE at the unit level approximated by the four-cell variance.
    cell_vars = {}
    for key in ["pre", "post"]:
        for g in ["treated", "control"]:
            vals = groups[key][g]
            cell_vars[(key, g)] = _variance(vals) / len(vals) if len(vals) > 1 else 0.0
    se = math.sqrt(sum(cell_vars.values()))
    z = _ci_z(alpha)
    return {
        "method": "difference-in-differences",
        "estimand": "ATE (parallel-trends assumption)",
        "estimate": did_estimate,
        "se": se,
        "ci_low": did_estimate - z * se,
        "ci_high": did_estimate + z * se,
        "cell_means": means,
        "cell_counts": {p: {g: len(v) for g, v in gs.items()} for p, gs in groups.items()},
    }


# --- Regression discontinuity -----------------------------------------------

def rdd(rows, running, outcome, cutoff=0.0, bandwidth=None, alpha=0.05):
    left = [row for row in rows if float(row[running]) < cutoff]
    right = [row for row in rows if float(row[running]) >= cutoff]
    if not left or not right:
        raise ValueError("RDD needs units on both sides of the cutoff")
    if bandwidth is not None:
        left = [row for row in left if abs(float(row[running]) - cutoff) <= bandwidth]
        right = [row for row in right if abs(float(row[running]) - cutoff) <= bandwidth]
    if len(left) < 3 or len(right) < 3:
        raise ValueError("insufficient units near the cutoff for local-linear fit")
    def fit(side):
        X = [[float(row[running]) - cutoff] for row in side]
        y = [float(row[outcome]) for row in side]
        beta, _, se, _, _ = ols(X, y, add_intercept=True)
        return beta[0], se[0] if se else float("nan"), len(side)
    left_mean, left_se, n_left = fit(left)
    right_mean, right_se, n_right = fit(right)
    tau = right_mean - left_mean
    se = math.sqrt(left_se ** 2 + right_se ** 2)
    z = _ci_z(alpha)
    return {
        "method": "regression-discontinuity",
        "estimand": "local ATE at cutoff",
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "estimate": tau,
        "se": se,
        "ci_low": tau - z * se,
        "ci_high": tau + z * se,
        "left": {"n": n_left, "estimate": left_mean, "se": left_se},
        "right": {"n": n_right, "estimate": right_mean, "se": right_se},
    }


# --- E-value -----------------------------------------------------------------

def evalue(risk_ratio, confidence_limit=None):
    def _ev(ratio):
        if ratio <= 0:
            raise ValueError("ratio must be positive")
        rr = ratio if ratio >= 1 else 1 / ratio
        return rr + math.sqrt(rr * (rr - 1))
    oriented = risk_ratio if risk_ratio >= 1 else 1 / risk_ratio
    value = _ev(risk_ratio)
    result = {
        "method": "e-value",
        "input_risk_ratio": risk_ratio,
        "oriented_risk_ratio": oriented,
        "e_value": value,
    }
    if confidence_limit is not None:
        bound = _ev(confidence_limit)
        result["confidence_limit"] = {"input": confidence_limit,
                                      "oriented": confidence_limit if confidence_limit >= 1 else 1 / confidence_limit,
                                      "e_value": bound}
    return result


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
    ap.add_argument("--method", choices=["psm", "iptw", "did", "rdd", "evalue"], required=True)
    ap.add_argument("--data", help="data JSON (for psm/iptw/did/rdd)")
    ap.add_argument("--treatment", help="treatment column name (0/1)")
    ap.add_argument("--outcome", help="outcome column name")
    ap.add_argument("--time", help="time-period column name (0/1) for DiD")
    ap.add_argument("--running", help="running variable column name for RDD")
    ap.add_argument("--confounders", help="comma-separated confounder columns (psm/iptw)")
    ap.add_argument("--cutoff", type=float, default=0.0, help="RDD cutoff")
    ap.add_argument("--bandwidth", type=float, help="RDD bandwidth (default: full sample)")
    ap.add_argument("--caliper", type=float, default=0.2, help="PSM caliper in SD units")
    ap.add_argument("--truncate", type=float, default=0.0, help="IPTW weight truncation quantile")
    ap.add_argument("--risk-ratio", type=float, help="risk ratio for evalue")
    ap.add_argument("--confidence-limit", type=float, help="confidence limit closest to 1 for evalue")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs")
    args = ap.parse_args(argv)

    try:
        if not 0 < args.alpha < 1:
            raise ValueError("alpha must be in (0, 1)")

        if args.method == "evalue":
            if args.risk_ratio is None:
                raise ValueError("--risk-ratio is required for --method evalue")
            result = evalue(args.risk_ratio, args.confidence_limit)
            ensure_output_path(args.out, [], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "causal-e-value",
                "tool_version": VERSION,
                **result,
                "warnings": [
                    "Applies to risk-ratio scale inputs only; odds/hazard ratios require justified approximation or conversion outside this tool.",
                    "An E-value quantifies one unmeasured-confounding strength benchmark; it does not prove identification, exchangeability, or causal validity.",
                ],
            }
            write_json(args.out, artifact)
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

        if not args.data:
            raise ValueError("--data is required for design-based methods")
        source = Path(args.data).resolve(strict=True)
        payload = json.loads(source.read_text(encoding="utf-8"))
        rows = payload.get("rows") or (payload if isinstance(payload, list) else None)
        if not isinstance(rows, list):
            raise ValueError("data must be a list or an object with a 'rows' list")

        if args.method == "psm":
            for required in (args.treatment, args.outcome, args.confounders):
                if not required:
                    raise ValueError("--treatment, --outcome, --confounders required for psm")
            confounders = [c.strip() for c in args.confounders.split(",") if c.strip()]
            result = psm(rows, args.treatment, args.outcome, confounders, args.caliper, args.alpha)
        elif args.method == "iptw":
            for required in (args.treatment, args.outcome, args.confounders):
                if not required:
                    raise ValueError("--treatment, --outcome, --confounders required for iptw")
            confounders = [c.strip() for c in args.confounders.split(",") if c.strip()]
            result = iptw(rows, args.treatment, args.outcome, confounders, args.truncate, args.alpha)
        elif args.method == "did":
            for required in (args.treatment, args.outcome, args.time):
                if not required:
                    raise ValueError("--treatment, --outcome, --time required for did")
            result = did(rows, args.treatment, args.outcome, args.time, args.alpha)
        else:  # rdd
            for required in (args.running, args.outcome):
                if not required:
                    raise ValueError("--running, --outcome required for rdd")
            result = rdd(rows, args.running, args.outcome, args.cutoff, args.bandwidth, args.alpha)

        ensure_output_path(args.out, [str(source)], args.force)
        artifact = {
            "schema_version": "1.0.0",
            "artifact_type": "causal-estimate",
            "tool_version": VERSION,
            "source": str(source),
            **result,
            "warnings": [
                "Estimates rely on unverifiable design assumptions (exchangeability, overlap, parallel trends, continuity). They do not prove causality.",
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
