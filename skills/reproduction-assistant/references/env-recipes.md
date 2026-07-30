# Environment Setup Recipes

Read this file during the `env_generate` step, and whenever `env_detect` surfaces
a vague or conflicting dependency manifest. It turns fuzzy declarations into
concrete, defensible version choices — and records every guess as an assumption.

## 1. Deciding the CUDA / framework pair

The single most common root cause of reproduction failure is a CUDA ↔ framework
mismatch. Work from **what the machine has** (driver) and **what the paper used**
(date + declared versions) toward a concrete wheel.

### Driver first

- `nvidia-smi` top-right shows the driver's *maximum supported* CUDA version.
  Any CUDA runtime ≤ that works; newer does not (unless you can upgrade the driver).
- No `nvidia-smi` output / no GPU → go to section 5 (CPU fallback).

### CUDA ↔ PyTorch quick reference (prebuilt wheels)

- PyTorch wheels bundle their own CUDA runtime; you only need a compatible
  **driver**, not a matching system CUDA toolkit install.
- Rule of thumb: install with the index URL for a CUDA runtime ≤ driver max:
  `pip install torch==<ver> --index-url https://download.pytorch.org/whl/cu118` (or `cu121`, `cu124`, `cu126`, `cu128`).
- Rough pairings (verify against the repo's era, not this list alone):
  - paper ≤ 2021 → torch 1.7–1.10, CUDA 10.2/11.1/11.3
  - 2022–2023 → torch 1.12–1.13 (cu116/cu117) or torch 2.0 (cu117/cu118)
  - 2024+ → torch 2.1–2.4 (cu118/cu121/cu124)

### CUDA ↔ TensorFlow quick reference

- TF is pickier: each TF release is built against one specific cuDNN+CUDA pair.
  - TF 2.10 → CUDA 11.2, last version with native Windows GPU support
  - TF 2.11–2.13 → CUDA 11.8 (Linux)
  - TF 2.14–2.15 → CUDA 12.2/11.8; TF 2.16+ → CUDA 12.3
- If the repo pins an old TF, prefer the **NVIDIA NGC container**
  (`nvcr.io/nvidia/tensorflow:YY.MM-tf2-py3`) over hand-matching cuDNN — hand-matching cuDNN is the classic silent-failure trap.

### Checklist before installing

- [ ] driver max CUDA ≥ chosen runtime CUDA
- [ ] GPU compute capability supported by the wheel (old GPUs, e.g. Maxwell/sm_50, dropped in newer torch — error: `no kernel image is available`)
- [ ] repo's Python version compatible with the chosen framework version

## 2. Inferring versions when requirements are unpinned

Repos often say `torch`, `transformers`, `numpy` with no pin. Inference order
(stop at the first that yields a value; **record the choice + reason as an assumption** in the env report):

1. README / paper text stating a version ("we use PyTorch 1.9").
2. A lockfile or secondary manifest: `requirements-dev.txt`, `setup.py` pins,
   CI config (`.github/workflows/*.yml` often has the exact `pip install` lines — frequently the *only* working recipe).
3. `Dockerfile` / `environment.yml` in the repo.
4. **Contemporaneous version**: pick the latest release of the package *before
   the paper's last commit date*. Query release dates: `pip index versions <pkg>`
   (or PyPI JSON API `https://pypi.org/pypi/<pkg>/json`). This beats "latest"
   almost every time for fast-moving libs (`transformers`, `tokenizers`, `numpy`).
5. If the paper's numbers came from a specific checkpoint, prefer the library
   version named in the checkpoint's config (`config.json` often records
   `transformers_version`).

Red flags that demand pinning rather than guessing: `transformers`, `tokenizers`,
`numpy` (1.x vs 2.x breaks pickled arrays and C extensions), `datasets`,
`pytorch-lightning`, `protobuf`, `tokenizers` ↔ `transformers` internal coupling.

## 3. Docker vs conda vs venv — decision tree

```
Does the repo ship a Dockerfile / docker-compose?
├─ yes → use it first; it's the author's own recipe. Only rebuild if it fails.
└─ no → Does the repo need system libs (gcc toolchain, cuda toolkit, ffmpeg,
        openmpi, graphviz, R, system BLAS) or a specific CUDA?
    ├─ yes → Docker (write Dockerfile.reproduce; base on
    │        pytorch/pytorch:<torch>-cuda<x.y>-cudnn<n>-devel or NGC images)
    └─ no → Does the manifest include non-pip packages
            (environment.yml with conda-only deps, e.g. cudatoolkit, mkl, openmpi)?
        ├─ yes → conda (environment.yml); keep channels explicit
        │        (conda-forge), export a lock: conda env export --no-builds
        └─ no → python3 -m venv + pinned requirements.lock
                 (cheapest, most transparent; preferred default on Linux/Win)
```

Always record *why* the choice was made in the env report, so a later failure
can revisit the decision instead of flailing.

## 4. Common system-level dependencies (pip won't tell you)

Symptom → missing system package (Debian/Ubuntu names):

- `fatal error: Python.h` → `python3-dev` (build-essential too)
- wheel build fails for `psycopg2` → `libpq-dev`; `mysqlclient` → `libmysqlclient-dev`
- `ImportError: libGL.so.1` (opencv / matplotlib headless) → `libgl1 libglib2.0-0`
- `ffmpeg`/`av` errors in video/audio repos → `ffmpeg libavcodec-dev`
- `libsndfile` for audio (`soundfile`, `librosa`) → `libsndfile1`
- horovod / mpi4py build errors → `openmpi-bin libopenmpi-dev`
- `graphviz` render errors → system `graphviz` package, not just the pip one
- Windows: many science wheels need the *Microsoft C++ Build Tools* if no
  prebuilt wheel exists for your Python version — check `pip install` output for
  "building wheel" on packages that should have wheels; that usually means wrong
  Python minor version (e.g. 3.13 too new for old pins).

## 5. GPU unavailable → CPU fallback risks

A CPU run is a **smoke test, not a reproduction**. Risks to state explicitly:

- **Non-determinism changes direction**: some ops differ numerically between
  CUDA and CPU kernels; results can shift beyond tolerance.
- **Throughput**: training that took 8 GPU-hours may take weeks on CPU.
  Reduce epochs/steps and label the run "non-original configuration, values cannot be directly compared with the paper".
- **OOM shape changes**: CUDA OOM errors disappear; RAM OOM may appear instead.
- **Code paths**: repos often have `if cuda:` branches — the CPU path is usually
  the *less tested* one (e.g. missing `.cpu()` moves, `pin_memory` hangs).
- **Mixed precision**: `torch.cuda.amp` is a no-op-ish path on CPU; bf16 on CPU
  is slow or unsupported in older torch.
- Verdict policy: CPU-fallback metrics are reported with `mismatch` expected
  and a note; never presented as confirming the paper.

## 6. Env report template (write into `env/env-report.md`)

```
- Choice: docker | conda | venv — because <one line>
- Python: <ver> (declared by <source> | assumed: latest before commit <date>)
- Framework: torch==<x> + cu<y> — because <source/assumption>
- Key pins: <name>==<ver> — <source | assumption: release before <date>>
- System packages: <list>
- Unresolved risks: <e.g. "transformers unpinned; assumed 4.21.0 (2022-08)">
```
