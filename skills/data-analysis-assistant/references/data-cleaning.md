# Research Data Cleaning Decision Checklist

Read this file **when the profiling step reveals data-quality problems** (missing values, duplicates, inconsistent units/codings, date issues, outliers) and the user wants to clean data before analysis. Do not load it for a clean dataset.

**Golden rule**: cleaning is destructive and reviewers can ask about it. Every action must be (1) decided by a rule below, (2) executed by a re-runnable script (prefer `scripts/clean_csv.py` over hand-editing), and (3) recorded with row counts so it can be quoted verbatim in the Methods section. Never overwrite the raw file — write a new `*_clean.csv` and keep the cleaning log.

## 1. Missing values: diagnose the mechanism BEFORE choosing a fix

The choice of method depends on *why* data are missing, not how much is missing.

### Discriminating MCAR / MAR / MNAR

| Mechanism | Definition | How to check (executable) | Example |
|---|---|---|---|
| **MCAR** (missing completely at random) | Missingness unrelated to any data | Split rows into missing-vs-not on column X; compare distributions of *other* columns (t-test / chi-square). No differences → consistent with MCAR. | Device battery died at random; sample vial dropped. |
| **MAR** (missing at random) | Missingness depends on *observed* variables | The group comparison above shows differences (e.g. older subjects miss follow-up more), but within covariate strata missingness looks random. | Older participants skip the optional questionnaire. |
| **MNAR** (missing not at random) | Missingness depends on the *unobserved* value itself | Cannot be proven from data. Suspect when: missingness is extreme at scale ends, dropouts cluster after bad outcomes, or domain logic says so. Document the suspicion explicitly. | Patients with severe symptoms stop reporting pain scores. |

**Practical test**: run `stat_test.py --test ttest/chi2` comparing an auxiliary column between rows where the target is present vs missing (add a temporary 0/1 indicator column). p < 0.05 → reject MCAR.

### Strategy selection by mechanism and missing rate

- **< 5% missing, any mechanism** → complete-case (listwise deletion) is usually fine; report the n dropped.
- **MCAR/MAR, 5–40%**:
  - Mean/median imputation is acceptable only for *covariates* in exploratory analysis — it distorts variance and biases correlations toward zero. Never impute the *primary outcome* with a point value.
  - Preferred: multiple imputation (`mice` in R, `IterativeImputer` in sklearn) — beyond the bundled scripts; state the method and number of imputations in Methods.
  - Categorical: add an explicit `"missing"` level rather than imputing, if "unknown" is informative.
- **MNAR or > 40% missing** → imputation cannot rescue the column. Options: drop the column, restrict the analysis population, or model the missingness (selection/pattern-mixture models). Escalate to the user — this is a design decision, not a cleaning decision.
- **Never**: impute before train/test split in predictive work (leakage); impute group labels; silently treat `0`/`999`/`-1` as real values when they are sentinel codes (recode to missing first).

**Report wording**: 「共 N 条记录，其中 k 条因 X 变量缺失被剔除（占比 x%），缺失机制经检验与 MCAR 一致/存在 MAR 迹象……」

## 2. Duplicate records

- **Exact duplicates** (all columns equal, `profile.py` reports `dup_rows`): almost always an export/join artifact → dedupe, keep first. Exception: legitimate repeated measures with no time/ID column — confirm with the user before deleting.
- **Key duplicates** (same subject/ID, different values): do NOT delete blindly. Decide by cause:
  - Re-import of the same record with updated fields → keep latest (needs a timestamp column).
  - Longitudinal data mis-shaped as wide → reshape, not dedupe.
  - Genuine double-entry → resolve against the source instrument; if unresolvable, drop both and log.
- After dedupe, always re-check row count against the expected enrollment/collection log.

## 3. Unit & coding consistency

