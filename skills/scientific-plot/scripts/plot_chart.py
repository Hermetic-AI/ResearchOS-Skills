#!/usr/bin/env python3
"""Publication-grade statistical charts from CSV (Prism/Origin/Excel replacement).

Purpose: render chart templates (grouped_bar, scatter_regression, line,
paired_points, boxplot, violin, raincloud, heatmap, survival, forest, volcano, manhattan, pca, umap, enrichment_bubble, network, sankey) under four journal themes (nature, science, ieee,
prism), with error bars (sd/sem/ci95), scipy significance-star brackets, and
multi-panel canvases. Vector-first export: SVG + PDF + PNG (300 DPI).

Dependencies: matplotlib, numpy (pip install matplotlib numpy);
scipy is required only for --compare-groups (pip install scipy).

CLI:
  python3 plot_chart.py data.csv --template grouped_bar --x condition --y score \
      --group treatment --error sem --theme nature --column single --out fig1
  python3 plot_chart.py data.csv --template violin --x group --y value \
      --compare-groups --control placebo --seed 42 --out fig2
  python3 plot_chart.py data.csv --theme science --out fig3 \
      --panel "boxplot|cond|val" --panel "scatter_regression|dose|val"
  python3 plot_chart.py surv.csv --template survival --time days --event dead \
      --group arm --out fig4

Output: <out>.svg, <out>.pdf, <out>.png (300 dpi), and <out>.stats.json with
descriptives, regression coefficients, and test results (test name, statistic,
exact p, star symbol) for the figure caption.
"""

import argparse
import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MM = 1 / 25.4
COLUMN_IN = {"single": 89 * MM, "double": 183 * MM}

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442"]
PALETTES = {
    "nature": OKABE_ITO,
    "science": ["#3B4CC0", "#E18700", "#4A9B5E", "#B40426", "#7F7F7F", "#00A0B0"],
    "ieee": ["#262626", "#737373", "#B8B8B8", "#000000", "#969696", "#D9D9D9"],
    "prism": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
}
IEEE_LINESTYLES = ["-", "--", ":", "-."]
IEEE_HATCHES = ["", "//", "\\\\", "xx", "..", "++"]

_EXTRA_PALETTES = None


def _load_extra_palettes():
    """Named discrete palettes from scripts/palettes.json (ggsci / grDevices /
    RColorBrewer / zhihu-curated top-journal schemes)."""
    global _EXTRA_PALETTES
    if _EXTRA_PALETTES is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "palettes.json")
        try:
            with open(path, encoding="utf-8") as f:
                _EXTRA_PALETTES = json.load(f)["palettes"]
        except OSError:
            _EXTRA_PALETTES = {}
    return _EXTRA_PALETTES


def resolve_palette(args):
    """Series colors for this run: --palette NAME overrides the theme default."""
    name = getattr(args, "palette", None)
    if not name:
        return PALETTES[args.theme]
    extra = _load_extra_palettes()
    if name in extra:
        return extra[name]["colors"]
    # forgiving lookup: case-insensitive, ignore spaces/underscores/dashes
    norm = name.lower().replace(" ", "").replace("_", "").replace("-", "")
    for key, val in extra.items():
        if key.lower().replace(" ", "").replace("_", "").replace("-", "") == norm:
            return val["colors"]
    if name in PALETTES:
        return PALETTES[name]
    sys.exit(f"unknown palette {name!r}; run --list-palettes to see options")

THEMES = {
    "nature": {
        "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.linewidth": 0.6, "lines.linewidth": 1.0, "lines.markersize": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.direction": "out", "ytick.direction": "out",
        "axes.grid": False, "legend.frameon": False, "font.family": "sans-serif",
    },
    "science": {
        "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.linewidth": 0.7, "lines.linewidth": 1.0, "lines.markersize": 3,
        "xtick.major.width": 0.7, "ytick.major.width": 0.7,
        "xtick.direction": "out", "ytick.direction": "out",
        "axes.grid": False, "legend.frameon": False, "font.family": "sans-serif",
    },
    "ieee": {
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.linewidth": 0.8, "lines.linewidth": 1.0, "lines.markersize": 4,
        "xtick.direction": "in", "ytick.direction": "in",
        "axes.grid": True, "grid.linewidth": 0.4, "grid.alpha": 0.4,
        "legend.frameon": True, "font.family": "serif",
    },
    "prism": {
        "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.linewidth": 1.0, "lines.linewidth": 1.5, "lines.markersize": 5,
        "xtick.direction": "out", "ytick.direction": "out",
        "axes.grid": False, "legend.frameon": False, "font.family": "sans-serif",
    },
}
EXPORT_RC = {"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.add_argument("csv", nargs="?", help="input CSV file")
    p.add_argument("--template", choices=["grouped_bar", "scatter_regression", "line", "paired_points", "boxplot", "violin", "raincloud", "heatmap", "survival", "forest", "roc", "pr", "calibration", "funnel", "volcano", "manhattan", "pca", "umap", "enrichment_bubble", "network", "sankey"])
    p.add_argument("--x"), p.add_argument("--y"), p.add_argument("--group"), p.add_argument("--z")
    p.add_argument("--time"), p.add_argument("--event"), p.add_argument("--id", help="subject ID required by paired_points")
    p.add_argument("--ci-low", help="lower confidence-limit column required by forest")
    p.add_argument("--ci-high", help="upper confidence-limit column required by forest")
    p.add_argument("--no-survival-ci", action="store_true", help="omit Greenwood 95%% confidence bands for survival curves")
    p.add_argument("--risk-table", action="store_true", help="add number-at-risk table below survival curves")
    p.add_argument("--error", choices=["sd", "sem", "ci95", "none"], default="sd")
    p.add_argument("--theme", choices=list(THEMES), default="nature")
    p.add_argument("--palette", help="named discrete palette overriding the theme colors "
                                     "(e.g. npg, aaas, nejm, lancet, jama, Okabe-Ito, Set1, zhihu-29); "
                                     "see --list-palettes and references/color-palettes.md")
    p.add_argument("--list-palettes", action="store_true", help="print available palette names and exit")
    p.add_argument("--column", choices=list(COLUMN_IN), default="single")
    p.add_argument("--compare-groups", action="store_true", help="run scipy tests and draw star brackets")
    p.add_argument("--control", help="compare all groups against this one instead of all pairs")
    p.add_argument("--test", choices=["auto", "ttest", "mannwhitney"], default="auto")
    p.add_argument("--stars", help='manual stars, e.g. "A>B:**;A>C:ns" (skips testing)')
    p.add_argument("--hide-ns", action="store_true")
    p.add_argument("--star-step", type=float, default=0.05, help="bracket step as fraction of y-range")
    p.add_argument("--panel", action="append", default=[], help='multi-panel spec "template|x|y[|group[|z]]"; repeatable')
    p.add_argument("--shared-legend", action="store_true", help="collect panel legends into one figure-level legend")
    p.add_argument("--share-x", action="store_true", help="share x-axis limits across multi-panels; use only for compatible scales")
    p.add_argument("--share-y", action="store_true", help="share y-axis limits across multi-panels; use only for compatible scales")
    p.add_argument("--title"), p.add_argument("--xlabel"), p.add_argument("--ylabel")
    p.add_argument("--cmap", default="RdBu_r")
    p.add_argument("--center", type=float, default=0.0)
    p.add_argument("--bins", type=int, default=10, help="number of equal-width probability bins for calibration (2-50)")
    p.add_argument("--p-threshold", type=float, default=0.05, help="reference p-value threshold for volcano plots (0-1)")
    p.add_argument("--effect-threshold", type=float, default=1.0, help="absolute effect threshold for volcano plots (>=0)")
    p.add_argument("--neighbors", type=int, default=15, help="UMAP neighborhood size (2 or greater)")
    p.add_argument("--no-zero-baseline", action="store_true")
    p.add_argument("--overlay-points", action="store_true")
    p.add_argument("--no-overlay-points", action="store_true")
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="figure", help="output basename (no extension)")
    p.add_argument("--formats", default="svg,pdf,png", help="comma-separated Matplotlib formats; use svg,pdf,png by default, or include tiff/eps for journals")
    p.add_argument("--statistics-source", help="validated stat-results JSON used for formal manual annotations")
    p.add_argument("--star-map", help='formal bracket mapping, e.g. "A>B=primary;A>C=secondary"; requires --statistics-source')
    p.add_argument("--manifest-out", help="figure-manifest path (default <out>.manifest.json)")
    p.add_argument("--force", action="store_true", help="replace existing derived figure outputs")
    return p.parse_args()


