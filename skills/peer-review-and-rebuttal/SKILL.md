---
name: peer-review-and-rebuttal
description: Triage peer-review comments, create auditable response matrices, trace requested revisions to manuscript locations and evidence, simulate review checks, and keep rebuttal claims consistent with actual changes. Use when users receive reviewer comments, need a rebuttal letter, response-to-reviewers matrix, revision plan, mock peer review, or revision consistency audit.
---

# Peer Review and Rebuttal

Respond accurately, specifically, and respectfully. Never claim an experiment, analysis, citation check, or manuscript change was completed unless an artifact or location verifies it.

## Create a response matrix

```bash
python scripts/init_response_matrix.py --out response-matrix.json --manuscript-version v1 --comments reviewer-comments.json
```

Each comment gets an ID, priority, category, planned action, evidence/location placeholder, status, and unresolved-decision field. Draft replies must distinguish agreement, clarification, partial change, and justified non-change.

## Audit completed responses

```bash
python scripts/audit_response_matrix.py --matrix response-matrix.json --manuscript revised.md --out response-audit.json
```

Rows marked `addressed`/`complete`/`completed` require `evidence_or_location`. Use `text:<exact revised phrase>` or `artifact:<path>` for mechanical checks; the audit does not decide whether a revision is substantively adequate.

`python scripts/init_mock_review.py --out mock-review.json --manuscript-version v2` creates human-review prompts tied to expected evidence; it does not create actual reviewer comments.

## Triage

- Critical: validity, ethics, data availability, statistical conclusion, or central claim.
- Major: design, missing analysis/control, interpretation, reproducibility, or key literature.
- Minor: clarity, style, citation, layout, and localized presentation.

Use `paper-writing-assistant`, `data-analysis-assistant`, `scientific-plot`, or `reproduction-assistant` for substantive changes, then attach the resulting location/artifact before marking a response complete.

## Review templates and reporting-guideline checks

```bash
python scripts/review_simulator.py --mode template --venue journal --out review.json
python scripts/review_simulator.py --mode checklist --guideline consort --manuscript manuscript.md --sections "title,methods" --out checklist.json
python scripts/review_simulator.py --mode full --venue conference --guideline strobe --manuscript manuscript.md --sections "methods" --out review.json
```

`--mode template` produces a venue-specific review skeleton. `--mode checklist`
scores a manuscript against CONSORT / STROBE / PRISMA by keyword presence.
`--mode full` combines both.

## Resources

- `scripts/review_simulator.py` — venue review templates and reporting-guideline compliance scoring.
- `references/review-checklists.md` — review structure and checklist usage rules.
- `scripts/init_response_matrix.py` — protected reviewer-comment response scaffold.
