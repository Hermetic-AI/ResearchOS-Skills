---
name: thesis-defense-assistant
description: Plan an evidence-backed thesis defense with contribution statements, claim-to-evidence traceability, examiner-question preparation, limitations, and follow-up actions. Use when users need a thesis defense outline, viva preparation, mock examiner questions, defense slide narrative, or defense evidence audit.
---

# Thesis Defense Assistant

The goal is preparation, not performance guarantees. Do not invent examiner opinions, research results, citations, or committee requirements. Mark uncertainty and limitations explicitly.

## Initialize a defense brief

```bash
python scripts/init_defense_brief.py --out defense-brief.json --thesis-title "Title" --candidate "Candidate role/name"
```

The brief keeps contributions, evidence links, anticipated questions, limitations, and planned follow-up decisions in one auditable artifact.

## Create question coverage prompts

```bash
python scripts/question_coverage.py --brief defense-brief.json --out question-coverage.json
```

The checklist covers scope, methods, evidence, novelty and limitations, plus each declared contribution/limitation. It is a preparation template, not a prediction of examiner questions or a source of answers.

## Generate defense Q&A and audit timing and coverage

```bash
python scripts/defense_qa.py --brief defense-brief.json --slides 20 --minutes 30 \
    --out defense-qa.json
```

Generates likely examiner questions from the thesis question, contributions, and limitations; simulates a Q&A run where each question carries a difficulty tier (foundational / methodological / critical) and a placeholder answer the candidate must fill with verified content. It also audits presentation timing against the slide count and flags contributions that lack a linked evidence entry. Use `--max-difficulty` to scale the preparation. This is a preparation aid, not a prediction of the real examination and never a source of answers. Read `references/defense-preparation.md` when planning categories, timing, and coverage.

## Workflow

1. State the thesis question, scope, and contributions in language supported by the thesis or artifacts.
2. Link each contribution to chapter/section locations and figures, tables, data, code, or literature evidence.
3. Prepare concise answers for methods, validity, robustness, novelty, ethics, and limitations; never turn speculation into fact.
4. Generate the Q&A prep and timing/coverage audit with `defense_qa.py`; resolve every open question and uncovered contribution.
5. Use `paper-writing-assistant` for claim/citation checks and `academic-presentation-poster` for the visual storyboard.

## Resources

- `scripts/init_defense_brief.py` — protected defense-preparation scaffold.
- `scripts/defense_qa.py` — examiner-question prep, timing audit, and contribution-evidence coverage check.
