---
name: survey-and-psychometrics
description: Plan auditable survey design and psychometric validation including constructs, item mapping, cognitive testing, reliability, validity, EFA, CFA, measurement invariance, IRT, and Rasch workflows. Use when users ask to design a questionnaire, validate a scale, assess reliability/validity, run factor analysis, test measurement invariance, or plan IRT/Rasch analysis.
---

# Survey and Psychometrics

Define the construct and intended use before choosing reliability thresholds or factor models. A high alpha alone does not validate a scale; do not reuse copyrighted instruments or claim validation without an appropriate sample and analysis.

## Create a validation charter

```bash
python scripts/init_scale_plan.py --out scale-plan.json --construct "Construct" --population "Population" --use "group comparison"
```

The charter records construct definition, item/content evidence, response format, translation/accessibility, sampling, EFA/CFA split or replication, reliability, invariance, IRT/Rasch, and missing-data decisions.

## Compute transparent internal consistency

```bash
python scripts/cronbach_alpha.py responses.csv --items q1,q2,q3 --out reliability.json
```

The calculation uses complete cases only and records every dropped row count. Specify `--reverse` and `--max-score` for declared reverse-scored items. Alpha is one limited consistency statistic, not a validation conclusion.

`python scripts/audit_item_responses.py responses.csv --items q1,q2 --min-score 1 --max-score 5` audits item completeness and declared ranges before psychometric modeling.

## Analysis boundaries

- Check item wording, cognitive interviews/pilot feedback, reverse coding, dimensionality, local dependence, and floor/ceiling effects.
- Pre-specify whether EFA is exploratory and CFA/invariance are confirmatory; avoid selecting models solely by fit indices.
- Compare groups only after the required level of measurement invariance for the intended claim is supported.
- Route calculations to `data-analysis-assistant`; retain item-level data permissions and never expose respondent identifiers.

## Factor analysis, reliability, and Rasch

```bash
python scripts/psychometrics.py --mode efa --csv responses.csv --items q1,q2,q3,q4 --factors 2 --out efa.json
python scripts/psychometrics.py --mode reliability --csv responses.csv --items q1,q2,q3 --out reliability.json
python scripts/psychometrics.py --mode rasch --csv responses.csv --items q1,q2,q3 --out rasch.json
```

`--mode efa` runs principal-factor extraction with varimax rotation.
`--mode reliability` computes Cronbach's alpha, item-total correlations, and
alpha-if-item-deleted. `--mode rasch` fits a basic 1PL model and reports item
difficulty, person ability, and infit.

## Resources

- `scripts/psychometrics.py` — EFA, reliability, item-total correlations, and basic Rasch fit.
- `references/factor-and-irt.md` — factor analysis, invariance, and IRT/Rasch guidance.
- `scripts/init_scale_plan.py` — protected construct/psychometric validation charter.
