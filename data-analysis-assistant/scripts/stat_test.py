"""Statistical test dispatcher for research data.

Purpose:
    Run a named statistical test on a CSV file, compute the effect size, and
    emit a structured result (statistic, p-value, effect size) plus a Chinese
    conclusion template following the reporting rules in
    references/test-selection.md (non-significant != no difference;
    multiple-comparison reminder). The script is fully deterministic.

Dependencies:
    numpy, scipy  ->  install once with:  pip install scipy numpy

CLI usage:
    python3 stat_test.py data.csv --test <name> [options]

    Group comparisons (require --value and --group):
      ttest        two-group t-test; --paired for ttest_rel, --welch for
                   Welch (unequal variances). Effect size: Cohen's d.
      mannwhitney  Mann-Whitney U (two groups). Effect size: rank-biserial r.
      anova        one-way ANOVA (2+ groups). Effect size: eta squared.
      kruskal      Kruskal-Wallis (2+ groups). Effect size: eta squared (H).
    Categorical association (require --col1 and --col2):
      chi2         chi-square test of independence. Effect size: Cramer's V.
      fisher       Fisher's exact test (2x2 tables only). Effect size: odds ratio.
    Correlation (require --x and --y):
      pearson      Pearson correlation (r is the effect size).
      spearman     Spearman rank correlation (rho is the effect size).
    Assumption checks:
      shapiro      Shapiro-Wilk normality (--value; --group -> per group).
      levene       Levene variance homogeneity (--value and --group).
    Multiple-comparison correction (no CSV needed):
      adjust       correct a list of p-values; requires
                   --method bonferroni|holm|fdr_bh and
                   --pvalues "0.01,0.04,0.20" (comma-separated).
                   Outputs per-p-value adjusted values and significance.

    Confidence intervals: ttest and pearson results include a 95% CI
    (mean difference / correlation coefficient) via scipy's
    result.confidence_interval(); --ci 0.90 changes the level.

    Common options: --alpha 0.05  --alternative two-sided|less|greater
                    --ci 0.95  --delimiter ,  --encoding utf-8
                    --format json|md

Output format:
    JSON (--format json, default) or Markdown (--format md):
      {test, statistic, p_value, alpha, significant, effect_size: {name, value,
      magnitude}, confidence_interval: {parameter, level, low, high} (when
      available), groups/columns context, conclusion (Chinese template),
      reminders: [multiple-comparison / power disclaimers]}
    For --test adjust: {test, method, alpha, n_tests, results: [{label, p_value,
      p_adjusted, significant}], conclusion, reminders}
    Exit code 0 on success, 1 on bad input, 2 on missing dependencies.
"""

import argparse
import csv
import json
import sys

try:
    import numpy as np
    from scipy import stats
except ImportError:
    sys.stderr.write("error: numpy and scipy are required. Install with: pip install scipy numpy\n")
    sys.exit(2)

MISSING = {"", "na", "n/a", "nan", "null", "none", "-"}


def load_csv(path, delimiter, encoding):
    with open(path, newline="", encoding=encoding) as f:
        rows = list(csv.reader(f, delimiter=delimiter))
    if len(rows) < 2:
        raise SystemExit("error: CSV needs a header row and at least one data row")
    header, data = rows[0], rows[1:]
    return header, data


def get_col(header, data, name):
    if name not in header:
        raise SystemExit(f"error: column '{name}' not found. Available: {header}")
    i = header.index(name)
    return [r[i].strip() if i < len(r) else "" for r in data]


def numeric_col(header, data, name):
    vals = []
    for v in get_col(header, data, name):
        if v.lower() in MISSING:
            vals.append(np.nan)
        else:
            try:
                vals.append(float(v))
            except ValueError:
                raise SystemExit(f"error: column '{name}' is not numeric (bad value: {v!r})")
    return np.array(vals, dtype=float)


