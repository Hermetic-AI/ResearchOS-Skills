---
name: systematic-review-meta-analysis
description: Plan and audit systematic reviews and meta-analyses with PICOS, transparent screening decisions, PRISMA counts, risk-of-bias assessment boundaries, effect-size extraction, heterogeneity, publication-bias, and GRADE workflows. Use when users ask for a systematic review, PRISMA screening, meta-analysis protocol, study selection log, risk-of-bias plan, evidence certainty, or pooled-effect workflow.
---

# Systematic Review and Meta Analysis

Use this skill only with a prespecified question and explicit inclusion/exclusion criteria. It coordinates records from `scholarly-search-manager` and evidence notes from `literature-reader`; it does not treat search results as included studies.

## Protocol first

```bash
python scripts/init_review.py --root review-001 --title "Review title" --question "Question" --population "..." --intervention "..." --comparator "..." --outcomes "..."
```

The new protocol has `PICOS`, screening states, PRISMA counters, extraction and risk-of-bias placeholders. It is a draft, not a registration or reporting-guideline compliance certificate.

## Record screening decisions

```bash
python scripts/record_screening.py --records records.json --decisions title-abstract-decisions.json --stage title_abstract --out screening-log.json
```

Every input record must have exactly one human-supplied decision. Exclusions and duplicates require a reason. The script validates and preserves the decision log; it does not classify studies.

## Screening and synthesis boundaries

- Record one decision per record with a reason; do not silently exclude duplicates or full texts.
- Assess risk of bias with a tool appropriate to the study design; do not infer it from abstracts.
- Pool only compatible estimands, populations, timepoints, and effect measures. State fixed/random effect model, heterogeneity, and missing-data decisions before calculation.
- Use `data-analysis-assistant` for validated computation, and preserve study-level inputs and seed/model settings.

- `scripts/audit_risk_of_bias.py` — validates a human-assessed risk-of-bias ledger for study/tool/domain/judgment/rationale completeness; it never assigns RoB judgments.

## Effect-size synthesis and meta-analysis

```bash
python scripts/meta_analysis.py --mode effects --studies studies.json --measure smd --out effects.json
python scripts/meta_analysis.py --mode pool --effects effects.json --model random --out meta.json
```

`--mode effects` derives per-study SMD / Hedges' g / RR / OR with confidence
intervals. `--mode pool` runs fixed or DerSimonian-Laird random-effects
inverse-variance meta-analysis, reporting Q, I², tau², and forest-plot weights.

## Resources

- `scripts/meta_analysis.py` — effect-size computation and inverse-variance meta-analysis.
- `references/synthesis-protocols.md` — synthesis decisions, heterogeneity, and GRADE boundaries.
- `scripts/init_review.py` — protected PICOS/PRISMA protocol scaffold.
