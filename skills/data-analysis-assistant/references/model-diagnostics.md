# Model diagnostics

Run diagnostics after fitting a prespecified OLS or GLM model, before treating individual coefficients as final conclusions.

```bash
python scripts/model_diagnostics.py data.csv --formula "outcome ~ treatment + baseline" --family ols --out diagnostics.json
python scripts/model_diagnostics.py counts.csv --formula "count ~ treatment + exposure" --family poisson --out diagnostics.json
```

The artifact reports VIF, the largest Cook's distances/leverage values, and:

- OLS: residual distribution screen (Jarque–Bera), Durbin–Watson, and Breusch–Pagan screen;
- GLM: Pearson dispersion; Poisson dispersion materially above 1 is a prompt to assess overdispersion, excess zeros, dependence, or an alternative model.

These are diagnostic flags, not automated exclusion rules or binary proof that a model is valid. Inspect data provenance, plots, functional form, residual patterns, covariate overlap, cluster structure, and substantive plausibility. VIF is undefined/unstable under perfect collinearity and is not a causal-confounding diagnostic. Few clusters and influential units require design-specific sensitivity analysis.

The implementation uses public [Statsmodels diagnostics and influence APIs](https://www.statsmodels.org/stable/stats.html); no upstream code is bundled.
