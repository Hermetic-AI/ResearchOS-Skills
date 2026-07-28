# Result Comparison Protocol

Read this file during the `compare` step — before choosing tolerances, and
before writing verdicts into the comparison card or the paper's reproduction
section. `scripts/compare_results.py` implements the mechanics; this file is
the judgment layer.

## 1. What tolerance is defensible?

Tolerance is not a constant. Set it per metric family, from the expected noise
sources, and state the basis on the card. Reference magnitudes:

| Noise source | Typical magnitude on final metric | Set tolerance ≥ |
| --- | --- | --- |
| Same seed, same machine, deterministic run | ~0 (exact or 1e-6) | exact match expected |
| Seed variance (same config, different seeds) | classification acc: ±0.1–0.5 pp; small datasets: ±1–3 pp; RL returns: ±10–30% | the reported std across seeds |
| Framework/version numeric drift (TF↔PT, cuDNN algo choice) | last-digit to ±0.1 pp | 0.1–0.5% relative |
| Hardware drift (GPU arch, TF32 on Ampere+ by default!) | ±0.05–0.3 pp; TF32 can flip borderline cases | 0.5% relative |
| Different train pipeline (reimplementation, not author's code) | ±1–5 pp is common | 2–5% relative — argue, don't just accept |
| Reduced-scale run (fewer steps/data) | unbounded | non-comparable, declare it |

Rules:
- **Default 1% relative** (the script default) only when you have no noise
  estimate. Once you have run-to-run std, replace tolerance with
  `max(1% relative, 2 × std)`.
- **TF32 trap**: PyTorch enables TF32 matmuls on Ampere+ since 1.12. If the
  paper predates Ampere and you run on A100/H100, expect ±0.1–0.3 pp drift.
  Set `torch.backends.cuda.matmul.allow_tf32 = False` for a strict check.
- **Percentages vs points**: for accuracy-type metrics reported in %, prefer
  stating tolerance in percentage points (e.g. ±0.3 pp) — relative error on
  92% vs 92.3% looks tiny while being a real gap.
- **BLEU/ROUGE/meteor**: tokenizer and implementation differences dominate;
  ±0.5–1.0 BLEU is the floor for "same" unless identical eval code is used.

## 2. Seeds, runs, and variance

- One reproduced number is an anecdote. Minimum reporting unit:
  **mean ± std over n runs with different seeds**.
- How many runs:
  - n=1: only acceptable for deterministic pipelines (fixed seed + deterministic
    flags) or huge runs; label "single run, seed=<s>".
  - n=3: minimum for claiming variance matches the paper.
  - n=5–10: when the paper reports std and you want to claim it's within noise.
- If the paper reports mean±std over n seeds, reproduce with the **same n and
  seed protocol** if discoverable; otherwise state your seeds.
- Feed the per-run values to `compare_results.py` as a list in the repro
  `value` field (`"value": [75.8, 76.0, 75.9]`); the script reports mean, std,
  spread, and judges using the mean.

## 3. Verdict discipline

- `match` means: within the *stated* tolerance *with the basis recorded*. A
  match under tolerance you never justified is not a match.
- `mismatch` triggers diagnosis (`references/diagnostics.md`), not just a red
  row. Before concluding "the paper is wrong", eliminate in order:
  1. wrong eval subset / split (most common)
  2. wrong checkpoint or config variant (paper's Table 2 ≠ default config)
  3. metric definition (e.g. best-vs-last epoch, EMA weights, test-time aug)
  4. preprocessing/eval-code difference
  5. genuine noise (your std overlaps the gap)
- **Non-comparable situations — declare, don't force**: reduced-scale runs,
  CPU fallback, substituted dataset (e.g. ImageNet subset), different eval
  protocol. Mark the row non-comparable and say why; never average these into
  the match rate.

## 4. Writing the reproduction note into a paper/report

A defensible comparison card contains, per claim:

- claim: (model, dataset, metric, paper value, paper location: table/section)
- reproduced: mean ± std (n runs, seeds listed), artifact path per run
- environment delta: commit sha, key versions vs paper's, hardware
- tolerance and its basis (from section 1)
- verdict + for mismatches: the diagnosis summary and what was ruled out

Template paragraph (English artifact, adapt to the paper's language):

> We reproduced <model> on <dataset> (<paper>, Table <k>) using the authors'
> code at commit <sha>. Over <n> runs (seeds <list>) we obtain <mean ± std>
> vs the reported <value> (tolerance ±<t> based on <basis>): <verdict>.
> Environment: <key deltas>. <For mismatch: gap of <x> pp remains after
> ruling out eval-split, checkpoint, and metric-definition differences;
> suspected cause: <...>.>

Red lines for write-ups: never drop failing rows from the table; never round
reproduced values toward the paper's; never claim "consistent with the paper"
without stating n and tolerance.
