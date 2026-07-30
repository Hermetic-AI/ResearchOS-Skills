# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ResearchOS-Skills is a collection of 28 independent research-oriented agent skills (Anthropic `SKILL.md` format). Each skill is **self-contained** under `skills/` with zero cross-skill dependencies — copy one directory and it runs standalone. Skills cover the full research lifecycle. Python 3.11+, Apache-2.0.

## Project Structure

```
├── skills/               ← 28 independent, self-contained skills
│   ├── literature-reader/
│   │   ├── SKILL.md            # routing + workflow (≤~150 lines)
│   │   ├── agents/openai.yaml  # client discoverability metadata
│   │   ├── scripts/            # zero-dependency Python CLIs (stdlib)
│   │   └── references/         # on-demand domain knowledge
│   └── ... (27 more)
├── tests/                ← project-level pytest suite (references skills/ via ROOT)
├── schemas/              ← versioned cross-skill JSON contracts
├── tools/                ← validate_skills.py, validate_artifact.py, release_preflight.py
└── docs/                 ← DEVELOPMENT_ROADMAP.md (88/88 items complete), OPEN_SOURCE_AUDIT.md
```

## Common Commands

```bash
# Install (use `python`, NOT `python3` on Windows Git Bash — the python3 Store stub exits silently)
python -m pip install -e ".[dev]"          # base dev deps (pytest, jsonschema, PyYAML)
python -m pip install -e ".[analysis]"      # NumPy + SciPy
python -m pip install -e ".[plot]"          # Matplotlib + NumPy + SciPy
python -m pip install -e ".[pdf]"           # pdfplumber
python -m pip install -e ".[validation]"    # SciPy + Statsmodels
python -m pip install -e ".[models]"        # pandas + Statsmodels

# Validate skill structure (frontmatter, resources, openai.yaml, Python syntax)
python tools/validate_skills.py

# Run full test suite
python -m pytest

# Run a single test file or test
python -m pytest tests/test_artifact_schema.py
python -m pytest tests/test_cli_help.py::test_all_python_clis_support_help_and_version

# Validate a JSON artifact against the cross-skill schema
python tools/validate_artifact.py result.json --type stat-results

# Release preflight (read-only; never grants approval)
python tools/release_preflight.py
```

## Architecture

### Skill Independence

Each skill is fully self-contained. Scripts import only from Python stdlib or their own skill directory. **No script imports from another skill.** This means:
- A skill can be copied out and run independently.
- Tests reference skills via `ROOT / "skills" / "<skill-name>" / "scripts" / "<script>.py"`.
- `tools/validate_skills.py` scans `skills/*/SKILL.md` (falls back to root for single-skill checkouts).

### Progressive Disclosure Model

Every skill follows the same three-layer structure:
- **`SKILL.md`** — routing layer. ≤~150 lines. Frontmatter (`name` + `description` only), when-to-use, workflow skeleton, file index. Loads `references/*` only when a workflow step calls for it.
- **`references/`** — on-demand domain knowledge (decision trees, method guides, contract details).
- **`scripts/`** — deterministic Python CLIs. Zero-dependency (stdlib) preferred.
- **`agents/openai.yaml`** — discoverability metadata (`display_name`, `short_description` 25–64 chars, `default_prompt` mentioning `$skill-name`).

### Cross-Skill Artifact Protocol

Skills communicate through versioned JSON artifacts validated against `schemas/researchos-artifacts.schema.json` (Draft 2020-12). Each artifact carries a `provenance` block (sources, command, tool version, seed, timestamps) and, where claims are made, `evidence_anchor` entries (source, page, quote, extraction method, verification status).

Key artifact types: `paper-note`, `literature-matrix`, `research-gap`, `design-brief`, `analysis-plan`, `cleaning-manifest`, `stat-results`, `figure-manifest`, `reproduction-card`, `pdf-extraction`, `preregistration-manifest`, `sequential-design-plan`, `model-diagnostics`, `resampling-estimate`, `bayesian-estimate`, `sensitivity-analysis`, `imputation-manifest`, `data-dictionary`, `bibliography-*`, `time-series-forecast`, `competing-risk-estimate`, `evidence-audit`, `graph-entity-identity-audit`, `graph-temporal-conflict-audit`, `remote-dataset-manifest-audit`, `isolation-plan`, `decision-provenance-trace`, `anonymization-screen`, `manuscript-consistency-screen`, `docx-citation-screen`, `docx-structure-audit`, `markdown-project-audit`, `slide-deck-manuscript`, `defense-qa-simulator`, `protocol-compliance-checklist`, `release-audit-report`, `patent-family-report`.

### CLI Contract (applies to every script)

- Supports `--help` and `--version` (version must match `pyproject.toml`: currently `0.1.0`).
- Invalid usage returns nonzero exit code with diagnostics on **stderr**; stdout stays clean for machine-readable output.
- File-writing CLIs refuse to replace existing output unless `--force` is supplied, and **never** overwrite their source data (even with `--force`).
- Randomized behavior accepts a fixed `--seed` and surfaces it in output.
- Deterministic machine-readable output (JSON) where applicable.

### Test Layout

Tests live in `tests/` (configured via `pyproject.toml` `testpaths`). Each test file references scripts via:
```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "<skill-name>" / "scripts" / "<script>.py"
```

New scripts must cover normal, boundary, and failure paths. CI runs Python 3.11–13 on Ubuntu + Windows.

## Conventions

- Skill directory names: lowercase hyphenated, under 64 chars; `name` in frontmatter must match directory name.
- Frontmatter `description` carries trigger scenarios (EN + 中文口语短语) and "NOT for X" routing boundaries between sibling skills.
- Reports to the user default to **Chinese**; artifact content follows the artifact's language.
- Never overwrite raw research data — write a new artifact and record provenance.
- Never fabricate citations, evidence, statistics, or successful executions.
- Do not commit credentials, private research data, participant info, model checkpoints, scraped articles, or generated workspace artifacts (`workspace/` is gitignored).
- Scanned-PDF OCR uses locally installed `pdftoppm` (Poppler) and `tesseract` — neither is bundled; OCR is always labeled in the output artifact.
