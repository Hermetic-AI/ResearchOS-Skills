---
name: research-software-quality
description: Create auditable quality plans for research software covering versioning, environments, testing, validation datasets, CI, licensing, releases, and citation. Use when users need a research software quality plan, reproducibility checklist, release readiness review, scientific code audit, or software paper evidence ledger.
---

# Research Software Quality

Quality claims require verifiable evidence. Do not claim a package is tested, reproducible, secure, benchmarked, or release-ready without recorded commands, environments, datasets, and outcomes.

## Initialize a quality plan

```bash
python scripts/init_quality_plan.py --out quality-plan.json --project "Project" --version-label "0.1.0"
```

## Screen release declarations

```bash
python scripts/release_readiness.py --plan quality-plan.json --out release-readiness.json
```

The screen requires declared environment, test, scientific validation, CI, checklist, license, and citation evidence. It does not run tests or authorize a release.

## Audit release readiness and capture a benchmark baseline

```bash
python scripts/release_audit.py repo_dir --out release-audit.json
```

Inventories the repository for release-required artifacts (LICENSE, README, version, changelog, tests, CITATION.cff), resolves the release version from a `--release-version` override or common version files, and runs an optional benchmark command (`--benchmark`, defaulting to a tiny built-in probe) recording wall-clock time and, where the platform exposes it, peak memory. The audit is a pre-flight check: it does not execute the project's own test suite, publish a release, or authorize distribution. Read `references/release-readiness.md` when preparing a release.

## Workflow

1. Record supported platforms, language/runtime, dependency lockfiles, data/model versions, and deterministic seed policy.
2. Define unit, integration, scientific-validation, and regression evidence separately; use representative data that may be distributed legally.
3. Attach CI runs, coverage or other quality measures, lint/type checks, benchmark protocol, and failure criteria before release claims.
4. Verify license, third-party notices, citation metadata, changelog, archive DOI intent, and security disclosure process.
5. Use `reproduction-assistant` for executable provenance and package evidence.

`python scripts/collect_repository_evidence.py repo_dir --pretty` inventories read-only repository quality evidence. It does not execute tests or authorize a release.

## Resources

- `scripts/init_quality_plan.py` — protected research-software quality evidence scaffold.
- `scripts/release_audit.py` — release-readiness inventory plus an optional benchmark harness.
