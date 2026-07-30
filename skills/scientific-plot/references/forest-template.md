# Forest plot

- **Data shape**: one row per estimate, with a label column (`--y`), effect estimate (`--x`), and already-computed lower/upper limits (`--ci-low`, `--ci-high`).
- **What it draws**: estimate points, horizontal confidence intervals, and a dashed reference at `--center` (default `0`). It never computes an effect size or confidence interval.
- **Use**: show comparable model coefficients or study-level estimates. Ensure all estimates are on the same scale; use `--center 1` for ratio measures where one is the null.
- **Guardrail**: input confidence limits must enclose the estimate. Cite the analysis artifact supplying them in the figure caption or manifest provenance.

