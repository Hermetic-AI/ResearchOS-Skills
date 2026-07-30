# Gap Analysis Methodology

Used by the `literature-reader` skill:
- Function 2 does not read this file — comparison dimensions live in
  `references/comparison-matrix.md`.
- Function 3 reads this file **in full**.

Purpose: turn a compared paper set into candidate research gaps with a type
label and an honest feasibility verdict — not a generic "future work" list.

---

## Comparison dimensions

The dimension library, discipline-specific columns, note-to-matrix alignment
rules, and conflict-handling rules live in **`references/comparison-matrix.md`**.
Function 2 reads that file, not this one. Gap identification below assumes a
matrix built by those rules; the signals it scans for (empty regions, `?`
rows, conflict clusters, monoculture) are defined there.

---

## Gap identification workflow (Function 3)

### Step 1 — Dimension scan
Walk the matrix column by column and look for:
- **Empty regions**: a method class never applied to a dataset/setting that
  dominates the matrix.
- **Rows of `?`**: dimensions the whole literature ignores (e.g. nobody reports
  compute cost, nobody evaluates on real users).
- **Conflict clusters**: unresolved contradictions (see above).
- **Monoculture**: one dataset/metric/baseline used by ≥ 70% of papers → results
  may be artifacts of that choice.
- **Recency edge**: the newest 1–2 papers open a direction older ones can't cover.

### Step 2 — Enumerate gap candidates
For each signal from Step 1, write one candidate in the form:
"Under condition X, using method Y to solve problem Z — currently nobody has done it / only W has done it but with flaw Q."
A candidate without an "evidence" pointer to ≥ 2 matrix rows is speculation — keep it
but label it `[weak evidence]`.

### Step 3 — Gap-type classification

| Type | Definition | Example | Typical risk |
|---|---|---|---|
| **Method gap** Method | known problem, but an applicable method family never tried | diffusion models never used for this PDE | may have been tried and failed silently |
| **Data gap** Data | method exists, but no dataset/benchmark for the real setting | models trained on clean data, no noisy-domain benchmark | data collection cost dominates |
| **Population gap** Population | evidence comes from one narrow population; others never studied | findings from WEIRD undergrad samples; models trained on adult data, deployed on children | "new population" alone may be judged incremental |
| **Setting-transfer gap** Setting-transfer | validated in one context, untested where conditions differ | works on English, untested on low-resource languages; lab results, no field trial | "just transfer" may be trivial and unpublishable — must predict *why* transfer should break or hold |
| **Theory gap** Theory | empirical success/failure without explanation | method works, no convergence or mechanism analysis | hard to scope for a master's thesis |
| **Evaluation gap** Evaluation | shared metric/protocol is flawed or gamed | SOTA driven by test-set leakage; accuracy on imbalanced data | community may reject the critique |
| **Negative-result gap** Negative-result | a plausible approach was likely tried and failed, but nothing is published — the failure is invisible | everyone uses method family A for X; nobody reports whether the obvious family B fails | you may be re-walking into the same wall; find indirect evidence first |

Population and setting-transfer gaps look similar but fail differently: a
population gap asks "does the effect exist in group Y at all", a transfer gap
asks "does a validated mechanism survive changed conditions". Keep them
separate — the study designs differ (new sampling vs new environment).

### Step 3b — Evidence requirements per gap type

A gap claim is only as strong as the evidence that the space is truly empty.
Before writing up a candidate, collect the type-specific evidence:

