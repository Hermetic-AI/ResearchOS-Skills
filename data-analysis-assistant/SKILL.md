---
name: data-analysis-assistant
description: Research data analysis assistant covering five capabilities — (1) data profiling with normality hints (schema, descriptive stats, skewness/kurtosis, missing values, outlier flags), (2) rule-based data cleaning with a citable cleaning log (missing-value mechanism MCAR/MAR/MNAR decisions, dedupe, unit/coding consistency, date parsing, outlier keep/correct/drop/bin decisions), (3) automatic statistical test selection and execution (t-test / Welch / Mann-Whitney / ANOVA / Kruskal / chi-square / Fisher / Pearson / Spearman) with effect sizes (Cohen's d, eta squared, Cramer's V) and confidence intervals, (4) multiple-comparison correction (Bonferroni / Holm / BH-FDR), and (5) APA-7-style statistical reporting guidance (exact p, effect size + CI mandatory, text/table/figure division of labor). Use when the user asks to 分析实验数据/数据画像/数据清洗/异常值处理/选统计检验/显著性检验/算p值/效应量/多重比较校正/报告统计结果 ("analyze my data", "which statistical test should I use", "clean this CSV", "check for outliers", "run a significance test", "adjust p-values", "how do I report this result", "实验数据该用什么检验", "帮我看看数据质量", "p值校正"). NOT for literature reading or summarizing papers — use literature-reader instead; NOT for structuring findings into a knowledge graph — use knowledge-graph-builder instead; NOT for designing experiments or hypotheses before data exists — use experiment-designer instead; NOT for writing paper prose around results — use paper-writing-assistant instead; NOT for re-running published code to reproduce results — use reproduction-assistant instead.
---

# Data Analysis Assistant (数据处理分析)

For researchers (grad students) working with experimental data. Reports to the user are in Chinese by default; content written into artifacts follows the artifact's language.

**Global conventions**
- **Report first, modify later**: produce findings and suggestions; never overwrite the user's raw data files. Cleaning runs through `scripts/clean_csv.py` with an explicit rules file, always writing a new `*_clean.csv` plus a cleaning log.
- **Every statistical conclusion must include**: test name, statistic, exact p-value, significance verdict at alpha = 0.05, effect size, and confidence interval when available. Follow the wording rules in `references/test-selection.md` (notably: non-significant ≠ no difference).
- **Reproducibility**: prefer the bundled scripts over ad-hoc analysis; when randomness is involved, always pass a fixed seed.

## Capabilities overview

| # | Capability | Entry point |
|---|------------|-------------|
| 1 | Data profiling & normality hints | `python3 scripts/profile.py data.csv --format both` |
| 2 | Data cleaning with citable log | `python3 scripts/clean_csv.py data.csv rules.json --out clean.csv` |
| 3 | Statistical test selection | decision tree in `references/test-selection.md` |
| 4 | Test execution + effect size + CI | `python3 scripts/stat_test.py data.csv --test <name> ...` |
| 5 | Multiple-comparison correction | `python3 scripts/stat_test.py --test adjust --method holm --pvalues "p1,p2,..."` |

## When to use / not use

Use when the user has data (CSV) and asks about data quality, cleaning, outliers, which test to run, p-values, effect sizes, p-value correction, or how to report statistics. Do **not** use for paper prose, citation checks, literature reading, experiment design, or figure beautification (those belong to the sibling skills listed in the description).

## Workflow

1. **Profile first (always)**: run
   `python3 scripts/profile.py <file.csv> --format both`
   Per-column schema (numeric/categorical/datetime/text), descriptive stats, skewness/kurtosis with a normality hint (screen only — confirm with Shapiro-Wilk), missing counts, suspected outliers (IQR and z-score), duplicates/constant columns. Use `--out report.md --format md` to save the report.
2. **Clean if needed**: read `references/data-cleaning.md` — **only when profiling reveals quality problems (missing values, duplicates, inconsistent units/codings, date issues, outliers); skip for a clean dataset**. It gives the decision rules: MCAR/MAR/MNAR discrimination before choosing an imputation strategy, duplicate handling, unit/coding/date consistency checks, and the outlier keep/correct/drop/bin decision tree with the justification each action must record. Agree the rules with the user, write them as a JSON rules file, then run
   `python3 scripts/clean_csv.py <file.csv> rules.json --out <clean.csv> --log cleaning_log.md`
   The log records per-step affected row counts and reasons — citable in the Methods section.
3. **Choose the test**: read `references/test-selection.md` — **only when the analysis reaches test selection**. Confirm the research question, group/value columns, independent vs paired samples with the user. Apply the decision tree (normality via Shapiro, variance homogeneity via Levene).
4. **Run the test**: requires scipy + numpy — install once with `pip install scipy numpy`. Then e.g.
   `python3 scripts/stat_test.py <clean.csv> --test ttest --value score --group group_col`
   Output is JSON (`--format json` default) or Markdown (`--format md`) with statistic, exact p, effect size, 95% CI (ttest/pearson; `--ci` changes the level), and a fill-in Chinese conclusion template.
5. **Correct for multiple comparisons** whenever more than one test ran on the same dataset:
   `python3 scripts/stat_test.py --test adjust --method holm --pvalues "0.01,0.04,0.20" --labels "m1,m2,m3"`
   Method choice (Bonferroni vs Holm vs BH-FDR) per the table in `references/reporting.md`.
6. **Report in Chinese**: read `references/reporting.md` — **only when writing up results**. It enforces the APA-7 completeness checklist (statistic + df, exact p, effect size with CI, descriptives, correction statement), exact-vs-threshold p rules, and the text/table/figure division of labor. Combine profile context + test results into a short report; if the result feeds a paper section, hand the numbers to the user or the paper-writing-assistant skill — this skill does not write paper prose.

## File index

- `scripts/profile.py` — zero-dependency (stdlib only) CSV profiler: schema, descriptive stats with skewness/kurtosis and a normality hint, missing values, IQR/z-score outlier flags, duplicate/constant-column checks. JSON + Markdown output, `--out` writes a report file.
- `scripts/clean_csv.py` — zero-dependency declarative CSV cleaner: applies a JSON rules file (dedupe / fill_missing / drop_outliers / convert_type, each with a required rationale) and emits a cleaned CSV plus a per-step cleaning log (rows/values affected, reasons) for the Methods section.
- `scripts/stat_test.py` — scipy/numpy test dispatcher: ttest_ind / ttest_rel (paired) / mannwhitneyu / f_oneway / kruskal / chi2_contingency / fisher_exact / pearsonr / spearmanr, assumption checks (shapiro, levene), effect sizes (Cohen's d, eta squared, Cramer's V), confidence intervals (ttest, pearson), and an `adjust` subcommand for multiple-comparison correction (bonferroni / holm / fdr_bh) from a p-value list. Emits statistic + exact p + effect size + CI + Chinese conclusion template.
- `references/test-selection.md` — test selection decision tree (two-group / three-or-more / categorical / correlation paths), effect-size interpretation thresholds, and reporting-wording rules (disclaimers, multiple-comparison reminders).
- `references/data-cleaning.md` — cleaning decision checklist: MCAR/MAR/MNAR discrimination tests and strategy selection, duplicate-record handling, unit/coding/date consistency, outlier keep/correct/exclude/winsorize decision tree with the justification each action must record, and Methods-section reporting of cleaning.
- `references/reporting.md` — statistical reporting standards: APA-7 completeness checklist, exact p vs threshold rules, mandatory effect size + CI, Bonferroni/Holm/BH-FDR selection table, copy-edit-ready APA sentence templates, and the text/table/figure division of labor.
