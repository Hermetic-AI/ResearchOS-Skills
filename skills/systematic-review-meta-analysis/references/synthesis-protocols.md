# Synthesis protocols

Statistical synthesis pools study-level effect sizes. It does not replace
risk-of-bias assessment, GRADE, or a pre-specified analysis plan.

## Effect-size extraction

Choose the effect measure compatible with the included studies' data:

- **SMD / Hedges' g** — continuous outcomes reported as means/SDs. Hedges' g
  applies a small-sample bias correction to Cohen's d.
- **Risk ratio (RR)** — binary outcomes from 2x2 tables. Computed on the log
  scale; use a 0.5 zero-cell correction when a cell is empty.
- **Odds ratio (OR)** — binary outcomes, also log-scale with zero-cell
  correction.

Always record the direction of effect so that positive/negative values are
consistent across studies.

## Meta-analysis models

- **Fixed-effect** — assumes one true effect underlies all studies. Use only
  when heterogeneity is negligible and clinically justified.
- **Random-effects (DerSimonian-Laird)** — assumes effects are distributed
  around a mean. Default choice; reports between-study variance tau².

## Heterogeneity

- **Cochran's Q** — chi-squared test for heterogeneity; low power when few
  studies are included.
- **I²** — percentage of variation due to heterogeneity rather than chance.
  Rough guide: 25% low, 50% moderate, 75% high. It describes magnitude, not
  cause.
- **tau²** — absolute between-study variance; used to re-weight studies in
  random-effects pooling.

## Forest plot data

For each study report: estimate, standard error, confidence interval, and the
model weight. The pooled estimate is shown as a diamond with its confidence
interval.

## Publication bias

A synthesis artifact does not assess publication bias. Plan funnel-plot and
Egger-type checks separately, and interpret them cautiously with few studies.

## GRADE

GRADE rates certainty of evidence across risk of bias, inconsistency,
indirectness, imprecision, and publication bias. A pooled effect size is only
one input; do not conflate a precise pooled estimate with high certainty.

## Boundaries

- Pool only compatible estimands, populations, timepoints, and effect measures.
- State the model, heterogeneity, and missing-data decisions before calculation.
- Use `data-analysis-assistant` for validated computation; preserve study-level
  inputs and model settings.
