# Knowledge-graph artifact handoff

Use `paper-note` artifacts defined in `../schemas/researchos-artifacts.schema.json` as a normalized ingestion source. `build_graph.py` scans them alongside Markdown, performs a zero-dependency contract check, and quarantines invalid artifacts as graph errors. Validate with the canonical schema before ingestion:

```bash
python tools/validate_artifact.py note.paper-note.json --type paper-note
python3 scripts/build_graph.py notes -o graph.json --warnings graph-warnings.md
```

- Create or resolve one paper node from `paper.title`, DOI, year, and authors.
- Create one claim node per `claims[]` item and one `supports` edge per evidence anchor; never discard page, section, line, quote, extraction method, or verification state.
- Treat contributions and limitations as claims, not automatically as ontology relations.
- Keep the source artifact path and schema version on imported nodes.
- Reject or quarantine artifacts that fail the local contract check; the canonical JSON Schema remains authoritative.

The graph JSON remains the knowledge-graph skill's native output. Do not relabel it as one of the interchange artifact types unless a dedicated graph contract is added in a future schema version.
