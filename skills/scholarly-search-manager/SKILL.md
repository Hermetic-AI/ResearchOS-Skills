---
name: scholarly-search-manager
description: Plan auditable scholarly searches, normalize and deduplicate local citation records, verify identifiers when explicitly authorized, track query provenance, and exchange literature libraries. Use when users need a database search strategy, search log, DOI-based deduplication, citation chasing plan, RIS/BibTeX/CSL-JSON exchange, or a reproducible literature search handoff.
---

# Scholarly Search Manager

Keep discovery separate from evidence assessment. A record's presence in a search result does not establish scientific support.

## Search plan

Before querying an external database, record the question, concepts/synonyms, Boolean string, database, dates, filters, and retrieval date. Online queries, downloads, and citation chasing require the user's authorization and the target service's terms.

## Local deduplication

Normalize a local JSON list before screening:

```bash
python scripts/dedupe_records.py records.json --out library.json
```

The script groups exact normalized DOI values first, then conservative title/year candidates. It never deletes records: it selects a canonical record and preserves all member IDs for review.

## Handoff

Send the deduplicated library to `literature-reader` for evidence extraction; send a screening-ready export to `systematic-review-meta-analysis` when a protocol exists. Do not claim a PRISMA count or verify an identifier without source evidence.

`python scripts/export_ris.py library.json --out library.ris` exports local records to RIS with protected output; it does not search or verify metadata.

## Search management and exchange

```bash
python scripts/search_manager.py --mode plan --query query.json --out search-plan.json
python scripts/search_manager.py --mode dedupe --library results.json --out deduped.json
python scripts/search_manager.py --mode export --library library.json --format ris --out library.ris
```

`--mode plan` formats a structured query into PubMed / Crossref / Semantic
Scholar search strings (templates only — online queries require user
authorization). `--mode dedupe` clusters by normalized DOI then title/year.
`--mode export` writes RIS, BibTeX, or CSV with protected output.

## Resources

- `scripts/search_manager.py` — query planning, DOI/title deduplication, and RIS/BibTeX/CSV exchange.
- `references/search-protocols.md` — search strategy, provenance, and handoff rules.
- `scripts/dedupe_records.py` — local JSON record deduplication with review-preserving clusters.