def split_groups(header, data, value_col, group_col):
    vals = numeric_col(header, data, value_col)
    groups = get_col(header, data, group_col)
    out = {}
    for v, g in zip(vals, groups):
        if g.lower() in MISSING or np.isnan(v):
            continue
        out.setdefault(g, []).append(v)
    return {g: np.array(vs) for g, vs in sorted(out.items())}


def require_n_groups(groups, n=None):
    if n is not None and len(groups) != n:
        raise SystemExit(f"error: test needs exactly {n} groups, got {len(groups)}: {list(groups)}")
    if n is None and len(groups) < 2:
        raise SystemExit(f"error: test needs at least 2 groups, got {len(groups)}")


def cohens_d(a, b):
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    if pooled == 0:
        return 0.0
    return float((a.mean() - b.mean()) / pooled)


def d_magnitude(d):
    d = abs(d)
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def eta2_magnitude(e):
    if e < 0.01:
        return "negligible"
    if e < 0.06:
        return "small"
    if e < 0.14:
        return "medium"
    return "large"


def r_magnitude(r):
    r = abs(r)
    if r < 0.1:
        return "negligible"
    if r < 0.3:
        return "small"
    if r < 0.5:
        return "medium"
    return "large"


def cramers_v_magnitude(v):
    if v < 0.1:
        return "negligible"
    if v < 0.3:
        return "small"
    if v < 0.5:
        return "medium"
    return "large"


def fmt_p(p):
    return f"{p:.4g}" if p >= 0.0001 else "<0.0001"


def verdict(p, alpha):
    return "显著" if p < alpha else "不显著"


def build_result(test, statistic, p_value, alpha, effect, context, extra_reminders=()):
    sig = p_value < alpha
    es = f"，效应量 {effect['name']} = {effect['value']:.3f}（{effect['magnitude']}）" if effect else ""
    if sig:
        conclusion = (f"{test}：差异/关联具有统计学意义（统计量 = {statistic:.4g}，"
                      f"p = {fmt_p(p_value)}{es}，α = {alpha}）。")
    else:
        conclusion = (f"{test}：未发现统计学显著差异/关联（统计量 = {statistic:.4g}，"
                      f"p = {fmt_p(p_value)}{es}，α = {alpha}）。")
    reminders = list(extra_reminders)
    if not sig:
        reminders.append("注意：不显著 ≠ 无差异——可能是样本量不足（统计功效不够）或效应本身较小，请勿表述为“两组无差异”。")
    reminders.append("若对同一数据做了多次检验（多指标/两两比较/亚组分析），必须进行多重比较校正（Bonferroni 或 Benjamini-Hochberg FDR）；未校正的结果应视为探索性结论。可用 stat_test.py --test adjust --method holm --pvalues \"p1,p2,...\" 计算校正后 p 值。")
    return {
        "test": test,
        "statistic": round(float(statistic), 6),
        "p_value": float(p_value),
        "alpha": alpha,
        "significant": bool(sig),
        "effect_size": effect,
        "context": context,
        "conclusion": conclusion,
        "reminders": reminders,
    }


def attach_ci(result, ci, parameter, level):
    result["confidence_interval"] = {
        "parameter": parameter, "level": level,
        "low": round(float(ci.low), 6), "high": round(float(ci.high), 6),
    }
    return result


def run_ttest(header, data, args):
    groups = split_groups(header, data, args.value, args.group)
    require_n_groups(groups, 2)
    (g1, a), (g2, b) = groups.items()
    if args.paired:
        if len(a) != len(b):
            raise SystemExit("error: paired t-test requires equal group sizes")
        res = stats.ttest_rel(a, b, alternative=args.alternative)
        d = float((a - b).mean() / (a - b).std(ddof=1)) if (a - b).std(ddof=1) > 0 else 0.0
        name = "paired t-test (ttest_rel)"
    else:
        res = stats.ttest_ind(a, b, equal_var=not args.welch, alternative=args.alternative)
        d = cohens_d(a, b)
        name = "Welch's t-test" if args.welch else "Student's t-test (ttest_ind)"
    effect = {"name": "Cohen's d", "value": round(d, 6), "magnitude": d_magnitude(d)}
    ctx = {"value": args.value, "group": args.group,
           "groups": {g1: int(len(a)), g2: int(len(b))},
           "means": {g1: round(float(a.mean()), 6), g2: round(float(b.mean()), 6)}}
    r = build_result(name, res.statistic, res.pvalue, args.alpha, effect, ctx)
    return attach_ci(r, res.confidence_interval(args.ci),
                     "mean difference" if not args.paired else "mean of paired differences",
                     args.ci)


