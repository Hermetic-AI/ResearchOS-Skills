---
name: causal-inference-assistant
description: Plan auditable observational causal analyses with explicit estimands, DAG variables, identification assumptions, matching/weighting/IV/DID/RDD/synthetic-control routing, diagnostics, and sensitivity analyses. Use when users ask causal questions from non-randomized data, DAGs, confounder adjustment, propensity scores, instrumental variables, difference-in-differences, regression discontinuity, synthetic control, or causal sensitivity analysis.
---

# Causal Inference Assistant

Start with a causal question and an estimand, not a model. This skill documents assumptions; it cannot prove exchangeability, exclusion restrictions, parallel trends, or causal validity from data alone.

## Create an analysis charter

```bash
python scripts/init_causal_plan.py --out causal-plan.json --treatment "A" --outcome "Y" --estimand ATE --population "Eligible cohort"
```

The draft requires a DAG variable inventory, pre-treatment confounder rationale, positivity/consistency checks, design-specific assumptions, diagnostics, and sensitivity analyses. Route model fitting to `data-analysis-assistant` only after the charter is reviewed.

## Validate a declared DAG

```bash
python scripts/validate_dag.py --dag dag.json --out dag-audit.json
```

The DAG JSON declares nodes with one role and directed edges. The audit rejects malformed/cyclic graphs and flags role conflicts; it deliberately does not select an adjustment set or establish identification.

`python scripts/e_value.py --risk-ratio 2.1 --confidence-limit 1.3` calculates a descriptive E-value for a supplied risk-ratio-scale estimate; it is not an identification test.

## Method routing

- Backdoor adjustment / matching / weighting: measured confounding, overlap, correct temporal ordering.
- IV: relevance, exclusion, independence, monotonicity and interpretable complier estimand.
- DID: treatment timing, no anticipation, plausible parallel trends/event-study diagnostics.
- RDD: fixed threshold, no manipulation, bandwidth and continuity diagnostics.
- Synthetic control: one/few treated units, pre-period fit and donor-pool justification.

Never adjust for post-treatment variables, colliders, or instruments merely because they improve prediction.

## Estimate and sensitivity

```bash
python scripts/causal_estimate.py --method psm --data data.json --treatment treated --out matched.json
python scripts/causal_estimate.py --method iptw --data data.json --treatment treated --out weighted.json
python scripts/causal_estimate.py --method did --data data.json --treatment treated --time post --out did.json
python scripts/causal_estimate.py --method rdd --data data.json --running score --cutoff 0.0 --out rdd.json
python scripts/causal_estimate.py --method evalue --risk-ratio 2.1 --confidence-limit 1.3
```

PSM/IPTW estimate propensity scores via logistic regression (Newton-Raphson)
and report balance/weights. DiD and RDD estimate design-specific effects with
standard errors. `evalue` computes the E-value for a risk-ratio-scale estimate.

## Resources

- `scripts/causal_estimate.py` — PSM, IPTW, DiD, RDD estimation and E-value sensitivity.
- `references/design-implementation.md` — design assumptions and sensitivity analysis rules.
- `scripts/init_causal_plan.py` — protected causal estimand/assumption charter.
