# Preregistration and statistical analysis plans

Use this resource after the design interview and before collecting or viewing outcome data. The generated package is registry-neutral: adapt the Markdown to the destination registry without changing the frozen source specification.

## Required source specification

Create a UTF-8 JSON object with these required fields:

- `study_id`, `title`, `hypothesis`, `experimental_unit`
- `variables`, `treatments`, `outcomes`, `comparisons`, `planned_models` as arrays
- `alpha` strictly between 0 and 1

Recommended fields are `research_question`, `design_type`, `controls`, `sampling`, `sample_size_rationale`, `randomization`, `blinding`, `measurements`, `estimands`, `covariates`, `multiplicity`, `analysis_populations`, `exclusion_criteria`, `missing_data`, `diagnostics`, `sensitivity_analyses`, `interim_and_stopping`, `reporting`, `ethics`, `sharing`, `deviation_policy`, and `open_questions`.

Use `_TODO_` for genuinely unresolved values. Do not guess. A draft package preserves those markers; `--freeze` rejects them and every non-empty `open_questions` entry.

```json
{
  "study_id": "study-001",
  "title": "Example randomized experiment",
  "research_question": "Does the intervention improve the primary score?",
  "hypothesis": "The intervention increases the primary score.",
  "experimental_unit": "participant",
  "design_type": "parallel randomized controlled experiment",
  "variables": [{"name": "arm", "role": "treatment"}],
  "treatments": [{"name": "intervention"}, {"name": "control"}],
  "outcomes": [{"id": "primary-score", "role": "primary", "timepoint": "week 8"}],
  "comparisons": [{"id": "primary", "contrast": "intervention - control"}],
  "planned_models": ["linear regression with prespecified baseline adjustment"],
  "alpha": 0.05,
  "multiplicity": "One confirmatory primary outcome; no adjustment required.",
  "open_questions": []
}
```

## Create or freeze a package

```bash
python scripts/create_preregistration.py --input study.json --out-dir prereg-draft
python scripts/create_preregistration.py --input study.json --out-dir prereg-v1 --protocol-version 1.0.0 --freeze
```

The command writes five files. JSON artifacts support machine-to-machine handoff; Markdown files support human review; the manifest records status, provenance, unresolved paths, and SHA-256 checksums. Existing outputs are protected unless `--force` is explicit, and the source file is never overwritten.

## Review and amendment rules

1. Review hypotheses, experimental unit, treatment assignment, outcome roles and timepoints, estimands, exclusions, missing-data handling, multiplicity, models, and reporting rules.
2. Freeze only before outcome data are inspected. A checksum establishes what the package contained; it is not proof that an external registry received it.
3. Never silently edit a frozen package. Create a new protocol version and describe what changed, when, why, and whether outcome data had been accessed.
4. Separate confirmatory analyses from exploratory analyses in both the plan and eventual report.
5. Validate the JSON outputs with `tools/validate_artifact.py` using types `design-brief`, `analysis-plan`, and `preregistration-manifest`.

This tool does not submit to a registry, provide ethics approval, choose an analysis, or certify regulatory compliance.
