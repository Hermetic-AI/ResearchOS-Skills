# Reproduction Pipeline Discipline

Six steps: `clone → analyze → env_detect → env_generate → run → compare`.
Read this file before starting a reproduction run. It defines the rules every step must obey.

## Core principles (non-negotiable)

1. **Never fake success.** A step is `completed` only when its artifacts exist (logs, exit code 0, output files). If it failed, say it failed and show the log tail. Never paraphrase a failure as "basically worked".
2. **Every number carries a source.**
   - Paper-reported values → cite paper location (section / table / page).
   - Reproduced values → cite the artifact file path (e.g. `artifacts/metrics.json`).
   - If a value cannot be traced to a source, drop it from the comparison.
3. **Patches go to `patches/` only.** Suggested fixes are written as unified-diff or whole files into the run workspace's `patches/` directory and explained to the user. Never silently edit the cloned repo. Apply a patch only after the user confirms.
4. **Retry budget: max 2 retries per step.** Retry only when the failure cause is identified and fixed (e.g. missing package installed, wrong path corrected). Blind retries are forbidden. After 2 failed retries, stop and go to diagnosis (`references/diagnostics.md`).
5. **Log everything.** Each step writes a log file; keep at least the last ~50 lines available as `log_tail` for diagnosis.

## Suggested workspace layout

```
<run_dir>/
├── repo/            # git clone target
├── env/             # generated env files + env-report
├── logs/            # step-<n>-<name>.log, run.stdout.log, run.stderr.log
├── artifacts/       # metrics.json, checkpoints list, output figures
├── patches/         # suggested diffs (NOT applied)
└── report.md        # final reproduction & diagnosis report
```

## Step-by-step

### 1. clone
- `git clone --depth 1 <repo_url> repo/` (full clone only if the paper pins an old commit/tag — then checkout that ref).
- Record HEAD commit sha into the run notes; all later claims about "the code" refer to this sha.
- Failure: network/auth errors are usually not retryable more than once — report and ask the user for access or a local copy.

### 2. analyze
- Start with `python3 scripts/repo_probe.py <repo_dir>` for a structural profile (entry candidates, manifests, configs, data references, README commands) — treat its output as suggestions only.
- Find entry points, in priority order: commands stated in the paper / README "Experiments" section → `Makefile` / `*.sh` → `train.py` / `main.py` / `eval.py` / `run.py`.
- Read the README and the entry script yourself; do not trust filename guesses. Confirm: which config, dataset, and checkpoint the paper's headline numbers came from.
- Locate dependency manifests: `requirements*.txt`, `pyproject.toml`, `setup.py`, `environment.yml`, `Pipfile`, `Dockerfile`, plus `poetry.lock` / `uv.lock`, `flake.nix` / `shell.nix`, `renv.lock` / `DESCRIPTION`, Julia `Project.toml` / `Manifest.toml`, and MATLAB project files where present. Native files are evidence, not instructions to execute; read their README guidance and use the matching runtime only after confirmation.

### 3. env_detect
- Run `python3 scripts/parse_deps.py <repo_dir>` → unified dependency manifest (JSON, source file tagged per entry). Conflicts between sources (e.g. requirements.txt pins torch 1.x, pyproject says >=2) must be surfaced, not silently resolved.
- Probe the machine: `python3 --version`; `nvidia-smi` for GPU/CUDA; note OS.
- If the repo declares a GPU/CUDA requirement and the machine has none → warn early: full reproduction is infeasible; offer reduced-scale run (explicitly labeled non-comparable) or stop.

### 4. env_generate
- Produce a *suggested* environment file into `env/`:
  - Prefer Docker (`Dockerfile.reproduce`) when available and the repo needs system-level deps or specific CUDA.
  - Otherwise a pinned `requirements.lock` / `environment.yml` (venv or conda).
- Pin versions from the manifest; where the repo is vague (`torch` unpinned), use the README/paper's stated version or the version contemporary with the paper's date, and record the choice as an assumption.
- **Show the file to the user and get confirmation before building/installing.** Never install into the user's global Python without asking.

### 5. run
- Execute the confirmed entry command inside the prepared environment. Capture stdout, stderr, exit code, wall time.
- Set a timeout appropriate to the experiment; for long runs, stream logs to `logs/`.
- On failure: read the log tail, classify via `references/diagnostics.md`. Retry only after a concrete fix (≤2 retries).
- On success: collect artifacts. Reproduced metric values must come from files the run actually wrote (or numbers printed in logs, cited with the log path) — never from what the code "should" produce.

### 6. compare
- Pair paper claims `(model, dataset, metric, value, source)` with reproduced values on the `(model, dataset, metric)` key.
- Read `references/comparison-protocol.md` before choosing tolerances and before writing verdicts; prefer n-run mean ± std over single values (pass per-run lists to the script).
- Run `python3 scripts/compare_results.py ...` (default relative tolerance 1%; exactly-at-tolerance counts as match).
- Verdicts: `match` / `mismatch` / `missing_repro` (paper value exists but no reproduced value) / `missing_paper`.
- Present the comparison card (in Chinese to the user). For every `mismatch`, attempt diagnosis rather than just reporting the gap.

## Diagnosis handoff

When any step fails permanently (retry budget exhausted) or the comparison shows mismatches, switch to `references/diagnostics.md`:
classify each problem into **version / dependency / parameter / data**, gather the required evidence, write suggested fixes into `patches/`, and produce the final `report.md` + a Chinese summary for the user. Unclassifiable problems are listed as `info` — do not force a category.