def run_mannwhitney(header, data, args):
    groups = split_groups(header, data, args.value, args.group)
    require_n_groups(groups, 2)
    (g1, a), (g2, b) = groups.items()
    res = stats.mannwhitneyu(a, b, alternative=args.alternative)
    rbc = 1 - 2 * float(res.statistic) / (len(a) * len(b))  # rank-biserial correlation
    effect = {"name": "rank-biserial r", "value": round(rbc, 6), "magnitude": r_magnitude(rbc)}
    ctx = {"value": args.value, "group": args.group,
           "groups": {g1: int(len(a)), g2: int(len(b))},
           "medians": {g1: round(float(np.median(a)), 6), g2: round(float(np.median(b)), 6)}}
    r = build_result("Mann-Whitney U (mannwhitneyu)", res.statistic, res.pvalue,
                     args.alpha, effect, ctx)
    r["reminders"].insert(0, "该检验为非参数检验：通常因数据不满足正态性而选用，报告中请说明原因（如 Shapiro-Wilk 结果）。")
    return r


def run_anova(header, data, args):
    groups = split_groups(header, data, args.value, args.group)
    require_n_groups(groups)
    res = stats.f_oneway(*groups.values())
    allv = np.concatenate(list(groups.values()))
    grand = allv.mean()
    ss_between = sum(len(v) * (v.mean() - grand) ** 2 for v in groups.values())
    ss_total = ((allv - grand) ** 2).sum()
    eta2 = float(ss_between / ss_total) if ss_total > 0 else 0.0
    effect = {"name": "eta squared", "value": round(eta2, 6), "magnitude": eta2_magnitude(eta2)}
    ctx = {"value": args.value, "group": args.group,
           "groups": {g: int(len(v)) for g, v in groups.items()}}
    r = build_result("one-way ANOVA (f_oneway)", res.statistic, res.pvalue,
                     args.alpha, effect, ctx)
    r["reminders"].insert(0, "ANOVA 显著后需做事后检验（如 Tukey HSD）定位差异组，并对两两比较做校正。")
    return r


def run_kruskal(header, data, args):
    groups = split_groups(header, data, args.value, args.group)
    require_n_groups(groups)
    res = stats.kruskal(*groups.values())
    n = sum(len(v) for v in groups.values())
    k = len(groups)
    eta2h = max(0.0, (float(res.statistic) - k + 1) / (n - k))
    effect = {"name": "eta squared (H)", "value": round(eta2h, 6), "magnitude": eta2_magnitude(eta2h)}
    ctx = {"value": args.value, "group": args.group,
           "groups": {g: int(len(v)) for g, v in groups.items()}}
    r = build_result("Kruskal-Wallis (kruskal)", res.statistic, res.pvalue,
                     args.alpha, effect, ctx)
    r["reminders"].insert(0, "该检验为非参数检验：通常因数据不满足正态性而选用；显著后两两比较（Mann-Whitney U）必须校正。")
    return r


def build_table(header, data, args):
    c1, c2 = get_col(header, data, args.col1), get_col(header, data, args.col2)
    pairs = [(a, b) for a, b in zip(c1, c2)
             if a.lower() not in MISSING and b.lower() not in MISSING]
    if not pairs:
        raise SystemExit("error: no complete rows for the two categorical columns")
    l1 = sorted({a for a, _ in pairs})
    l2 = sorted({b for _, b in pairs})
    table = np.zeros((len(l1), len(l2)), dtype=int)
    for a, b in pairs:
        table[l1.index(a), l2.index(b)] += 1
    return table, l1, l2


