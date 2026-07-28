#!/usr/bin/env python3
"""Publication-grade statistical charts from CSV (Prism/Origin/Excel replacement).

Purpose: render six chart templates (grouped_bar, scatter_regression, boxplot,
violin, heatmap, survival) under four journal themes (nature, science, ieee,
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
    p.add_argument("csv", help="input CSV file")
    p.add_argument("--template", choices=["grouped_bar", "scatter_regression", "boxplot", "violin", "heatmap", "survival"])
    p.add_argument("--x"), p.add_argument("--y"), p.add_argument("--group"), p.add_argument("--z")
    p.add_argument("--time"), p.add_argument("--event")
    p.add_argument("--error", choices=["sd", "sem", "ci95", "none"], default="sd")
    p.add_argument("--theme", choices=list(THEMES), default="nature")
    p.add_argument("--column", choices=list(COLUMN_IN), default="single")
    p.add_argument("--compare-groups", action="store_true", help="run scipy tests and draw star brackets")
    p.add_argument("--control", help="compare all groups against this one instead of all pairs")
    p.add_argument("--test", choices=["auto", "ttest", "mannwhitney"], default="auto")
    p.add_argument("--stars", help='manual stars, e.g. "A>B:**;A>C:ns" (skips testing)')
    p.add_argument("--hide-ns", action="store_true")
    p.add_argument("--star-step", type=float, default=0.05, help="bracket step as fraction of y-range")
    p.add_argument("--panel", action="append", default=[], help='multi-panel spec "template|x|y[|group[|z]]"; repeatable')
    p.add_argument("--title"), p.add_argument("--xlabel"), p.add_argument("--ylabel")
    p.add_argument("--cmap", default="RdBu_r")
    p.add_argument("--center", type=float, default=0.0)
    p.add_argument("--no-zero-baseline", action="store_true")
    p.add_argument("--overlay-points", action="store_true")
    p.add_argument("--no-overlay-points", action="store_true")
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="figure", help="output basename (no extension)")
    p.add_argument("--formats", default="svg,pdf,png")
    return p.parse_args()


def load_rows(path, encoding):
    import csv
    with open(path, newline="", encoding=encoding) as f:
        return list(csv.DictReader(f))


def fcol(rows, name):
    vals = [r[name] for r in rows]
    try:
        return [float(v) for v in vals]
    except ValueError:
        return vals


def stars_of(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


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
    palette = PALETTES[args.theme]
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
        ax.set_ylim(bottom=0)
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
    palette = PALETTES[args.theme]
    groups = {None: rows} if not gcol else {g: [r for r in rows if r[gcol] == g]
                                            for g in dict.fromkeys(r[gcol] for r in rows)}
    for gi, (g, sub) in enumerate(groups.items()):
        x = np.array([float(r[xcol]) for r in sub])
        y = np.array([float(r[ycol]) for r in sub])
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


def jitter(n, scale, seed, np):
    return np.random.default_rng(seed).uniform(-scale, scale, n)


def plot_box_violin(ax, rows, spec, args, np, stats_out):
    xcol, ycol = spec["x"], spec["y"]
    xs = list(dict.fromkeys(r[xcol] for r in rows))
    data = [[float(r[ycol]) for r in rows if r[xcol] == x] for x in xs]
    palette = PALETTES[args.theme]
    overlay = not args.no_overlay_points if spec["template"] == "violin" else args.overlay_points
    if spec["template"] == "violin":
        parts = ax.violinplot(data, showextrema=False)
        for i, body in enumerate(parts["bodies"]):
            body.set_facecolor(palette[i % len(palette)])
            body.set_alpha(0.5)
            body.set_edgecolor("black")
            body.set_linewidth(0.5)
        ax.boxplot(data, widths=0.12, showfliers=False,
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
            ax.scatter(np.full(len(vals), i + 1) + jitter(len(vals), 0.06, args.seed + i, np),
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


def plot_survival(ax, rows, spec, args, np, stats_out):
    tcol, ecol, gcol = args.time or spec.get("x"), args.event or spec.get("y"), spec.get("group") or args.group
    palette = PALETTES[args.theme]
    groups = {None: rows} if not gcol else {g: [r for r in rows if r[gcol] == g]
                                            for g in dict.fromkeys(r[gcol] for r in rows)}
    for gi, (g, sub) in enumerate(groups.items()):
        times = sorted(float(r[tcol]) for r in sub)
        events = {float(r[tcol]): int(float(r[ecol])) for r in sub}
        t_pts, s_pts, cens = [0.0], [1.0], []
        surv, n = 1.0, len(times)
        for t in sorted(set(times)):
            d = sum(1 for tt in times if tt == t and events[tt] == 1)
            c = sum(1 for tt in times if tt == t and events[tt] == 0)
            t_pts += [t, t]
            s_pts += [s_pts[-1], surv * (1 - d / n)]
            surv = s_pts[-1]
            if c:
                cens.append((t, surv))
            n -= d + c
        ls = IEEE_LINESTYLES[gi % len(IEEE_LINESTYLES)] if args.theme == "ieee" else "-"
        ax.step(t_pts, s_pts, where="post", color=palette[gi % len(palette)], ls=ls, label=g)
        if cens:
            ax.scatter([c[0] for c in cens], [c[1] for c in cens], marker="|",
                       color=palette[gi % len(palette)], s=18, zorder=3)
        median = next((t for t, s in zip(t_pts, s_pts) if s <= 0.5), None)
        stats_out.append({"template": "survival", "group": g, "n": len(times),
                          "events": sum(events.values()), "median_survival": median})
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(args.xlabel or tcol)
    ax.set_ylabel(args.ylabel or "Survival probability")
    if gcol:
        ax.legend(title=gcol)


def render_panel(ax, rows, spec, args, np, stats_out):
    t = spec["template"]
    if t == "grouped_bar":
        plot_grouped_bar(ax, rows, spec, args, np, stats_out)
    elif t == "scatter_regression":
        plot_scatter_regression(ax, rows, spec, args, np, stats_out)
    elif t in ("boxplot", "violin"):
        plot_box_violin(ax, rows, spec, args, np, stats_out)
    elif t == "heatmap":
        plot_heatmap(ax, rows, spec, args, np, stats_out)
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


def main():
    args = parse_args()
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        sys.exit("matplotlib and numpy are required: pip install matplotlib numpy")
    plt.rcParams.update({**THEMES[args.theme], **EXPORT_RC})
    rows = load_rows(args.csv, args.encoding)
    stats_out = []
    width = COLUMN_IN[args.column]
    if args.panel:
        specs = [parse_panel(s) for s in args.panel]
        n = len(specs)
        ncols = n if n <= 2 else math.ceil(math.sqrt(n))
        nrows = math.ceil(n / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(width, width / ncols * 0.75 * nrows),
                                 squeeze=False)
        for i, (spec, ax) in enumerate(zip(specs, axes.flat)):
            render_panel(ax, rows, spec, args, np, stats_out)
            ax.text(-0.18, 1.05, chr(65 + i), transform=ax.transAxes,
                    fontsize=THEMES[args.theme]["axes.titlesize"], fontweight="bold", va="bottom")
        for ax in list(axes.flat)[n:]:
            ax.set_visible(False)
    else:
        if not args.template:
            sys.exit("--template is required (or use --panel)")
        spec = {"template": args.template, "x": args.x, "y": args.y,
                "group": args.group, "z": args.z}
        fig, ax = plt.subplots(figsize=(width, width * 0.75))
        render_panel(ax, rows, spec, args, np, stats_out)
    fig.tight_layout()
    for fmt in args.formats.split(","):
        fmt = fmt.strip()
        path = f"{args.out}.{fmt}"
        fig.savefig(path, dpi=300 if fmt == "png" else None, bbox_inches="tight")
        print(f"wrote {path}")
    with open(f"{args.out}.stats.json", "w", encoding="utf-8") as f:
        json.dump({"theme": args.theme, "seed": args.seed, "stats": stats_out}, f, indent=2, ensure_ascii=False)
    print(f"wrote {args.out}.stats.json")


if __name__ == "__main__":
    main()
