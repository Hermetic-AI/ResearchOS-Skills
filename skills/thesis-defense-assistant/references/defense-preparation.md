# Defense Preparation — Questions, Timing, and Coverage

A defense is an examination of the *thesis*, not a performance of the slides.
Preparation therefore centers on the written work and the evidence behind every
contribution. `defense_qa.py` generates preparation prompts and audits coverage;
it does not predict the real examination or supply answers.

## Anatomy of a defense

1. **Presentation** (usually 20–30 min): a narrative of the question, approach,
   core results, and their meaning. It is the opening statement, not the defense
   itself.
2. **Examination** (the bulk of the time): examiners probe the thesis's
   question, methods, evidence, novelty, limitations, and implications.
3. **Deliberation and outcome**: the candidate is usually asked to step out while
   the committee decides.

## Likely question categories

Examiners tend to return to a stable set of themes. Prepare a concise answer and
a verified location for each:

| Category | What is being tested |
|---|---|
| Research question and scope | Why this question, why this framing, what is excluded |
| Methods and assumptions | Why this design, what depends on each assumption, how checked |
| Evidence and robustness | Primary results, effect sizes, sensitivity, what could break them |
| Novelty and alternatives | What is genuinely new, what is incremental, closest prior work |
| Limitations and follow-up | Honest boundaries, what would be done differently, next steps |

`defense_qa.py` generates questions in three difficulty tiers:

- **Foundational**: state the claim and its supporting result (recall).
- **Methodological**: justify assumptions, design choices, and robustness (analyze).
- **Critical**: defend against the strongest alternative explanation (evaluate).

Use `--max-difficulty` to scale the preparation up or down; start with
`foundational` for early rehearsals and work up to `critical`.

## Timing

A common failure mode is a deck that is too dense to present calmly.

| Signal | Minutes per slide | Verdict |
|---|---|---|
| `< 0.75` | rushed | the audience cannot read the slides |
| `0.75 – 2.0` | comfortable | room for emphasis and asides |
| `2.0 – 3.0` | slow | acceptable for dense proof or demo slides |
| `> 3.0` | dragging | the talk loses momentum |

`defense_qa.py --slides N --minutes M` computes minutes per slide and flags decks
outside the comfortable band. Aim for the middle of the range on the first
rehearsal and cut slides, not content, if you are over budget.

## Contribution-evidence coverage

Every declared contribution must link to a verifiable location (chapter, section,
figure, table, data, code, or literature). `defense_qa.py` reports contributions
without a direct link and contributions that rely only on a shared evidence
ledger. Treat any uncovered contribution as an open risk: examiners gravitate
toward claims the candidate cannot point to on the page.

## Rules of engagement

- **Answer the thesis, not the slide.** If a question reaches beyond the
  presentation, anchor the answer in the written work and its artifacts.
- **Never fabricate a result, citation, or examiner opinion.** Mark uncertainty
  explicitly; "I did not test that, but the likely answer is X because Y" is
  honest and defensible.
- **Own the limitations.** A candid limitation, with a mitigation plan, scores
  better than a limitation the examiner has to extract.
- **Rehearse aloud.** A prepared answer that reads well often collapses under
  spoken questioning; practice with a colleague playing a critical examiner.
