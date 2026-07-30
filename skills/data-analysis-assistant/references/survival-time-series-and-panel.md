# Survival, competing risks, time series, and panel data

Install `.[models]` and use these workflows only after defining the estimand, time origin/index, observation unit, censoring/missingness mechanism, and dependence structure in the analysis plan.

## Cox proportional hazards

```bash
python scripts/survival_analysis.py cox survival.csv --formula "time ~ treatment + age" --status event --ties efron --out cox.json
```

`event` must be binary (`1` event, `0` right-censored). Use `--entry` for delayed entry, `--strata` for nonproportional baseline strata, and `--cluster` for grouped robust covariance. Report hazard ratios and confidence intervals only after checking proportional hazards, functional form, influential observations, event count per parameter, and informative censoring. A hazard ratio is neither a risk ratio nor a time ratio.

## Competing risks

```bash
python scripts/survival_analysis.py competing-risk competing.csv --time time --status cause --group treatment --at-times 12 24 36 --out cif.json
```

Use `0` for censoring and positive integers for mutually exclusive causes. Output is an Aalen–Johansen cumulative-incidence estimate with standard errors. It deliberately does **not** claim a Gray test or Fine–Gray subdistribution model. A cause-specific Cox model can be fitted by creating a prespecified binary event indicator for one cause, but its hazard estimand must not be relabeled as a subdistribution hazard.

## Time series

```bash
python scripts/temporal_panel_analysis.py timeseries series.csv --date month --value outcome --order 1,1,1 --seasonal-order 1,0,1,12 --steps 12 --out forecast.json
```

The SARIMAX workflow requires a unique, sorted, regular time index. If frequency cannot be inferred, define aggregation/alignment first and pass `--freq`; do not silently treat irregular observations as equally spaced. Inspect residual autocorrelation, stationarity/invertibility, seasonality, structural breaks, leakage, rolling-origin validation, and interval coverage. Forecast intervals are conditional on the fitted model and do not include model-selection uncertainty.

## Panel fixed effects

```bash
python scripts/temporal_panel_analysis.py panel panel.csv --formula "outcome ~ exposure + control" --entity firm --time year --effects two-way --out panel.json
```

The implementation adds entity/time indicator effects and clusters covariance by entity by default. It reports coefficients from the within-model while omitting nuisance fixed-effect dummy coefficients from `stat-results`. Confirm within-unit variation, parallel-trend or strict-exogeneity assumptions as applicable, serial/cross-sectional dependence, few-cluster corrections, dynamic-panel bias, and whether weights or staggered treatment require a specialized estimator. Two-way fixed effects are not automatically a valid difference-in-differences design.

## Artifact routing and API basis

- Cox and panel coefficients → `stat-results`.
- Cumulative incidence → `competing-risk-estimate`.
- SARIMAX coefficients and forecasts → `time-series-forecast`.

Implementation follows the public [Statsmodels duration API](https://www.statsmodels.org/stable/duration.html), [SARIMAX API](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html), and [sandwich covariance API](https://www.statsmodels.org/stable/stats.html). No upstream code is bundled.
