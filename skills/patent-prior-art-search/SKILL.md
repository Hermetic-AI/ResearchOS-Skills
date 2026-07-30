---
name: patent-prior-art-search
description: Plan and document auditable patent and non-patent prior-art searches with query logs, classification, date cutoffs, family tracking, evidence locations, and uncertainty labels. Use when users need a prior-art search plan, patent landscape evidence log, novelty-search query matrix, or invention disclosure literature search; do not use for legal opinions.
---

# Patent Prior-Art Search

This is research support, not legal advice, a freedom-to-operate opinion, patentability opinion, or a completeness guarantee. Preserve exact sources, dates, jurisdictions, query syntax, and document locations for qualified counsel or search professionals to review.

## Initialize a search ledger

```bash
python scripts/init_search_ledger.py --out prior-art-ledger.json --subject "Invention subject" --cutoff-date 2026-07-29
```

## Workflow

1. Break the subject into independently searchable technical features and synonyms; do not assume claim construction.
2. Record patent and non-patent sources separately, with database, jurisdiction, date searched, exact query, and result identifiers.
3. Track priority/publication dates, family links, claim/paragraph/figure locations, and relevance as a tentative research assessment.
4. Label gaps, access limits, language limits, and scope exclusions. Escalate conclusions to qualified counsel.

`python scripts/audit_feature_coverage.py features.json --pretty` checks manual feature-to-document locator coverage. It is not a legal analysis or patentability conclusion.

## Parse families, rank prior art, and visualize the family tree

```bash
python scripts/patent_family.py --ledger prior-art-ledger.json --out family-report.json \
    --mermaid-out family-tree.mmd --cutoff-date 2024-01-01
```

Parses patent family data from a `prior-art-search-ledger` (or a dedicated family file), computes per-family priority/publication timelines, ranks every family member as prior-art candidate by date proximity to a cutoff and by claims-token overlap with target claims (`--target-claims`), and emits a family tree as indented text and an optional Mermaid flowchart (`--mermaid-out`). Date proximity and token overlap are crude triage signals — they are not a novelty, obviousness, infringement, freedom-to-operate, or patentability conclusion. Read `references/patent-families.md` before interpreting the ranking, and escalate every conclusion to qualified counsel.

## Resources

- `scripts/init_search_ledger.py` — protected prior-art search plan and evidence ledger scaffold.
- `scripts/patent_family.py` — family timeline computation, prior-art ranking, and family-tree visualization.
