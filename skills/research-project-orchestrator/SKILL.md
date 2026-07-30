---
name: research-project-orchestrator
description: Initialize and coordinate auditable research projects across ResearchOS skills, including project folders, artifact handoffs, workflow routing, status, and provenance. Use when a user starts a study, asks what research step comes next, wants to connect literature/design/data/figures/manuscript/reproduction artifacts, or needs a project manifest.
---

# Research Project Orchestrator

Use this skill to coordinate, not replace, specialist skills. It never invents research findings or silently runs external code.

## Initialize

Create a new project root only when the target does not already exist:

```bash
python scripts/init_project.py --root study-001 --title "Study title"
```

It creates `inputs/`, `artifacts/`, `reports/`, `logs/`, and `patches/` plus `project-manifest.json`. The manifest records source artifacts, status, and the next routed skill. Do not place raw restricted data in the manifest.

Register an existing derived artifact with an explicit preview/apply boundary:

```bash
python scripts/update_project.py study-001 --artifact results.json --type stat-results
python scripts/update_project.py study-001 --artifact results.json --type stat-results --apply
```

The first command previews. Only `--apply` updates the manifest; raw data and the manifest itself cannot be registered as artifacts.

## Route by current artifact

- Question or corpus → `literature-reader`.
- Evidence-backed gap → `experiment-designer`.
- `design-brief` / `analysis-plan` → data collection, then `data-analysis-assistant`.
- `stat-results` → `scientific-plot` and `paper-writing-assistant`.
- `paper-note` → `knowledge-graph-builder` or literature synthesis.
- Code/paper results → `reproduction-assistant`.

Validate supplied JSON artifacts before using them. Report missing decisions rather than guessing: target population, primary estimand, protocol version, data permissions, and publication target.

`python scripts/audit_project_provenance.py study-001 --pretty` verifies registered artifact availability/checksums and manifest update provenance without modifying the project.

## Resources

- `scripts/init_project.py` — protected project scaffold plus manifest.
- `scripts/update_project.py` — preview/apply manifest status and artifact registration with deterministic next-skill routing.
