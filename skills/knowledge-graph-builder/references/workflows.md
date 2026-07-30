# End-to-End Workflow Playbooks

Three complete playbooks. Each lists trigger phrases, the exact step sequence (cross-referencing SKILL.md stages), deliverables, and the checkpoints where you must stop and confirm with the user. Do not read this file for a one-off question; read the playbook section that matches the current task.

## Playbook A — Cold start: build a graph over a new domain/vault

**Triggers**: "build a graph for this domain", "I just imported a batch of notes, help me build a knowledge graph", "build a graph from scratch".

1. **Recon (before running anything)**: count `.md` files and `paper-note` JSON artifacts. Sample 3–5 Markdown notes to learn the frontmatter dialect, and schema-validate normalized JSON before graph ingestion. If the vault is Obsidian-style with `[[links]]` or contains claim-anchored paper notes, the deterministic pass will be rich; if notes are flat summaries with no links/claims, expect a sparse graph.
2. **Baseline build**: `python3 scripts/build_graph.py <vault> -o graph.json --dot graph.dot --warnings warnings.md`. Record the numbers: files, nodes by type, edges by relation, unresolved-link count, evidence errors.
3. **Type census**: most scanned notes will be `type: note` fallback. Propose a typing pass in batches of ~10 notes (read each note's first paragraph + headings; assign `method/dataset/task/metric/topic`). Present the batch as a table (note / suggested type / one-sentence rationale) and get approval before editing frontmatter. Do not bulk-edit unapproved.
4. **Ontology check**: if the domain doesn't fit the built-in types (biomedical, chemistry, social science), read `ontology-design.md` §1 now and agree on custom types *before* typing hundreds of notes — retrofitting is the expensive path.
5. **Seed relation pass**: for the 10–20 highest-degree nodes (use `--stats` degree output), run SKILL.md Stage 3 proposals. Cold-start graphs gain the most from `improves-on`/`uses-dataset` on hub nodes.
6. **Deliverables**: `graph.json`, `graph.dot`, an English summary (scale statistics / main clusters / evidence gap list), and an `ontology.md` decision note if any custom types were adopted.

**Stop points**: after step 3 (typing approval), after step 4 (ontology sign-off), after step 5 (proposal approval).

**Cold-start pitfalls**: don't try to type every note in one pass — accuracy collapses past ~30 notes; don't resolve ambiguous wikilink targets by guessing — mark unresolved and ask; don't import folder hierarchy as `topic` structure without checking the folders actually mean something.

## Playbook B — Incremental: add new papers to an existing graph

**Triggers**: "add these new papers into the graph", "incremental update", "I read 5 more papers last week".

1. **Scope the delta**: identify the new/changed notes only (file mtimes, git status, or a user-supplied list). Never rebuild-and-retype the whole vault — existing frontmatter is settled fact.
2. **Rebuild projection**: run `build_graph.py` again (the projection is always rebuilt wholesale; only *frontmatter edits* are incremental). Diff against the previous `graph.json` if one was kept: new nodes, new unresolved links, new warnings.
3. **Type the newcomers**: same batch-table approval as Playbook A step 3, but smaller.
4. **Attach, don't float**: for each new paper note, the key question is *where it connects to the existing graph*. For each new node, search the vault for the 2–3 most likely existing neighbors (same task? same dataset? claims to improve an existing method?) and propose those edges first, with evidence quotes. A new node that ends the pass with zero typed edges is a failure — either propose connections or tell the user the note doesn't connect to anything yet.
5. **Alias sweep**: new papers often re-name existing concepts ("instruction tuning" vs. "instruction-tuning"). Check new unresolved concept placeholders against existing node labels/aliases; propose merges per `graph-schema.md` rules.
6. **Deliverables**: updated `graph.json`, a short English delta report (new node/edge counts, attachment positions, unconnected isolated notes, evidence gaps).

**Stop points**: proposal approval (steps 3–5 can be one combined table for a small batch).

**Incremental pitfalls**: re-proposing relations that were previously rejected — keep rejected proposals in the overlay/proposal log and skip them; letting new notes introduce near-duplicate concepts instead of linking to existing ones.

## Playbook C — Pre-survey: trace the landscape and locate citations before writing

**Triggers**: "I want to write a survey/related work, first sort out the lineage", "survey prep", "help me locate which paper each argument should cite".

1. **Frame the survey scope with the user**: 1–3 seed topics, time window, inclusion bar (e.g. only papers with `evaluates-on` evidence in the vault). Write the scope down — expansion budgets depend on it.
2. **Build/refresh the projection** and run `--stats` to find the hubs and isolated nodes; isolated nodes in scope are notes you read but never linked — flag them, they're likely survey blind spots.
3. **Lineage extraction**: for each seed, use `--query <graph.json> --seed <node> --depth 2 --relations improves-on,extends,outperforms,uses-dataset,evaluates-on,cites` to pull the lineage subgraph. Then follow `graph-rag.md` §4 (temporal narration) to produce the year-ordered evolution narrative.
4. **Fork/divergence mapping**: if the field split into competing lines, use `graph-rag.md` §3 (comparative mode) to identify the divergence nodes and write the divergence point analysis.
5. **Claim → citation table**: the deliverable that makes this a *survey prep* rather than a summary. For every sentence-level claim the user plans to make, produce: argument / supporting node / evidence citation (file:line + quote) / corresponding paper node (i.e. the citekey to cite). Claims with no evidence anchor go into a to-cite list — never invent a citation.
6. **Gap report**: `contradicts` edges and missing relations in scope = the survey's "open problems" section raw material. List them explicitly.
7. **Deliverables**: lineage narrative (English, with evidence anchors), divergence point analysis, argument–citation mapping table (Markdown table), to-cite list, optional Mermaid/DOT subgraph.

**Stop points**: after step 1 (scope sign-off), after step 5 (citation table review — this is what the user pastes into their draft workflow, often continuing with `paper-writing-assistant` for the actual prose).

**Survey-prep pitfalls**: narrating beyond the vault (the graph only knows what the notes say — say so when coverage is thin); citing a paper because it's famous rather than because the graph holds evidence for the specific claim; letting the citation table grow past the scope agreed in step 1.
