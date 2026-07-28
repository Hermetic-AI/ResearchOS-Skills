# End-to-End Workflow Playbooks

Three complete playbooks. Each lists trigger phrases, the exact step sequence (cross-referencing SKILL.md stages), deliverables, and the checkpoints where you must stop and confirm with the user. Do not read this file for a one-off question; read the playbook section that matches the current task.

## Playbook A — Cold start: build a graph over a new domain/vault

**Triggers**: "给这个领域建个图", "我刚导入了一批笔记，帮我建知识图谱", "build a graph from scratch".

1. **Recon (before running anything)**: count `.md` files, sample 3–5 notes to learn the frontmatter dialect (does the vault use `type:`? aliases? citekeys or wikilinks?). If the vault is Obsidian-style with `[[links]]` everywhere, the deterministic pass will be rich; if notes are flat summaries with no links, expect a sparse graph and warn the user that Stage 3 proposals will do the heavy lifting.
2. **Baseline build**: `python3 scripts/build_graph.py <vault> -o graph.json --dot graph.dot --warnings warnings.md`. Record the numbers: files, nodes by type, edges by relation, unresolved-link count, evidence errors.
3. **Type census**: most scanned notes will be `type: note` fallback. Propose a typing pass in batches of ~10 notes (read each note's first paragraph + headings; assign `method/dataset/task/metric/topic`). Present the batch as a table (笔记 / 建议类型 / 依据一句话) and get approval before editing frontmatter. Do not bulk-edit unapproved.
4. **Ontology check**: if the domain doesn't fit the built-in types (biomedical, chemistry, social science), read `ontology-design.md` §1 now and agree on custom types *before* typing hundreds of notes — retrofitting is the expensive path.
5. **Seed relation pass**: for the 10–20 highest-degree nodes (use `--stats` degree output), run SKILL.md Stage 3 proposals. Cold-start graphs gain the most from `improves-on`/`uses-dataset` on hub nodes.
6. **Deliverables**: `graph.json`, `graph.dot`, a Chinese summary (规模统计 / 主要簇 / 证据缺口清单), and an `ontology.md` decision note if any custom types were adopted.

**Stop points**: after step 3 (typing approval), after step 4 (ontology sign-off), after step 5 (proposal approval).

**Cold-start pitfalls**: don't try to type every note in one pass — accuracy collapses past ~30 notes; don't resolve ambiguous wikilink targets by guessing — mark unresolved and ask; don't import folder hierarchy as `topic` structure without checking the folders actually mean something.

## Playbook B — Incremental: add new papers to an existing graph

**Triggers**: "这批新论文加进图里", "incremental update", "我上周又读了5篇".

1. **Scope the delta**: identify the new/changed notes only (file mtimes, git status, or a user-supplied list). Never rebuild-and-retype the whole vault — existing frontmatter is settled fact.
2. **Rebuild projection**: run `build_graph.py` again (the projection is always rebuilt wholesale; only *frontmatter edits* are incremental). Diff against the previous `graph.json` if one was kept: new nodes, new unresolved links, new warnings.
3. **Type the newcomers**: same batch-table approval as Playbook A step 3, but smaller.
4. **Attach, don't float**: for each new paper note, the key question is *where it connects to the existing graph*. For each new node, search the vault for the 2–3 most likely existing neighbors (same task? same dataset? claims to improve an existing method?) and propose those edges first, with evidence quotes. A new node that ends the pass with zero typed edges is a failure — either propose connections or tell the user the note doesn't connect to anything yet.
5. **Alias sweep**: new papers often re-name existing concepts ("instruction tuning" vs. "instruction-tuning"). Check new unresolved concept placeholders against existing node labels/aliases; propose merges per `graph-schema.md` rules.
6. **Deliverables**: updated `graph.json`, a short Chinese delta report (新增节点/边数、接入位置、未接入的孤立笔记、证据缺口).

**Stop points**: proposal approval (steps 3–5 can be one combined table for a small batch).

**Incremental pitfalls**: re-proposing relations that were previously rejected — keep rejected proposals in the overlay/proposal log and skip them; letting new notes introduce near-duplicate concepts instead of linking to existing ones.

## Playbook C — Pre-survey: trace the landscape and locate citations before writing

**Triggers**: "我要写综述/related work，先梳理脉络", "survey prep", "帮我定位每个论点该引哪篇".

1. **Frame the survey scope with the user**: 1–3 seed topics, time window, inclusion bar (e.g. only papers with `evaluates-on` evidence in the vault). Write the scope down — expansion budgets depend on it.
2. **Build/refresh the projection** and run `--stats` to find the hubs and isolated nodes; isolated nodes in scope are notes you read but never linked — flag them, they're likely survey blind spots.
3. **Lineage extraction**: for each seed, use `--query <graph.json> --seed <node> --depth 2 --relations improves-on,extends,outperforms,uses-dataset,evaluates-on,cites` to pull the lineage subgraph. Then follow `graph-rag.md` §4 (temporal narration) to produce the year-ordered 演进叙述.
4. **Fork/divergence mapping**: if the field split into competing lines, use `graph-rag.md` §3 (comparative mode) to identify the divergence nodes and write the 分叉点分析.
5. **Claim → citation table**: the deliverable that makes this a *survey prep* rather than a summary. For every sentence-level claim the user plans to make (论点), produce: 论点 / 支撑节点 / 证据引文 (file:line + quote) / 对应 paper 节点（即该引的 citekey）. Claims with no evidence anchor go into a 待补引 list — never invent a citation.
6. **Gap report**: `contradicts` edges and missing relations in scope = the survey's "open problems" section raw material. List them explicitly.
7. **Deliverables**: 脉络叙述（中文、带证据锚点）、分叉点分析、论点–引用对照表（Markdown 表）、待补引清单、可选的 Mermaid/DOT 子图.

**Stop points**: after step 1 (scope sign-off), after step 5 (citation table review — this is what the user pastes into their draft workflow, often continuing with `paper-writing-assistant` for the actual prose).

**Survey-prep pitfalls**: narrating beyond the vault (the graph only knows what the notes say — say so when coverage is thin); citing a paper because it's famous rather than because the graph holds evidence for the specific claim; letting the citation table grow past the scope agreed in step 1.
