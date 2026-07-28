# Statistical Test Selection & Reporting Rules

Read this file **only when the analysis reaches the test-selection step** (after profiling). Do not load it during data profiling.

## Decision tree

### 1. Comparing two groups (continuous outcome)

1. Check normality per group: `shapiro` (p > 0.05 → approximately normal; small n < 30 makes Shapiro unreliable — also inspect histograms/Q-Q plots).
2. Check variance homogeneity: `levene` (p > 0.05 → variances approximately equal).
3. Select:
   - Normal **and** equal variance → `ttest_ind` (Student's t-test, `equal_var=true`)
   - Normal **but** unequal variance → `ttest_ind` with `equal_var=false` (Welch's t-test)
   - Non-normal → `mannwhitneyu` (Mann-Whitney U)
   - **Paired samples** (same subjects, before/after) → `ttest_rel` if differences are normal; otherwise report as Wilcoxon (not bundled — use `scipy.stats.wilcoxon` manually) and note the deviation.

### 2. Comparing three or more groups (continuous outcome)

- All groups normal and variances equal → `f_oneway` (one-way ANOVA); if significant, follow up with a post-hoc test (Tukey HSD) and apply multiple-comparison correction.
- Non-normal → `kruskal` (Kruskal-Wallis); if significant, follow up with pairwise Mann-Whitney U tests **with correction**.

### 3. Categorical association (contingency table)

- `chi2_contingency` (chi-square test of independence).
- If more than 20% of cells have expected frequency < 5, or any expected frequency < 1 → use `fisher_exact` instead (2x2 tables; for larger tables state the limitation).
- Effect size: Cramer's V (from `stat_test.py` output).

### 4. Correlation (two continuous variables)

- Both approximately normal → `pearsonr`.
- Non-normal, ordinal, or rank data → `spearmanr`.

## Effect-size interpretation (rough thresholds)

| Effect size | Small | Medium | Large |
|---|---|---|---|
| Cohen's d | 0.2 | 0.5 | 0.8 |
| eta squared (η²) | 0.01 | 0.06 | 0.14 |
| Cramer's V (df=1) | 0.1 | 0.3 | 0.5 |
| r (Pearson/Spearman) | 0.1 | 0.3 | 0.5 |

Always report the effect size alongside p. A tiny effect can be "significant" with large n; a large effect can be "non-significant" with small n.

## Reporting wording rules (报告话术规范)

These rules are mandatory in every conclusion.

1. **Significant (p < 0.05)**: 「差异具有统计学意义（检验名, 统计量 = X.XX, p = 0.XXX, 效应量 d = 0.XX）」 — include the direction of the difference (which group is higher).
2. **Not significant (p ≥ 0.05)**: 「未发现统计学显著差异（p = 0.XXX）」 — **immediately add the disclaimer**: 「注意：不显著不等于无差异，可能是样本量不足导致统计功效（power）不够，或效应本身较小。」Never write 「两组无差异」 or 「证明了没有区别」.
3. **Multiple comparisons**: whenever more than one test is run on the same dataset (multiple metrics, pairwise follow-ups, subgroup analyses), remind the user to apply a correction — Bonferroni (conservative) or Benjamini-Hochberg FDR (common). Even if no correction was applied this time, state it as a limitation: 「本次未进行多重比较校正，结果应视为探索性结论。」
4. **Non-parametric fallback**: when normality fails and you switch to Mann-Whitney/Kruskal/Spearman, state why in one sentence: 「因数据不满足正态性假设（Shapiro-Wilk p = 0.XXX），改用非参数检验 …」
5. **Effect size framing**: report magnitude using the thresholds above, e.g. 「效应量为中等（Cohen's d = 0.55）」.
6. Alpha defaults to 0.05; if the user specified a different alpha or a one-sided test, record it explicitly.
