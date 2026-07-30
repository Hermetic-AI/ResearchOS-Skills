---
name: reproduction-assistant
description: Reproduce paper code and experiments by probing repository entry points and dependencies, preparing an auditable environment plan, capturing runs, comparing reproduced and reported metrics with declared tolerances, and diagnosing version, dependency, parameter, or data failures from evidence. Use for 复现论文代码, 跑论文仓库, 配复现环境, 复现失败诊断, 结果对不上, reproduce this paper repository, or compare reproduced results. Not for general paper reading, new experiment design, statistical analysis, knowledge graphs, or manuscript writing.
---

# Reproduction Assistant

Helps reproduce a paper's code and experiments end to end: understand the repo, set up the environment, run experiments, compare results against paper-reported values, and diagnose failures.

> **NOT for literature surveys, paper reading, or manuscript writing** — this skill is for code/experiment reproduction only. Use literature-reader / paper-writing-assistant for those.

**Global conventions**

- **Never fake success**: if a step fails, report it failed with the log evidence. Never claim a run "basically worked" without artifacts proving it.
- **Every number carries a source**: paper-reported values cite the paper section/table; reproduced values cite the artifact file path that produced them.
- **Patches go to `patches/` only**: when diagnosing, write suggested fixes as diff files into a `patches/` directory and explain them — never silently modify the cloned repo.
- **Retry budget**: at most 2 retries per pipeline step; after that, stop retrying and go to diagnosis.
- **Reports to the user are in Chinese by default**; content written into artifacts (patches, env files, comparison cards committed alongside the repo) follows the artifact's language.
- **Machine-readable handoff**: after comparison, read `references/artifact-contracts.md` and emit a validated `reproduction-card` in addition to the human-readable report.

## Inputs