def load_rows(path, encoding):
    import csv
    with open(path, newline="", encoding=encoding) as f:
        return list(csv.DictReader(f))


def stars_of(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def load_formal_stars(args):
    """Resolve group comparisons to p-values by stable IDs in stat-results."""
    args.formal_stats = []
    if not args.star_map:
        return
    if not args.statistics_source:
        sys.exit("error: --star-map requires --statistics-source")
    if args.stars:
        sys.exit("error: use --stars or --star-map, not both")
    try:
        with open(args.statistics_source, encoding="utf-8") as handle:
            artifact = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: cannot read --statistics-source: {exc}")
    if artifact.get("schema_version") != "1.0.0" or artifact.get("artifact_type") != "stat-results":
        sys.exit("error: --statistics-source must be a ResearchOS stat-results artifact version 1.0.0")
    results = artifact.get("results")
    if not isinstance(results, list):
        sys.exit("error: stat-results artifact has no results list")
    by_id = {}
    for result in results:
        result_id = result.get("id")
        if not result_id or result_id in by_id:
            sys.exit("error: every stat-results row needs a unique non-empty id")
        by_id[result_id] = result
    resolved = []
    for item in args.star_map.split(";"):
        if "=" not in item or ">" not in item.split("=", 1)[0]:
            sys.exit(f"error: invalid --star-map item {item!r}; expected A>B=result_id")
        comparison, result_id = item.rsplit("=", 1)
        g1, g2 = (part.strip() for part in comparison.split(">", 1))
        result_id = result_id.strip()
        if result_id not in by_id:
            sys.exit(f"error: result id {result_id!r} not found in --statistics-source")
        row = by_id[result_id]
        p_value = row.get("adjusted_p_value")
        p_field = "adjusted_p_value"
        if p_value is None:
            p_value = row.get("p_value")
            p_field = "p_value"
        if not isinstance(p_value, (int, float)) or not 0 <= p_value <= 1:
            sys.exit(f"error: result {result_id!r} has no valid p-value")
        symbol = stars_of(float(p_value))
        resolved.append(f"{g1}>{g2}:{symbol}")
        args.formal_stats.append({
            "source": os.path.abspath(args.statistics_source),
            "result_id": result_id,
            "g1": g1,
            "g2": g2,
            "p_field": p_field,
            "p": float(p_value),
            "stars": symbol,
        })
    args.stars = ";".join(resolved)


def group_values(rows, key_col, val_col):
    groups = {}
    for r in rows:
        groups.setdefault(r[key_col], []).append(float(r[val_col]))
    return groups


def error_of(vals, kind, np):
    a = np.asarray(vals, dtype=float)
    sd = float(np.std(a, ddof=1)) if len(a) > 1 else 0.0
    sem = sd / math.sqrt(len(a))
    return {"sd": sd, "sem": sem, "ci95": 1.96 * sem, "none": 0.0}[kind]


def run_tests(groups, args):
    """Return (results, pairs): results for stats JSON, pairs of (g1, g2, symbol) for brackets."""
    try:
        from scipy import stats
    except ImportError:
        sys.exit("scipy is required for --compare-groups: pip install scipy")
    names = list(groups)
    pairs = [(c, n) for c in names for n in names if names.index(c) < names.index(n)]
    if args.control:
        if args.control not in groups:
            sys.exit(f"--control {args.control!r} not found in groups {names}")
        pairs = [(args.control, n) for n in names if n != args.control]
    pairs = pairs[:6]
    results = []
    if len(names) > 2:
        stat, p = stats.f_oneway(*[groups[n] for n in names])
        results.append({"test": "f_oneway", "statistic": float(stat), "p": float(p)})
    for g1, g2 in pairs:
        if len(names) == 2 and args.test == "auto":
            normal = all(len(groups[g]) >= 3 and stats.shapiro(groups[g]).pvalue > 0.05 for g in (g1, g2))
            test = "ttest" if normal else "mannwhitney"
        else:
            test = "ttest" if args.test == "auto" else args.test
        if test == "ttest":
            stat, p = stats.ttest_ind(groups[g1], groups[g2])
        else:
            stat, p = stats.mannwhitneyu(groups[g1], groups[g2])
        results.append({"test": "ttest_ind" if test == "ttest" else "mannwhitneyu",
                        "g1": g1, "g2": g2, "statistic": float(stat), "p": float(p), "stars": stars_of(p)})
    if len(pairs) > 1:
        print(f"warning: {len(pairs)} pairwise tests on the same dataset — apply Holm correction "
              "before choosing stars for publication (see references/significance.md)", file=sys.stderr)
    return results, [(r["g1"], r["g2"], r["stars"]) for r in results if "g1" in r]


def parse_manual_stars(spec):
    pairs = []
    for item in spec.split(";"):
        comp, sym = item.rsplit(":", 1)
        g1, g2 = comp.split(">", 1)
        pairs.append((g1.strip(), g2.strip(), sym.strip()))
    return pairs


def draw_brackets(ax, pairs, positions, tops, y_range, step_frac, hide_ns, fontsize):
    """Non-overlapping star brackets: start at global top + step, stack by step."""
    drawn = [(g1, g2, s) for g1, g2, s in pairs if s != "ns" or not hide_ns]
    for g1, g2, _ in drawn:
        for g in (g1, g2):
            if g not in positions:
                print(f"unknown group {g!r} in --stars (available: {', '.join(positions)})",
                      file=sys.stderr)
                sys.exit(2)
    drawn.sort(key=lambda d: abs(positions[d[1]] - positions[d[0]]))
    levels = []  # levels[lvl] = list of occupied (lo, hi) x-intervals
    y0 = max(tops.values()) + step_frac * y_range
    for g1, g2, sym in drawn:
        p1, p2 = positions[g1], positions[g2]
        lo, hi = min(p1, p2), max(p1, p2)
        lvl = 0
        while lvl < len(levels) and any(not (hi < a or lo > b) for a, b in levels[lvl]):
            lvl += 1
        if lvl == len(levels):
            levels.append([])
        levels[lvl].append((lo, hi))
        y = y0 + lvl * step_frac * y_range
        ax.plot([p1, p1, p2, p2], [y - 0.01 * y_range, y, y, y - 0.01 * y_range],
                lw=0.6, color="black", clip_on=False)
        ax.text((p1 + p2) / 2, y, sym, ha="center", va="bottom", fontsize=fontsize)
    if drawn:
        ax.set_ylim(top=y0 + len(levels) * step_frac * y_range + 0.06 * y_range)


def style_ax(ax, theme):
    if theme in ("nature", "science", "prism"):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)


