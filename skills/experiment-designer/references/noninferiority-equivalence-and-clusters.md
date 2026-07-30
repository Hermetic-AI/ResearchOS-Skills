# Noninferiority, equivalence, clustering, and attrition

Use this resource before running `scripts/power_analysis.py` for a non-superiority hypothesis or a cluster-randomized design.

## Noninferiority and equivalence

- A noninferiority margin is a scientific and clinical decision, not a value selected to make sample size convenient. Justify it from preserved effect, measurement scale, prior evidence, and domain requirements.
- This CLI uses a positive standardized margin. For noninferiority, larger effects are favorable and the null boundary is `effect <= -margin`.
- Equivalence uses two one-sided tests (TOST) with symmetric standardized bounds `[-margin, +margin]`. The expected effect must be strictly inside the bounds.
- The `alpha` argument is applied to each one-sided component for noninferiority/TOST. Leave `--sides` at its default; the CLI handles the hypothesis-specific tails internally.
- The implementation is a normal approximation for standardized mean tests. It does not cover binary-risk margins, ratio-scale margins, repeated measures, survival outcomes, covariate adjustment, or regulatory margin selection.

```bash
python scripts/power_analysis.py --test t_ind --solve n --hypothesis noninferiority --effect-size 0 --margin 0.30 --power 0.90
python scripts/power_analysis.py --test t_ind --solve n --hypothesis equivalence --effect-size 0 --margin 0.30 --power 0.90
```

Report the assumed true effect and a sensitivity grid over plausible margins/effects. For equivalence, plan and report the confidence interval against both bounds; a nonsignificant superiority test does not demonstrate equivalence.

## Cluster randomization

For mean cluster size `m`, intracluster correlation `ICC`, and cluster-size coefficient of variation `CV`, the CLI uses the approximate design effect:

`DE = 1 + [m(1 + CV²) - 1] × ICC`

It multiplies the independently randomized sample size by `DE`, rounds upward to complete clusters, then inflates enrollment for individual attrition. Use `CV=0` for equal cluster sizes.

```bash
python scripts/power_analysis.py --test t_ind --solve n --effect-size 0.40 --power 0.90 --cluster-size 20 --icc 0.04 --cluster-cv 0.30 --dropout 0.15
```

This approximation is only a screening calculation. Before sign-off:

1. confirm the randomized unit and whether treatment arms need separate cluster counts;
2. plan a cluster-aware analysis and degrees-of-freedom method;
3. assess the minimum number of independent clusters, not only participant count;
4. distinguish participant attrition from whole-cluster loss;
5. vary ICC, cluster-size distribution, effect, and dropout assumptions;
6. use a design-specific package or simulation for small cluster counts, unequal allocation, stratification/matching, repeated measures, or binary/survival outcomes.

Never estimate ICC from the outcome data and then present the resulting post-hoc power as an a priori design.
