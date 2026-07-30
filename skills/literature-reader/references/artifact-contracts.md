# Literature artifact contracts

Use the repository schema at `../schemas/researchos-artifacts.schema.json` as the canonical contract. Markdown remains the human-facing deliverable; add JSON when another skill will consume the result or the user requests a reusable project artifact.

## Outputs

- Single-paper note → `paper-note`
- Multi-paper matrix → `literature-matrix`
- Gap analysis → `research-gap`
- Raw/scanned PDF extraction → `pdf-extraction`
- Identifier, integrity, duplicate, and version audit → `bibliography-audit`
- Normalized portable literature library → `bibliography-library`
- Format conversion provenance → `bibliography-conversion`
- Claim-to-page evidence verification → `evidence-audit`
- Corpus processing checkpoint → `literature-batch`

Every JSON artifact must contain `schema_version: "1.0.0"`, the matching `artifact_type`, and `provenance`. Put the skill name in `provenance.created_by`; list each paper, DOI, file, or URL in `provenance.sources`; preserve unresolved fields as `null` or warnings rather than inventing values.

For `paper-note`, every core claim is a stable claim object with support level and one or more anchors containing `source`, `page` or `section`, a short `quote`, extraction method, and verification state. Audit it against `pdf-extraction` where possible. For matrices, keep dimensions and paper identifiers explicit. For gaps, use only `recommended`, `caution`, or `not-recommended` feasibility values.

Validate before handoff:

```bash
python tools/validate_artifact.py note.json --type paper-note
python tools/validate_artifact.py matrix.json --type literature-matrix
python tools/validate_artifact.py gaps.json --type research-gap
python tools/validate_artifact.py paper.extraction.json --type pdf-extraction
python tools/validate_artifact.py bibliography.audit.json --type bibliography-audit
python tools/validate_artifact.py library.normalized.json --type bibliography-library
python tools/validate_artifact.py library.bib.manifest.json --type bibliography-conversion
python tools/validate_artifact.py note.evidence-audit.json --type evidence-audit
python tools/validate_artifact.py derived/batch-state.json --type literature-batch
```
