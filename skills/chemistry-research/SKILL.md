---
name: chemistry-research
description: Plan auditable chemistry-research workflows with reaction or formulation conditions, reagent and sample provenance, analytical evidence, yield/selectivity boundaries, hazard/waste decisions, and data recording. Use when users need a chemistry experiment plan, reaction record, analytical characterization checklist, synthesis provenance plan, chemistry data ledger, or laboratory reporting readiness review.
---

# Chemistry Research

This skill prepares documentation, not laboratory instructions or safety authorization. Do not infer identity, purity, yield, selectivity, mechanism, stability, or hazard from a reaction scheme or a single analytical trace.

## Initialize a chemistry experiment plan

```bash
python scripts/init_chemistry_plan.py --out chemistry-plan.json --objective "Objective" --experiment-type synthesis
```

The plan captures declared reagents, conditions, sample lineage, analytical methods, controls, uncertainty, waste, and data artifacts. It does not prescribe procedures or run experiments.

## Workflow

1. Record intended objective, reagent identities/lot sources, reaction or formulation variables, controls, and planned stopping/failure criteria.
2. Define sample IDs, chain of custody, analytical methods, calibration/reference material, raw data paths, and integration/interpretation boundaries.
3. Link hazard, PPE, incompatibility, storage, spill and waste decisions to authorized local SOPs; do not replace them.
4. Use `experiment-designer`, `data-analysis-assistant`, `research-data-management`, and `research-integrity-and-ethics` for specialist artifacts.

## Resources

- `scripts/init_chemistry_plan.py` — protected chemistry experiment/provenance scaffold.