def run_chi2(header, data, args):
    table, l1, l2 = build_table(header, data, args)
    res = stats.chi2_contingency(table)
    n = table.sum()
    v = float(np.sqrt(res.statistic / (n * (min(table.shape) - 1)))) if min(table.shape) > 1 else 0.0
    effect = {"name": "Cramer's V", "value": round(v, 6), "magnitude": cramers_v_magnitude(v)}
    ctx = {"col1": args.col1, "col2": args.col2, "levels1": l1, "levels2": l2,
           "table": table.tolist()}
    small = (res.expected_freq < 5).mean()
    reminders = []
    if small > 0.2 or (res.expected_freq < 1).any():
        reminders.append(f"警告：{small:.0%} 的格子期望频数 < 5（或有 < 1），卡方近似不可靠，建议改用 Fisher 精确检验（2x2 表）。")
    r = build_result("chi-square test of independence (chi2_contingency)",
                     res.statistic, res.pvalue, args.alpha, effect, ctx, reminders)
    return r


def run_fisher(header, data, args):
    table, l1, l2 = build_table(header, data, args)
    if table.shape != (2, 2):
        raise SystemExit(f"error: fisher_exact requires a 2x2 table, got {table.shape}")
    odds, p = stats.fisher_exact(table, alternative=args.alternative)
    effect = {"name": "odds ratio", "value": round(float(odds), 6), "magnitude": "n/a"}
    ctx = {"col1": args.col1, "col2": args.col2, "levels1": l1, "levels2": l2,
           "table": table.tolist()}
    return build_result("Fisher's exact test (fisher_exact)", odds, p, args.alpha, effect, ctx)


def run_correlation(header, data, args, method):
    x = numeric_col(header, data, args.x)
    y = numeric_col(header, data, args.y)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    if len(x) < 3:
        raise SystemExit("error: need at least 3 complete pairs")
    res = (stats.pearsonr if method == "pearson" else stats.spearmanr)(x, y)
    ename = "r" if method == "pearson" else "rho"
    effect = {"name": ename, "value": round(float(res.statistic), 6),
              "magnitude": r_magnitude(res.statistic)}
    ctx = {"x": args.x, "y": args.y, "n": int(len(x))}
    name = "Pearson correlation (pearsonr)" if method == "pearson" else "Spearman correlation (spearmanr)"
    r = build_result(name, res.statistic, res.pvalue, args.alpha, effect, ctx)
    r["reminders"].append("相关不等于因果：显著相关不能推出因果关系。")
    if method == "pearson":
        attach_ci(r, res.confidence_interval(args.ci), "Pearson r", args.ci)
    return r


def run_shapiro(header, data, args):
    if args.group:
        groups = split_groups(header, data, args.value, args.group)
    else:
        v = numeric_col(header, data, args.value)
        groups = {"(all)": v[~np.isnan(v)]}
    out = {}
    all_normal = True
    for g, vals in groups.items():
        if len(vals) < 3:
            out[g] = {"error": "need at least 3 values"}
            continue
        res = stats.shapiro(vals)
        normal = res.pvalue > args.alpha
        all_normal = all_normal and normal
        out[g] = {"n": int(len(vals)), "W": round(float(res.statistic), 6),
                  "p_value": float(res.pvalue),
                  "normal_at_alpha": bool(normal)}
    return {
        "test": "Shapiro-Wilk normality (shapiro)",
        "alpha": args.alpha,
        "all_groups_normal": bool(all_normal),
        "groups": out,
        "conclusion": ("各组均满足正态性假设（p > α），可选用参数检验。"
                       if all_normal else
                       "至少一组不满足正态性假设（p ≤ α），建议改用非参数检验（两组：Mann-Whitney；多组：Kruskal-Wallis；相关：Spearman）。"),
        "reminders": ["样本量 < 30 时 Shapiro-Wilk 功效低，建议结合直方图/Q-Q 图判断。"],
    }