def plot_grouped_bar(ax, rows, spec, args, np, stats_out):
    xcol, ycol, gcol = spec["x"], spec["y"], spec.get("group")
    palette = resolve_palette(args)
    xs = list(dict.fromkeys(r[xcol] for r in rows))
    if gcol:
        gs = list(dict.fromkeys(r[gcol] for r in rows))
        w = 0.8 / len(gs)
        tops, positions = {}, {}
        for gi, g in enumerate(gs):
            means, errs, xpos = [], [], []
            for xi, x in enumerate(xs):
                vals = [float(r[ycol]) for r in rows if r[xcol] == x and r[gcol] == g]
                means.append(float(np.mean(vals)))
                errs.append(error_of(vals, args.error, np))
                xpos.append(xi + (gi - (len(gs) - 1) / 2) * w)
                positions[f"{x}|{g}"] = xpos[-1]
                tops[f"{x}|{g}"] = means[-1] + errs[-1]
            hatch = IEEE_HATCHES[gi % len(IEEE_HATCHES)] if args.theme == "ieee" else ""
            ax.bar(xpos, means, w * 0.9, yerr=errs, capsize=2, label=g,
                   color=palette[gi % len(palette)], hatch=hatch, edgecolor="black", linewidth=0.5,
                   error_kw=dict(lw=0.7))
        ax.set_xticks(range(len(xs)), xs)
        # outside the axes: bars occupy the full canvas, so any inside legend overlaps
        ax.legend(title=gcol, loc="upper left", bbox_to_anchor=(1.02, 1))
        if args.compare_groups or args.stars:
            pair_specs, tstats = significance_pairs(rows, xcol, ycol, gcol, xs, args)
            stats_out += tstats
            flat_pos, flat_tops = {}, {}
            for x in xs:
                for g in gs:
                    k = f"{x}|{g}"
                    flat_pos[k], flat_tops[k] = positions[k], tops[k]
            flat_pairs = [(f"{a[0]}|{a[1]}", f"{b[0]}|{b[1]}", s) for (a, b, s) in pair_specs]
            yr = ax.get_ylim()[1] - ax.get_ylim()[0]
            draw_brackets(ax, flat_pairs, flat_pos, flat_tops, yr, args.star_step, args.hide_ns,
                          THEMES[args.theme]["font.size"])
    else:
        means = [float(np.mean([float(r[ycol]) for r in rows if r[xcol] == x])) for x in xs]
        errs = [error_of([float(r[ycol]) for r in rows if r[xcol] == x], args.error, np) for x in xs]
        ax.bar(range(len(xs)), means, 0.7, yerr=errs, capsize=2, color=palette[0],
               edgecolor="black", linewidth=0.5, error_kw=dict(lw=0.7))
        ax.set_xticks(range(len(xs)), xs)
        if args.compare_groups or args.stars:
            pair_specs, tstats = significance_pairs(rows, xcol, ycol, None, xs, args)
            stats_out += tstats
            positions = {x: i for i, x in enumerate(xs)}
            tops = {x: means[i] + errs[i] for i, x in enumerate(xs)}
            pairs = [(a[1], b[1], s) for (a, b, s) in pair_specs]
            yr = ax.get_ylim()[1] - ax.get_ylim()[0]
            draw_brackets(ax, pairs, positions, tops, yr, args.star_step, args.hide_ns,
                          THEMES[args.theme]["font.size"])
    if not args.no_zero_baseline:
        ax.set_ylim(bottom=min(0.0, ax.get_ylim()[0]))
    ax.set_xlabel(args.xlabel or xcol)
    ax.set_ylabel(args.ylabel or ycol)


def significance_pairs(rows, xcol, ycol, gcol, xs, args):
    """Build bracket pair list. With groups: compare groups within the FIRST x category
    (multi-x star grids are unreadable; state the chosen category in the caption)."""
    if args.stars:
        raw = parse_manual_stars(args.stars)
        return [((xs[0], a) if gcol else (None, a), (xs[0], b) if gcol else (None, b), s) for a, b, s in raw], []
    key = gcol or xcol
    subset = [r for r in rows if r[xcol] == xs[0]] if gcol else rows
    groups = group_values(subset, key, ycol)
    results, pairs = run_tests(groups, args)
    return [((xs[0], a) if gcol else (None, a), (xs[0], b) if gcol else (None, b), s) for a, b, s in pairs], results


def plot_scatter_regression(ax, rows, spec, args, np, stats_out):
    xcol, ycol, gcol = spec["x"], spec["y"], spec.get("group")
    palette = resolve_palette(args)
    groups = {None: rows} if not gcol else {g: [r for r in rows if r[gcol] == g]
                                            for g in dict.fromkeys(r[gcol] for r in rows)}
    for gi, (g, sub) in enumerate(groups.items()):
        x = np.array([float(r[xcol]) for r in sub])
        y = np.array([float(r[ycol]) for r in sub])
        if len(x) < 3:
            sys.exit(f"scatter_regression needs >= 3 points per group "
                     f"(group {g!r} has {len(x)}) — a regression line and 95% CI band "
                     "are not meaningful below that")
        ls = IEEE_LINESTYLES[gi % len(IEEE_LINESTYLES)] if args.theme == "ieee" else "-"
        ax.scatter(x, y, color=palette[gi % len(palette)], label=g, zorder=3,
                   edgecolor="none", alpha=0.9)
        b, a = np.polyfit(x, y, 1)
        xs_line = np.linspace(x.min(), x.max(), 100)
        n = len(x)
        sxx = float(np.sum((x - x.mean()) ** 2))
        s = math.sqrt(float(np.sum((y - (a + b * x)) ** 2)) / (n - 2)) if n > 2 else 0.0
        se = s * np.sqrt(1 / n + (xs_line - x.mean()) ** 2 / sxx)
        try:
            from scipy import stats
            tcrit = float(stats.t.ppf(0.975, n - 2))
            r, p = stats.pearsonr(x, y)
        except ImportError:
            tcrit, r, p = 1.96, float(np.corrcoef(x, y)[0, 1]), None
        yfit = a + b * xs_line
        ax.plot(xs_line, yfit, color=palette[gi % len(palette)], ls=ls, zorder=2)
        ax.fill_between(xs_line, yfit - tcrit * se, yfit + tcrit * se,
                        color=palette[gi % len(palette)], alpha=0.15, linewidth=0, zorder=1)
        stats_out.append({"template": "scatter_regression", "group": g, "slope": float(b),
                          "intercept": float(a), "r": r, "p": p, "n": n, "band": "95% CI of fit"})
    if gcol:
        ax.legend(title=gcol)
    ax.set_xlabel(args.xlabel or xcol)
    ax.set_ylabel(args.ylabel or ycol)


def plot_line(ax, rows, spec, args, np, stats_out):
    xcol, ycol, gcol = spec["x"], spec["y"], spec.get("group")
    palette = resolve_palette(args)
    groups = {None: rows} if not gcol else {g: [r for r in rows if r[gcol] == g] for g in dict.fromkeys(r[gcol] for r in rows)}
    for i, (group, sub) in enumerate(groups.items()):
        points = sorted((float(r[xcol]), float(r[ycol])) for r in sub)
        if len(points) < 2: sys.exit(f"line needs >= 2 points per group (group {group!r})")
        x, y = zip(*points); color = palette[i % len(palette)]
        ax.plot(x, y, marker="o", ms=3, color=color, label=group,
                ls=IEEE_LINESTYLES[i % len(IEEE_LINESTYLES)] if args.theme == "ieee" else "-")
        stats_out.append({"template":"line", "group":group, "n":len(points), "x_range":[x[0], x[-1]]})
    if gcol: ax.legend(title=gcol)
    ax.set_xlabel(args.xlabel or xcol); ax.set_ylabel(args.ylabel or ycol)


