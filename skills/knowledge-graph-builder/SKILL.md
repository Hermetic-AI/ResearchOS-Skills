---
name: knowledge-graph-builder
description: Build evidence-anchored concept graphs from Markdown research notes and schema-validated ResearchOS paper-note JSON; preserve claim-level page/section/quote provenance; use typed nodes, controlled relations, approval-gated inference, lineage tracing, and Graphviz/tabular export. Use for building a knowledge graph, connecting reading notes into a graph, importing paper-notes, mapping claim evidence, tracing research threads, mapping concepts or claims across papers, or tracing a lineage. Not for deep-reading one paper (literature-reader), manuscript/citation editing, experiment design, statistics, or running paper code.
---

# Knowledge Graph Builder

Turn a directory of Markdown literature notes into a typed, evidence-anchored concept graph, then use the graph to trace research lineages and produce visualizations.

**Global conventions**
- **User-facing reports are in English by default**; content written into artifacts (note files, frontmatter) follows the artifact's own language.
- **Evidence first**: every semantic relation must carry an evidence anchor (source file + line/quote). Never assert a relation from model common sense alone.
- **Deterministic vs. AI-proposed relations stay separate**: wikilinks, `@citekey`, and explicit frontmatter `graph:` declarations are deterministic and go straight into the graph; relations you infer from reading notes are proposals and must be approved by the user before being written into frontmatter.
- **Normalized note ingestion**: when `paper-note` JSON artifacts are available, read `references/artifact-contracts.md`, validate them, and retain their evidence anchors during graph import.

## When to use / not use

Use when the user has multiple notes/papers and wants structure across them: concept maps, relation tables, lineage narratives, DOT/Mermaid visualization.

Do NOT use for: reading one paper in depth (`literature-reader`), writing or checking paper text/citations (`paper-writing-assistant`), experiment design (`experiment-designer`), data statistics (`data-analysis-assistant`), code reproduction (`reproduction-assistant`).

**Playbooks**: for the three big end-to-end scenarios — cold-start graph over a new vault, incremental ingestion of new papers, pre-survey landscape tracing with claim→citation tables — read the matching section of `references/workflows.md` first and follow it instead of improvising.

## Workflow

### Stage 1 — Scan and build the deterministic graph

1. Confirm the notes directory with the user (default: current working directory).
2. Run the zero-dependency script (Python 3, stdlib only):
   ```
   python3 scripts/build_graph.py <notes_dir> -o graph.json --dot graph.dot --warnings warnings.md
   ```
   It parses `[[wikilink]]` (with `|alias` / `#heading` forms, skipping code blocks), `@citekey`, `\cite{...}`, explicit frontmatter `graph:` relations, and every `artifact_type: paper-note` JSON. Valid paper notes become one paper node plus claim nodes; every source/page/section/line/quote/extraction-method/verification anchor becomes a preserved `supports` edge. Invalid paper notes are quarantined as graph errors, while unrelated JSON is ignored. It then emits nodes/edges JSON, DOT, and warnings. Useful flags: `--stats`, `--csv PREFIX`, and `--query graph.json --seed <node> --depth N --relations r1,r2`.
3. Read the warnings first: every explicit frontmatter relation without an `evidence` field is listed there. Report counts (nodes by type, edges by relation, unresolved links, evidence violations) to the user in English.
   For a release/readiness screen, run `python3 scripts/audit_evidence_anchors.py --graph graph.json --out evidence-audit.json`; it reports missing page/section, DOI, and verification fields without altering claims.

### Stage 2 — Normalize and type the concepts

4. Map raw nodes onto the controlled ontology — node types `method/dataset/task/metric/topic/paper` and the built-in relation table. Read `references/graph-schema.md` **at this point** for the full ontology, typing heuristics, alias-merging rules, and the evidence requirements per relation. Do not read both reference files up front.
5. If the domain does not fit the built-in types (e.g. genes/drugs, compounds/reactions), or the user asks about naming conventions, concept splitting/merging granularity, or ontology changes/migration, read `references/ontology-design.md` **at this point** — decide custom types *before* bulk typing.
6. Propose merges for obvious duplicates (case variants, plural/singular, alias frontmatter) and confirm with the user before treating them as one node.
   Use `python3 scripts/entity_identity_audit.py --graph graph.json --out entity-audit.json` to generate deterministic identity keys, conservative same-label proposals, and high-threshold same-type token-similarity candidates. It never rewrites graph IDs or applies a merge.

