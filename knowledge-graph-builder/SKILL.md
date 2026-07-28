---
name: knowledge-graph-builder
description: Build a domain concept graph from a pile of Markdown literature notes — typed concept nodes (method/dataset/task/metric/topic/paper), controlled-ontology relations with mandatory evidence anchors, research-lineage tracing, and Graphviz visualization. Use when the user wants to "build a knowledge graph from my notes", "map concepts across papers", "see how methods/datasets relate", "trace the research lineage of a topic", or visualize a note vault as a graph — including Chinese trigger phrases like "构建知识图谱/概念图", "梳理研究脉络", "把这些笔记连成图", "看看方法之间的演进关系". NOT for deep-reading a single paper — use literature-reader instead; NOT for drafting prose about a figure or checking citation/format compliance — use paper-writing-assistant instead; NOT for designing experiments — use experiment-designer instead; NOT for running statistics on experimental data — use data-analysis-assistant instead; NOT for re-running a paper's code — use reproduction-assistant instead.
---

# Knowledge Graph Builder

Turn a directory of Markdown literature notes into a typed, evidence-anchored concept graph, then use the graph to trace research lineages and produce visualizations.

**Global conventions**
- **User-facing reports are in Chinese by default**; content written into artifacts (note files, frontmatter) follows the artifact's own language.
- **Evidence first**: every semantic relation must carry an evidence anchor (source file + line/quote). Never assert a relation from model common sense alone.
- **Deterministic vs. AI-proposed relations stay separate**: wikilinks, `@citekey`, and explicit frontmatter `graph:` declarations are deterministic and go straight into the graph; relations you infer from reading notes are proposals and must be approved by the user before being written into frontmatter.

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
   It parses `[[wikilink]]` (with `|alias` / `#heading` forms, skipping code blocks), `@citekey`, `\cite{...}`, and explicit frontmatter `graph:` relation lists, then emits nodes/edges JSON, a Graphviz DOT file, and a warnings report for edges missing required evidence. Useful extra flags: `--stats` (degree distribution, isolated nodes, connected components, top hubs — use for vault health checks and hub discovery), `--csv PREFIX` (Gephi/Cytoscape-compatible `PREFIX.nodes.csv`/`PREFIX.edges.csv` export), `--query graph.json --seed <node> --depth N --relations r1,r2` (extract an evidence-whitelisted subgraph from a saved graph — no rescan needed).
3. Read the warnings first: every explicit frontmatter relation without an `evidence` field is listed there. Report counts (nodes by type, edges by relation, unresolved links, evidence violations) to the user in Chinese.

### Stage 2 — Normalize and type the concepts

4. Map raw nodes onto the controlled ontology — node types `method/dataset/task/metric/topic/paper` and the built-in relation table. Read `references/graph-schema.md` **at this point** for the full ontology, typing heuristics, alias-merging rules, and the evidence requirements per relation. Do not read both reference files up front.
5. If the domain does not fit the built-in types (e.g. genes/drugs, compounds/reactions), or the user asks about naming conventions, concept splitting/merging granularity, or ontology changes/migration, read `references/ontology-design.md` **at this point** — decide custom types *before* bulk typing.
6. Propose merges for obvious duplicates (case variants, plural/singular, alias frontmatter) and confirm with the user before treating them as one node.

### Stage 3 — Propose semantic relations (optional, approval-gated)

7. Where the deterministic graph is thin (nodes with no typed relations), read the relevant notes and propose relations (`improves-on`, `outperforms`, `evaluates-on`, `uses-dataset`, ...). **Each proposal must quote the evidence** (file + line + verbatim snippet).
8. Present proposals as a table (关系 / 起点 / 终点 / 证据引文 / 置信理由) and let the user approve/reject. Write approved ones back either by editing the note's frontmatter `graph:` list directly, or — for larger batches — by saving proposals to a JSON file (format in `scripts/merge_proposals.py` docstring) with `status: approved/rejected` and running `python3 scripts/merge_proposals.py proposals.json --vault <notes_dir>` (or `--overlay overlay.json` to keep them out of frontmatter). Then re-run `build_graph.py` so the graph reflects the fact source.

### Stage 4 — Lineage tracing and narration

9. For "梳理研究脉络/演进关系" requests, read `references/graph-rag.md` **at this point**: seed-concept recall → budgeted layer-by-layer expansion → pruning → lineage narrative where every claim cites its evidence anchor. It also covers comparative mode (divergence points of two research lines), year-ordered temporal narration, and community/cluster reasoning — read the relevant section per question type. Use `--query` to pull the seed subgraph mechanically before narrating.
10. Deliver the narrative in Chinese with evidence citations; explicitly say when the graph evidence is insufficient instead of filling gaps with general knowledge.

### Stage 5 — Visualization

11. `--dot` output can be rendered with `dot -Tsvg graph.dot -o graph.svg` if Graphviz is installed; `--csv` exports load directly into Gephi/Cytoscape for interactive exploration (layouts, community detection); otherwise hand the user the DOT file or an inline Mermaid `graph LR` block derived from the JSON for small subgraphs (< 40 nodes).

## File index

- `references/graph-schema.md` — controlled ontology: node types, built-in relation table, evidence anchor rules, frontmatter declaration format, deterministic vs. proposal pipeline.
- `references/ontology-design.md` — when to add custom node/relation types, naming conventions, granularity decisions (split vs. merge), ontology evolution and migration rules. Read during Stage 2 when the built-in ontology doesn't fit.
- `references/workflows.md` — end-to-end playbooks: cold-start graph building, incremental paper ingestion, pre-survey landscape tracing with claim→citation tables. Read the matching playbook at task start.
- `references/graph-rag.md` — graph-based lineage tracing: seed recall, budgeted expansion, pruning, evidence-cited narration, comparative divergence analysis, temporal narration, community/cluster concepts.
- `scripts/build_graph.py` — zero-dependency Markdown vault scanner: wikilink/`@citekey`/frontmatter-relation parsing, nodes/edges JSON, `--dot` Graphviz output, `--stats` detailed statistics, `--query` subgraph extraction, `--csv` Gephi/Cytoscape export, missing-evidence validation and warnings.
- `scripts/merge_proposals.py` — zero-dependency merger: writes approved relation proposals from a proposals JSON into note frontmatter `graph:` blocks (or a graph-overlay JSON), with dedup, validation, and dry-run.