def plot_paired_points(ax, rows, spec, args, np, stats_out):
    if not args.id: sys.exit("paired_points requires --id to align repeated observations")
    xcol, ycol = spec["x"], spec["y"]
    levels = list(dict.fromkeys(r[xcol] for r in rows))
    if len(levels) != 2: sys.exit("paired_points requires exactly two x levels")
    subjects = {}
    for row in rows: subjects.setdefault(row[args.id], {})[row[xcol]] = float(row[ycol])
    complete = [(sid, item[levels[0]], item[levels[1]]) for sid, item in subjects.items() if all(level in item for level in levels)]
    if len(complete) < 2: sys.exit("paired_points requires at least two complete subject pairs")
    for i, (_, before, after) in enumerate(complete): ax.plot([0,1], [before,after], color="#808080", lw=.6, zorder=1)
    for pos, level in enumerate(levels): ax.scatter(np.full(len(complete),pos), [p[pos+1] for p in complete], color=resolve_palette(args)[pos], s=12, zorder=2)
    ax.set_xticks([0,1], levels); ax.set_xlabel(args.xlabel or xcol); ax.set_ylabel(args.ylabel or ycol)
    stats_out.append({"template":"paired_points", "id_column":args.id, "n_pairs":len(complete), "levels":levels})


def jitter(n, scale, seed, np):
    return np.random.default_rng(seed).uniform(-scale, scale, n)


def plot_box_violin(ax, rows, spec, args, np, stats_out):
    xcol, ycol = spec["x"], spec["y"]
    xs = list(dict.fromkeys(r[xcol] for r in rows))
    data = [[float(r[ycol]) for r in rows if r[xcol] == x] for x in xs]
    palette = resolve_palette(args)
    overlay = not args.no_overlay_points if spec["template"] in ("violin", "raincloud") else args.overlay_points
    if spec["template"] in ("violin", "raincloud"):
        parts = ax.violinplot(data, showextrema=False)
        for i, body in enumerate(parts["bodies"]):
            body.set_facecolor(palette[i % len(palette)])
            body.set_alpha(0.5)
            body.set_edgecolor("black")
            body.set_linewidth(0.5)
            if spec["template"] == "raincloud":
                vertices = body.get_paths()[0].vertices
                vertices[:, 0] = np.minimum(vertices[:, 0], i + 1)
        positions = [i + 1.13 for i in range(len(data))] if spec["template"] == "raincloud" else None
        ax.boxplot(data, positions=positions, widths=0.12, showfliers=False,
                   medianprops=dict(color="black", lw=0.8),
                   boxprops=dict(lw=0.6), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
    else:
        bp = ax.boxplot(data, patch_artist=True, medianprops=dict(color="black", lw=0.8),
                        boxprops=dict(lw=0.6), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6),
                        flierprops=dict(markersize=2))
        for i, box in enumerate(bp["boxes"]):
            box.set_facecolor(palette[i % len(palette)] if args.theme != "ieee" else "white")
    if overlay:
        for i, vals in enumerate(data):
            point_center = i + 1.28 if spec["template"] == "raincloud" else i + 1
            ax.scatter(np.full(len(vals), point_center) + jitter(len(vals), 0.06, args.seed + i, np),
                       vals, s=6, color="black", alpha=0.6, zorder=3, edgecolor="none")
    ax.set_xticks(range(1, len(xs) + 1), xs)
    if args.compare_groups or args.stars:
        pair_specs, tstats = significance_pairs(rows, xcol, ycol, None, xs, args)
        stats_out += tstats
        positions = {x: i + 1 for i, x in enumerate(xs)}
        tops = {x: max(d) for x, d in zip(xs, data)}
        pairs = [(a[1], b[1], s) for (a, b, s) in pair_specs]
        yr = ax.get_ylim()[1] - ax.get_ylim()[0]
        draw_brackets(ax, pairs, positions, tops, yr, args.star_step, args.hide_ns,
                      THEMES[args.theme]["font.size"])
    ax.set_xlabel(args.xlabel or xcol)
    ax.set_ylabel(args.ylabel or ycol)


def plot_heatmap(ax, rows, spec, args, np, stats_out):
    import matplotlib.colors as mcolors
    if spec.get("z"):
        xcol, ycol, zcol = spec["x"], spec["y"], spec["z"]
        xs = list(dict.fromkeys(r[xcol] for r in rows))
        ys = list(dict.fromkeys(r[ycol] for r in rows))
        mat = np.full((len(ys), len(xs)), np.nan)
        for r in rows:
            mat[ys.index(r[ycol]), xs.index(r[xcol])] = float(r[zcol])
    else:
        cols = list(rows[0])
        ys = [r[cols[0]] for r in rows]
        xs = cols[1:]
        mat = np.array([[float(r[c]) for c in xs] for r in rows])
    lim = float(np.nanmax(np.abs(mat - args.center)))
    norm = mcolors.TwoSlopeNorm(vmin=args.center - lim, vcenter=args.center, vmax=args.center + lim) \
        if args.cmap == "RdBu_r" else None
    im = ax.imshow(mat, cmap=args.cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(xs)), xs)
    ax.set_yticks(range(len(ys)), ys)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    if mat.shape[0] <= 12 and mat.shape[1] <= 12:
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                ax.text(j, i, f"{mat[i, j]:.2g}", ha="center", va="center", fontsize=6)
    stats_out.append({"template": "heatmap", "shape": list(mat.shape), "center": args.center,
                      "min": float(np.nanmin(mat)), "max": float(np.nanmax(mat))})


def plot_forest(ax, rows, spec, args, np, stats_out):
    """Render effect estimates and their already-computed confidence intervals."""
    effect, label = spec["x"], spec["y"]
    low, high = args.ci_low, args.ci_high
    if not low or not high:
        sys.exit("forest requires --ci-low and --ci-high confidence-limit columns")
    missing = [col for col in (effect, label, low, high) if not col or col not in rows[0]]
    if missing:
        sys.exit(f"forest columns not found: {', '.join(missing)}")
    values = []
    for i, row in enumerate(rows, 1):
        try:
            est, lo, hi = float(row[effect]), float(row[low]), float(row[high])
        except ValueError:
            sys.exit(f"forest row {i} has non-numeric estimate or confidence limit")
        if lo > est or est > hi:
            sys.exit(f"forest row {i} must satisfy {low} <= {effect} <= {high}")
        values.append((str(row[label]), est, lo, hi))
    ypos = list(range(len(values) - 1, -1, -1))
    palette = resolve_palette(args)
    for i, ((name, est, lo, hi), y) in enumerate(zip(values, ypos)):
        ax.errorbar(est, y, xerr=[[est - lo], [hi - est]], fmt="o", color=palette[i % len(palette)], ecolor="#555555", capsize=2, markersize=4, zorder=2)
        stats_out.append({"template": "forest", "label": name, "estimate": est, "ci": [lo, hi]})
    ax.axvline(args.center, color="#555555", lw=.7, ls="--", zorder=0)
    ax.set_yticks(ypos, [item[0] for item in values])
    ax.set_xlabel(args.xlabel or effect)
    ax.set_ylabel(args.ylabel or label)


