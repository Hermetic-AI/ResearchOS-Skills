# Failure Diagnosis: Signal → Category Mapping

Read this file when a pipeline step fails permanently or results mismatch.
Four categories: **version**, **dependency**, **parameter**, **data**.

Rules:
- Every diagnosis needs **evidence** (a log excerpt of ~5 lines around the signal, or `file:line`). No evidence, no claim — say "insufficient evidence" instead.
- Suggested fixes that change code/config are written into `patches/` as diffs, never silently applied.
- Severity: `blocker` (run cannot proceed) / `warning` (runs but results untrustworthy) / `info` (FYI, includes unclassifiable problems).

## Mapping table

| Signal (log pattern / condition) | Category | Typical cause |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'X'` | dependency | package not installed; undeclared transitive dep |
| `ImportError: cannot import name ...` | dependency | wrong package version (API moved/renamed) |
| pip `ResolutionImpossible` / `conflicting dependencies` | dependency | version constraints conflict |
| `ERROR: No matching distribution found for X==...` | version | pinned version unavailable for this Python/platform |
| `CUDA error: no kernel image is available for execution on the device` | version | framework binary built for different CUDA compute capability |
| `The NVIDIA driver on your system is too old (found version ...)` | version | driver < CUDA runtime requirement |
| `torch.cuda.is_available()` False but repo expects GPU | version | CPU-only wheel installed, or no GPU |
| Python minor mismatch vs README (e.g. repo needs 3.8, env is 3.12) | version | removed stdlib APIs (`imp`, `collections.Mapping`, `np.float`...) |
| `AttributeError: module 'numpy' has no attribute 'float'` etc. | version | new major version removed deprecated aliases |
| Artifacts produced but metrics mismatch AND log shows default seed/lr warnings, config key missing, "using default ..." | parameter | seed/hyperparameter/config not aligned with paper |
| Config file missing keys the code reads with defaults | parameter | paper used a config not committed / different YAML |
| `FileNotFoundError` / `No such file or directory` pointing at a dataset path | data | dataset not downloaded, wrong root path |
| `checksum` / `md5 mismatch` on dataset download | data | corrupted/partial download |
| download/preprocess script exists but never ran (dataset dir empty) | data | skipped data-prep step |
| `RuntimeError: CUDA out of memory` | parameter | batch size too large for local GPU (reduce + label non-comparable) |
| `Segmentation fault` / exit 139, no traceback | version | native extension ABI mismatch — see "Hard failure signals" below |
| `Killed` (system OOM killer) | parameter/data | dataloader workers × prefetch exhaust RAM |
| `NCCL timeout` / collective watchdog | version | NCCL/driver mismatch or wrong network interface — confirm single-GPU first |
| `md5/checksum mismatch`, `BadGzipFile`, `tarfile.ReadError` | data | corrupted/partial dataset download; verify checksum yourself |
| tokenizer warnings / vocab-size mismatch, results silently off | version | tokenizer stack drift — pin to checkpoint-recorded version |
| `FutureWarning`/`DeprecationWarning` → `TypeError`/`ImportError` of documented API | dependency | installed version newer than repo era; pin contemporaneous version |

## Per-category requirements

### version
- **Evidence**: the error line + the repo's declared version (README / setup.py `python_requires` / CUDA note) + the environment's actual version (`python3 --version`, `pip show torch`, `nvidia-smi`).
- **Fix**: regenerate the env file pinned to the declared versions; if the pin is unavailable, choose the closest contemporaneous version and record it as an assumption.

### dependency
- **Evidence**: the import-error traceback (top frame = which file imports what) + current installed version (`pip show X`, or "not installed").
- **Fix**: add/pin the package in the env file; for API-moved imports, downgrade to the version contemporary with the repo's last commit. Re-run `parse_deps.py` after fixing to confirm the manifest is consistent.

### parameter
- **Evidence**: the "using default X" / seed warning log lines + the config file actually used vs the paper's stated hyperparameters (cite paper section) + `git log` showing whether the paper's config was ever committed.
- **Fix**: a patch in `patches/` aligning seed/lr/batch-size/config path with the paper. If the paper doesn't state the value, say so — do not guess silently; if you must pick, mark the run as non-comparable.

### data
- **Evidence**: the FileNotFoundError path + the dataset directory listing (missing/empty) + the repo's download/preprocess instructions (README section or script path).
- **Fix**: the exact download/preprocess commands to run (or a patch fixing a wrong hardcoded path). If the dataset requires manual access (license form), stop and tell the user — do not fabricate data.

## Hard failure signals (crashes and infra failures)

Each entry: signal → category → minimal confirmation steps. "Minimal
reproduction confirmation" = the smallest command that proves the diagnosis
before you touch the env or write a patch. Always run the confirmation — a
guess that skips it is how wrong fixes get applied.

### Segmentation fault (exit code 139 / `Segmentation fault`, no Python traceback)
- **Category**: version (native lib ABI mismatch) or dependency (compiled extension vs runtime).
- Typical causes: compiled extension (`numpy`/`pyarrow`/`tokenizers`/custom CUDA op) built against different Python or CUDA than the runtime; mixing conda and pip native libs; corrupt checkpoint fed to a C parser.
- **Minimal confirmation**:
  1. `python3 -X faulthandler -c "import <top suspect pkg>"` — find which import dies.
  2. Rerun with `PYTHONFAULTHANDLER=1 python3 train.py ...` → native crash gets a Python frame.
  3. `pip check` for broken dependency graphs; `ldd` / `objdump` not needed if step 1–2 already isolate the module.
- Fix: reinstall that package pinned to a wheel matching your Python/CUDA (no source build unless intended); record as version assumption.

### OOM — two distinct kinds
- `RuntimeError: CUDA out of memory` → **parameter** (batch too large for local GPU) or version (memory-inefficient path in a newer framework).
  - **Minimal confirmation**: run the same command with batch size halved. If it proceeds past the crash point, confirmed. Also `nvidia-smi` during the run: memory climbing to 100% before crash = capacity; crash at <80% with fragmentation warning = fragmentation (`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` may help).
  - Fix: reduce batch + enable gradient accumulation to keep the *effective* batch — and label the run non-comparable if the paper's batch had to change.
- System RAM OOM (process killed, `Killed` in shell, `dmesg` shows oom-killer) → **parameter/data** (dataloader workers × prefetch, or dataset loaded fully into RAM).
  - **Minimal confirmation**: `dmesg | tail` (Linux) shows `Out of memory: Killed process`; rerun with `num_workers=0`. If it survives, the worker prefetch was the cause.

### NCCL / distributed timeouts (`NCCL timeout`, `Watchdog caught collective operation timeout`, `Connection reset by peer` on rank N)
- **Category**: version (NCCL/CUDA mismatch) or environment infra; sometimes data (one rank stuck on slow I/O looks like a hang).
- **Minimal confirmation**:
  1. Does it hang with a **single GPU** (`CUDA_VISIBLE_DEVICES=0`, world size 1)? If yes → not NCCL at all; it's a data/compute hang → data category.
  2. `python3 -c "import torch; torch.cuda.init()"` then a 2-GPU all-reduce smoke: `torchrun --nproc_per_node=2 -m torch.distributed.run` style minimal script — if even `all_reduce` on two tensors times out, it's NCCL/driver/network, not the repo.
  3. Check `NCCL_DEBUG=INFO` log for the transport chosen (IB vs socket); behind containers/NAT, `NCCL_SOCKET_IFNAME` wrong interface is the classic cause.
- Fix: pin NCCL via the matching torch wheel (don't hand-install NCCL); set the interface env var; increase `timeout=` only after 1–3 are understood.

### Dataset verification failure (`checksum mismatch`, `md5 does not match`, `BadGzipFile`, `tarfile.ReadError`, corrupt archive)
- **Category**: data.
- **Minimal confirmation**:
  1. Recompute the checksum yourself: `md5sum <file>` (or sha256) and compare with the value in the download script/README — don't trust the downloader's message.
  2. Check file size against the expected size in the script; a 90%-sized file = interrupted download.
  3. Delete the file and re-download once (counts as one retry). Repeated mismatch from the same mirror = upstream changed the file → the paper's data version is gone; record exact new checksum and mark results affected.
- Never silence the checksum check in the repo code as a "fix".

### Tokenizer / preprocessing version drift (runs fine, results off; `Token indices sequence length is longer than ...`, vocab size mismatch in embeddings, `sentencepiece` load error)
- **Category**: version (quiet result corruption — the dangerous kind).
- Typical causes: `transformers`/`tokenizers` major bump changed default tokenizer behavior (added special tokens, changed padding side, fast-vs-slow default); `sentencepiece` model re-encoded differently; tiktoken encoding renamed.
- **Minimal confirmation**:
  1. Tokenize one fixed string with the installed version and compare against a reference: `python3 -c "from transformers import AutoTokenizer; t=AutoTokenizer.from_pretrained('<id>'); print(t('hello world'))"`. Compare `input_ids` with those produced by the version contemporary with the paper (same one-liner in a scratch venv).
  2. `config.json` / `tokenizer_config.json` of the checkpoint records `transformers_version` — install that exact version and re-tokenize.
- Fix: pin tokenizer stack to the checkpoint-recorded version; if results then match, this was it — write it into the comparison card as the root cause.

### API deprecation / removal (`FutureWarning` → later `TypeError: unexpected keyword argument`, `ImportError: cannot import name 'X' from 'Y'`, `AttributeError` on a documented method)
- **Category**: dependency (version drift).
- **Minimal confirmation**:
  1. Read the traceback's top repo frame → which call uses the removed API.
  2. `pip show <pkg>` → installed version; compare with the repo's last commit date. If installed >> commit date, drift confirmed.
  3. `pip index versions <pkg>` → find the latest release *before* the commit date; install it in the scratch env and re-run the failing import/call only.
- Fix: pin to the contemporaneous version (preferred) or write a `patches/` diff updating the call site — never do both silently; prefer the pin, since repo-contemporary code is what produced the paper's numbers.

## Output format

Group findings by category, each item:

```
- [severity] Title
  Category: version|dependency|parameter|data
  Evidence: <log excerpt or file:line>
  Suggestion: <what to change; patch file path if written>
  Retried: <n> times (if applicable)
```

The user-facing summary is in Chinese; unclassifiable items go under `info` with "证据不足，未强行分类".
