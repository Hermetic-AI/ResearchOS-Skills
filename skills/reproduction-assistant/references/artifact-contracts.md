# Reproduction artifact contract

Use `../schemas/researchos-artifacts.schema.json` as the canonical interchange schema and emit `reproduction-card` after comparison.

Record the exact repository commit, environment description, and one comparison per metric. Verdict values are `match`, `mismatch`, `missing-repro`, `missing-paper`, or `non-comparable`. Reduced-scale runs are always `non-comparable`, even if their direction resembles the paper.

In provenance, record the paper/table source, repository, commands, tool version, seeds, and warnings. A comparison without both a paper evidence locator and a reproduced artifact locator is incomplete and must not be presented as verified reproduction.

```bash
python tools/validate_artifact.py reproduction.json --type reproduction-card
```