def plot_discrimination_curve(ax, rows, spec, args, np, stats_out):
    """Plot empirical ROC or precision-recall curve from supplied binary labels/scores."""
    score_col, label_col = spec["x"], spec["y"]
    if not score_col or not label_col or score_col not in rows[0] or label_col not in rows[0]:
        sys.exit("roc/pr requires --x score column and --y binary label column")
    try:
        pairs = sorted(((float(row[score_col]), int(float(row[label_col]))) for row in rows), reverse=True)
    except ValueError:
        sys.exit("roc/pr score must be numeric and label must be 0 or 1")
    if not pairs or any(label not in (0, 1) for _, label in pairs):
        sys.exit("roc/pr label column must contain both 0 and 1 only")
    positives, negatives = sum(label for _, label in pairs), sum(1-label for _, label in pairs)
    if not positives or not negatives: sys.exit("roc/pr needs at least one positive and one negative label")
    tp = fp = 0; fpr = [0.0]; tpr = [0.0]; recall = [0.0]; precision = [1.0]
    for _, label in pairs:
        tp += label; fp += 1-label
        fpr.append(fp / negatives); tpr.append(tp / positives); recall.append(tp / positives); precision.append(tp / (tp + fp))
    palette = resolve_palette(args)
    if spec["template"] == "roc":
        auc = float(getattr(np, "trapezoid", np.trapz)(tpr, fpr))
        ax.plot(fpr, tpr, color=palette[0], label=f"AUC = {auc:.3g}")
        ax.plot([0, 1], [0, 1], color="#777777", ls="--", lw=.7, label="chance")
        ax.set_xlabel(args.xlabel or "False positive rate"); ax.set_ylabel(args.ylabel or "True positive rate")
        stats_out.append({"template":"roc", "n":len(pairs), "positives":positives, "negatives":negatives, "auc":auc})
    else:
        ap = float(getattr(np, "trapezoid", np.trapz)(precision, recall))
        baseline = positives / len(pairs)
        ax.plot(recall, precision, color=palette[0], label=f"AP = {ap:.3g}")
        ax.axhline(baseline, color="#777777", ls="--", lw=.7, label="prevalence")
        ax.set_xlabel(args.xlabel or "Recall"); ax.set_ylabel(args.ylabel or "Precision")
        stats_out.append({"template":"pr", "n":len(pairs), "positives":positives, "negatives":negatives, "average_precision_trapezoidal":ap})
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.legend()


def plot_calibration(ax, rows, spec, args, np, stats_out):
    """Plot equal-width binned predicted probability versus observed frequency."""
    score_col, label_col = spec["x"], spec["y"]
    if not 2 <= args.bins <= 50: sys.exit("calibration --bins must be between 2 and 50")
    if not score_col or not label_col or score_col not in rows[0] or label_col not in rows[0]:
        sys.exit("calibration requires --x predicted-probability column and --y binary label column")
    try: pairs = [(float(row[score_col]), int(float(row[label_col]))) for row in rows]
    except ValueError: sys.exit("calibration probabilities must be numeric and labels must be 0 or 1")
    if not pairs or any(not 0 <= score <= 1 or label not in (0, 1) for score, label in pairs):
        sys.exit("calibration needs probabilities in [0,1] and binary labels 0/1")
    edges = np.linspace(0, 1, args.bins + 1); detail = []
    for i in range(args.bins):
        left, right = edges[i], edges[i + 1]
        subset = [(s, y) for s, y in pairs if left <= s < right or (i == args.bins - 1 and s == right)]
        if subset:
            mean_score = float(np.mean([s for s, _ in subset])); observed = float(np.mean([y for _, y in subset]))
            detail.append({"bin": [float(left), float(right)], "n": len(subset), "mean_predicted": mean_score, "observed_frequency": observed})
    palette = resolve_palette(args)
    ax.plot([0, 1], [0, 1], color="#777777", ls="--", lw=.7, label="ideal calibration")
    ax.plot([row["mean_predicted"] for row in detail], [row["observed_frequency"] for row in detail], marker="o", color=palette[0], label="binned observations")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.set_xlabel(args.xlabel or "Mean predicted probability"); ax.set_ylabel(args.ylabel or "Observed frequency"); ax.legend()
    stats_out.append({"template":"calibration", "n":len(pairs), "bins_requested":args.bins, "nonempty_bins":detail})


def plot_funnel(ax, rows, spec, args, np, stats_out):
    """Plot supplied effect estimates against standard errors; no asymmetry test."""
    effect, se_col = spec["x"], spec["y"]
    if not effect or not se_col or effect not in rows[0] or se_col not in rows[0]:
        sys.exit("funnel requires --x effect-estimate column and --y standard-error column")
    try: pairs=[(float(row[effect]), float(row[se_col])) for row in rows]
    except ValueError: sys.exit("funnel effect and standard-error columns must be numeric")
    if not pairs or any(se <= 0 for _,se in pairs):sys.exit("funnel standard errors must be positive")
    maximum=max(se for _,se in pairs); grid=np.linspace(0, maximum, 100); center=args.center
    palette=resolve_palette(args)
    ax.scatter([x for x,_ in pairs],[y for _,y in pairs],color=palette[0],edgecolor="none",alpha=.85)
    ax.axvline(center,color="#555555",lw=.7,ls="--")
    ax.plot(center-1.96*grid,grid,color="#777777",lw=.7,ls="--")
    ax.plot(center+1.96*grid,grid,color="#777777",lw=.7,ls="--")
    ax.set_ylim(maximum*1.05,0);ax.set_xlabel(args.xlabel or effect);ax.set_ylabel(args.ylabel or se_col)
    stats_out.append({"template":"funnel","n":len(pairs),"center":center,"reference_limits":"effect = center ± 1.96 × standard_error (visual guide only)"})


def plot_volcano(ax, rows, spec, args, np, stats_out):
    """Plot supplied effect sizes against supplied (preferably adjusted) p-values.

    This is descriptive: it does not calculate p-values or declare discoveries.
    """
    effect, p_col = spec["x"], spec["y"]
    if not effect or not p_col or effect not in rows[0] or p_col not in rows[0]:
        sys.exit("volcano requires --x effect-size column and --y p-value column")
    if not 0 < args.p_threshold < 1 or args.effect_threshold < 0:
        sys.exit("volcano requires 0 < --p-threshold < 1 and --effect-threshold >= 0")
    try:
        pairs = [(float(row[effect]), float(row[p_col])) for row in rows]
    except ValueError:
        sys.exit("volcano effect sizes and p-values must be numeric")
    if not pairs or any(not 0 < p <= 1 for _, p in pairs):
        sys.exit("volcano p-values must be in (0, 1]; use a finite floor instead of zero")
    cutoff = -math.log10(args.p_threshold)
    palette = resolve_palette(args)
    highlighted = [(x, p) for x, p in pairs if abs(x) >= args.effect_threshold and p <= args.p_threshold]
    other = [(x, p) for x, p in pairs if abs(x) < args.effect_threshold or p > args.p_threshold]
    ax.scatter([x for x, p in other], [-math.log10(p) for x, p in other], color="#999999", s=12, alpha=.65, edgecolor="none", label="other")
    ax.scatter([x for x, p in highlighted], [-math.log10(p) for x, p in highlighted], color=palette[0], s=14, alpha=.9, edgecolor="none", label="meets supplied thresholds")
    ax.axhline(cutoff, color="#555555", lw=.7, ls="--")
    ax.axvline(-args.effect_threshold, color="#555555", lw=.7, ls="--")
    ax.axvline(args.effect_threshold, color="#555555", lw=.7, ls="--")
    ax.set_xlabel(args.xlabel or effect); ax.set_ylabel(args.ylabel or f"-log10({p_col})")
    ax.legend()
    stats_out.append({"template":"volcano", "n":len(pairs), "effect_threshold":args.effect_threshold,
                      "p_threshold":args.p_threshold, "highlighted_n":len(highlighted),
                      "note":"descriptive threshold overlay; p-values are supplied, not calculated"})


