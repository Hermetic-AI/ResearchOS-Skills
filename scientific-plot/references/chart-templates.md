# Chart Templates — Data Shapes and Design Details

Six templates in `scripts/plot_chart.py`. Read this when picking a template or when a render looks wrong.

## grouped_bar

- **Data shape**: long-format CSV — one categorical x column, one numeric y column, optional categorical group column. Raw rows (not pre-aggregated); the script computes mean + error per cell.
- **Required args**: `--x`, `--y`; `--group` for grouped bars (omit for simple bars).
- **Error**: `--error sd|sem|ci95|none`. Default `sd`. SEM looks smaller but is a precision-of-mean statement — say which in the caption.
- **Design**: grouped bars with caps on error bars; y-axis starts at 0 unless `--no-zero-baseline` (truncated bar axes exaggerate differences — flag it in the caption if used). With `--compare-groups`, star brackets span x categories within each group cluster (or groups within one x when no `--group`).

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

## Multi-panel

Repeat `--panel "template|x|y[|group[|z]]"` (pipe-separated) instead of `--template/--x/--y`. Each panel gets a bold label A, B, C … at the top-left. Panels share the theme and column width; the grid is one row for ≤ 2 panels, otherwise roughly square.
