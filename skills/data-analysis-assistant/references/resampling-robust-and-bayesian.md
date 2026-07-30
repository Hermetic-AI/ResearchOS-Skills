# Resampling, robust, and Bayesian analysis

Use `scripts/resampling_bayesian.py` only after defining the estimand and resampling unit. Every stochastic method requires and records a seed.

```bash
python scripts/resampling_bayesian.py bootstrap --stat difference --a 1,2,3 --b 2,3,4 --reps 5000 --seed 42
python scripts/resampling_bayesian.py permutation --stat correlation --x 1,2,3 --y 2,4,6 --reps 5000 --seed 42
python scripts/resampling_bayesian.py robust --a 1,2,3,4,100 --b 2,3,4,5,6 --trim 0.2
python scripts/resampling_bayesian.py bayes-binomial --success-a 18 --total-a 30 --success-b 12 --total-b 30 --prior-a 1 --prior-b 1 --seed 42
```

## Interpretation boundaries

- Bootstrap output is a percentile confidence interval, not a guarantee of coverage for small, skewed, dependent, clustered, paired, or time-series data. Resample the scientific unit, not arbitrary rows.
- Permutation output is a two-sided Monte-Carlo p-value with the +1 correction. The exchangeability scheme must preserve pairing, strata, clusters, or time blocks.
- Robust mode performs Welch-style trimmed-mean comparison. It does not automatically solve heteroscedasticity, dependence, missingness, or selective outlier removal; pre-specify trimming.
- Bayesian mode is an independent beta-binomial model for two proportions. It outputs posterior probability and a credible interval—not a p-value or confidence interval. Vary priors and report the sensitivity analysis.

The CLI intentionally does not present generic resampling as a substitute for a design-aware hierarchical, paired, clustered, or serially correlated analysis. Use a dedicated model/simulation for those settings.

## Equivalence, noninferiority, and missing-data sensitivity

```bash
python scripts/inference_extensions.py equivalence --a 10,11,9 --b 10.2,10.5,9.8 --low -1 --upp 1
python scripts/inference_extensions.py noninferiority --a 10,11,9 --b 10.2,10.5,9.8 --margin 1
python scripts/inference_extensions.py missing-sensitivity --observed-effect 0.3 --observed-se 0.1 --missing-fraction 0.15 --delta-low -1 --delta-high 1
```

TOST uses raw lower/upper equivalence bounds; noninferiority uses a positive raw margin with null `difference <= -margin`. Both require an externally justified, pre-specified bound. The missing-data command is a transparent delta grid, not multiple imputation and not a claim that missingness is MAR.

## Multiple imputation (numeric CSV)

```bash
python scripts/mice_impute.py raw.csv --out completed.csv --columns outcome,baseline,age --iterations 20 --seed 42
```

The command uses Statsmodels MICE predictive-mean matching and writes a protected new CSV plus an `imputation-manifest`. Include outcome and analysis predictors where appropriate, diagnose the missingness mechanism, and pool estimates across multiple imputations for inferential claims; this utility deliberately returns one completed data set rather than pooled inference. Implementation reference: [Statsmodels MICEData](https://www.statsmodels.org/stable/generated/statsmodels.imputation.mice.MICEData.html).

Artifacts are `resampling-estimate`, `stat-results` (robust mode), `bayesian-estimate`, and `imputation-manifest`. Public implementation bases: [SciPy trimmed t-test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html) and Python [random.betavariate](https://docs.python.org/3/library/random.html#random.betavariate).
