---
name: data-analysis-assistant
description: Analyze collected research data through profiling, cleaning, statistical tests, regression/GLM/ANCOVA, GEE/mixed models, Cox survival and competing risks, SARIMAX time series, panel fixed effects, assumptions, effect sizes, intervals, multiplicity, and structured reporting. Use for 分析实验数据, 数据画像, 数据清洗, 回归, 广义线性模型, ANCOVA, 重复测量, 混合效应模型, Cox, 生存分析, 竞争风险, 时间序列, 面板数据, 显著性检验, p值, 效应量, 置信区间, 多重比较校正, or analyze my dataset. Not for pre-data experiment design, literature reading, figures, manuscript prose, knowledge graphs, or reproducing published code.
---

# Data Analysis Assistant (数据处理分析)

For researchers (grad students) working with experimental data. Reports to the user are in Chinese by default; content written into artifacts follows the artifact's language.

> **NOT for 综述/文献阅读/论文写作** — 该 skill 仅用于已收集实验数据的统计分析与清洗。文献阅读用 literature-reader，论文写作用 paper-writing-assistant。

**Global conventions**
- **Report first, modify later**: produce findings and suggestions; never overwrite the user's raw data files. Cleaning runs through `scripts/clean_csv.py` with an explicit rules file, always writing a new `*_clean.csv` plus a cleaning log.
- **Every statistical conclusion must include**: test name, statistic, exact p-value, significance verdict at alpha = 0.05, effect size, and confidence interval when available. Follow the wording rules in `references/test-selection.md` (notably: non-significant ≠ no difference).
- **Reproducibility**: prefer the bundled scripts over ad-hoc analysis; when randomness is involved, always pass a fixed seed.
- **Analysis-plan integrity**: when an `analysis-plan` exists, read `references/artifact-contracts.md`, report deviations explicitly, and output validated `cleaning-manifest`/`stat-results` JSON for downstream skills.

## Capabilities overview

| # | Capability | Entry point |
|---|------------|-------------|
| 1 | Data profiling & normality hints | `python3 scripts/profile.py data.csv --format both` |
| 2 | Data cleaning with citable log | `python3 scripts/clean_csv.py data.csv rules.json --out clean.csv` |
| 3 | Statistical test selection | decision tree in `references/test-selection.md` |
| 4 | Test execution + effect size + CI | `python3 scripts/stat_test.py data.csv --test <name> ...` |
| 5 | Multiple-comparison correction | `python3 scripts/stat_test.py --test adjust --method holm --pvalues "p1,p2,..."` |
| 6 | Regression / GLM / ANCOVA / GEE / MixedLM | `python3 scripts/model_analysis.py data.csv --model <type> --formula "y ~ x"` |
| 7 | Cox / competing risks / SARIMAX / panel FE | `scripts/survival_analysis.py` and `scripts/temporal_panel_analysis.py` |
| 8 | Bootstrap / permutation / robust / Bayesian | `python3 scripts/resampling_bayesian.py <mode> ...` |
| 9 | Residual / VIF / influence / dispersion diagnostics | `python3 scripts/model_diagnostics.py data.csv --formula "y ~ x"` |
| 10 | Equivalence / noninferiority / missing-data sensitivity | `python3 scripts/inference_extensions.py <mode> ...` |
| 11 | Numeric MICE imputation with protected output | `python3 scripts/mice_impute.py raw.csv --out completed.csv --columns outcome,baseline` |
| 12 | Bootstrap effect-size confidence interval | `python3 scripts/effect_size_ci.py data.csv --metric cohens-d --value score --group arm --seed 42` |
| 13 | Inspect/convert tabular formats + data dictionary | `python3 scripts/tabular_io.py inspect data.xlsx --dictionary-out dictionary.json` |

## When to use / not use

Use when the user has data (CSV) and asks about data quality, cleaning, outliers, which test to run, p-values, effect sizes, p-value correction, or how to report statistics. Do **not** use for paper prose, citation checks, literature reading, experiment design, or figure beautification (those belong to the sibling skills listed in the description).

## Workflow

