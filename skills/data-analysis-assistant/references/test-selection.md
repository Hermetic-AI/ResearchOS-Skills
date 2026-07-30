# Statistical Test Selection & Reporting Rules

Read this file **only when the analysis reaches the test-selection step** (after profiling). Do not load it during data profiling.

## Decision tree

### 1. Comparing two groups (continuous outcome)

1. Check normality per group: `--test shapiro` (p > 0.05 → approximately normal; small n < 30 makes Shapiro unreliable — also inspect histograms/Q-Q plots).
2. Check variance homogeneity: `--test levene` (p > 0.05 → variances approximately equal).
3. Select:
   - Normal **and** equal variance → `--test ttest` (Student's t-test, `scipy.stats.ttest_ind`)
   - Normal **but** unequal variance → `--test ttest --welch` (Welch's t-test, `ttest_ind` with `equal_var=False`)
   - Non-normal → `--test mannwhitney` (Mann-Whitney U, `scipy.stats.mannwhitneyu`)
   - **Paired samples** (same subjects, before/after) → `--test ttest --paired` (`scipy.stats.ttest_rel`) if differences are normal; otherwise report as Wilcoxon (not bundled — use `scipy.stats.wilcoxon` manually) and note the deviation.

### 2. Comparing three or more groups (continuous outcome)

- All groups normal and variances equal → `--test anova` (one-way ANOVA, `scipy.stats.f_oneway`); if significant, follow up with a post-hoc test (Tukey HSD) and apply multiple-comparison correction.
- Non-normal → `--test kruskal` (Kruskal-Wallis, `scipy.stats.kruskal`); if significant, follow up with pairwise Mann-Whitney U tests **with correction**.

### 3. Categorical association (contingency table)

- `--test chi2` (chi-square test of independence, `scipy.stats.chi2_contingency`).
- If more than 20% of cells have expected frequency < 5, or any expected frequency < 1 → use `--test fisher` instead (`scipy.stats.fisher_exact`; 2x2 tables, for larger tables state the limitation).
- Effect size: Cramer's V (from `stat_test.py` output).

### 4. Correlation (two continuous variables)

- Both approximately normal → `--test pearson` (`scipy.stats.pearsonr`).
- Non-normal, ordinal, or rank data → `--test spearman` (`scipy.stats.spearmanr`).

## Effect-size interpretation (rough thresholds)

| Effect size | Small | Medium | Large |
|---|---|---|---|
| Cohen's d | 0.2 | 0.5 | 0.8 |
| eta squared (η²) | 0.01 | 0.06 | 0.14 |
| Cramer's V (df=1) | 0.1 | 0.3 | 0.5 |
| r (Pearson/Spearman) | 0.1 | 0.3 | 0.5 |

Always report the effect size alongside p. A tiny effect can be "significant" with large n; a large effect can be "non-significant" with small n.

For the CI of an effect size not supplied by `stat_test.py`, use the matching seeded bootstrap command, for example:

```bash
python scripts/effect_size_ci.py data.csv --metric cohens-d --value score --group arm --reps 2000 --seed 42
```

Supported metrics are `cohens-d`, `rank-biserial`, `eta-squared`, `cramers-v`, `pearson`, and `spearman`. The output is a `stat-results` artifact with an effect-size interval; resample clusters, pairs, or time blocks only with a design-aware method instead of this row-wise helper.

## Reporting wording rules

These rules are mandatory in every conclusion.

1. **Significant (p < 0.05)**: "The difference is statistically significant (test name, statistic = X.XX, p = 0.XXX, effect size d = 0.XX)" — include the direction of the difference (which group is higher).
2. **Not significant (p ≥ 0.05)**: "No statistically significant difference was found (p = 0.XXX)" — **immediately add the disclaimer**: "Note: not significant does not mean no difference; it may be due to insufficient sample size leading to inadequate statistical power, or the effect itself is small." Never write "the two groups have no difference" or "proves there is no difference".
3. **Multiple comparisons**: whenever more than one test is run on the same dataset (multiple metrics, pairwise follow-ups, subgroup analyses), remind the user to apply a correction — Bonferroni (conservative) or Benjamini-Hochberg FDR (common). Even if no correction was applied this time, state it as a limitation: "No multiple-comparison correction was applied this time; results should be treated as exploratory conclusions."
4. **Non-parametric fallback**: when normality fails and you switch to Mann-Whitney/Kruskal/Spearman, state why in one sentence: "Because the data do not meet the normality assumption (Shapiro-Wilk p = 0.XXX), a non-parametric test was used instead ..."
5. **Effect size framing**: report magnitude using the thresholds above, e.g. "The effect size is medium (Cohen's d = 0.55)".
6. Alpha defaults to 0.05; if the user specified a different alpha or a one-sided test, record it explicitly.
