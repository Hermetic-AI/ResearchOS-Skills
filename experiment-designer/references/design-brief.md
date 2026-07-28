# Design Brief — 5-Segment Interview Template

Read this at workflow step 1. Walk the user through the five segments **in order, one at a time**. Ask the questions, capture the answers verbatim, and write them into a design brief file (suggested: `design_brief.md` in the user's project directory). If the user can't answer a segment yet, write `_TODO: <reason>_` and move on — never fabricate answers. The skill's value is structured prompting: forcing the user to articulate what they'd otherwise leave implicit.

Keep chat output short: quote answers in the brief, summarize in one sentence in chat (Chinese).

## Segment 1 — Hypothesis

Goal: a falsifiable hypothesis, not a topic area.

Ask:
- What exactly do you claim will happen, and why? ("X increases Y under conditions Z" — not "we study X".)
- What observation would **falsify** it?
- What is the smallest experiment whose result would change your next action?

Capture: hypothesis statement, falsification condition, primary outcome.

## Segment 2 — Variables

Goal: every variable named, typed, and leveled.

Ask:
- Independent variable(s): what do you manipulate? For each factor, list the exact levels (e.g. dose 0/10/50 mg, temperature 20/60 °C).
- Dependent variable(s): what do you measure, in what units, and which is the **primary** endpoint?
- Nuisance variables: what varies that you do *not* care about — batch, day, operator, site, litter, plate position, baseline differences? For each: will you block it, hold it constant, or randomize across it?

Capture: factor table (name, type, levels), primary/secondary endpoints, nuisance-factor plan.

## Segment 3 — Treatments & controls

Goal: a treatment structure whose comparisons answer segment 1.

Ask:
- What are the treatment arms?
- Which controls isolate which alternative explanation — negative (time), vehicle (delivery medium), sham (procedure), positive (assay works)? (Selection guide: `design-types.md`.)
- Can measurement be blinded? Can allocation be concealed?

Capture: arm list, control list with the role of each, blinding plan.

## Segment 4 — Sample & randomization

Goal: the unit of replication and the allocation mechanism.

Ask:
- What is the experimental unit — the level at which treatment is applied? (3 mice × 100 cells = n of 3, not 300.)
- How many units per arm, and why? (If unknown, defer to the power-analysis step and fill in the result.)
- Allocation: complete randomization or permuted blocks? Any stratification factor (sex, site, baseline severity)?
- Who generates the schedule, and is the seed archived?

Capture: unit definition, n per arm (or `_TODO_` pending power analysis), randomization method + seed.

## Segment 5 — Measurement & analysis plan

Goal: the analysis fixed before data exists.

Ask:
- How is the primary endpoint measured, and what is the measurement error / reliability?
- What is the planned primary test (e.g. two-sample t-test on the primary endpoint)? Does it match the design (blocks/strata/nesting in the model)?
- What effect size would matter scientifically (smallest effect of interest), and where does that number come from — pilot, literature, or convention?
- What are the exclusion criteria and the dropout/missing-data plan, fixed in advance?

Capture: measurement protocol, primary analysis, effect-size justification, exclusion/missing-data rules.

## Brief file format

```markdown
---
project: <name>
last_updated: <ISO date>
status: draft        # draft | reviewed | locked
seed: <seed used for any generated schedule, or null>
---

## 1. Hypothesis
## 2. Variables
## 3. Treatments & controls
## 4. Sample & randomization
## 5. Measurement & analysis plan
```

Fill each section with the user's answers verbatim. If the file already exists, update — don't replace; keep human edits, fill only blanks unless the user asks to regenerate.

After saving, print a short report (Chinese): sections completed, strongest spot, weakest spot, suggested next step (typically: choose design type → generate schedule → power analysis).
