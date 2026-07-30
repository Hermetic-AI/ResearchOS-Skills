---
name: scientific-plot
description: Create publication-ready research figures from CSV, including grouped bars, regression scatterplots, line and paired-point plots, boxplots, violin plots, heatmaps, forest plots, Kaplan-Meier curves, journal themes, named palettes, significance brackets, multi-panels, and SVG/PDF/300-DPI export; also generate Excalidraw/SVG schematics and check Mermaid, Graphviz, or PlantUML sources. Use for research figures, paper illustrations, statistical charts, significance stars, error bars, boxplots, violin plots, heatmaps, forest plots, survival curves, 300dpi export, flowcharts, architecture diagrams, Nature-style figures, or drawing a diagram. Not for choosing formal statistical tests or cleaning data (data-analysis-assistant), or writing captions and manuscript prose (paper-writing-assistant).
---

# Scientific Plot

For researchers who need figures: publication-grade statistical charts (Prism/Origin/Excel replacements), hand-drawn-style schematics (Excalidraw/SVG), and code-as-diagram sources (mermaid/graphviz/plantuml). Reports to the user are in English by default; figure labels and artifacts follow the artifact's language (journal figures are usually English).

**Global conventions**
- **Draw, don't compute**: this skill renders figures. If the user has no test results yet and asks *which* test to run, hand off to data-analysis-assistant; use `--compare-groups` here only for quick in-figure star brackets.
- **Vector first**: always deliver SVG + PDF; PNG is the 300 DPI fallback for slides/word. Never deliver PNG alone for journal submission.
- **Reproducibility**: prefer the bundled scripts; pass `--seed` whenever jitter/sampling is involved and record the exact CLI in the figure log.
- **Dependencies**: `plot_chart.py` needs matplotlib + numpy once (`pip install matplotlib numpy`; `pip install scipy` for auto star brackets). The diagram scripts are zero-dependency.
- **Formal statistics come from analysis**: for submission figures, read `references/artifact-contracts.md` and consume validated `stat-results`; treat `--compare-groups` as exploratory only. Emit a `figure-manifest` beside final files.

## Priority tiers

| Tier | Capability | Entry point |
|------|-----------|-------------|
| 1 (highest) | Statistical charts from CSV | `python3 scripts/plot_chart.py data.csv --template <t> --theme nature --out fig1` |
| 2 | Schematic diagrams | `python3 scripts/excalidraw_gen.py scene.json --out arch.excalidraw.md` |
| 3 | Code-as-diagram | `python3 scripts/diagram_check.py --lang mermaid --in flow.mmd` |

Use `python3 scripts/palette_audit.py --colors "#0072B2,#E69F00,#009E73"` to screen a proposed categorical palette for white/black contrast and RGB separation. It is not a replacement for grayscale and color-vision-deficiency review.

## Tier 1: statistical charts

1. **Pick a template** (data shape → template):

   | Data shape | Template |
   |---|---|
   | categorical x × numeric y, ± group | `grouped_bar` |
   | two numeric variables, trend claim | `scatter_regression` |
   | ordered numeric x, trajectory per series | `line` |
   | same subjects at two conditions | `paired_points` with `--id` |
   | distribution per group, n ≥ 30 | `boxplot` |
   | distribution per group, small n | `violin` (scatter overlay) |
   | distribution plus box and raw points | `raincloud` (half violin + box + points) |
   | matrix / x×y intensity | `heatmap` (diverging, centered 0) |
   | estimates with precomputed confidence intervals | `forest` with `--ci-low` and `--ci-high` |
   | binary labels and prediction scores | `roc` or `pr` (`--x` score, `--y` label) |
   | predicted probabilities and binary labels | `calibration` (`--x` probability, `--y` label, `--bins`) |
   | supplied estimates and standard errors | `funnel` (`--x` effect, `--y` standard error; descriptive only) |
   | supplied effects and p/q-values | `volcano` (`--x` effect, `--y` p-value; descriptive threshold overlay only) |
   | supplied chromosome, position, and p/q-values | `manhattan` (`--x` position, `--y` p-value, `--group` chromosome; descriptive only) |
   | numeric feature matrix, optional labels | `pca` (all numeric CSV columns; `--group` is an optional label column) |
   | numeric feature matrix, optional labels | `umap` (requires optional `umap-learn`; `--neighbors`, `--seed`, optional `--group`) |
   | supplied pathway terms, enrichment scores, and p/q-values | `enrichment_bubble` (`--x` score, `--y` term, `--z` p/q-value; descriptive only) |
   | supplied source/target edges, optional weights | `network` (`--x` source, `--y` target, optional `--z` weight; descriptive only) |
   | supplied source-to-target flows | `sankey` (`--x` source, `--y` target, `--z` non-negative flow; descriptive only) |
   | time-to-event with censoring | `survival` (Kaplan-Meier) |

   Template design details (when violin beats boxplot, field requirements) — **read `references/chart-templates.md` only when unsure which template fits or a render looks wrong**.
