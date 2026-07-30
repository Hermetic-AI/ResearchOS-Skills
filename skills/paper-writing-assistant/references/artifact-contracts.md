# Manuscript artifact handoff

Use the canonical contracts in `../schemas/researchos-artifacts.schema.json` to avoid retyping evidence and numbers.

## Inputs

- `paper-note` and `literature-matrix` supply source-backed claims and comparisons.
- `stat-results` supplies exact statistics, p-values, effect sizes, intervals, and correction results.
- `figure-manifest` supplies data, statistics source, command, seed, and output provenance.
- `reproduction-card` supplies verified match/mismatch statements.

Validate artifacts before use. Cite the originating source rather than citing the JSON file as scientific evidence. Never convert a warning, missing value, or `non-comparable` verdict into a positive claim. When manuscript text conflicts with a validated artifact, report the conflict and ask which source is authoritative before editing.

```bash
python tools/validate_artifact.py results.json --type stat-results
```