def plot_manhattan(ax, rows, spec, args, np, stats_out):
    """Plot supplied chromosome, position and p/q values without association testing."""
    position, p_col, chrom = spec["x"], spec["y"], spec.get("group")
    if not position or not p_col or not chrom or any(col not in rows[0] for col in (position, p_col, chrom)):
        sys.exit("manhattan requires --x genomic-position --y p-value and --group chromosome columns")
    if not 0 < args.p_threshold < 1:
        sys.exit("manhattan requires 0 < --p-threshold < 1")
    records = []
    for i, row in enumerate(rows, 1):
        try:
            pos, p = float(row[position]), float(row[p_col])
        except ValueError:
            sys.exit(f"manhattan row {i} has non-numeric position or p-value")
        if pos < 0 or not 0 < p <= 1:
            sys.exit("manhattan positions must be >= 0 and p-values in (0, 1]")
        records.append((str(row[chrom]), pos, p))
    def chrom_key(label):
        return (0, int(label)) if label.isdigit() else (1, label.lower())
    groups = sorted({label for label, _, _ in records}, key=chrom_key)
    palette, offset, centers = resolve_palette(args), 0.0, []
    for index, label in enumerate(groups):
        values = sorted((pos, p) for c, pos, p in records if c == label)
        maximum = max(pos for pos, _ in values)
        xs = [offset + pos for pos, _ in values]
        ax.scatter(xs, [-math.log10(p) for _, p in values], color=palette[index % len(palette)], s=9, edgecolor="none", alpha=.8)
        centers.append((offset + maximum / 2, label)); offset += maximum
    ax.axhline(-math.log10(args.p_threshold), color="#555555", lw=.7, ls="--")
    ax.set_xticks([center for center, _ in centers], [label for _, label in centers])
    ax.set_xlabel(args.xlabel or chrom); ax.set_ylabel(args.ylabel or f"-log10({p_col})")
    stats_out.append({"template":"manhattan", "n":len(records), "chromosomes":groups,
                      "p_threshold":args.p_threshold,
                      "note":"descriptive plot of supplied values; no association testing or coordinate validation"})


def plot_sankey(ax, rows, spec, args, np, stats_out):
    """Render supplied source-to-target amounts as a two-sided flow diagram."""
    source, target, weight = spec["x"], spec["y"], spec.get("z")
    if not source or not target or not weight or any(col not in rows[0] for col in (source, target, weight)):
        sys.exit("sankey requires --x source, --y target, and --z non-negative flow columns")
    flows = []
    for i, row in enumerate(rows, 1):
        try:
            amount = float(row[weight])
        except ValueError:
            sys.exit(f"sankey row {i} has a non-numeric flow")
        if amount < 0:
            sys.exit("sankey flow values must be non-negative")
        flows.append((str(row[source]), str(row[target]), amount))
    if not flows:
        sys.exit("sankey needs at least one flow")
    left, right = sorted({a for a, _, _ in flows}), sorted({b for _, b, _ in flows})
    left_y = {node: 1 - (i + 1) / (len(left) + 1) for i, node in enumerate(left)}
    right_y = {node: 1 - (i + 1) / (len(right) + 1) for i, node in enumerate(right)}
    maximum = max(amount for _, _, amount in flows) or 1.0
    palette = resolve_palette(args)
    for index, (a, b, amount) in enumerate(flows):
        ax.plot([.08, .92], [left_y[a], right_y[b]], color=palette[index % len(palette)], alpha=.45,
                lw=1 + 14 * amount / maximum, solid_capstyle="round", zorder=1)
    for node, y in left_y.items():
        ax.scatter([.08], [y], s=30, color="#333333", zorder=2); ax.text(.05, y, node, ha="right", va="center", fontsize=6)
    for node, y in right_y.items():
        ax.scatter([.92], [y], s=30, color="#333333", zorder=2); ax.text(.95, y, node, ha="left", va="center", fontsize=6)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    stats_out.append({"template":"sankey", "n_flows":len(flows), "n_sources":len(left), "n_targets":len(right),
                      "flow_column":weight, "note":"two-sided visualization of supplied flows; no inferred hierarchy or flow-conservation validation"})


def plot_network(ax, rows, spec, args, np, stats_out):
    """Draw a deterministic circular network from supplied source/target edges."""
    source, target, weight = spec["x"], spec["y"], spec.get("z")
    if not source or not target or any(col not in rows[0] for col in (source, target)):
        sys.exit("network requires --x source and --y target columns; --z weight is optional")
    edges = []
    for i, row in enumerate(rows, 1):
        try:
            value = float(row[weight]) if weight else 1.0
        except ValueError:
            sys.exit(f"network row {i} has non-numeric weight")
        if value < 0:
            sys.exit("network weights must be non-negative")
        edges.append((str(row[source]), str(row[target]), value))
    nodes = sorted({node for left, right, _ in edges for node in (left, right)})
    if not nodes:
        sys.exit("network needs at least one edge")
    positions = {node:(math.cos(2 * math.pi * i / len(nodes)), math.sin(2 * math.pi * i / len(nodes))) for i, node in enumerate(nodes)}
    maximum = max(value for _, _, value in edges) or 1.0
    for left, right, value in edges:
        x1, y1 = positions[left]; x2, y2 = positions[right]
        ax.plot([x1, x2], [y1, y2], color="#999999", alpha=.55, lw=.4 + 2.2 * value / maximum, zorder=1)
    palette = resolve_palette(args)
    ax.scatter([positions[node][0] for node in nodes], [positions[node][1] for node in nodes], s=48, color=palette[0], edgecolor="white", linewidth=.5, zorder=2)
    for node in nodes:
        x, y = positions[node]; ax.text(x, y, node, ha="center", va="center", fontsize=6, zorder=3)
    ax.set_aspect("equal"); ax.axis("off")
    stats_out.append({"template":"network", "n_nodes":len(nodes), "n_edges":len(edges), "weight_column":weight,
                      "layout":"deterministic circular", "note":"visualization only; no graph inference, community detection, or centrality analysis"})


def plot_enrichment_bubble(ax, rows, spec, args, np, stats_out):
    """Plot supplied enrichment scores and p/q values; never performs enrichment."""
    score, term, p_col = spec["x"], spec["y"], spec.get("z")
    if not score or not term or not p_col or any(col not in rows[0] for col in (score, term, p_col)):
        sys.exit("enrichment_bubble requires --x enrichment-score --y term --z p/q-value columns")
    values = []
    for i, row in enumerate(rows, 1):
        try:
            effect, p = float(row[score]), float(row[p_col])
        except ValueError:
            sys.exit(f"enrichment_bubble row {i} has non-numeric score or p/q-value")
        if not 0 < p <= 1:
            sys.exit("enrichment_bubble p/q-values must be in (0, 1]")
        values.append((str(row[term]), effect, p))
    values.sort(key=lambda value: value[1])
    scale = [-math.log10(p) for _, _, p in values]
    sizes = [30 + 35 * item for item in scale]
    palette = resolve_palette(args)
    y_pos = list(range(len(values)))
    colors = [palette[0] if effect >= 0 else palette[3 % len(palette)] for _, effect, _ in values]
    ax.scatter([effect for _, effect, _ in values], y_pos, s=sizes, c=colors, alpha=.78, edgecolor="none")
    ax.axvline(0, color="#888888", lw=.6, ls="--")
    ax.set_yticks(y_pos, [term for term, _, _ in values])
    ax.set_xlabel(args.xlabel or score); ax.set_ylabel(args.ylabel or term)
    stats_out.append({"template":"enrichment_bubble", "n_terms":len(values), "p_value_column":p_col,
                      "bubble_area":"30 + 35 * -log10(supplied p/q-value)",
                      "note":"supplied enrichment values only; no pathway test or multiple-testing correction performed"})


