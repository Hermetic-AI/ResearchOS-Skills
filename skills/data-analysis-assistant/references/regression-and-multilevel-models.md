# Regression, GLM, ANCOVA, repeated-measure GEE, and mixed models

Use `scripts/model_analysis.py` after profiling/cleaning and after confirming the estimand and model in the `analysis-plan`. Install the optional stack with `python -m pip install -e ".[models]"`.

## Model routing

- `ols`: continuous outcome with a prespecified linear mean model.
- `ancova`: the same OLS engine, explicitly labeled ANCOVA; include treatment and prespecified baseline outcome/covariates. Do not adjust for post-treatment variables.
- `glm`: Gaussian, binomial, Poisson, or negative-binomial family. Match the response scale and distribution; coefficients remain on the link scale unless transformed deliberately.
- `gee`: population-average repeated/clustered analysis with independence, exchangeable, or AR(1) working correlation and cluster-robust inference.
- `mixedlm`: subject/cluster-specific linear mixed model with random intercept by default; use `--re-formula` only when the random-effects structure is scientifically justified and supported by the data.

```bash
python scripts/model_analysis.py clean.csv --model ols --formula "score ~ treatment + age" --out results.json
python scripts/model_analysis.py clean.csv --model ancova --formula "followup ~ treatment + baseline" --cov-type HC3 --out results.json
python scripts/model_analysis.py clean.csv --model glm --family binomial --formula "response ~ treatment + baseline" --out results.json
python scripts/model_analysis.py long.csv --model gee --formula "score ~ treatment * time" --groups subject_id --cov-structure exchangeable --out results.json
python scripts/model_analysis.py long.csv --model mixedlm --formula "score ~ treatment * time" --groups subject_id --re-formula "1 + time" --out results.json
```

The restricted formula interface permits column names, `C(column)`, numbers, and `~ + - * :`; it rejects arbitrary Python expressions. Rename columns to simple identifiers before modeling.

## Required checks

1. Confirm outcome type, link, independent unit, repeated/cluster unit, treatment timing, and covariate causal role.
2. Inspect missingness and record rows dropped. Complete-case deletion is not automatically valid under MAR/MNAR.
3. Diagnose linearity, residual distribution/variance, influential observations, collinearity, GLM dispersion and zero inflation, covariance structure, random-effect singularity, and convergence. The model CLI does not replace those diagnostics.
4. Interpret coefficients on the correct scale and include confidence intervals. A coefficient is an unstandardized effect estimate, not a universal effect size.
5. For interactions, report planned contrasts/marginal effects instead of interpreting only component coefficients.
6. Compare ML fits—not REML likelihoods—when fixed-effect structures differ. Avoid data-driven random-effect simplification without disclosure.
7. Treat any fitted formula absent from `analysis-plan.planned_models` as a named deviation; the CLI records an exact-string warning when `--analysis-plan` is supplied.

The output is a `stat-results` artifact with stable coefficient IDs, estimates, test statistics, p-values, confidence intervals, model metadata, provenance, convergence state, and deletion warnings. Downstream plots should refer to result IDs rather than recomputing the model.

Implementation/API basis: [Statsmodels formula API](https://www.statsmodels.org/stable/api.html), [formula safety/evaluation environment](https://www.statsmodels.org/stable/generated/statsmodels.formula.api.glm.html), and [GEE documentation](https://www.statsmodels.org/stable/gee.html). Pandas and Statsmodels are optional installed dependencies; no upstream code is vendored.
