# Identifier Verification, Retraction Alerts, and Version Merging

## Table of Contents

- [Safe Defaults](#safe-defaults)
- [Offline Auditing](#offline-auditing)
- [Online Verification](#online-verification)
- [Retraction and Correction Signals](#retraction-and-correction-signals)
- [Deduplication and Version Families](#deduplication-and-version-families)
- [Conclusion Boundaries](#conclusion-boundaries)

## Safe Defaults

`audit_bibliography.py` does not access the network by default; it only normalizes DOI/arXiv/PMID, checks syntax, and identifies duplicates and version families. It reads from `extract_metadata.py`'s JSON or a JSON array of entries, deletes no records, does not automatically replace preprints with journal versions, and does not write "not found" as "genuinely valid."

```bash
python3 scripts/extract_metadata.py references.txt --pretty > metadata.json
python3 scripts/audit_bibliography.py metadata.json --out bibliography.audit.json
python tools/validate_artifact.py bibliography.audit.json --type bibliography-audit
```

## Offline Auditing

Offline results include:

- Normalized identifier values and syntax status;
- Strong matches on identical DOI, identical PMID, or identical arXiv base number;
- Probabilistic matches jointly supported by title, first author, and year;
- arXiv version numbers and "preprint → formally published version" candidate relationships;
- Suggested canonical entries and merge evidence for each cluster.

The canonical entry is used only for prioritizing metadata aggregation: DOI version first, then PMID, then arXiv, with higher arXiv versions preferred over lower ones. Version history, publication dates, title changes, and citation context must be preserved by a human.

After downloading the Retraction Watch CSV published by Crossref, verify offline:

```bash
python3 scripts/audit_bibliography.py metadata.json \
  --retraction-index retraction-watch.csv \
  --out bibliography.audit.json
```

This data is provided by Crossref under CC0 and updated on workdays. When publishing results that use the data, cite the source per Crossref/Retraction Watch's instructions; the repository does not bundle a database snapshot.

## Online Verification

Online mode is an explicit opt-in and requires a contact email:

```bash
python3 scripts/audit_bibliography.py metadata.json \
  --online --email researcher@example.org \
  --out bibliography.audit.json
```

- DOI: queries `https://api.crossref.org/works/{doi}`, identifying the client via `mailto` and User-Agent.
- arXiv: calls `https://export.arxiv.org/api/query?id_list=...` in batch, parsing Atom; only one batch request is sent per run.
- PMID: calls NCBI ESummary in batch, sending `tool` and `email`. Comply with the NCBI E-utilities usage policy; this feature does not copy abstracts. NCBI disclaimers and copyright notices: <https://www.ncbi.nlm.nih.gov/home/about/policies/>.

The email is used only for request identification and is replaced with `<redacted>` when writing the provenance command. API timeouts, rate limiting, service errors, or parse failures are written to warnings and are not disguised as "not found." Bulk harvesting should use the bulk/OAI-PMH/FTP channels provided by each institution.

## Retraction and Correction Signals

Crossref `update-to` and the Retraction Watch CSV may yield retraction, withdrawal, expression of concern, correction, or reinstatement; PubMed's publication type may also mark Retracted Publication.

- `critical`: retraction or withdrawal; stop treating the record as unaffected evidence and return to the original notice to verify scope and date.
- `warning`: expression of concern; not equivalent to retraction, but must be disclosed in reviews and citation decisions.
- `notice`: correction, reinstatement, and similar records; the content before and after the update must be compared.

Different sources may report the same event repeatedly; do not interpret duplicate entries as multiple retractions. Database record hits are an alert entry point; the final conclusion should revisit the publisher's notice and the paper's page.

## Deduplication and Version Families

- `probable-duplicate`: strong identifiers are identical, or titles are highly similar and first author and year are compatible.
- `version-family`: same arXiv base number, or the title supports a preprint-to-formally-published relationship.
- `evidence` stores per-pair matching rationale and similarity scores; do not retain only a single black-box score.
- Merging uses the union of identifiers, the full author list, version dates, and source records as the basis. Do not retroactively write new experiments or modified conclusions from the formal version back into an older preprint.
- Short titles, missing authors, conference-extended versions, and translations are prone to false positives; clustering actions are fixed to `review-and-merge-metadata; do-not-delete-automatically`.

## Conclusion Boundaries

A correctly formed identifier syntax does not mean it is registered; an API hit does not mean the paper is trustworthy; a miss in the retraction database does not mean it has not been retracted; a similar title does not prove identity of work. Reports should state "no signal was found under the sources and time of this query," and preserve the query time, input checksum, service warnings, and manual review status.