1. **Profile first (always)**: run
   `python3 scripts/profile.py <file.csv> --format both`
   Per-column schema (numeric/categorical/datetime/text), descriptive stats, skewness/kurtosis with a normality hint (screen only — confirm with Shapiro-Wilk), missing counts, suspected outliers (IQR and z-score), duplicates/constant columns. Use `--out report.md --format md` to save the report.
2. **Clean if needed**: read `references/data-cleaning.md` — **only when profiling reveals quality problems (missing values, duplicates, inconsistent units/codings, date issues, outliers); skip for a clean dataset**. It gives the decision rules: MCAR/MAR/MNAR discrimination before choosing an imputation strategy, duplicate handling, unit/coding/date consistency checks, and the outlier keep/correct/drop/bin decision tree with the justification each action must record. Agree the rules with the user, write them as a JSON rules file, then run
   `python3 scripts/clean_csv.py <file.csv> rules.json --out <clean.csv> --log cleaning_log.md --artifact-out cleaning-manifest.json`
   The log records per-step affected row counts and reasons — citable in the Methods section.
3. **Choose the test**: read `references/test-selection.md` — **only when the analysis reaches test selection**. Confirm the research question, group/value columns, independent vs paired samples with the user. Apply the decision tree (normality via Shapiro, variance homogeneity via Levene).
4. **Run the test**: requires scipy + numpy — install once with `pip install scipy numpy`. Then e.g.
   `python3 scripts/stat_test.py <clean.csv> --test ttest --value score --group group_col --artifact-out stat-results.json --result-id primary`
   Output is JSON (`--format json` default) or Markdown (`--format md`) with statistic, exact p, effect size, 95% CI (ttest/pearson; `--ci` changes the level), and a fill-in Chinese conclusion template.
5. **Correct for multiple comparisons** whenever more than one test ran on the same dataset:
   `python3 scripts/stat_test.py --test adjust --method holm --pvalues "0.01,0.04,0.20" --labels "m1,m2,m3"`
   Method choice (Bonferroni vs Holm vs BH-FDR) per the table in `references/reporting.md`.
6. **Fit a model when the estimand requires it**: read `references/regression-and-multilevel-models.md`, then use `scripts/model_analysis.py` for OLS/ANCOVA, GLM, population-average GEE, or linear MixedLM. Supply `--analysis-plan` when available; inspect diagnostics before interpreting coefficients.
7. **Route structured/time-dependent data explicitly**: for time-to-event data, competing events, regular time series, or entity-time panels, read `references/survival-time-series-and-panel.md`, then use the corresponding script. Do not substitute cause-specific hazards for subdistribution hazards, irregular observations for a regular series, or generic two-way fixed effects for a justified causal design.
8. **Use resampling/Bayesian methods deliberately**: read `references/resampling-robust-and-bayesian.md`; define the resampling unit, Monte-Carlo budget, seed, robust estimand, or prior before running `scripts/resampling_bayesian.py`.
9. **Diagnose fitted models**: read `references/model-diagnostics.md` and run `scripts/model_diagnostics.py`. Treat flags as prompts for investigation and sensitivity analysis, never as automatic row deletion.
10. **Make bounded inference explicit**: read `references/resampling-robust-and-bayesian.md` before using `scripts/inference_extensions.py`; record the prespecified equivalence/noninferiority margin or missingness delta range.
11. **Impute only with an explicit missing-data rationale**: read `references/data-cleaning.md` and `references/resampling-robust-and-bayesian.md`, choose numeric predictors deliberately, then run `scripts/mice_impute.py`. It protects raw and derived outputs and produces one completed CSV plus `imputation-manifest`; do not mistake it for pooled MI inference.
12. **Add the effect-size interval where the base test lacks one**: use `scripts/effect_size_ci.py` for Cohen's d, rank-biserial r, eta squared, Cramer's V, Pearson r, or Spearman rho. Read `references/resampling-robust-and-bayesian.md` first and preserve the scientific resampling unit.
13. **Normalize non-CSV data before analysis**: use `scripts/tabular_io.py inspect` to write a `data-dictionary`, then `convert` only when a legacy CSV-only script needs a derived CSV. Preserve the source, never overwrite a derived output, and verify units/codes against the study protocol.
14. **Report in Chinese**: read `references/reporting.md` — **only when writing up results**. It enforces the APA-7 completeness checklist (statistic + df, exact p, effect size with CI, descriptives, correction statement), exact-vs-threshold p rules, and the text/table/figure division of labor. Combine profile context + test results into a short report; if the result feeds a paper section, hand the numbers to the user or the paper-writing-assistant skill — this skill does not write paper prose.

