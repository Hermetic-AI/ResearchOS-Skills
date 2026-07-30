#!/usr/bin/env python3
"""EFA, reliability, item-total correlations, and basic Rasch fit (stdlib only).

Purpose:
    A zero-dependency psychometric helper. It (1) computes a correlation matrix
    from item-level response data, (2) extracts factors by the principal-factor
    method and rotates loadings with varimax, (3) reports communalities and the
    variance explained, (4) computes Cronbach's alpha, item-total correlations,
    and alpha-if-item-deleted, and (5) fits a basic Rasch (1PL) model via
    joint maximum likelihood and reports item difficulty and person ability with
    simple infit statistics. It does not establish validity, invariance, or
    adequacy for any specific use.

Dependencies:
    None (Python 3.8+ standard library only; matrix ops via nested lists).

CLI usage:
    python3 psychometrics.py --mode efa --csv responses.csv --items q1,q2,q3,q4 \\
        --factors 2 --out efa.json
    python3 psychometrics.py --mode reliability --csv responses.csv --items q1,q2,q3 \\
        --out reliability.json
    python3 psychometrics.py --mode rasch --csv responses.csv --items q1,q2,q3 \\
        --out rasch.json

    Common options: --force  --version  --reverse q4,q5

Output format:
    A JSON artifact per mode with loadings / alpha / item statistics / Rasch
    parameters, plus diagnostics. Every artifact carries schema_version,
    artifact_type, tool_version, and warnings. Exit code 0 on success, 1 on bad
    input.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

VERSION = "0.1.0"

# --- Matrix helpers ----------------------------------------------------------

def matmul(A, B):
    rows_a, cols_a = len(A), len(A[0])
    rows_b, cols_b = len(B), len(B[0])
    if cols_a != rows_b:
        raise ValueError("inner matrix dimensions do not match")
    Bt = [[B[i][j] for i in range(rows_b)] for j in range(cols_b)]
    return [[sum(a * b for a, b in zip(A[i], Bt[j])) for j in range(cols_b)] for i in range(rows_a)]


def transpose(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def clone_matrix(A):
    return [list(row) for row in A]


def eigen_2x2(M):
    a, b, c, d = M[0][0], M[0][1], M[1][0], M[1][1]
    trace = a + d
    det = a * d - b * c
    disc = trace * trace - 4 * det
    if disc < 0:
        disc = 0.0
    sqrt_disc = math.sqrt(disc)
    lam1 = (trace + sqrt_disc) / 2.0
    lam2 = (trace - sqrt_disc) / 2.0
    # Eigenvectors.
    def vec(lam):
        if abs(b) > 1e-9:
            return [lam - d, b]
        if abs(c) > 1e-9:
            return [c, lam - a]
        return [1.0, 0.0]
    v1 = vec(lam1)
    v2 = vec(lam2)
    norm = math.hypot(v1[0], v1[1]) or 1.0
    v1 = [v1[0] / norm, v1[1] / norm]
    norm = math.hypot(v2[0], v2[1]) or 1.0
    v2 = [v2[0] / norm, v2[1] / norm]
    return (lam1, v1), (lam2, v2)


def power_iteration(M, iterations=100):
    """Return the dominant eigenvalue/eigenvector of a symmetric matrix."""
    n = len(M)
    vec = [1.0 / math.sqrt(n)] * n
    for _ in range(iterations):
        new = [sum(M[i][j] * vec[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in new)) or 1.0
        vec = [x / norm for x in new]
    av = [sum(M[i][j] * vec[j] for j in range(n)) for i in range(n)]
    lam = sum(vec[i] * av[i] for i in range(n))
    return lam, vec


def deflate(M, lam, vec):
    n = len(M)
    return [[M[i][j] - lam * vec[i] * vec[j] for j in range(n)] for i in range(n)]


def top_k_eigen(M, k, iterations=200):
    """Return the top-k (eigenvalue, eigenvector) pairs of a symmetric matrix."""
    Mc = clone_matrix(M)
    pairs = []
    for _ in range(k):
        lam, vec = power_iteration(Mc, iterations=iterations)
        pairs.append((lam, vec))
        Mc = deflate(Mc, lam, vec)
    return pairs


# --- Data loading ----------------------------------------------------------

def load_items(csv_path, items, reverse=None):
    reverse = set(reverse or [])
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("CSV has no data rows")
    missing = [c for c in items if c not in rows[0]]
    if missing:
        raise ValueError(f"missing item columns: {missing}")
    max_score = {}
    for row in rows:
        for item in items:
            max_score[item] = max(max_score.get(item, float("-inf")), float(row[item]))
    data = []
    dropped = 0
    for row in rows:
        try:
            vals = []
            for item in items:
                v = float(row[item])
                if item in reverse:
                    v = max_score[item] - v
                vals.append(v)
            data.append(vals)
        except (ValueError, TypeError):
            dropped += 1
    return data, max_score, dropped


def column_means(matrix):
    n = len(matrix)
    k = len(matrix[0])
    return [sum(matrix[i][j] for i in range(n)) / n for j in range(k)]


def correlation_matrix(matrix):
    n = len(matrix)
    k = len(matrix[0])
    means = column_means(matrix)
    sds = []
    for j in range(k):
        var = sum((matrix[i][j] - means[j]) ** 2 for i in range(n)) / (n - 1)
        sds.append(math.sqrt(var) if var > 0 else 0.0)
    corr = [[0.0] * k for _ in range(k)]
    for a in range(k):
        for b in range(k):
            if sds[a] == 0 or sds[b] == 0:
                corr[a][b] = 0.0
            else:
                corr[a][b] = sum((matrix[i][a] - means[a]) * (matrix[i][b] - means[b])
                                 for i in range(n)) / ((n - 1) * sds[a] * sds[b])
            if a == b:
                corr[a][b] = 1.0
    return corr


# --- EFA: principal factor + varimax ----------------------------------------

def principal_factor(corr, factors, iterations=200):
    k = len(corr)
    # Initial communality estimates: squared multiple correlations (use max off-diagonal as simple SMC proxy).
    communalities = []
    for i in range(k):
        others = [corr[i][j] ** 2 for j in range(k) if j != i]
        communalities.append(max(others) if others else 1.0)
    reduced = [[corr[i][j] if i != j else communalities[i] for j in range(k)] for i in range(k)]
    for _ in range(50):
        pairs = top_k_eigen(reduced, factors, iterations=iterations)
        loadings = [[0.0] * factors for _ in range(k)]
        for f, (lam, vec) in enumerate(pairs):
            if lam < 0:
                lam = 0.0
            scale = math.sqrt(lam)
            for i in range(k):
                loadings[i][f] = vec[i] * scale
        new_comm = [sum(loadings[i][f] ** 2 for f in range(factors)) for i in range(k)]
        new_comm = [min(c, 1.0) for c in new_comm]
        if all(abs(new_comm[i] - communalities[i]) < 1e-6 for i in range(k)):
            communalities = new_comm
            break
        communalities = new_comm
        reduced = [[corr[i][j] if i != j else communalities[i] for j in range(k)] for i in range(k)]
    return loadings, communalities, pairs


def varimax(loadings, iterations=200, tol=1e-6):
    k = len(loadings)
    factors = len(loadings[0])
    if factors < 2:
        return loadings
    rotated = clone_matrix(loadings)
    for _ in range(iterations):
        for f1 in range(factors):
            for f2 in range(f1 + 1, factors):
                u = [rotated[i][f1] ** 2 - rotated[i][f2] ** 2 for i in range(k)]
                v = [2 * rotated[i][f1] * rotated[i][f2] for i in range(k)]
                A = sum(u)
                B = sum(v)
                C = sum(ui * ui - vi * vi for ui, vi in zip(u, v))
                D = sum(2 * ui * vi for ui, vi in zip(u, v))
                numer = D - 2 * A * B / k
                denom = C - (A * A - B * B) / k
                if abs(denom) < 1e-12:
                    continue
                phi = 0.25 * math.atan2(numer, denom)
                cos_phi, sin_phi = math.cos(phi), math.sin(phi)
                for i in range(k):
                    l1 = rotated[i][f1]
                    l2 = rotated[i][f2]
                    rotated[i][f1] = l1 * cos_phi + l2 * sin_phi
                    rotated[i][f2] = -l1 * sin_phi + l2 * cos_phi
    return rotated


def run_efa(csv_path, items, factors, reverse=None):
    data, max_score, dropped = load_items(csv_path, items, reverse)
    n = len(data)
    if n < 2:
        raise ValueError("need at least two complete response rows")
    if factors < 1 or factors > len(items):
        raise ValueError("factors must be between 1 and the number of items")
    corr = correlation_matrix(data)
    loadings, communalities, pairs = principal_factor(corr, factors)
    rotated = varimax(loadings)
    eigenvalues = [max(0.0, lam) for lam, _ in pairs]
    total_var = sum(eigenvalues)
    variance_explained = [lam / len(items) for lam in eigenvalues]
    structure = []
    for i, item in enumerate(items):
        structure.append({
            "item": item,
            "communalities": communalities[i],
            "loadings": [rotated[i][f] for f in range(factors)],
        })
    return {
        "n_complete": n,
        "n_dropped": dropped,
        "factors": factors,
        "eigenvalues": eigenvalues,
        "variance_explained": variance_explained,
        "total_variance_explained": sum(variance_explained),
        "loadings": structure,
    }


# --- Reliability -------------------------------------------------------------

def cronbach_alpha(matrix):
    n = len(matrix)
    k = len(matrix[0])
    if k < 2:
        return float("nan"), [float("nan")] * k, [float("nan")] * k, []
    item_variances = []
    for j in range(k):
        col = [matrix[i][j] for i in range(n)]
        item_variances.append(_variance(col))
    totals = [sum(row) for row in matrix]
    total_variance = _variance(totals)
    if total_variance <= 0:
        raise ValueError("total score variance must be positive")
    alpha = k / (k - 1) * (1 - sum(item_variances) / total_variance)
    item_total = []
    for j in range(k):
        col = [matrix[i][j] for i in range(n)]
        rest = [sum(matrix[i][jj] for jj in range(k) if jj != j) for i in range(n)]
        item_total.append(_correlation(col, rest))
    alpha_if_deleted = []
    for j in range(k):
        sub = [[matrix[i][jj] for jj in range(k) if jj != j] for i in range(n)]
        alpha_if_deleted.append(cronbach_alpha(sub))
    return alpha, item_variances, item_total, alpha_if_deleted


def _variance(values):
    m = sum(values) / len(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - 1)


def _correlation(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / (n - 1))
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / (n - 1))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / ((n - 1) * sx * sy)


def run_reliability(csv_path, items, reverse=None):
    data, max_score, dropped = load_items(csv_path, items, reverse)
    n = len(data)
    if n < 2 or len(items) < 2:
        raise ValueError("need at least two items and two complete rows")
    alpha, item_variances, item_total, alpha_if_deleted = cronbach_alpha(data)
    return {
        "n_complete": n,
        "n_dropped": dropped,
        "n_items": len(items),
        "cronbach_alpha": alpha,
        "item_variances": dict(zip(items, item_variances)),
        "item_total_correlations": dict(zip(items, item_total)),
        "alpha_if_item_deleted": dict(zip(items, alpha_if_deleted)),
    }


# --- Rasch (1PL) basic fit ---------------------------------------------------

def run_rasch(csv_path, items, reverse=None, max_iter=50):
    data, max_score, dropped = load_items(csv_path, items, reverse)
    n = len(data)
    k = len(items)
    if n < 2 or k < 2:
        raise ValueError("Rasch needs at least two persons and two items")
    # Dichotomize at the item median for a basic 1PL fit.
    difficulties = [0.0] * k
    abilities = [0.0] * n
    thresholds = []
    for j in range(k):
        col = sorted(data[i][j] for i in range(n))
        median = col[len(col) // 2]
        thresholds.append(median)
    scores = [0] * n
    for i in range(n):
        for j in range(k):
            if data[i][j] >= thresholds[j]:
                scores[i] += 1
    # Joint maximum likelihood (simplified).
    for iteration in range(max_iter):
        # Update person abilities.
        new_abilities = []
        for i in range(n):
            total = 0.0
            for j in range(k):
                p = _rasch_p(abilities[i], difficulties[j])
                total += (1 if data[i][j] >= thresholds[j] else 0) - p
            new_abilities.append(abilities[i] + total / max(k, 1))
        abilities = new_abilities
        # Update item difficulties.
        new_difficulties = []
        for j in range(k):
            total = 0.0
            for i in range(n):
                p = _rasch_p(abilities[i], difficulties[j])
                total += p - (1 if data[i][j] >= thresholds[j] else 0)
            new_difficulties.append(difficulties[j] + total / max(n, 1))
        difficulties = new_difficulties
    # Infit (unweighted mean square) per item.
    item_infit = []
    for j in range(k):
        numerator, denom = 0.0, 0.0
        for i in range(n):
            obs = 1 if data[i][j] >= thresholds[j] else 0
            p = _rasch_p(abilities[i], difficulties[j])
            residual = obs - p
            w = p * (1 - p)
            numerator += w * residual ** 2
            denom += w
        item_infit.append((numerator / denom) if denom > 0 else float("nan"))
    return {
        "n_complete": n,
        "n_dropped": dropped,
        "n_items": k,
        "thresholds": dict(zip(items, thresholds)),
        "item_difficulties": dict(zip(items, difficulties)),
        "item_infit": dict(zip(items, item_infit)),
        "person_abilities_mean": sum(abilities) / n,
        "person_abilities_sd": math.sqrt(_variance(abilities)) if n > 1 else 0.0,
    }


def _rasch_p(theta, beta):
    x = theta - beta
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


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
    ap.add_argument("--mode", choices=["efa", "reliability", "rasch"], required=True)
    ap.add_argument("--csv", required=True, help="item-level response CSV")
    ap.add_argument("--items", required=True, help="comma-separated item columns")
    ap.add_argument("--factors", type=int, default=2, help="number of factors (efa)")
    ap.add_argument("--reverse", default="", help="comma-separated reverse-scored items")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs")
    args = ap.parse_args(argv)

    try:
        items = [c.strip() for c in args.items.split(",") if c.strip()]
        reverse = [c.strip() for c in args.reverse.split(",") if c.strip()] if args.reverse else []
        if len(items) < 2:
            raise ValueError("--items needs at least two columns")
        source = Path(args.csv).resolve(strict=True)

        if args.mode == "efa":
            result = run_efa(str(source), items, args.factors, reverse)
        elif args.mode == "reliability":
            result = run_reliability(str(source), items, reverse)
        else:
            result = run_rasch(str(source), items, reverse)

        ensure_output_path(args.out, [str(source)], args.force)
        artifact = {
            "schema_version": "1.0.0",
            "artifact_type": f"psychometrics-{args.mode}",
            "tool_version": VERSION,
            "source": str(source),
            **result,
            "warnings": [
                "Results are descriptive and depend on sample, item quality, and model assumptions; they do not establish validity, invariance, or adequacy for any specific use.",
            ],
        }
        write_json(args.out, artifact)
        print(json.dumps(artifact, ensure_ascii=False, indent=2))
        return 0

    except (OSError, ValueError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