- **Units**: scan numeric columns for bimodal clusters ~a constant factor apart (e.g. kg vs lb ≈ 2.205, cm vs m = 100). Check against plausible ranges (human height 0.5–2.5 m; if max is 180 the unit is cm). Convert everything to the unit stated in the protocol and record the conversion factor applied.
- **Categorical codings**: normalize case, whitespace, and synonyms (`"Male"`, `"male"`, `"M"`, `"1"`) to one controlled vocabulary. Build the mapping table explicitly and keep it — it belongs in supplementary material.
- **Sentinel values**: `-99`, `-999`, `999`, `0`, `"N/A"` used as missing codes must be recoded to missing *before* any statistics; `profile.py` treats common string sentinels as missing but cannot know numeric sentinels — look for them as spikes at extremes in the min/max of the profile.
- **Yes/No and boolean codings**: pick one representation (`0/1`) and convert; mixed `"TRUE"/"Yes"/1` breaks group splits.

## 4. Date parsing

- **Ambiguous formats**: `01/02/2024` is Jan 2 (US) or Feb 1 (EU). Resolve from context: values > 12 in either position disambiguate; otherwise ask the user or check the data-collection locale. State the assumed format in the log.
- **Mixed formats in one column**: parse per-format lists (the profiler's `DT_FORMATS` covers common ISO/US/EU forms); count how many rows matched each format and flag if more than one format matched.
- **Excel serial dates**: numbers around 40000–50000 in a date column are Excel serials (days since 1899-12-30). Convert; do not treat as numeric.
- **Timezone**: for timestamped measurements across sites, normalize to UTC before computing intervals.
- After parsing, sanity-check the range: dates before study start or in the future indicate shifted rows or year typos (e.g. `2024` vs `2042`).

## 5. Outlier decision tree

`profile.py` flags outliers by IQR and z-score rules; **flagging is not a reason to delete**. For each flagged value walk this tree:

1. **Measurement/entry error?** Physically impossible (negative height, pH 74, age 250) → **correct** if the true value is recoverable from source; otherwise **set to missing** (not delete the row — other columns may be valid). Log as "impossible value".
2. **Not from the target population?** (a calibration run, a pilot subject, contamination) → **exclude the row**, record the exclusion criterion as an eligibility rule, not as "outlier removal".
3. **Valid but extreme value from the target population** → **keep**. Then choose the analysis strategy:
   - Use a robust/non-parametric test (Mann-Whitney, Spearman) or report medians/IQR — the standard answer for skewed biological data.
   - Or transform (log/sqrt) if the variable is naturally multiplicative (concentrations, incomes, reaction times).
   - **Winsorize / bin** only when you must keep a parametric model *and* the extremes are trustworthy but uninteresting (e.g. capping follow-up days at the study horizon). Winsorizing percentile and direction must be pre-justified.
4. **Influential-point check**: if the value is kept in a parametric analysis, run the key test with and without it. If the conclusion flips, report both — this is mandatory disclosure.

### Required justification per action (record in the cleaning log)

| Action | Use when | Must record |
|---|---|---|
| Keep (default) | Value plausible | Why the extreme is plausible (domain reason) |
| Correct | True value recoverable | Source of correction (lab sheet, instrument log) |
| Set to missing | Impossible value, row otherwise valid | Rule defining "impossible" (plausible range) |
| Exclude row | Not target population | Eligibility criterion, n excluded |
| Winsorize/bin | Valid extremes, parametric model needed | Percentile/bound, direction, pre-registered rationale |
| Sensitivity analysis | Decision is borderline | Both results (with/without), whether conclusion changes |

**Anti-patterns** (reviewers reject these): deleting outliers until p < 0.05; z-score trimming on skewed data (z assumes normality); applying different rules per group; any outlier action not reported in Methods.

## 6. Cleaning report for the Methods section

Every cleaned dataset ships with a log (the `clean_csv.py` `--log` output) listing, per step: rule, column(s) affected, rows/values changed, rationale. In the paper, condense to 2–4 sentences: initial n → exclusion criteria with counts → imputation/correction methods → final n. A participant/data flow (initial → excluded per reason → analyzed) is strongly recommended.
