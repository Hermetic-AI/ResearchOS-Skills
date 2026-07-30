# Contributing to ResearchOS-Skills

Thank you for helping improve open research workflows. Contributions may add a skill, improve an existing workflow, fix a deterministic script, add tests, or clarify evidence and safety boundaries.

## Before opening a change

1. Search existing skills and issues to avoid overlapping capabilities.
2. Keep each skill narrowly routable. Put detailed knowledge in `references/` and repeatable operations in `scripts/`.
3. Do not add copyrighted papers, screenshots, datasets, templates, or palettes without a redistribution-compatible license and attribution.
4. Never include secrets, personal data, unpublished participant data, model checkpoints, or generated workspace artifacts.

## Skill requirements

- Use a lowercase hyphenated directory name under 64 characters.
- Keep only `name` and `description` in SKILL.md frontmatter.
- Put all trigger and exclusion language in `description`.
- Keep SKILL.md concise and use imperative instructions.
- Add `agents/openai.yaml` with a display name, short description, and a default prompt that explicitly names `$skill-name`.
- Prefer Python standard library scripts. Declare and justify third-party dependencies when they materially improve correctness.
- Never overwrite raw research data. Write a new artifact and record provenance.
- For randomized behavior, accept a seed and make it visible in output.

## Validation

From the repository root, run:

```bash
python tools/validate_skills.py
python -m pytest
python experiment-designer/scripts/validate_power_calculations.py  # after installing .[validation]
```

Test normal, boundary, and failure paths. A new script must:

- Support `--help` and `--version`, with the version matching `pyproject.toml`.
- Return nonzero on invalid input and write diagnostics to stderr without corrupting machine-readable stdout.
- Refuse to replace an existing output unless the user supplies `--force`.
- Reject any output path that resolves to a source-data path, even when `--force` is supplied.
- Write deterministic machine-readable output where applicable and expose every random seed.

Numerical scientific methods must include an independent reference comparison or simulation-based check, document tolerances and uncovered cases, and run in the scientific-stack CI job when optional dependencies are required.

## Pull requests

Explain the research use case, routing boundary, evidence/safety considerations, tests performed, and any third-party material. Keep unrelated changes out of the pull request. By contributing, you agree that your contribution is licensed under Apache-2.0.