| Type | Required evidence that the gap is real |
|---|---|
| Method gap | The method family appears **nowhere** in the matrix rows, AND a search of the last 2 years' preprints finds no attempt (silently-failed risk). State the method's applicability premise in one line — why it *should* work here. |
| Data gap | ≥ 2 matrix rows work around the missing data (proxies, synthetic substitutes, clean-data-only training) — the workaround is the evidence. A gap nobody works around is usually a gap nobody needs. |
| Population gap | Matrix's population column is ≥ 80% monoculture, AND the excluded population is named explicitly with a reason to expect difference (physiology, culture, age), not just "hasn't been done". |
| Setting-transfer gap | The boundary condition is identified (what exactly changes between contexts: distribution shift, resource constraints, regulation), AND ≥ 1 row documents a failed or degraded transfer in an analogous case. |
| Theory gap | The empirical effect is replicated across ≥ 2 independent rows (an unreplicated effect needs replication, not theory), AND existing theory rows fail to cover it. |
| Evaluation gap | The flaw is demonstrable: you can point to the leakage path, the gaming behavior, or a concrete case where the metric ranks methods wrongly. Suspicion without a mechanism is a complaint, not a gap. |
| Negative-result gap | Indirect evidence only: the approach is conspicuously absent despite being obvious; related papers cite "preliminary experiments did not improve" without details; practitioners' forums/report mention failures. Label `[indirect evidence]` and plan a cheap probe experiment as the first step. |

### Step 3c — Gap statement sentence templates

A usable gap statement names: condition + missing thing + why it matters +
evidence. Templates (fill the slots, cut what does not apply):

- **Method gap**: "For <problem Z>, existing work is all based on <method family A> (matrix rows <…>); no study has yet tried <method family B>. Given <B's applicability premise>, this gap is worth exploring."
- **Data gap**: "Existing <methods/models> are all validated on <ideal-condition data> (rows <…>); there is no public benchmark for <real-world setting>, leading to <specific consequence: unable to evaluate / results overestimated>."
- **Population gap": "Existing evidence comes almost entirely from <population P> (matrix population column <…>); because of <reason to expect difference>, it remains unknown whether the conclusions generalize to <population Q>."
- **Setting-transfer gap": "<Method/effect> has been established in <setting A> (rows <…>), but <setting B> changes <boundary condition>; the analogous case <row X> shows degraded performance after transfer, so the reliability of direct transfer is doubtful."
- **Theory gap": "<Phenomenon> has been replicated by multiple independent studies (rows <…>), but its <mechanism/convergence/boundary> lacks theoretical explanation, limiting <extrapolation/improvement>."
- **Evaluation gap": "The field commonly adopts <protocol/metric> (rows <…>), but a <specific flaw mechanism> exists, leading to <misled conclusion>; a <corrected protocol> is needed for re-evaluation."
- **Negative-result gap": "Although <method family B> is a natural candidate for <problem Z>, the literature reports no attempt (including failure reports); indirect evidence <…> suggests it may fail, but the reason for failure is unknown."

Every statement ends with the evidence pointer; a gap statement without a
matrix-row reference is an opinion.

### Step 4 — Feasibility verdict

Score each candidate on four axes, then give one verdict:

1. **Data availability**: does the needed data/benchmark exist or can it be built within
   the user's timeline? Non-negotiable.
2. **Method maturity**: are the required building blocks published + implemented
   (usable code), or would the user be building infrastructure from scratch?
3. **Effort vs degree requirements**: a master's thesis ≈ 1 well-scoped contribution;
   a PhD chapter ≈ 2–3. Reject candidates needing a new field.
4. **Competition risk**: is an active group obviously working on this (recent preprints,
   workshop tracks)? Crowded ≠ impossible, but the differentiation must be named.

Verdicts:
- **Feasible** — all four axes pass; name the first concrete step.
- **Cautious** — one axis weak; state the mitigation (narrow scope, find collaborator,
  reproduce first).
- **Not recommended** — two+ axes fail; say why plainly. A candid "not recommended" is a valuable
  deliverable, not a failure of the analysis.

### Output format (Chinese report)

```
## Research Gap Analysis Report (based on N-paper comparison matrix)

### Candidate gap 1: <one-sentence description>
- Evidence: matrix rows <A, B, C> — <which column's signal>
- Type: Method gap / Data gap / Population gap / Setting-transfer gap / Theory gap / Evaluation gap / Negative-result gap
- Feasibility: Feasible (or Cautious / Not recommended)
  - Data availability: …
  - Method maturity: …
  - Effort match: …
  - Competition risk: …
- Differentiation from existing literature: <one sentence>
- Suggested first step: <one concrete action completable within two weeks>

(Sorted by feasibility × value; weak-evidence candidates listed last)
```
