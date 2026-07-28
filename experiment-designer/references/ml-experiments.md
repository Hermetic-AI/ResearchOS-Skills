# ML/AI Experiment Design

Read this when the experiment evaluates a machine-learning model, training procedure, or system component (workflow step 2, ML branch). The core design principles are the same as anywhere else — controls, replication, no leakage between selection and evaluation — but they map onto ML-specific machinery: baselines, ablations, hyperparameter budgets, seeds, and benchmark hygiene.

## Baseline selection discipline

A claim "our method improves X" is only as strong as the baseline it beats.

- **Use the strongest published baseline**, not the easiest one. Reviewers check. If a stronger baseline exists and you skip it, state why (unavailable code, license, compute).
- **Re-run baselines yourself under your data splits, preprocessing, and budget.** Borrowing published numbers from a different pipeline compares pipelines, not methods. Report both reproduced and published numbers when they differ.
- **Give baselines a fair tuning budget.** A baseline with default hyperparameters vs. your tuned model measures your tuning, not your method. Budget rule: the baseline's hyperparameter search gets at least the same number of trials as yours.
- **Include a dumb baseline.** Majority class, last-value carry-forward, linear model on raw features. If your deep model barely beats logistic regression, that is the finding.
- **Match the comparison level.** Comparing your full system against a baseline system; comparing a novel component against the same system with a standard component swapped in. Don't mix levels.

## Ablation design

Ablation answers "which components carry the gain?" — but only under the design's attribution limits.

- **Leave-one-out (LOO) is the default**: full system + one run per component removed. Cheap (k+1 runs), but each attribution is conditional on all other components — two components that only help together both look useless. Flag this explicitly in the paper.
- **Full ablation (all 2^k − 1 subsets)** is the only design that maps interactions; cost explodes (k=6 → 63 training runs). Use for k ≤ 5 or for a suspicious component pair (a targeted 2×2).
- **Cumulative add-one is order-dependent**: shared gains are credited to whatever is added first. Justify the order (e.g. chronological development) or average over orders.
- Ablate **one thing at a time**; a "variant" that changes the loss, the architecture, and the data simultaneously attributes nothing.
- Generate the matrix with `scripts/ablation_planner.py` (loo / all / add modes); shuffle the run order so config identity doesn't align with cluster noise or hardware drift.

## Hyperparameter search budget

The search protocol is part of the method and must be reported.

| Strategy | When | Budget rule |
|---|---|---|
| Grid | 1–3 hyperparameters, coarse ranges | cost = product of grid sizes; never grid-search >3 dims |
| Random | default for 4+ dims | ~60 trials finds a top-5% config with 95% probability (Bergstra & Bengio 2012); strictly better than grid when few dims matter |
| Bayesian / successive halving (ASHA, Hyperband) | expensive runs, many dims | report the surrogate/acquisition and the early-stopping rule; early stopping biases against slow starters — state it |

Rules:

- **Tune on a validation set, never the test set.** Test is touched once, at the end. If you iterate against test performance, you have tuned on test.
- **Fix the budget before searching** (trials × GPU-hours) and report it; a method that needs 10× the search budget to win is a different result than one that wins at equal budget.
- Nested evaluation when the dataset is small: outer split for evaluation, inner split for tuning — otherwise the reported score is optimistic.

## Seeds and variance reporting

ML results are random variables; a single run is an anecdote.

- **≥ 3 seeds minimum, 5 preferred** for final numbers (10 for high-variance settings like RL). Report mean ± std (or all per-seed scores), not the max.
- Sources of variance to control or report: weight init, data order/augmentation, data split itself, hardware nondeterminism. For the strongest claims, vary the *data split* too (different folds), not just the init.
- Compare methods with a **paired test across matched seeds/folds** (paired t or Wilcoxon signed-rank), not by comparing confidence intervals of independent means.
- Fix the seed for every run (`--seed` in every script); log it with the result. A result you cannot regenerate is a liability.

## Benchmark leakage checklist

Leakage inflates scores and invalidates comparisons. Check each of these explicitly:

1. **Train/test overlap** — exact duplicates or near-duplicates across the split (deduplicate with embedding or n-gram overlap, not just string equality).
2. **Preprocessing leakage** — scalers, imputers, feature selection, or vocabulary fitted on the full dataset before splitting. Fit inside the training fold only.
3. **Tuning on test** — model/epoch/threshold selected by test performance. Use a validation split.
4. **Temporal leakage** — predicting the past from the future (random split of time-series data). Split by time.
5. **Group leakage** — same patient/user/molecule scaffold in both train and test. Split by group identity, not by row.
6. **Contamination of pretrained models** — the benchmark test set (or paraphrases of it) inside the pretraining corpus. Check the model card; run a contamination check; prefer benchmarks published after the pretraining cutoff.
7. **Metric gaming** — reporting the metric variant your method happens to maximize; report the benchmark's standard metric.

## Compute budget reporting

Report, per experiment: GPU/TPU type and count, wall-clock hours, total GPU-hours (and/or FLOPs), number of training runs including search and failed runs, and — for pretraining-scale work — estimated energy/CO2. Declare the compute budget **in the design phase** so a result is interpretable as "what is achievable within this budget," and compare methods at equal compute, not just equal architecture. Practical implication for design: cap the total budget first, then allocate it across baseline tuning, ablations, and seed replicates — seed replicates are usually the first thing cut and should not be.

## ML experiment review checklist

- Strongest available baseline, re-run under identical splits and tuning budget?
- Ablation design stated (LOO/full/add) with its attribution limit acknowledged?
- Hyperparameter search: strategy, budget, and tuning split reported — test untouched?
- ≥ 3 seeds, mean ± std, paired comparison across seeds?
- All 7 leakage checks passed (or residual risk stated)?
- Compute budget declared and reported?
