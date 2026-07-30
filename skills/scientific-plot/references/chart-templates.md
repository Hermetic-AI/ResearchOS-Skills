# Chart Templates — Data Shapes and Design Details

Six templates in `scripts/plot_chart.py`. Read this when picking a template or when a render looks wrong.

## grouped_bar

- **Data shape**: long-format CSV — one categorical x column, one numeric y column, optional categorical group column. Raw rows (not pre-aggregated); the script computes mean + error per cell.
- **Required args**: `--x`, `--y`; `--group` for grouped bars (omit for simple bars).
- **Error**: `--error sd|sem|ci95|none`. Default `sd`. SEM looks smaller but is a precision-of-mean statement — say which in the caption.
- **Design**: grouped bars with caps on error bars; y-axis starts at 0 unless `--no-zero-baseline` (truncated bar axes exaggerate differences — flag it in the caption if used). With `--compare-groups`, when `--group` is given star brackets compare the groups within the FIRST x category only (state that category in the caption); without `--group`, brackets compare across x categories.

## scatter_regression

- **Data shape**: two numeric columns; optional group column for per-group fits.
- **Required args**: `--x`, `--y`; optional `--group`.
- **What it draws**: points + least-squares line + 95% confidence band of the *fit* (not prediction interval). Reports slope, intercept, R, p in the stats JSON.
- **Design**: if the claim is correlation, also report Spearman when the relationship is monotone-but-nonlinear (that decision belongs to data-analysis-assistant; this script only draws the linear fit).

## boxplot

- **Data shape**: numeric y column + categorical x (or group) column.
- **When**: n ≥ ~30 per group, or when outliers matter more than distribution shape. Box hides bimodality.
- **What it draws**: matplotlib boxplot (median line, IQR box, 1.5×IQR whiskers, flier points). Add `--overlay-points` to jitter raw points on top (uses `--seed`).

## violin

- **Data shape**: same as boxplot.
- **When**: n < 30, or when distribution shape (bimodality, skew) is the point. **Always keep the scatter overlay on for small n** (default on; `--no-overlay-points` to disable) — a violin from 8 points without the raw dots is misleading.
- **What it draws**: KDE violin + inner boxplot + jittered raw points.

## heatmap

- **Data shape**: either (a) long format with `--x`, `--y`, `--z` (pivoted), or (b) a wide matrix CSV where the first column is the row label and remaining columns are numeric.
- **What it draws**: diverging colormap (`RdBu_r`) centered at `--center` (default 0), colorbar, cell values annotated when ≤ 12×12.
- **Design**: use the diverging palette only when 0 (or `--center`) is meaningful (log2 fold change, correlation, residuals). For sequential magnitudes (counts, intensities) the center is arbitrary — prefer `--cmap viridis`.

## survival

- **Data shape**: `--time` (duration), `--event` (1 = event occurred, 0 = censored), optional `--group`.
- **What it draws**: Kaplan-Meier step curves per group with censoring tick marks; stats JSON carries median survival per group. No log-rank test in this script — if the user wants a p-value for the curves, that is a data-analysis-assistant task.
- **Design**: y-axis fixed 0–1; do not truncate.

## volcano

- **Data shape**: one supplied effect-size column (`--x`, commonly log2 fold change) and one supplied p-value or adjusted q-value column (`--y`).
- **What it draws**: effect size versus `-log10(p)`, with descriptive lines at `--effect-threshold` and `--p-threshold` (defaults 1 and 0.05). Points meeting both supplied thresholds are colored separately.
- **Boundary**: this template does not calculate p-values, correct multiple comparisons, or establish discoveries. Use the adjusted-value column only when the analysis plan requires it, state which value was plotted, and keep a finite floor for underflowed zero values.

## manhattan

- **Data shape**: supplied chromosome labels (`--group`), within-chromosome non-negative positions (`--x`), and p-values or adjusted q-values (`--y`).
- **What it draws**: cumulative positions grouped by supplied chromosome label and `-log10(p)`, with an optional descriptive p-value line (`--p-threshold`).
- **Boundary**: it does not validate genome build, chromosome lengths, variant identity, coordinate sorting, p-value calculation, or multiple-testing correction. State the assembly and whether p or q-values were plotted outside the figure.

## pca

- **Data shape**: rows are samples and all columns are numeric features, except an optional categorical `--group` label column.
- **What it draws**: PC1 versus PC2 from centered (not scaled) features, and records explained-variance ratios in the stats artifact.
- **Boundary**: feature filtering, missing-value policy, normalization, scaling, batch correction, and interpretation belong upstream. Report those choices; PCA is not UMAP.

## umap

- **Data shape**: same numeric feature matrix as `pca`; optional `--group` is a categorical label column.
- **Dependency and reproducibility**: requires explicit optional `umap-learn`; set `--seed` and record the installed version, `--neighbors`, preprocessing, feature filtering, and missing-data policy.
- **Boundary**: UMAP is an exploratory projection, not a cluster test or evidence of group separation. It must not replace PCA, model diagnostics, or a prespecified inferential analysis.

## enrichment_bubble

- **Data shape**: supplied term labels (`--y`), enrichment scores (`--x`), and p-values or adjusted q-values (`--z`).
- **What it draws**: score on x, terms on y, and bubble area proportional to `-log10` of the supplied p/q value; sign is shown with two colors.
- **Boundary**: it does not choose a gene universe, run pathway analysis, resolve term redundancy, or correct multiple tests. State the database/version, background universe, score meaning, and whether p or q-values were supplied.

## network

- **Data shape**: source (`--x`) and target (`--y`) columns, with optional non-negative edge weight (`--z`).
- **What it draws**: a deterministic circular layout whose edge width is proportional to supplied weights.
- **Boundary**: this is not graph inference. It does not infer missing edges, directionality, communities, centrality, or causal structure; use `knowledge-graph-builder` for semantic graph artifacts.

## sankey

- **Data shape**: source (`--x`), target (`--y`), and non-negative flow (`--z`) columns.
- **What it draws**: a two-sided source-to-target flow diagram, with line width proportional to the supplied flow.
- **Boundary**: this is not an arbitrary multi-stage Sankey solver. It does not infer hierarchy, validate flow conservation, aggregate duplicate edges, or establish causal flow; provide an already-reviewed flow table.

## Multi-panel

Repeat `--panel "template|x|y[|group[|z]]"` (pipe-separated) instead of `--template/--x/--y`. Each panel gets a bold label A, B, C … at the top-left. Panels share the theme and column width; the grid is one row for ≤ 2 panels, otherwise roughly square.