- Paper reference (arXiv link / PDF / the paper's stated results table) — used to extract `(model, dataset, metric, value)` claims. Only record values explicitly seen in the paper; never invent them.
- Repo URL or a local path to the cloned repository.
- Optional: environment preference (docker / venv / conda / just advise).

## Workflow skeleton

Run a six-step pipeline. The discipline for each step (retry budget, logging, patch policy, honesty rules) is in `references/pipeline.md` — **read it before starting the pipeline**. Do not read all references up front; load each file only when its step or condition is reached.

1. **clone**: `git clone --depth 1 <repo_url>` into the run workspace; record the HEAD commit sha.
2. **analyze**: run `python3 scripts/repo_probe.py <repo_dir>` for a structural profile (entry-point candidates, manifests, config files, data references, README run commands), then **verify by reading the README and entry script yourself** — the probe only suggests.
   Record version evidence before treating a repository as paper-aligned: `python3 scripts/git_evidence.py <repo_dir> --expected-commit <paper-sha>`. It reads HEAD/tag/origin/submodules/LFS status and never changes Git state.
3. **env_detect**: run `python3 scripts/parse_deps.py <repo_dir> [--export requirements.lock]` to get a unified Python/Conda dependency manifest (JSON, each entry tagged with its source file). It separately reports non-Python environment evidence for Poetry/uv, Nix, R, Julia, MATLAB/Octave, Docker, and Make; inspect those native files before choosing an environment. Also probe the local environment (python version, `nvidia-smi` if relevant).
   Before execution, record a new provenance snapshot: `python3 scripts/provenance_snapshot.py repo --command "python train.py" --data dataset.csv --config config.yaml --seed 42 --env CUDA_VISIBLE_DEVICES --out run-001/provenance.json`. It records local git state/diff, platform/GPU probe, selected environment-variable hashes, command, seed, config and dataset checksums without changing the repository.
   Record dataset license/terms and version evidence separately: `python3 scripts/data_evidence.py --data dataset.csv --license "https://example.org/terms" --version-source "doi:..." --out run-001/dataset-evidence.json`. It only inventories supplied files and never asserts permission.
4. **env_generate**: based on the manifest, *suggest* an environment file (pinned `requirements.lock`, `environment.yml`, or `Dockerfile.reproduce`). Write it into the run workspace, present it to the user, and let them confirm before installing/building. Do not silently install packages system-wide. **Read `references/env-recipes.md` here** for CUDA↔framework pairings, unpinning inference order, Docker/conda/venv decision tree, and CPU-fallback risks.
   Before any untrusted command, generate a review-only least-privilege plan: `python3 scripts/isolation_plan.py repo --run-dir run-001 --command "python train.py" --data dataset`. Network defaults to none; this command never runs repository code and user confirmation remains required.
5. **run**: execute the entry command in the prepared environment; capture stdout/stderr, exit code, and artifacts (metrics files, checkpoints).
6. **compare**: **read `references/comparison-protocol.md` first** to set a defensible tolerance and seed/run-count policy, then extract reproduced values from run artifacts and run `python3 scripts/compare_results.py` to produce a comparison card (markdown/JSON) with `match` / `mismatch` / `missing_repro` / `missing_paper` verdicts (relative error ≤ tolerance ⇒ match; default tolerance 1%). Repro values may be per-run lists → the card reports mean ± std and judges on the mean.
   After review, create a checksum inventory and, only when explicitly requested, a ZIP archive: `python3 scripts/reproduction_package.py run-001 --level reduced-scale --out run-001-package.json --archive run-001.zip`. Sensitive filename patterns and caches are excluded, but the user must review every file and its distribution permission.

**On any failure or mismatch**: read `references/diagnostics.md`, classify the failure into **version / dependency / parameter / data** using its signal→category mapping (incl. hard failures: segfault, OOM, NCCL timeout, dataset checksum, tokenizer drift, API deprecation — each with minimal confirmation steps), collect the required evidence per category, and produce a Chinese diagnosis report with suggested fixes (as files under `patches/` when the fix is a concrete code/config change).

**Reduced-scale runs**: if the full experiment is infeasible (no GPU, dataset too large), a reduced run is allowed only when explicitly labeled "非原配置，数值不可与论文直接对标" — compare such values with verdict `mismatch` expected, and say so.

## Scripts (all zero-dependency, stdlib only)

- `scripts/repo_probe.py` — structural profile of a repo: Python/R/Julia/MATLAB/Octave entry candidates, dependency manifests, runtime hints (Docker/Nix/Poetry/uv/etc.), config files, data references, README run-command extraction.
  `python3 scripts/repo_probe.py <repo_dir> [--pretty] [--readme-max-bytes 200000]`
- `scripts/parse_deps.py` — parse `requirements.txt` / `pyproject.toml` (PEP 621) / `setup.py` / `setup.cfg` / `Pipfile` / `environment.yml` into one unified Python/Conda dependency JSON list; separately reports unparsed native environment evidence for Poetry/uv, Nix, R, Julia, MATLAB/Octave, Docker, and Make. `--export PATH` writes only pip-installable dependencies. Requires Python 3.11+ (uses stdlib `tomllib`).
  `python3 scripts/parse_deps.py <repo_dir> [--pretty] [--export requirements.lock]`
- `scripts/compare_results.py` — compare paper-claimed vs reproduced values; repro `value` may be a per-run list (reports mean ± std, n, spread; judges on the mean); verdict by relative error ≤ tolerance; outputs a markdown comparison card or JSON.
  `python3 scripts/compare_results.py --paper claims.json --repro repro.json [--tolerance 0.01] [--format md|json]`
  Add `--artifact-out reproduction.json --repository-commit <sha> --environment-json env.json` for a validated cross-skill `reproduction-card`; existing artifacts require explicit `--force`.
  (pairs may also be passed inline; see the script's docstring/`-h`)

- `scripts/remote_data_manifest.py` — offline audit of declared remote dataset IDs, URLs, license/terms, versions, and optional SHA-256 syntax; it never downloads, contacts URLs, or verifies permissions.

## File index

- `references/pipeline.md` — six-step pipeline discipline: clone → analyze → env_detect → env_generate → run → compare; honesty rules, patch policy, retry budget. Read before starting the pipeline.
- `references/env-recipes.md` — environment setup recipes: CUDA↔PyTorch/TensorFlow pairings, version inference when unpinned, Docker/conda/venv decision tree, system-level deps, CPU-fallback risks, env report template. Read at `env_generate` (and on vague manifests).
- `references/comparison-protocol.md` — tolerance magnitudes by noise source, seed/run-count and variance reporting, non-comparable declarations, how to write the comparison into a paper. Read at `compare`.
- `references/diagnostics.md` — failure-signal → category mapping (version / dependency / parameter / data), hard-failure confirmations (segfault, OOM, NCCL, checksum, tokenizer drift, API deprecation), evidence requirements and fix suggestions per category. Read on failure or mismatch.
- `references/artifact-contracts.md` — versioned `reproduction-card` fields, verdicts, evidence, and validation command. Read at compare/handoff.
- `scripts/repo_probe.py`, `scripts/parse_deps.py`, `scripts/compare_results.py` — see above.
- `scripts/isolation_plan.py` — review-only Docker-oriented least-privilege plan with read-only repo/data mounts, isolated run workspace, default network denial, and credential-mount prohibitions. Add `--generate-script PATH [--backend venv|docker]` to emit a runnable `.sh`/`.bat` script with safety checks (refuses repo==run, verifies mounts, sets HOME to a temp dir). Additive; existing flags unchanged.
- `scripts/git_evidence.py` — read-only evidence for HEAD/tag/origin, expected commit alignment, submodule SHAs, and Git LFS files. Additive extensions: `--lfs-fetch-check` (dry-run fetch, reports missing files), `--submodule-check` (per-submodule SHA/init/clean state), `--tag <tag>` (alignment with a release tag, not just exact-match at HEAD). All Git operations are read-only.
- `scripts/dataset_download_manifest.py` — generate a download manifest from a dataset spec JSON (url, expected_checksum, license, version); `--verify` checks local files against sha256, `--export <path>` writes a runnable download+verify shell script. Zero deps, protected output, `--version`, `--force`.
- `scripts/provenance_snapshot.py` — protected JSON snapshot of local git state, environment basics, command, and supplied dataset checksums.
- `scripts/reproduction_package.py` — checksum manifest and explicit reproduction-level label for a reviewed run folder; excludes common caches and never archives, deletes, or collects files automatically.