def plot_umap(ax, rows, spec, args, np, stats_out):
    """UMAP projection from numeric feature columns, using explicit optional dependency."""
    try:
        import umap
    except ImportError:
        sys.exit("umap template requires optional umap-learn: pip install umap-learn")
    group_col = spec.get("group")
    columns = [name for name in rows[0] if name != group_col]
    try:
        matrix = np.asarray([[float(row[name]) for name in columns] for row in rows], dtype=float)
    except ValueError:
        sys.exit("umap needs numeric feature columns; pass --group only for a categorical label column")
    if matrix.shape[0] < 3 or matrix.shape[1] < 2 or not np.isfinite(matrix).all() or args.neighbors < 2:
        sys.exit("umap needs at least three complete rows, two numeric features, and --neighbors >= 2")
    n_neighbors = min(args.neighbors, matrix.shape[0] - 1)
    embedding = umap.UMAP(n_components=2, n_neighbors=n_neighbors, random_state=args.seed).fit_transform(matrix)
    palette = resolve_palette(args)
    if group_col:
        labels = list(dict.fromkeys(row[group_col] for row in rows))
        for index, label in enumerate(labels):
            idx = [i for i, row in enumerate(rows) if row[group_col] == label]
            ax.scatter(embedding[idx, 0], embedding[idx, 1], color=palette[index % len(palette)], s=16, edgecolor="none", alpha=.85, label=label)
        ax.legend(title=group_col)
    else:
        ax.scatter(embedding[:, 0], embedding[:, 1], color=palette[0], s=16, edgecolor="none", alpha=.85)
    ax.set_xlabel(args.xlabel or "UMAP 1"); ax.set_ylabel(args.ylabel or "UMAP 2")
    stats_out.append({"template":"umap", "n_samples":int(matrix.shape[0]), "n_features":int(matrix.shape[1]), "feature_columns":columns, "n_neighbors":n_neighbors, "seed":args.seed, "dependency":"umap-learn", "note":"projection only; feature preprocessing and interpretation must be documented upstream"})


def plot_pca(ax, rows, spec, args, np, stats_out):
    """PCA biplot of numeric CSV columns, optionally colored by a supplied group."""
    group_col = spec.get("group")
    excluded = {group_col} if group_col else set()
    columns = [name for name in rows[0] if name not in excluded]
    try:
        matrix = np.asarray([[float(row[name]) for name in columns] for row in rows], dtype=float)
    except ValueError:
        sys.exit("pca needs numeric feature columns; pass --group only for a categorical label column")
    if matrix.shape[0] < 2 or matrix.shape[1] < 2 or not np.isfinite(matrix).all():
        sys.exit("pca needs at least two complete rows and two numeric feature columns")
    centered = matrix - np.mean(matrix, axis=0)
    _, singular, vectors = np.linalg.svd(centered, full_matrices=False)
    if len(singular) < 2:
        sys.exit("pca needs at least two non-empty components")
    scores = centered @ vectors[:2].T
    variance = singular ** 2
    ratio = variance / variance.sum() if variance.sum() else np.zeros_like(variance)
    palette = resolve_palette(args)
    if group_col:
        labels = list(dict.fromkeys(row[group_col] for row in rows))
        for index, label in enumerate(labels):
            idx = [i for i, row in enumerate(rows) if row[group_col] == label]
            ax.scatter(scores[idx, 0], scores[idx, 1], color=palette[index % len(palette)], s=16, edgecolor="none", alpha=.85, label=label)
        ax.legend(title=group_col)
    else:
        ax.scatter(scores[:, 0], scores[:, 1], color=palette[0], s=16, edgecolor="none", alpha=.85)
    ax.axhline(0, color="#aaaaaa", lw=.5); ax.axvline(0, color="#aaaaaa", lw=.5)
    ax.set_xlabel(args.xlabel or f"PC1 ({ratio[0] * 100:.1f}% variance)")
    ax.set_ylabel(args.ylabel or f"PC2 ({ratio[1] * 100:.1f}% variance)")
    stats_out.append({"template":"pca", "n_samples":int(matrix.shape[0]), "n_features":int(matrix.shape[1]),
                      "feature_columns":columns, "explained_variance_ratio":[float(ratio[0]), float(ratio[1])],
                      "note":"features centered but not scaled; choose scaling upstream and report it"})


def plot_survival(ax, rows, spec, args, np, stats_out):
    tcol, ecol, gcol = args.time or spec.get("x"), args.event or spec.get("y"), spec.get("group") or args.group
    palette = resolve_palette(args)
    groups = {None: rows} if not gcol else {g: [r for r in rows if r[gcol] == g]
                                            for g in dict.fromkeys(r[gcol] for r in rows)}
    risk_rows, max_time = [], 0.0
    for gi, (g, sub) in enumerate(groups.items()):
        records = sorted((float(r[tcol]), int(float(r[ecol]))) for r in sub)
        if any(event not in (0, 1) for _, event in records): sys.exit("survival --event must contain 0 (censored) or 1 (event)")
        times = [time for time, _ in records]; t_pts, s_pts, low_pts, high_pts, cens = [0.0], [1.0], [1.0], [1.0], []
        surv, n, greenwood = 1.0, len(times), 0.0
        for t in sorted(set(times)):
            d = sum(1 for tt, event in records if tt == t and event == 1)
            c = sum(1 for tt, event in records if tt == t and event == 0)
            t_pts += [t, t]
            previous = surv; surv *= 1 - d / n
            if d and n > d: greenwood += d / (n * (n - d))
            se = surv * math.sqrt(greenwood)
            low, high = max(0.0, surv - 1.96 * se), min(1.0, surv + 1.96 * se)
            s_pts += [previous, surv]; low_pts += [low_pts[-1], low]; high_pts += [high_pts[-1], high]
            surv = s_pts[-1]
            if c:
                cens.extend([(t, surv)] * c)
            n -= d + c
        ls = IEEE_LINESTYLES[gi % len(IEEE_LINESTYLES)] if args.theme == "ieee" else "-"
        ax.step(t_pts, s_pts, where="post", color=palette[gi % len(palette)], ls=ls, label=g)
        if not args.no_survival_ci:
            ax.fill_between(t_pts, low_pts, high_pts, step="post", color=palette[gi % len(palette)], alpha=.15, linewidth=0)
        if cens:
            ax.scatter([c[0] for c in cens], [c[1] for c in cens], marker="|",
                       color=palette[gi % len(palette)], s=18, zorder=3)
        median = next((t for t, s in zip(t_pts, s_pts) if s <= 0.5), None)
        risk_rows.append((g, times)); max_time = max(max_time, max(times, default=0.0))
        stats_out.append({"template": "survival", "group": g, "n": len(times), "events": sum(event for _, event in records), "median_survival": median, "confidence_band": None if args.no_survival_ci else "Greenwood normal approximation 95%"})
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(args.xlabel or tcol)
    ax.set_ylabel(args.ylabel or "Survival probability")
    if gcol:
        ax.legend(title=gcol)
    if args.risk_table:
        ticks = np.linspace(0, max_time, 5)
        cells = [[str(sum(time >= tick for time in times)) for tick in ticks] for _, times in risk_rows]
        labels = [str(group) if group is not None else "All" for group, _ in risk_rows]
        table = ax.table(cellText=cells, rowLabels=labels, colLabels=[f"{tick:g}" for tick in ticks], cellLoc="center", bbox=[0, -0.38, 1, .22])
        table.auto_set_font_size(False); table.set_fontsize(6)
        ax.set_xlabel((args.xlabel or tcol) + "\nNumber at risk")