def run_levene(header, data, args):
    groups = split_groups(header, data, args.value, args.group)
    require_n_groups(groups)
    res = stats.levene(*groups.values())
    equal = res.pvalue > args.alpha
    return {
        "test": "Levene variance homogeneity (levene)",
        "statistic": round(float(res.statistic), 6),
        "p_value": float(res.pvalue),
        "alpha": args.alpha,
        "equal_variances": bool(equal),
        "groups": {g: int(len(v)) for g, v in groups.items()},
        "conclusion": ("方差齐性成立（p > α），两组比较可用 Student's t 检验。"
                       if equal else
                       "方差齐性不成立（p ≤ α），两组比较请用 Welch t 检验（--welch）。"),
        "reminders": [],
    }


def adjust_pvalues(pvals, method):
    """Return adjusted p-values in the original order.

    bonferroni: p * m (capped at 1)
    holm:       step-down; adjusted[i] = max_{k<=i} min(1, (m-k) * p_sorted[k])
    fdr_bh:     Benjamini-Hochberg step-up; adjusted[i] = min_{k>=i} min(1, m/k * p_sorted[k])
    """
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj_sorted = [0.0] * m
    if method == "bonferroni":
        return [min(1.0, p * m) for p in pvals]
    if method == "holm":
        running = 0.0
        for rank, idx in enumerate(order):
            running = max(running, min(1.0, (m - rank) * pvals[idx]))
            adj_sorted[rank] = running
    elif method == "fdr_bh":
        running = 1.0
        for rank in range(m - 1, -1, -1):
            running = min(running, m / (rank + 1) * pvals[order[rank]])
            adj_sorted[rank] = running
    out = [0.0] * m
    for rank, idx in enumerate(order):
        out[idx] = adj_sorted[rank]
    return out


METHOD_NAMES = {"bonferroni": "Bonferroni", "holm": "Holm", "fdr_bh": "Benjamini-Hochberg FDR"}


def run_adjust(args):
    if not args.pvalues:
        raise SystemExit("error: --test adjust requires --pvalues \"p1,p2,...\"")
    try:
        pvals = [float(x) for x in args.pvalues.split(",") if x.strip() != ""]
    except ValueError:
        raise SystemExit("error: --pvalues must be comma-separated numbers")
    if not pvals:
        raise SystemExit("error: --pvalues is empty")
    if any(p < 0 or p > 1 for p in pvals):
        raise SystemExit("error: all p-values must be within [0, 1]")
    labels = [x.strip() for x in args.labels.split(",")] if args.labels else []
    if labels and len(labels) != len(pvals):
        raise SystemExit("error: --labels count must match --pvalues count")
    adj = adjust_pvalues(pvals, args.method)
    results = [{
        "label": labels[i] if labels else f"test_{i + 1}",
        "p_value": pvals[i],
        "p_adjusted": round(adj[i], 6),
        "significant": bool(adj[i] < args.alpha),
    } for i in range(len(pvals))]
    n_sig = sum(1 for r in results if r["significant"])
    return {
        "test": f"multiple-comparison correction ({METHOD_NAMES[args.method]})",
        "method": args.method,
        "alpha": args.alpha,
        "n_tests": len(pvals),
        "n_significant_after_correction": n_sig,
        "results": results,
        "conclusion": (f"经 {METHOD_NAMES[args.method]} 校正后（α = {args.alpha}），"
                       f"{len(pvals)} 个检验中有 {n_sig} 个保持显著。校正后的 p 值见 results。"),
        "reminders": [
            "Bonferroni/Holm 控制族错误率（FWER），适用于少量验证性检验；BH-FDR 控制错误发现率，适用于大量探索性检验。",
            "报告中须写明校正方法与校正后 p 值，如 “Holm-corrected p = .04”。",
        ],
    }


