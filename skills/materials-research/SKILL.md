---
name: materials-research
description: Plan auditable materials-research workflows with composition, synthesis/processing, sample lineage, characterization, test conditions, uncertainty, safety, and data-provenance decisions. Use when users need a materials experiment plan, synthesis record, characterization checklist, sample lineage plan, property-test protocol, or materials data provenance review.
---

# Materials Research

Do not infer material identity, phase, purity, performance, stability, or safety from a nominal composition alone. Preserve batch, process and instrument context; do not treat an uncalibrated or incomplete measurement as a property claim.

## Initialize a materials plan

```bash
python scripts/init_materials_plan.py --out materials-plan.json --material-system "System" --target-property "Property"
```

The plan records formulation, process variables, sample/batch lineage, characterization and test conditions, calibration/uncertainty, safety and provenance. It does not execute synthesis or analyze instruments.

## Workflow

1. Declare intended material system, formulation ranges, synthesis route, process variables and batch/sample IDs.
2. Define characterization methods, calibration/reference materials, instrument settings, environmental conditions and raw-data locations.
3. Pre-specify property tests, replicates, failure criteria, uncertainty treatment and sample exclusion rules.
4. Use `experiment-designer`, `data-analysis-assistant`, `scientific-plot`, `research-data-management`, and `research-integrity-and-ethics` for their specialist artifacts.

## Resources

- `scripts/init_materials_plan.py` — protected materials experiment/provenance scaffold.
