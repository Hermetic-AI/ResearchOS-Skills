# Design implementation and sensitivity calculations

Observational causal analyses rest on assumptions that data alone cannot
prove. Document every assumption explicitly and probe its fragility.

## Estimand first

Define the estimand (ATE, ATT, ATC, CATE) and the target population before
choosing a method. The estimand determines which confounders must be adjusted
and which diagnostics matter.

## Propensity-score methods

- **Estimation** — logistic regression of treatment on pre-treatment
  confounders. Check positivity/overlap (no propensity score near 0 or 1).
- **Matching** — 1:1 greedy nearest-neighbor within a caliper (e.g. 0.2 SD of
  the logit propensity). Report the number of matched pairs and standardized
  mean differences after matching.
- **IPTW** — inverse-probability-of-treatment weights, stabilized and
  optionally truncated. Check weight distributions for extreme values.

## Difference-in-differences

- Requires parallel pre-trends between treated and control groups.
- The estimand is the interaction (treated x post) term.
- Cluster standard errors at the unit level when repeated measures are present.

## Regression discontinuity

- Sharp design: treatment is a deterministic function of the running variable
  crossing a cutoff.
- Fit local-linear OLS on each side of the cutoff within a bandwidth.
- The estimand is the jump at the cutoff; it is local to units near the cutoff.
- Check for manipulation of the running variable and covariate balance.

## Sensitivity analyses

- **E-value** — the minimum strength of association (on the risk-ratio scale)
  that an unmeasured confounder would need to have with both treatment and
  outcome to explain away the observed effect. Compute it for the estimate and
  for the confidence limit closest to the null.
- Report E-values on the risk-ratio scale; convert odds/hazard ratios only with
  a justified approximation.

## Boundaries

- No method proves exchangeability, exclusion restrictions, parallel trends, or
  continuity from data alone.
- Do not adjust for post-treatment variables, colliders, or instruments without
  a DAG-based rationale.
- Route model fitting to `data-analysis-assistant` only after the causal
  charter is reviewed.