def to_markdown(r):
    lines = [f"# Statistical Test Report", ""]
    lines.append(f"- Test: {r['test']}")
    if "statistic" in r:
        lines.append(f"- Statistic: {r['statistic']} | p = {fmt_p(r['p_value'])} | "
                     f"alpha = {r['alpha']} | significant: {r['significant']}")
    if r.get("effect_size"):
        e = r["effect_size"]
        lines.append(f"- Effect size: {e['name']} = {e['value']} ({e['magnitude']})")
    if r.get("confidence_interval"):
        c = r["confidence_interval"]
        lines.append(f"- {c['level']:.0%} CI for {c['parameter']}: [{c['low']}, {c['high']}]")
    if r.get("results"):
        lines += ["", "| Test | p | p adjusted | Significant |", "|---|---|---|---|---|"]
        for row in r["results"]:
            lines.append(f"| {row['label']} | {row['p_value']:.4g} "
                         f"| {row['p_adjusted']:.4g} | {row['significant']} |")
    lines += ["", "## 结论", "", r["conclusion"]]
    if r.get("reminders"):
        lines += ["", "## 注意事项", ""]
        lines += [f"- {m}" for m in r["reminders"]]
    return "\n".join(lines)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?", help="input CSV (not needed for --test adjust)")
    ap.add_argument("--test", required=True,
                    choices=["ttest", "mannwhitney", "anova", "kruskal",
                             "chi2", "fisher", "pearson", "spearman",
                             "shapiro", "levene", "adjust"])
    ap.add_argument("--value", help="numeric value column")
    ap.add_argument("--group", help="categorical group column")
    ap.add_argument("--col1", help="first categorical column (chi2/fisher)")
    ap.add_argument("--col2", help="second categorical column (chi2/fisher)")
    ap.add_argument("--x", help="first numeric column (correlation)")
    ap.add_argument("--y", help="second numeric column (correlation)")
    ap.add_argument("--paired", action="store_true", help="paired t-test")
    ap.add_argument("--welch", action="store_true", help="Welch t-test (unequal variances)")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--alternative", choices=["two-sided", "less", "greater"],
                    default="two-sided")
    ap.add_argument("--ci", type=float, default=0.95, help="confidence level for CIs (ttest, pearson)")
    ap.add_argument("--method", choices=["bonferroni", "holm", "fdr_bh"],
                    default="holm", help="correction method (--test adjust)")
    ap.add_argument("--pvalues", help="comma-separated p-values (--test adjust)")
    ap.add_argument("--labels", help="comma-separated test labels (--test adjust)")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--encoding", default="utf-8")
    ap.add_argument("--format", choices=["json", "md"], default="json")
    args = ap.parse_args(argv)

    if args.test == "adjust":
        r = run_adjust(args)
        print(json.dumps(r, ensure_ascii=False, indent=2) if args.format == "json" else to_markdown(r))
        return 0
    if not args.file:
        raise SystemExit(f"error: --test {args.test} requires an input CSV file")

    def need(*opts):
        for o in opts:
            if getattr(args, o) is None:
                raise SystemExit(f"error: --test {args.test} requires --{o.replace('_', '-')}")

    header, data = load_csv(args.file, args.delimiter, args.encoding)
    dispatch = {
        "ttest": lambda: (need("value", "group"), run_ttest(header, data, args))[1],
        "mannwhitney": lambda: (need("value", "group"), run_mannwhitney(header, data, args))[1],
        "anova": lambda: (need("value", "group"), run_anova(header, data, args))[1],
        "kruskal": lambda: (need("value", "group"), run_kruskal(header, data, args))[1],
        "chi2": lambda: (need("col1", "col2"), run_chi2(header, data, args))[1],
        "fisher": lambda: (need("col1", "col2"), run_fisher(header, data, args))[1],
        "pearson": lambda: (need("x", "y"), run_correlation(header, data, args, "pearson"))[1],
        "spearman": lambda: (need("x", "y"), run_correlation(header, data, args, "spearman"))[1],
        "shapiro": lambda: (need("value"), run_shapiro(header, data, args))[1],
        "levene": lambda: (need("value", "group"), run_levene(header, data, args))[1],
    }
    r = dispatch[args.test]()
    print(json.dumps(r, ensure_ascii=False, indent=2) if args.format == "json" else to_markdown(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
