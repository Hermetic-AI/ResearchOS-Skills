---
name: scientific-plot
description: Scientific figure generation assistant covering three priority tiers — (1) publication-grade statistical charts from CSV (grouped bar with error bars, scatter with 95% CI regression band, boxplot, violin with scatter overlay, diverging heatmap, Kaplan-Meier survival) with journal themes (nature / science / ieee / prism), automatic significance-star brackets from scipy tests, and vector-first export (PDF/SVG + PNG 300 DPI); (2) hand-drawn-style schematic generation as Obsidian-compatible .excalidraw.md scenes and simple SVG box-and-arrow diagrams; (3) code-as-diagram sources (mermaid / graphviz DOT / plantuml) with syntax-level sanity checks and renderer suggestions. Use when the user asks to 画论文插图/画统计图/显著性星标图/误差棒图/画箱线图小提琴图/画热图/生存曲线/导出300dpi/投稿图片格式/画流程图/画架构示意图/excalidraw图/mermaid图 ("make a figure from this CSV", "add significance stars", "Nature-style figure", "export 300 dpi", "draw a flowchart/architecture diagram"). NOT for computing statistics themselves (test selection, p-values, cleaning, effect sizes) — use data-analysis-assistant, which does the math; this skill only draws what the data says. NOT for writing figure captions or paper prose — use paper-writing-assistant instead.
---

# Scientific Plot (科研绘图)

For researchers who need figures: publication-grade statistical charts (Prism/Origin/Excel replacements), hand-drawn-style schematics (Excalidraw/SVG), and code-as-diagram sources (mermaid/graphviz/plantuml). Reports to the user are in Chinese by default; figure labels and artifacts follow the artifact's language (journal figures are usually English).

**Global conventions**
- **Draw, don't compute**: this skill renders figures. If the user has no test results yet and asks *which* test to run, hand off to data-analysis-assistant; use `--compare-groups` here only for quick in-figure star brackets.
- **Vector first**: always deliver SVG + PDF; PNG is the 300 DPI fallback for slides/word. Never deliver PNG alone for journal submission.
- **Reproducibility**: prefer the bundled scripts; pass `--seed` whenever jitter/sampling is involved and record the exact CLI in the figure log.
- **Dependencies**: `plot_chart.py` needs matplotlib + numpy once (`pip install matplotlib numpy`; `pip install scipy` for auto star brackets). The diagram scripts are zero-dependency.

## Priority tiers

| Tier | Capability | Entry point |
|------|-----------|-------------|
| 1 (highest) | Statistical charts from CSV | `python3 scripts/plot_chart.py data.csv --template <t> --theme nature --out fig1` |
| 2 | Schematic diagrams | `python3 scripts/excalidraw_gen.py scene.json --out arch.excalidraw.md` |
| 3 | Code-as-diagram | `python3 scripts/diagram_check.py --lang mermaid --in flow.mmd` |

## Tier 1: statistical charts

1. **Pick a template** (data shape → template):

   | Data shape | Template |
   |---|---|
   | categorical x × numeric y, ± group | `grouped_bar` |
   | two numeric variables, trend claim | `scatter_regression` |
   | distribution per group, n ≥ 30 | `boxplot` |
   | distribution per group, small n | `violin` (scatter overlay) |
   | matrix / x×y intensity | `heatmap` (diverging, centered 0) |
   | time-to-event with censoring | `survival` (Kaplan-Meier) |

   Template design details (when violin beats boxplot, field requirements) — **read `references/chart-templates.md` only when unsure which template fits or a render looks wrong**.
2. **Pick a journal theme**: `nature` (7 pt body / 8 pt title, 89 mm single / 183 mm double column), `science` (7–9 pt, no grid, outward ticks), `ieee` (grayscale, dash/hatch series, print-safe), `prism` (default colors, slides/demos). Full parameter tables and the pre-submission checklist — **read `references/journal-themes.md` only when preparing a submission figure or the user names a journal**.
3. **Render**:
   `python3 scripts/plot_chart.py data.csv --template grouped_bar --x condition --y score --group treatment --error sem --theme nature --column single --out fig1`
   Writes `fig1.svg`, `fig1.pdf`, `fig1.png` (300 DPI). Use `--title/--xlabel/--ylabel` and `--encoding` for non-UTF-8 CSVs.
4. **Significance stars** (optional): add `--compare-groups [--control NAME]` to run scipy tests (two groups: t-test if normal else Mann-Whitney; >2: one-way ANOVA + pairwise) and draw star brackets. Rules: `* p<0.05, ** p<0.01, *** p<0.001, ns` otherwise; brackets start 5% of the y-range above the error bar and step up 5% per level without overlap. Test choice, multiple-comparison (Holm) reminder, and the layout algorithm — **read `references/significance.md` only when star brackets are requested or disputed**.
5. **Multi-panel canvas**: repeat `--panel "template|x|y[|group]"` for a labeled subplot grid (A, B, C …) sharing one theme.

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

- `scripts/plot_chart.py` — matplotlib chart engine: six templates, four journal themes (rcParams), error bars (sd/sem/ci95), scipy significance brackets with non-overlapping layout, multi-panel grid, Kaplan-Meier, vector-first export. `--seed` for jitter.
- `scripts/excalidraw_gen.py` — zero-dependency generator of Obsidian-compatible `.excalidraw.md` scenes from a nodes/edges JSON (auto layered layout, bound text, arrows).
- `scripts/diagram_check.py` — zero-dependency sanity checker + renderer advisor for mermaid / graphviz DOT / plantuml sources.
- `references/chart-templates.md` — six template deep-dives: data shape, required columns, design decisions. Read when picking or debugging a template.
- `references/journal-themes.md` — full theme parameter tables (font sizes, line widths, palettes, spine/tick rules, mm↔inch) and the pre-submission checklist. Read for submission figures.
- `references/significance.md` — star rules, test selection, Holm multiple-comparison reminder, bracket layout algorithm. Read when star brackets are requested.
- `references/diagram-formats.md` — .excalidraw.md structure, mermaid/DOT/plantuml patterns and syntax pitfalls. Read for tier-2/3 work.
