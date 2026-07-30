# Experiment artifact contracts

Use `../schemas/researchos-artifacts.schema.json` as the canonical interchange schema.

## Inputs

- Accept a `research-gap` artifact as evidence for the study motivation.
- Accept `paper-note` artifacts as sources for prior effect sizes and baseline rates, but verify the cited evidence before using a number.

## Outputs

- Write the interview result as `design-brief`.
- Write the confirmed estimand, outcomes, comparisons, models, alpha, and multiplicity rule as `analysis-plan` before data collection.
- Bundle those artifacts with human-readable preregistration/SAP documents and hashes in a `preregistration-manifest` when the study is being preregistered.
- Write multiple-endpoint allocation, interim spending budgets, stopping rules, and prespecified adaptations as `sequential-design-plan`.

Both outputs require `schema_version: "1.0.0"`, `artifact_type`, and provenance. Record unresolved choices under `open_questions`; never replace `_TODO_` decisions with guessed values. Record generated schedules separately as CSV/JSON and cite their path, command, and seed in provenance.

```bash
python tools/validate_artifact.py design.json --type design-brief
python tools/validate_artifact.py analysis-plan.json --type analysis-plan
python tools/validate_artifact.py preregistration-manifest.json --type preregistration-manifest
python tools/validate_artifact.py sequential-design-plan.json --type sequential-design-plan
```

Use `scripts/create_preregistration.py` to derive all three machine-readable artifacts from one source specification. Drafts may contain explicit `_TODO_` markers. Frozen packages must have no unresolved decisions; amendments receive a new protocol version and must not silently replace the historical frozen package.
