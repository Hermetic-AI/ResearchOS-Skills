# Repeated-measure, longitudinal, and survival sample size

Use `scripts/longitudinal_power.py` only when its estimand and assumptions match the planned primary analysis. Always repeat calculations across plausible effect, correlation, event, and attrition values.

## Repeated mean

`repeated-mean` targets a constant between-group mean difference averaged over equally informative measurements. Effect size is standardized by the marginal per-measure SD. It assumes compound symmetry with common within-unit correlation and complete measurements before participant-level dropout inflation.

```bash
python scripts/longitudinal_power.py repeated-mean --effect-size 0.40 --measurements 4 --correlation 0.50 --dropout 0.15
```

It is not a generic repeated-measures ANOVA calculator. Time-varying effects, baseline adjustment, visit-specific variances, nonspherical covariance, intermittent missingness, and treatment-by-time contrasts require design-specific software or simulation.

## Longitudinal slope

`longitudinal-slope` targets a between-group difference in linear slopes. The effect is the slope difference per time unit divided by the marginal outcome SD. Measurement spacing matters explicitly.

```bash
python scripts/longitudinal_power.py longitudinal-slope --slope-effect 0.10 --times 0,1,3,6 --correlation 0.50 --dropout 0.15
```

The approximation assumes linear change, equal allocation, common compound-symmetric covariance, and complete scheduled measurements. Random slopes, informative dropout, nonlinear trajectories, ceiling effects, and irregular observation processes need a mixed-model simulation aligned to the planned estimator.

## Survival/log-rank

`survival` uses the Schoenfeld proportional-hazards event approximation. It first estimates required events, then divides by a user-supplied overall probability of observing the event by analysis time and inflates for dropout.

```bash
python scripts/longitudinal_power.py survival --hazard-ratio 0.70 --event-probability 0.60 --power 0.90 --dropout 0.10
```

The event probability must come from credible external/pilot evidence and match accrual, follow-up, censoring, and the endpoint definition. The simple conversion does not model those processes. If proportional hazards may fail, choose the target estimand and analysis first (for example, a milestone probability or restricted mean survival time) and validate power by simulation. Competing risks also require a cause-specific design calculation.

## Source basis

- Schoenfeld, *Sample-Size Formula for the Proportional-Hazards Regression Model*, Biometrics 1983;39:499–503, https://doi.org/10.2307/2531021
- Schoenfeld, *The asymptotic properties of nonparametric tests for comparing survival distributions*, Biometrika 1981;68:316–319, https://doi.org/10.1093/biomet/68.1.316
- Hedeker, Gibbons, and Waternaux, *Sample Size Estimation for Longitudinal Designs with Attrition*, Journal of Educational and Behavioral Statistics 1999;24:70–93, https://doi.org/10.3102/10769986024001070

No source code or proprietary tables from these publications are included; the repository implementation is an independent, documented normal approximation.