## File index

- `scripts/profile.py` — zero-dependency (stdlib only) CSV profiler: schema, descriptive stats with skewness/kurtosis and a normality hint, missing values, IQR/z-score outlier flags, duplicate/constant-column checks. JSON + Markdown output, `--out` writes a report file.
- `scripts/clean_csv.py` — zero-dependency declarative CSV cleaner with raw-input protection and derived-output overwrite guards. Applies dedupe / fill_missing / drop_outliers / convert_type rules and emits a cleaned CSV, citable log, and optional schema-validated `cleaning-manifest`.
- `scripts/stat_test.py` — scipy/numpy test dispatcher: ttest_ind / ttest_rel (paired) / mannwhitneyu / f_oneway / kruskal / chi2_contingency / fisher_exact / pearsonr / spearmanr, assumption checks (shapiro, levene), effect sizes, confidence intervals, and multiple-comparison correction. `--artifact-out` writes a versioned `stat-results` artifact with overwrite protection.
- `scripts/model_analysis.py` — pandas/Statsmodels formula models: OLS/ANCOVA, Gaussian/binomial/Poisson/negative-binomial GLM, repeated-measure GEE, and linear MixedLM; writes coefficient-level `stat-results`.
- `scripts/survival_analysis.py` — Cox proportional hazards with delayed entry/strata/cluster options and Aalen–Johansen competing-risk estimates.
- `scripts/temporal_panel_analysis.py` — univariate SARIMAX forecasts and entity/time fixed-effect panel regression with clustered covariance.
- `scripts/resampling_bayesian.py` — seeded percentile bootstrap, Monte-Carlo permutation, trimmed-mean comparison, and beta-binomial posterior comparison.
- `scripts/model_diagnostics.py` — OLS/GLM residual screens, VIF, Cook's distance/leverage, and Pearson dispersion diagnostics.
- `scripts/inference_extensions.py` — raw-scale TOST equivalence, Welch noninferiority, and deterministic missing-data delta sensitivity grids.
- `scripts/mice_impute.py` — numeric Statsmodels MICE predictive-mean-matching completion; never overwrites raw or existing derived files and writes `imputation-manifest`.
- `scripts/effect_size_ci.py` — seeded percentile-bootstrap CIs for every effect-size family emitted by `stat_test.py`; outputs a schema-valid `stat-results` artifact.
- `scripts/tabular_io.py` — protected inspection/conversion for CSV, TSV, JSON records, XLSX, and Parquet; creates a schema-valid `data-dictionary`.
- `references/test-selection.md` — test selection decision tree (two-group / three-or-more / categorical / correlation paths), effect-size interpretation thresholds, and reporting-wording rules (disclaimers, multiple-comparison reminders).
- `references/data-cleaning.md` — cleaning decision checklist: MCAR/MAR/MNAR discrimination tests and strategy selection, duplicate-record handling, unit/coding/date consistency, outlier keep/correct/exclude/winsorize decision tree with the justification each action must record, and Methods-section reporting of cleaning.
- `references/reporting.md` — statistical reporting standards: APA-7 completeness checklist, exact p vs threshold rules, mandatory effect size + CI, Bonferroni/Holm/BH-FDR selection table, copy-edit-ready APA sentence templates, and the text/table/figure division of labor.
- `references/artifact-contracts.md` — `analysis-plan` input plus `cleaning-manifest` and `stat-results` handoff rules. Read when artifacts cross skill boundaries.
- `references/regression-and-multilevel-models.md` — model routing, restricted formulas, interpretation boundaries, and required diagnostics.
- `references/survival-time-series-and-panel.md` — estimands, assumptions, CLI examples, output contracts, and explicit Cox/competing-risk/time-series/panel boundaries.
- `references/resampling-robust-and-bayesian.md` — resampling units, robust-estimand and prior boundaries, output semantics, and examples.
- `references/model-diagnostics.md` — diagnostics routing, interpretation limits, and required follow-up.