2. **Pick a journal theme**: `nature` (7 pt body / 8 pt title, 89 mm single / 183 mm double column), `science` (7–9 pt, no grid, outward ticks), `ieee` (grayscale, dash/hatch series, print-safe), `prism` (default colors, slides/demos). Full parameter tables and the pre-submission checklist — **read `references/journal-themes.md` only when preparing a submission figure or the user names a journal**.
3. **Pick series colors (optional)**: `--palette NAME` overrides the theme's default colors with any of 227 named discrete schemes (`npg`, `aaas`, `nejm`, `lancet`, `jama`, `Okabe-Ito`, curated `zhihu-*` top-journal combos, …); `--list-palettes` browses them. Palette and theme are orthogonal (colors vs typography). Selection guidance, colorblind-safety rules, and `--cmap` advice for heatmaps — **read `references/color-palettes.md` when the user asks about color schemes or you are unsure which palette fits**.
4. **Render**:
   `python3 scripts/plot_chart.py data.csv --template grouped_bar --x condition --y score --group treatment --error sem --theme nature --column single --out fig1`
   Writes `fig1.svg`, `fig1.pdf`, `fig1.png` (300 DPI), `fig1.stats.json`, and a schema-versioned `fig1.manifest.json`. For TIFF/EPS submission requirements, use `--formats svg,pdf,tiff,eps` (TIFF is 300 DPI). Existing outputs require explicit `--force`. For formal brackets, use `--statistics-source stat-results.json --star-map "A>B=primary;A>C=secondary"`; the plotter resolves stable result IDs, prefers adjusted p-values, and cannot combine this path with exploratory `--compare-groups`.
   For Kaplan-Meier figures, confidence bands are on by default and censoring marks are shown; add `--risk-table` for a number-at-risk table. Use `--no-survival-ci` only when the protocol/journal gives a specific reason.
5. **Significance stars** (optional): add `--compare-groups [--control NAME]` to run scipy tests (two groups: t-test if normal else Mann-Whitney; >2: one-way ANOVA + pairwise) and draw star brackets. Rules: `* p<0.05, ** p<0.01, *** p<0.001, ns` otherwise; brackets start 5% of the y-range above the error bar and step up 5% per level without overlap. Test choice, multiple-comparison (Holm) reminder, and the layout algorithm — **read `references/significance.md` only when star brackets are requested or disputed**.
6. **Multi-panel canvas**: repeat `--panel "template|x|y[|group]"` for a labeled subplot grid (A, B, C …) sharing one theme. Add `--shared-legend`; use `--share-x`/`--share-y` only where panels have compatible units and scales.

## Tier 2: schematic diagrams

For hand-drawn-style architecture/mechanism schematics, write a small declarative JSON (`{"nodes": [...], "edges": [...]}`) and run:
`python3 scripts/excalidraw_gen.py scene.json --out arch.excalidraw.md [--seed 42]`
Output opens directly in Obsidian (excalidraw-plugin) or imports into excalidraw.com. The .excalidraw.md format essentials, SVG fallback, and layout options — **read `references/diagram-formats.md` before writing scene JSON by hand**.

## Tier 3: code-as-diagram

No renderer lives in this environment, so scripts only *check and save* source: `python3 scripts/diagram_check.py --lang mermaid|dot|plantuml --in source.mmd [--out checked.mmd]` runs syntax-level sanity checks (header declaration, bracket balance, common pitfalls) and prints the local render command (`npx mmdc`, `dot -Tsvg`, plantuml jar). Common syntax patterns and pitfalls — **read `references/diagram-formats.md` when a check fails or the user asks for a specific diagram type** (flowchart / sequence / er / gantt / DOT). Do not claim a diagram "renders correctly" from checks alone.

## Export checklist (journal figures)

- [ ] SVG + PDF exported; PNG is 300 DPI and not the only artifact
- [ ] Fonts embedded / TrueType (`pdf.fonttype=42` is set by all themes)
- [ ] Width matches target column (`--column single|double`), text ≥ 7 pt at final size
- [ ] Axis labels include units; panel labels (A, B, C) match caption references
- [ ] Star brackets state the test + correction in the caption (test name comes from the script's stats JSON)

## File index

- `scripts/plot_chart.py` — matplotlib chart engine: six templates, four journal themes (rcParams), `--palette` access to 227 named discrete palettes (scripts/palettes.json), error bars (sd/sem/ci95), scipy significance brackets with non-overlapping layout, multi-panel grid, Kaplan-Meier, vector-first export. `--seed` for jitter.
- `scripts/palettes.json` — 227 discrete color schemes (ggsci / grDevices / RColorBrewer / zhihu-curated top-journal combos), converted from the MIT-licensed lcpmgh/colors collection.
- `scripts/excalidraw_gen.py` — zero-dependency generator of Obsidian-compatible `.excalidraw.md` scenes from a nodes/edges JSON (auto layered layout, label-aware node sizing, bound text, arrows). The SVG fallback (`--out fig.svg`) renders multi-line labels, rectangle/ellipse/diamond shapes with boundary-attached edges, curved fan-out for bidirectional edge pairs, and halo-backed edge labels.
- `scripts/diagram_check.py` — zero-dependency sanity checker + renderer advisor for mermaid / graphviz DOT / plantuml sources.
- `references/chart-templates.md` — six template deep-dives: data shape, required columns, design decisions. Read when picking or debugging a template.
- `references/journal-themes.md` — full theme parameter tables (font sizes, line widths, palettes, spine/tick rules, mm↔inch) and the pre-submission checklist. Read for submission figures.
- `references/significance.md` — star rules, test selection, Holm multiple-comparison reminder, bracket layout algorithm. Read when star brackets are requested.
- `references/color-palettes.md` — palette selection guide: category-count and colorblind-safety rules, journal-matched schemes (npg/aaas/nejm/lancet/jama), recommended workhorses, `--cmap` advice for continuous data. Read when the user asks about color schemes or a palette choice is unclear.
- `references/diagram-formats.md` — .excalidraw.md structure, mermaid/DOT/plantuml patterns and syntax pitfalls. Read for tier-2/3 work.
- `references/artifact-contracts.md` — formal `stat-results` input and reproducible `figure-manifest` output. Read for cross-skill or submission workflows.
- `examples/tier1/` — worked examples for the six templates (example CSVs + rendered PNGs, plus three palette effect images `p_npg/p_nejm/p_zhihu.png`); usable as visual baselines.
