# Search protocols

A search strategy is only as auditable as its documentation. Record the full
provenance of every query before you run it.

## Building a structured query

1. **Question** — write the review question in one sentence (PICOS when applicable).
2. **Concepts** — break the question into 2-4 core concepts. For each concept,
   list the primary term and synonyms (controlled vocabulary + free text).
3. **Database choice** — pick databases appropriate to the discipline
   (PubMed/MEDLINE, Embase, Scopus, Web of Science, Crossref, Semantic Scholar,
   domain archives). No single database is exhaustive.
4. **Field tags** — use database-specific tags (PubMed `[tiab]`, `[mh]`) to
   balance sensitivity and specificity.
5. **Filters** — date ranges, language, species, study design. State every
   filter explicitly; do not rely on a database's default limits.

## Database-specific string formatting

- **PubMed** — Boolean combinations of quoted phrases with field tags, e.g.
  `("synaptic plasticity"[tiab] OR "neural plasticity"[tiab]) AND memory[tiab]`.
- **Crossref / Semantic Scholar** — free-text queries; no field tags. Keep
  them simple and rely on post-retrieval screening.
- **Scopus / WoS** — use their advanced field codes (TITLE-ABS-KEY, TS).

## Provenance to record

For every search run, log: database, exact search string, date range, filters,
retrieval date, and number of records retrieved. Store this in a search log
(`search-plan.json`) so the search is reproducible.

## Deduplication

After export, deduplicate the merged library:

- Match **normalized DOI** first (strip `https://doi.org/`, `doi:` prefix,
  lowercase).
- Then match **normalized title + year** as a conservative candidate cluster.
- Never delete records automatically; select a canonical record and preserve
  all member IDs for human review.

## Format exchange

Export the deduplicated library to the format your workflow needs:

- **RIS** — widely supported by reference managers (Zotero, EndNote).
- **BibTeX** — for LaTeX-based writing.
- **CSV** — for screening in spreadsheets.

These are offline format conversions only; they do not verify metadata against
an external source.

## Handoff

- Send the deduplicated library to `literature-reader` for evidence extraction.
- Send a screening-ready export to `systematic-review-meta-analysis` once a
  protocol exists.
- Do not claim a PRISMA count or verify an identifier without source evidence.
