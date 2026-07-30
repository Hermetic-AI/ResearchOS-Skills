# Reading Workflows: Triage / Deep Read / Critical Review

Used by the `literature-reader` skill. Read the section matching the depth the
user asked for — do not load all three unless the user is escalating depth
mid-session (triage → deep read is a common path).

Depth is a budget decision, not a virtue. A 200-paper survey phase runs on
triage; the 10 papers a thesis is built on deserve critical review. Say which
depth you are operating at so the user can correct it.

---

## 1. Triage (rapid screening) — 3–8 minutes per paper

**Goal**: a keep / skim-later / drop verdict plus a two-line justification.
Output is a decision, not a note.

### Procedure
1. Title + abstract. Extract: problem, claimed method class, claimed result.
2. Figures and tables only — captions first, then the one figure the authors
   put first (it is almost always the method overview or the headline result).
3. First and last paragraph of the conclusion (limitations often hide in the
   last one).
4. Verdict against the user's current question:
   - **Keep (deep-read candidate)**: directly addresses the user's question, or is a
     baseline/foundation the user's work must cite and beat.
   - **Skim-later**: same area, useful for related-work padding, no deep read
     needed now.
   - **Drop**: different problem, or a known-superseded method, or a venue/
     quality signal too weak to trust (see red flags below).

### Triage checklist
- [ ] Problem matches the user's question? (topic overlap ≠ problem overlap)
- [ ] Method class already represented in the kept set? (2nd–3rd paper of a
      class only needs triage unless it claims a state change)
- [ ] Venue / year acceptable for the user's purpose? (a 2015 "SOTA" is not SOTA)
- [ ] Is it a survey? If yes: mine its reference list, do not deep-read it as
      a primary source.
- [ ] Reproducibility signal at triage level: code link in abstract/footnote?

### Time traps
- Reading the introduction linearly — it is marketing; skip to contributions.
- Triage-reading a paper you already decided to deep-read. Decide, then switch
  mode.
- Keeping everything "just in case". A keep-rate above ~40% of a search result
  set means the search query was too broad; tighten it instead.

---

## 2. Deep read — 1–3 hours per paper

**Goal**: a structured note (per `note-template.md`) good enough that the user
can defend the paper in a group meeting without reopening the PDF.

### Procedure
1. First pass (15 min): triage pass + section headings + all figures. Write
   down 3 questions the paper must answer (e.g. "how is X disentangled from
   Y?", "where does the training signal come from?").
2. Second pass: method section *with the questions in hand*. Reconstruct the
   pipeline on paper: input → transformation → output. If you cannot draw it,
   you have not read it.
3. Third pass: experiments. For each table: what is compared, what is held
   fixed, what would make the claim collapse. Identify the *load-bearing
   experiment* — the one table/figure without which the paper's thesis fails.
4. Fill the note template. Then write the one-paragraph "explain to advisor"
   summary from memory; check against the paper; fix gaps.

### Deep-read checklist
- [ ] Can state the technical gap (not just the topic) in one sentence.
- [ ] Can name the single design choice the method stands or falls with.
- [ ] Can name the load-bearing experiment and its comparator.
- [ ] Key numbers quoted with their baselines, not alone.
- [ ] At least one limitation found that the authors did not state.
- [ ] Reusable resources verified (code link exists, license checked if the
      user will build on it).

### Time traps
- Highlighting without reconstructing. If the note's method section paraphrases
  the paper's section order, it was copied, not read.
- Equation-by-equation reading on the first pass — most notation is defined
  late; read for structure first, return for symbols.

---

## 3. Critical review — for papers the thesis depends on

**Goal**: a verdict on whether the paper's claims can bear the weight the user
plans to put on them (as foundation, baseline, or target of critique).

Run the deep-read procedure first, then the audit below. Every checkpoint is a
common failure point — check it even when the paper looks strong.

### 3.1 Experiment audit
- **Baseline fairness**: are baselines tuned with the same budget (search
  space, epochs, data augmentation) as the proposed method? A baseline quoted
  from the baseline's original paper — trained on a different split or
  backbone — is not a comparison, it is a citation.
- **Statistical vs practical significance**: a 0.2-point gain with no variance
  reported is noise until proven otherwise. Look for: multiple seeds, std/CI,
  significance tests. Also check the reverse: a "significant" p-value on a
  0.1% absolute gain may be statistically real and practically irrelevant.
- **Sample size / power** (empirical and biomedical work): is n justified
  (power analysis, or at least comparable to prior work)? Underpowered
  studies produce effects that fail to replicate; n=12 fMRI studies and
  single-cohort clinical results are the classic cases.
- **Data leakage**: does anything from the test set influence training or
  model selection? Common disguises: preprocessing/normalization fit on the
  full dataset before splitting; feature selection on all data; hyperparameter
  tuning on the test set; near-duplicate samples across the split (same
  patient, same source text, same molecule scaffold).
- **Evaluation protocol**: is the metric appropriate (accuracy on imbalanced
  data is the canonical trap)? Is the test set actually out-of-distribution
  relative to training, or a random split of the same distribution?

### 3.2 Reproducibility red flags
- No code, no data, and "available upon request" — treat claimed numbers as
  unverifiable; cite with that caveat.
- Hyperparameters missing or "in the appendix" that does not exist.
- Headline number appears only in a figure with no table (cannot be checked,
  easy to misread).
- Claims scope far beyond evidence: trained on one dataset, claimed as
  "general"; English-only experiments, claimed as "language-independent".
- Ablations that remove exactly one component at a time but never the
  expensive one — the gain may live in the unablated part.
- Reviewer-bait citations: claims of superiority over a method published the
  same month, which the authors cannot seriously have evaluated.

### 3.3 Argumentation audit
- **Claim-evidence match**: map each abstract claim to the table/figure that
  supports it. Abstract claims with no corresponding experiment are the
  single most common overreach.
- **Assumption load**: list the assumptions the method needs (i.i.d. data,
  labels available, stationarity, linearity). For each, ask whether it holds
  in the *user's* setting — a paper can be correct and still inapplicable.
- **Threats the authors did not discuss**: selection bias in the dataset,
  construct validity of the proxy metric, ecological validity of the lab
  setting.

### Verdict scale
- **Trustworthy and dependable (load-bearing)**: audits pass; safe to build on.
- **Trustworthy but needs verification (trust but verify)**: minor gaps (missing seeds, no code);
  usable as a baseline, but the user should reproduce the headline number
  before betting a chapter on it.
- **Suspect / questionable**: any of — unfair baselines, leakage signal, n clearly
  underpowered, claims beyond evidence. Cite it if you must, never build on it.

### Time traps
- Symmetric skepticism: auditing a minor citation at the same depth as the
  thesis's core baseline. Critical review is reserved for ≤ ~10 papers.
- Confusing "I found flaws" with "the paper is worthless" — the verdict is
  about *how much weight it can bear*, not about fault-counting.

---

## Depth escalation rules

- Triage → deep read when: the paper is kept AND (it is a likely baseline /
  foundation / direct competitor of the user's work).
- Deep read → critical review when: the user's own argument would collapse if
  this paper were wrong (foundation), or the user plans to outperform it
  (baseline), or to cite its critique (target).
- Never escalate because a paper is merely famous. Fame determines citation
  obligation, not reading depth.
