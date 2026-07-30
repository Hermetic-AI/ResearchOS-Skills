---
name: research-proposal-and-grant
description: Create evidence-backed research proposal and grant-planning artifacts with scoped aims, milestones, budget assumptions, risks, and compliance placeholders. Use when users need a proposal outline, Specific Aims, grant work plan, budget narrative, feasibility plan, or funder-ready evidence ledger.
---

# Research Proposal and Grant

Do not fabricate preliminary results, collaborators, budgets, funder requirements, or compliance approvals. Treat every grant call and institutional rule as source material that must be supplied or verified.

## Initialize a proposal charter

```bash
python scripts/init_proposal_charter.py --out proposal-charter.json --title "Project title" --question "Research question" --funder "Funder or call"
```

The charter holds the question, aims, innovation, approach, milestones, budget assumptions, risks, evidence placeholders, and unresolved compliance decisions. It is a planning artifact, not a submission.

## Audit Specific Aims completeness

```bash
python scripts/audit_specific_aims.py --charter proposal-charter.json --out aims-audit.json
```

Each declared aim needs a title, objective, approach, expected deliverable, and feasibility evidence ID or explicit rationale. The audit checks planning completeness only, not fundability or scientific merit.

`python scripts/audit_budget_assumptions.py proposal-charter.json --pretty` checks human-entered budget assumptions for amount, rationale, and rule-source fields; it never approves a budget.

## Workflow

1. Record the call URL/document, deadline, eligibility, page limits, budget rules, and required sections.
2. Make each aim falsifiable, scoped, and connected to an outcome and feasibility evidence.
3. Add a milestone, deliverable, dependency, owner, and fallback for every work package.
4. Label all costs as estimates until a supplier, institutional, or funder source is attached.
5. Send substantive study design and analysis to `experiment-designer` and `data-analysis-assistant`; record their artifacts before finalizing claims.

## Resources

- `scripts/init_proposal_charter.py` — protected grant-planning artifact scaffold.
