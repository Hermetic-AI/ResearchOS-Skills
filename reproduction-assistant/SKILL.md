---
name: reproduction-assistant
description: Paper code and experiment reproduction assistant. Parses a paper's code repository (entry points, dependency manifests), advises on environment setup (parse dependencies → generate env file suggestions), automatically compares reproduced results against paper-reported values with tolerance-based match/mismatch/missing verdicts, and classifies failures into version/dependency/parameter/data categories with evidence requirements. Use when the user wants to reproduce a paper's code or experiments, e.g. "reproduce this paper's repo", "复现这篇论文的代码/实验", "跑一下这个论文仓库", "为什么复现不出来/复现失败诊断", "论文结果对不上/结果对标", "帮我配这篇论文的环境". NOT for reading/summarizing papers — use literature-reader instead; NOT for structuring extracted concepts into a knowledge graph — use knowledge-graph-builder instead; NOT for designing new experiments — use experiment-designer instead; NOT for analyzing result data statistically — use data-analysis-assistant instead; NOT for writing up findings — use paper-writing-assistant instead.
---

# Reproduction Assistant

Helps reproduce a paper's code and experiments end to end: understand the repo, set up the environment, run experiments, compare results against paper-reported values, and diagnose failures.

**Global conventions**

- **Never fake success**: if a step fails, report it failed with the log evidence. Never claim a run "basically worked" without artifacts proving it.
- **Every number carries a source**: paper-reported values cite the paper section/table; reproduced values cite the artifact file path that produced them.
- **Patches go to `patches/` only**: when diagnosing, write suggested fixes as diff files into a `patches/` directory and explain them — never silently modify the cloned repo.
- **Retry budget**: at most 2 retries per pipeline step; after that, stop retrying and go to diagnosis.
- **Reports to the user are in Chinese by default**; content written into artifacts (patches, env files, comparison cards committed alongside the repo) follows the artifact's language.

## Inputs

- Paper reference (arXiv link / PDF / the paper's stated results table) — used to extract `(model, dataset, metric, value)` claims. Only record values explicitly seen in the paper; never invent them.
- Repo URL or a local path to the cloned repository.
- Optional: environment preference (docker / venv / conda / just advise).

## Workflow skeleton

Run a six-step pipeline. The discipline for each step (retry budget, logging, patch policy, honesty rules) is in `references/pipeline.md` — **read it before starting the pipeline**. Do not read all references up front; load each file only when its step or condition is reached.

1. **clone**: `git clone --depth 1 <repo_url>` into the run workspace; record the HEAD commit sha.
2. **analyze**: run `python3 scripts/repo_probe.py <repo_dir>` for a structural profile (entry-point candidates, manifests, config files, data references, README run commands), then **verify by reading the README and entry script yourself** — the probe only suggests.
3. **env_detect**: run `python3 scripts/parse_deps.py <repo_dir> [--export requirements.lock]` to get a unified dependency manifest (JSON, each entry tagged with its source file; supports requirements.txt / pyproject.toml / setup.py / setup.cfg / Pipfile / environment.yml). Also probe the local environment (python version, `nvidia-smi` if relevant).
4. **env_generate**: based on the manifest, *suggest* an environment file (pinned `requirements.lock`, `environment.yml`, or `Dockerfile.reproduce`). Write it into the run workspace, present it to the user, and let them confirm before installing/building. Do not silently install packages system-wide. **Read `references/env-recipes.md` here** for CUDA↔framework pairings, unpinning inference order, Docker/conda/venv decision tree, and CPU-fallback risks.
5. **run**: execute the entry command in the prepared environment; capture stdout/stderr, exit code, and artifacts (metrics files, checkpoints).
6. **compare**: **read `references/comparison-protocol.md` first** to set a defensible tolerance and seed/run-count policy, then extract reproduced values from run artifacts and run `python3 scripts/compare_results.py` to produce a comparison card (markdown/JSON) with `match` / `mismatch` / `missing_repro` / `missing_paper` verdicts (relative error ≤ tolerance ⇒ match; default tolerance 1%). Repro values may be per-run lists → the card reports mean ± std and judges on the mean.

**On any failure or mismatch**: read `references/diagnostics.md`, classify the failure into **version / dependency / parameter / data** using its signal→category mapping (incl. hard failures: segfault, OOM, NCCL timeout, dataset checksum, tokenizer drift, API deprecation — each with minimal confirmation steps), collect the required evidence per category, and produce a Chinese diagnosis report with suggested fixes (as files under `patches/` when the fix is a concrete code/config change).

**Reduced-scale runs**: if the full experiment is infeasible (no GPU, dataset too large), a reduced run is allowed only when explicitly labeled "非原配置，数值不可与论文直接对标" — compare such values with verdict `mismatch` expected, and say so.

## Scripts (all zero-dependency, stdlib only)

- `scripts/repo_probe.py` — structural profile of a repo: entry-point candidates, dependency manifests, config files, data references, README run-command extraction.
  `python3 scripts/repo_probe.py <repo_dir> [--pretty]`
- `scripts/parse_deps.py` — parse `requirements.txt` / `pyproject.toml` (PEP 621) / `setup.py` / `setup.cfg` / `Pipfile` / `environment.yml` into one unified dependency JSON list, each entry tagged with its source file; `--export PATH` writes a pip-installable requirements file.
  `python3 scripts/parse_deps.py <repo_dir> [--pretty] [--export requirements.lock]`
- `scripts/compare_results.py` — compare paper-claimed vs reproduced values; repro `value` may be a per-run list (reports mean ± std, n, spread; judges on the mean); verdict by relative error ≤ tolerance; outputs a markdown comparison card or JSON.
  `python3 scripts/compare_results.py --paper claims.json --repro repro.json [--tolerance 0.01] [--format md|json]`
  (pairs may also be passed inline; see the script's docstring/`-h`)

## File index

- `references/pipeline.md` — six-step pipeline discipline: clone → analyze → env_detect → env_generate → run → compare; honesty rules, patch policy, retry budget. Read before starting the pipeline.
- `references/env-recipes.md` — environment setup recipes: CUDA↔PyTorch/TensorFlow pairings, version inference when unpinned, Docker/conda/venv decision tree, system-level deps, CPU-fallback risks, env report template. Read at `env_generate` (and on vague manifests).
- `references/comparison-protocol.md` — tolerance magnitudes by noise source, seed/run-count and variance reporting, non-comparable declarations, how to write the comparison into a paper. Read at `compare`.
- `references/diagnostics.md` — failure-signal → category mapping (version / dependency / parameter / data), hard-failure confirmations (segfault, OOM, NCCL, checksum, tokenizer drift, API deprecation), evidence requirements and fix suggestions per category. Read on failure or mismatch.
- `scripts/repo_probe.py`, `scripts/parse_deps.py`, `scripts/compare_results.py` — see above.