### Stage 3 — Propose semantic relations (optional, approval-gated)

7. Where the deterministic graph is thin (nodes with no typed relations), read the relevant notes and propose relations (`improves-on`, `outperforms`, `evaluates-on`, `uses-dataset`, ...). **Each proposal must quote the evidence** (file + line + verbatim snippet).
8. Present proposals as a table (relation / source / target / evidence citation / confidence rationale) and let the user approve/reject. Write approved ones back either by editing the note's frontmatter `graph:` list directly, or — for larger batches — by saving proposals to a JSON file (format in `scripts/merge_proposals.py` docstring) with `status: approved/rejected` and running `python3 scripts/merge_proposals.py proposals.json --vault <notes_dir>` (or `--overlay overlay.json` to keep them out of frontmatter). Then re-run `build_graph.py` so the graph reflects the fact source.

### Stage 4 — Lineage tracing and narration

9. For research-lineage / evolution-relationship requests, read `references/graph-rag.md` **at this point**: seed-concept recall → budgeted layer-by-layer expansion → pruning → lineage narrative where every claim cites its evidence anchor. It also covers comparative mode (divergence points of two research lines), year-ordered temporal narration, and community/cluster reasoning — read the relevant section per question type. Use `--query` to pull the seed subgraph mechanically before narrating.
10. Deliver the narrative in English with evidence citations; explicitly say when the graph evidence is insufficient instead of filling gaps with general knowledge.

### Stage 5 — Visualization

11. `--dot` output can be rendered with `dot -Tsvg graph.dot -o graph.svg` if Graphviz is installed; `--csv` exports load directly into Gephi/Cytoscape for interactive exploration (layouts, community detection); otherwise hand the user the DOT file or an inline Mermaid `graph LR` block derived from the JSON for small subgraphs (< 40 nodes).

- `scripts/audit_temporal_conflicts.py` — read-only audit of optional year/validity fields, lineage time inversions, and `contradicts` coexisting with other relations; it never resolves or removes a relation.

## File index

- `references/graph-schema.md` — controlled ontology: node types, built-in relation table, evidence anchor rules, frontmatter declaration format, deterministic vs. proposal pipeline.
- `references/ontology-design.md` — when to add custom node/relation types, naming conventions, granularity decisions (split vs. merge), ontology evolution and migration rules. Read during Stage 2 when the built-in ontology doesn't fit.
- `references/workflows.md` — end-to-end playbooks: cold-start graph building, incremental paper ingestion, pre-survey landscape tracing with claim→citation tables. Read the matching playbook at task start.
- `references/artifact-contracts.md` — validated `paper-note` ingestion and evidence-preservation rules. Read only for normalized JSON input.
- `references/graph-rag.md` — graph-based lineage tracing: seed recall, budgeted expansion, pruning, evidence-cited narration, comparative divergence analysis, temporal narration, community/cluster concepts.
- `scripts/build_graph.py` — zero-dependency Markdown + `paper-note` JSON scanner: validates the normalized note contract, preserves claim evidence on graph edges, parses wikilink/`@citekey`/frontmatter relations, and emits JSON/DOT/CSV, detailed stats, subgraphs, and warnings.
- `scripts/add_relation.py` — zero-dependency CLI to idempotently append one relation to a note's frontmatter `graph:` list (`--note/--relation/--target/--quote [--line] [--dry-run]`), emitting YAML compatible with build_graph.py's parser — use instead of hand-editing frontmatter.
- `scripts/merge_proposals.py` — zero-dependency merger: writes approved relation proposals from a proposals JSON into note frontmatter `graph:` blocks (or a graph-overlay JSON), with dedup, validation, and dry-run.
- `scripts/graph_entity_merge.py` — zero-dependency apply-side counterpart to `entity_identity_audit.py`: interactively (or via `--auto-merge`) approves same-label alias merges and same-type similarity candidates, rewrites the graph so each group shares one canonical id, merges/dedups edges, drops removed nodes, and records every merge in a `merges` provenance array. Output is protected unless `--force` is explicit.
- `scripts/export_graph.py` — zero-dependency GraphML, GEXF, JSON-LD, and RDF/Turtle exporter for an existing ResearchOS graph JSON; outputs are protected unless `--force` is explicit.
- `scripts/analyze_graph.py` — deterministic weak-component/community screen, degree centrality, and optional node/edge diff between graph versions; it never infers or edits relations.
