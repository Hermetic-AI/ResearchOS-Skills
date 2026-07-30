# Reporting Statistical Results (APA 7th + Journal Practice)

Read this file **when results are finalized and need to be written up** (user report, results section, abstract numbers). Do not load it during profiling or test selection. For wording templates see `references/test-selection.md`; this file governs *format and completeness*.

## 1. The completeness checklist — every inferential claim needs all of

1. Test name + design info (paired/independent, one/two-sided if not the default).
2. Test statistic with degrees of freedom: `t(58)`, `F(2, 87)`, `χ²(1, N = 120)`, `U`, `r(98)`.
3. **Exact p-value** (see §2).
4. **Effect size with its confidence interval** (see §3). p alone is not a result.
5. Descriptive statistics per group (M, SD or Mdn, IQR; n per group) — before or alongside the inferential line.
6. Alpha and any correction applied (§4), stated once per family of tests.

Missing any of these → the sentence is not submittable.

## 2. p-values: exact vs threshold

- **Report exact p to 2–3 decimals**: `p = .023`, `p = .37`. Round to 2–3 significant digits; `p < .001` only when p is genuinely below .001 (never write `p = .000` — it is impossible).
- **No "asterisk only" reporting**: `p < .05` without the exact value hides the difference between p = .049 and p = .0009. Tables may add stars *in addition to* exact values, with a footnote defining them.
- APA style omits the leading zero for statistics bounded by 1: `p = .03`, `r = .42` — but keeps it for unbounded ones: `d = 0.45` is acceptable, journal permitting; stay consistent within one paper.
- **Do not call p between .05 and .10 "marginally significant" / "a trend"** as evidence — report the exact p, the effect size with CI, and let the reader judge. If the study was powered for a smaller effect, say so as a limitation.
- p ≥ alpha wording: "was not statistically significant" — never "no difference" or "no effect" (see `test-selection.md` wording rules).

## 3. Effect sizes and confidence intervals (mandatory)

- **Which one**: Cohen's d (t-tests), η² or partial η² (ANOVA — state which), Cramer's V or odds ratio (categorical), r (correlation), rank-biserial r (Mann-Whitney).
- **Always attach a CI**: "d = 0.55, 95% CI [0.12, 0.98]". An effect size without a CI is as incomplete as p without an effect size. `stat_test.py` emits CIs for mean differences and correlations; for others, bootstrap or cite the software used.
- **Mean differences**: report the raw difference with its CI in original units too ("groups differed by 4.2 points, 95% CI [1.1, 7.3]") — readers think in the measured unit, not in d.
- Standardized effect sizes from tiny samples are unstable; with n < 20/group, emphasize the CI width over the point estimate.

## 4. Multiple comparisons: choosing the correction

Decide **per family of related tests** (one family = one research question's set of tests), and state the method before results.

| Method | Controls | Use when | Trade-off |
|---|---|---|---|
| **Bonferroni** (α/m) | FWER, any dependence | Small m (≤ ~5–10), confirmatory claims, pre-registered tests | Most conservative; with m > 20 power collapses |
| **Holm** (step-down) | FWER, any dependence | Same situations as Bonferroni — **always ≥ Bonferroni in power, so prefer it as the default FWER method** | Slightly more computation; per-comparison adjusted p varies |
| **BH (Benjamini-Hochberg FDR)** | Expected false-discovery proportion | Large m (omics, many metrics, voxel/pixel tests), exploratory screens where some false positives are tolerable | Does NOT control familywise error; findings need replication |
| None (label exploratory) | — | Hypothesis-generating analyses | Mandatory wording: "uncorrected, results are exploratory" |

Rules of thumb:
- One pre-registered primary outcome → no correction needed; say so.
- Pairwise follow-ups after ANOVA/Kruskal → correct within that family (or use Tukey/Dunn which correct internally).
- Correcting across unrelated research questions is wrong — it inflates m and kills power.
- Report *adjusted* p-values and name the method: "Holm-corrected p = .04". `stat_test.py --test adjust --method holm` computes Bonferroni / Holm / BH from a p-value list.
- If raw and corrected verdicts differ, report both — that is the honest sensitivity statement.

## 5. APA-7 format templates (copy-edit ready)

- Two groups: `An independent-samples t-test showed higher X in the treatment group (M = 12.4, SD = 3.1) than the control group (M = 9.8, SD = 2.7), t(58) = 3.42, p = .001, d = 0.89, 95% CI [0.35, 1.43].`
- ANOVA: `X differed across conditions, F(2, 87) = 5.61, p = .005, η² = .11. Holm-corrected pairwise comparisons showed ...`
- Categorical: `Group membership was associated with response, χ²(1, N = 120) = 6.73, p = .009, V = .24; odds ratio = 2.8, 95% CI [1.3, 6.1].`
- Correlation: `X correlated positively with Y, r(98) = .42, p < .001, 95% CI [.25, .57].`
- Non-significant: `..., t(58) = 1.21, p = .231, d = 0.31, 95% CI [-0.20, 0.82]. Given the sample size, the study had 80% power to detect d ≥ 0.74 only; smaller effects cannot be ruled out.`
- Statistics are italicized in manuscripts (t, F, p, d, r, M, SD, n/N); spaces around `=`; round consistently (df exact, statistics 2 decimals).

## 6. Division of labor: text vs tables vs figures

- **Text**: the story — direction, magnitude, and the *key* statistics. Never dump every number of every test into prose; one sentence per claim.
- **Table**: when > ~4 groups/comparisons or many parallel tests (e.g. 10 metrics × 2 groups). Table columns: variable, group descriptives, statistic, df, exact p, effect size [CI]. Table footnote carries alpha, correction method, and n.
- **Figure**: for distributions, interactions, and effect magnitudes (forest plots for CIs). A figure must add information the table cannot (shape, spread, overlap) — do not use a bar chart to restate two means; and never use figures to hide non-significant results reported nowhere else.
- Each number appears **once**: in text OR table OR figure, cross-referenced — not duplicated.
- Descriptive statistics (M ± SD, n) belong in a table whenever there are ≥ 3 groups; the text then carries only inferential results.
