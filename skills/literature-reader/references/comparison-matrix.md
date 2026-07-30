# Comparison Matrix: Dimension Library and Assembly Rules

Used by **Function 2** of the `literature-reader` skill. Read this file when
choosing comparison dimensions and assembling the matrix; `gap-analysis.md`
assumes the matrix was built by these rules.

The matrix is the deliverable — its job is to make clusters, conflicts, and
empty regions visible at a glance. Everything here serves that one job.

---

## 1. Core dimensions (all disciplines)

| Dimension | What goes in the cell | Notes |
|---|---|---|
| Question | one sentence | the *technical* gap addressed, not just the topic |
| Method | method class + key design | e.g. "GNN + sparse attention" |
| Data | dataset names, size, domain | shared datasets → cluster signal |
| Main claim | one sentence, with number | always quote with comparator |
| Evidence | simulation / empirical / theoretical / benchmark / review | mark `(abstract-only)` if abstract-only |
| Limitation | most important caveat, one line | your judgment, not only the authors' |
| Relevance | high / medium / low + one phrase | relative to the user's project |

## 2. Discipline-specific dimension library

Pick the core set + 2–4 from the matching column. More than ~10 columns makes
the matrix unreadable — cut before adding.

### ML / CS
- **Compute**: training/inference cost, hardware, parameters/FLOPs —
  papers hiding cost differences often win on budget, not method.
- **Artifacts**: code / weights / data released? license?
- **Baseline strength**: tuned contemporary baselines vs quoted old
  numbers — the cheapest way results are inflated.
- **Protocol**: benchmark + split + metric; watch for
  benchmark-specific tuning.

### Biomedical / experimental sciences
- **n / power**: cohort size, sites (single vs multi-center),
  power analysis present?
- **Setting**: in vitro / in vivo / clinical phase; model organism;
  apparatus.
- **Controls**: placebo / active control / standard-of-care;
  blinding and randomization where applicable.
- **Endpoints**: primary endpoint and whether it is clinical or a
  surrogate/proxy.

### Social sciences
- **Population**: who, how sampled, WEIRD-sample warning, response
  rate.
- **Identification**: RCT / IV / DID / RDD / correlational — the
  causal-claim ceiling is set here.
- **Measurement**: instrument, reliability/validity evidence, proxy vs
  construct gap.
- **Robustness**: alternative specifications, sensitivity analyses.

### Engineering / applied
- **Conditions**: operating range, load, environment, scale (lab vs
  pilot vs field).
- **Performance**: the standard quantity in the field + units; a
  matrix without units is unusable.
- **Constraints**: cost, energy, weight, latency, safety standards met.
- **Validation**: simulation-only vs hardware prototype vs field
  trial — the biggest confidence gap in the column.

### Humanities (adjust core set)
- Replace Data with **Corpus**: sources, archives, editions.
- Replace Method with **Approach**: close reading / discourse analysis /
  quantitative / comparative.
- Add **Framework**: the theoretical lens; conflicting lenses on the
  same corpus are the humanities' conflict cluster.

---

## 3. Assembling the matrix from reading notes

If Function-1 notes exist, cells auto-align by note field — do not re-read the
papers:

| Matrix column | Note field source |
|---|---|
| Question | note §1, last sentence (technical gap) |
| Method | note §2, the "key design" line |
| Data | note §4 Data bullet |
| Main claim | note §4 Key results (number + comparator only) |
| Evidence | derived: §4 contents + `(abstract-only)` if no full read |
| Limitation | note §5 "My assessment" first item |
| Relevance | note header one-liner vs the user's project |

Papers without notes: fill from abstract + figures only, and mark the
evidence cell `(abstract-only)`. Never upgrade an abstract-only cell to look like a
deep-read cell — sparsity is honest information.

Cell discipline:
- One line per cell; if a cell needs two lines, the column is wrong or the
  note was too vague.
- `?` = not determinable from available text. Acceptable; a fabricated cell
  is not.
- Numbers carry their comparator and unit: "72.1 vs 70.3 (Acc, %)".

---

## 4. Reading the finished matrix (cross-row observation block)

After the table, always write a short synthesis covering:
- **Clusters**: which papers share method class or dataset — they answer one
  question redundantly; cite the best, skim the rest.
- **Conflicts**: see rules below.
- **Load-bearing citations**: for each claim the user will reuse, which single
  row is the strongest support.
- **Column-wide patterns**: e.g. "all papers evaluate on the same dataset" — these feed
  directly into gap analysis.

### Conflict-handling rules
- Never average conflicting claims. Mark both cells `⚠️conflict` and diagnose in
  the cross-row observation block.
- Diagnose before judging — check in order:
  1. **Different data/split**: same dataset name, different split or version?
  2. **Different metric/protocol**: same metric name, different computation?
  3. **Different setting/conditions**: population, dose, hardware, scale.
  4. **Different method version**: citing each other's numbers across
     versions without re-running.
- If 1–4 explain the difference, it is not a scientific conflict — record the
  boundary condition each claim holds under.
- If unexplained after 1–4, the conflict is a **prime gap candidate**: mark it
  for Function 3. Unresolved contradictions are the highest-value gaps because
  resolving them is guaranteed publishable interest.
- When citing a conflicted claim later, cite both papers and the boundary
  condition, not the number you prefer.
