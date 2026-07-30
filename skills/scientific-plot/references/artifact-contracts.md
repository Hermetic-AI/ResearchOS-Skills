# Figure artifact contracts

Use `../schemas/researchos-artifacts.schema.json` as the canonical interchange schema.

## Input

For formal inferential annotations, consume `stat-results` and map each bracket to a stable result `id` with `--star-map "A>B=primary;A>C=secondary"`. Prefer `adjusted_p_value` when present, otherwise use `p_value`. Do not recalculate the formal test in the plotting workflow. The built-in `--compare-groups` path is exploratory and must be labeled as such.

## Output

Write `figure-manifest` beside submission figures. Include a stable `figure_id`, every output path, data sources, the `stat-results` path when used, theme, and provenance containing the exact command, tool version, seed, and warnings.

```bash
python tools/validate_artifact.py fig1.manifest.json --type figure-manifest
```

The manifest documents reproducibility; it does not replace a caption. Captions must still state the test, correction, sample size, error-bar definition, and symbol meanings.