def render_panel(ax, rows, spec, args, np, stats_out):
    t = spec["template"]
    if t == "grouped_bar":
        plot_grouped_bar(ax, rows, spec, args, np, stats_out)
    elif t == "scatter_regression":
        plot_scatter_regression(ax, rows, spec, args, np, stats_out)
    elif t == "line":
        plot_line(ax, rows, spec, args, np, stats_out)
    elif t == "paired_points":
        plot_paired_points(ax, rows, spec, args, np, stats_out)
    elif t in ("boxplot", "violin", "raincloud"):
        plot_box_violin(ax, rows, spec, args, np, stats_out)
    elif t == "heatmap":
        plot_heatmap(ax, rows, spec, args, np, stats_out)
    elif t == "forest":
        plot_forest(ax, rows, spec, args, np, stats_out)
    elif t in ("roc", "pr"):
        plot_discrimination_curve(ax, rows, spec, args, np, stats_out)
    elif t == "calibration":
        plot_calibration(ax, rows, spec, args, np, stats_out)
    elif t == "funnel":
        plot_funnel(ax, rows, spec, args, np, stats_out)
    elif t == "volcano":
        plot_volcano(ax, rows, spec, args, np, stats_out)
    elif t == "manhattan":
        plot_manhattan(ax, rows, spec, args, np, stats_out)
    elif t == "sankey":
        plot_sankey(ax, rows, spec, args, np, stats_out)
    elif t == "network":
        plot_network(ax, rows, spec, args, np, stats_out)
    elif t == "enrichment_bubble":
        plot_enrichment_bubble(ax, rows, spec, args, np, stats_out)
    elif t == "pca":
        plot_pca(ax, rows, spec, args, np, stats_out)
    elif t == "umap":
        plot_umap(ax, rows, spec, args, np, stats_out)
    elif t == "survival":
        plot_survival(ax, rows, spec, args, np, stats_out)
    style_ax(ax, args.theme)
    if args.title and len(args.panel) <= 1:
        ax.set_title(args.title)


def parse_panel(s):
    parts = s.split("|")
    if len(parts) < 3:
        sys.exit(f"--panel needs at least 'template|x|y', got: {s!r}")
    return {"template": parts[0], "x": parts[1], "y": parts[2],
            "group": parts[3] or None if len(parts) > 3 else None,
            "z": parts[4] if len(parts) > 4 else None}


def ensure_outputs(args, paths):
    protected = {os.path.abspath(args.csv)}
    if args.statistics_source:
        protected.add(os.path.abspath(args.statistics_source))
    for path in paths:
        resolved = os.path.abspath(path)
        if resolved in protected:
            sys.exit(f"error: figure output must not replace an input file: {path}")
        if os.path.exists(resolved) and not args.force:
            sys.exit(f"error: output exists: {path}; use --force to replace derived figures")


def figure_manifest(args, output_paths, manifest_path):
    sources = [{"kind": "file", "locator": os.path.abspath(args.csv)}]
    warnings = []
    statistics_source = None
    if args.statistics_source:
        statistics_source = os.path.abspath(args.statistics_source)
        sources.append({"kind": "file", "locator": statistics_source})
    if args.compare_groups:
        warnings.append("significance tests were computed inside the plotting script and are exploratory")
    if args.stars and not args.statistics_source:
        warnings.append("manual significance stars have no validated stat-results source")
    return {
        "schema_version": "1.0.0",
        "artifact_type": "figure-manifest",
        "provenance": {
            "created_by": "scientific-plot/plot_chart.py",
            "tool_version": "0.1.0",
            "command": " ".join(sys.argv),
            "seed": args.seed,
            "sources": sources,
            "warnings": warnings,
        },
        "figure_id": os.path.basename(args.out),
        "outputs": [os.path.abspath(path) for path in output_paths],
        "data_sources": [{"kind": "file", "locator": os.path.abspath(args.csv)}],
        "statistics_source": statistics_source,
        "theme": args.theme,
        "manifest_path": os.path.abspath(manifest_path),
    }


def main():
    args = parse_args()
    if args.list_palettes:
        extra = _load_extra_palettes()
        print("theme defaults:", ", ".join(PALETTES))
        print(f"named palettes ({len(extra)}, from scripts/palettes.json):")
        for key, val in sorted(extra.items()):
            print(f"  {key:<16} [{val['source']:<13}] {val['n']:>2} colors  "
                  + " ".join(val['colors'][:6]) + (" ..." if val['n'] > 6 else ""))
        return 0
    if not args.csv:
        sys.exit("error: csv is required unless --list-palettes is given")
    if args.statistics_source and not os.path.isfile(args.statistics_source):
        sys.exit(f"error: --statistics-source does not exist: {args.statistics_source}")
    if args.statistics_source and args.compare_groups:
        sys.exit("error: choose formal --statistics-source or exploratory --compare-groups, not both")
    load_formal_stars(args)
    formats = [fmt.strip() for fmt in args.formats.split(",") if fmt.strip()]
    if not formats:
        sys.exit("error: --formats must contain at least one extension")
    output_paths = [f"{args.out}.{fmt}" for fmt in formats]
    stats_path = f"{args.out}.stats.json"
    manifest_path = args.manifest_out or f"{args.out}.manifest.json"
    all_outputs = output_paths + [stats_path, manifest_path]
    if len({os.path.abspath(path) for path in all_outputs}) != len(all_outputs):
        sys.exit("error: figure, stats, and manifest output paths must be distinct")
    ensure_outputs(args, all_outputs)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        sys.exit("matplotlib and numpy are required: pip install matplotlib numpy")
    plt.rcParams.update({**THEMES[args.theme], **EXPORT_RC})
    rows = load_rows(args.csv, args.encoding)
    stats_out = list(args.formal_stats)
    width = COLUMN_IN[args.column]
    if args.panel:
        specs = [parse_panel(s) for s in args.panel]
        n = len(specs)
        ncols = n if n <= 2 else math.ceil(math.sqrt(n))
        nrows = math.ceil(n / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(width, width / ncols * 0.75 * nrows),
                                 squeeze=False, sharex=args.share_x, sharey=args.share_y)
        for i, (spec, ax) in enumerate(zip(specs, axes.flat)):
            render_panel(ax, rows, spec, args, np, stats_out)
            ax.text(-0.18, 1.05, chr(65 + i), transform=ax.transAxes,
                    fontsize=THEMES[args.theme]["axes.titlesize"], fontweight="bold", va="bottom")
        for ax in list(axes.flat)[n:]:
            ax.set_visible(False)
        if args.shared_legend:
            handles, labels = [], []
            for axis in axes.flat:
                legend = axis.get_legend()
                if legend:
                    for handle, label in zip(*axis.get_legend_handles_labels()):
                        if label not in labels: handles.append(handle); labels.append(label)
                    legend.remove()
            if handles:
                fig.legend(handles, labels, loc="upper center", ncol=min(len(labels), 4), frameon=False)
    else:
        if not args.template:
            sys.exit("--template is required (or use --panel)")
        spec = {"template": args.template, "x": args.x, "y": args.y,
                "group": args.group, "z": args.z}
        fig, ax = plt.subplots(figsize=(width, width * 0.75))
        render_panel(ax, rows, spec, args, np, stats_out)
    fig.tight_layout()
    for fmt, path in zip(formats, output_paths):
        fig.savefig(path, dpi=300 if fmt.lower() in {"png", "tif", "tiff"} else None, bbox_inches="tight")
        print(f"wrote {path}")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump({"theme": args.theme, "seed": args.seed, "stats": stats_out}, f, indent=2, ensure_ascii=False)
    print(f"wrote {stats_path}")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(figure_manifest(args, output_paths, manifest_path), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
