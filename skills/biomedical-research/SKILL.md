---
name: biomedical-research
description: Plan auditable biomedical research workflows with population/specimen definitions, endpoints, safety monitoring, biospecimen governance, registration, reporting guidelines, and evidence boundaries. Use when users need a biomedical study plan, clinical/translational research checklist, endpoint plan, specimen handling plan, safety-monitoring checklist, or biomedical reporting readiness review.
---

# Biomedical Research

This skill prepares research artifacts; it never grants IRB/ethics approval, clinical eligibility, diagnostic interpretation, treatment advice, laboratory accreditation, or regulatory authorization.

## Initialize a biomedical study plan

```bash
python scripts/init_biomedical_plan.py --out biomedical-plan.json --study "Study title" --study-type observational
```

The plan records population, endpoints, interventions/exposures, specimens, safety, consent, registration, reporting and data governance decisions. Attach authorized sources before considering a protocol ready.

## Workflow

1. Define study purpose, population, eligibility, units, endpoints/estimands, timepoints and clinically meaningful thresholds.
2. Record specimen chain-of-custody, assay version, blinding, batch effects, storage, destruction and access constraints where applicable.
3. Use `protocol-authoring`, `experiment-designer`, `data-analysis-assistant`, `research-integrity-and-ethics`, and `research-data-management` for their specialist artifacts.
4. Preserve safety/monitoring, adverse-event, consent, registration and reporting decisions without inferring approvals.

## Resources

- `scripts/init_biomedical_plan.py` — protected biomedical study-planning scaffold.
