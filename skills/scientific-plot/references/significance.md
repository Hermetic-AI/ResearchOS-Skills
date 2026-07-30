# Significance Stars — Rules, Tests, and Bracket Layout

## Star rules

| p-value | Symbol |
|---|---|
| p < 0.001 | `***` |
| p < 0.01 | `**` |
| p < 0.05 | `*` |
| p ≥ 0.05 | `ns` |

Conventions: brackets are drawn only between compared groups; `ns` is shown by default (reviewers ask for it) — hide with `--hide-ns`. Always state the test and alpha in the caption.

## Test selection (script behavior with `--compare-groups`)

- **Two groups**: Shapiro-Wilk normality on both (needs n ≥ 3). Both normal → independent `ttest_ind`; otherwise `mannwhitneyu`. Override with `--test ttest|mannwhitney`.
- **Three or more groups**: overall `f_oneway` (one-way ANOVA) is recorded in the stats JSON; pairwise two-sample t-tests then run **regardless of whether the omnibus p is significant** — check the omnibus p before interpreting the stars. `--control NAME` compares every group against the control, otherwise all pairs (capped at 6 brackets to keep the figure readable; refine the pair list by editing the CSV or running twice with subsets).
- Paired designs, Welch correction, Kruskal-Wallis and post-hoc tests are **not** in this script — that is data-analysis-assistant territory; import its verdicts and pass stars manually with `--stars "A>B:**;A>C:ns"` when the test must differ.

## Multiple comparisons — Holm reminder

With k pairwise tests on the same dataset, raw p-values inflate false positives. The script reports raw p in the stats JSON and prints a warning when k > 1; **apply Holm correction before choosing stars for publication**: sort p ascending, compare pᵢ against α/(k−i), stop at the first non-rejection. The `adjust` subcommand of data-analysis-assistant's `stat_test.py` does this from a p-value list. State the correction in the caption.

## Bracket layout algorithm

1. Base height = the global highest point of ALL error bars (max of mean + error over every drawn group), not per-pair.
2. Compute the data y-range R of everything drawn.
3. First bracket level sits at `global_top + 0.05·R`; every further level adds `0.05·R`.
4. Pairs are sorted by horizontal span (shortest first) and greedily assigned the lowest level whose x-interval does not collide with an already-placed bracket at that level — guarantees no overlap.
5. Bracket: horizontal line at the level with short vertical ticks down at both ends; star text centered above the line.
6. The y-axis upper limit is extended to fit the highest level + text.

The 5%-of-range step is a readability heuristic, not a standard; adjust `--star-step` if labels collide with very tall error bars.
