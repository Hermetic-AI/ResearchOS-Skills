# Analysis artifact contracts

Use `../schemas/researchos-artifacts.schema.json` as the canonical interchange schema.

## Input

Read `analysis-plan` when available. Treat deviations from its outcomes, comparisons, alpha, multiplicity rule, or planned models as deviations that must be named and justified; do not silently rewrite the plan after seeing results.

## Outputs

- Cleaning → `cleaning-manifest`, with immutable input/output locators and an ordered list of actions, rationales, and affected counts.
- Inference → `stat-results`, with one stable result `id` per comparison and test name, statistic, exact p-value, effect size/CI when available, adjusted p-value when applicable, and provenance.
- Competing-risk cumulative incidence → `competing-risk-estimate`; do not force descriptive CIF values into hypothesis-test fields.
- Time-series models and forecasts → `time-series-forecast`, including regular frequency, orders, coefficients, intervals, convergence, and warnings.
- Bootstrap/permutation → `resampling-estimate`; beta-binomial posterior comparisons → `bayesian-estimate`. Do not write posterior probabilities into `p_value` fields.
- Model checks → `model-diagnostics`, separate from inferential results so flags cannot be mistaken for conclusions.
- Delta-based missing-data grids → `sensitivity-analysis`; distinguish them from imputed datasets and primary inferential artifacts.

Human-readable Markdown may accompany JSON, but downstream plotting and writing should consume the JSON values rather than retyping them.

```bash
python tools/validate_artifact.py cleaning.json --type cleaning-manifest
python tools/validate_artifact.py results.json --type stat-results
python tools/validate_artifact.py cif.json --type competing-risk-estimate
python tools/validate_artifact.py forecast.json --type time-series-forecast
python tools/validate_artifact.py bootstrap.json --type resampling-estimate
python tools/validate_artifact.py posterior.json --type bayesian-estimate
python tools/validate_artifact.py diagnostics.json --type model-diagnostics
python tools/validate_artifact.py sensitivity.json --type sensitivity-analysis
```
