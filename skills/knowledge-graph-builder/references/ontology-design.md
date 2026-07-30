# Ontology Design — Custom Types, Naming, Granularity, Evolution

Read this when the built-in ontology in `graph-schema.md` does not fit the user's domain, when duplicate/messy concept names keep appearing, or when the graph is about to be restructured. Design decisions here are expensive to change later — make them deliberately and record them.

## 1. When to add a custom node or relation type

The built-in types (`paper/method/dataset/task/metric/topic/note`) cover most ML/CS literature. Add a custom type **only when all three hold**:

1. **A recurring set of nodes shares a role the built-ins cannot express.** One oddball node is not a type — use `topic` or a tag. Rule of thumb: ≥ 5 nodes that would otherwise be mis-typed.
2. **Queries need to filter on it.** A type you never filter by is documentation, not structure. If "list all X" or "expand only along Y" is a real question the user asks, a type earns its place; otherwise use a `topic` node plus `mentions`.
3. **The distinction is stable across papers.** Do not encode a fleeting subfield fashion (e.g. "LLM-agent" as a node type in 2024) — encode it as a `topic` so it can be retired without a migration.

Common legitimate extensions by field:

| Field | Extra node types | Extra relations |
| --- | --- | --- |
| Biomedical | `gene`, `drug`, `disease`, `pathway` | `targets`, `inhibits`, `associated-with` |
| Chemistry | `compound`, `reaction`, `catalyst` | `synthesizes`, `catalyzes` |
| Social science | `theory`, `construct`, `instrument`, `population` | `operationalizes`, `measures`, `moderates` |
| Systems/SE | `system`, `workload`, `hardware` | `deployed-on`, `benchmarked-with` |

Cost reminder: every custom relation must be added to `KNOWN_RELATIONS` in `build_graph.py` (otherwise it degrades to `mentions`), and every custom type should get a DOT shape. Propose the patch, don't silently declare the type in frontmatter.

**Never do this:** inventing relations on the fly inside a single note (`graph: - relation: kinda-related-to`). Unknown relations degrade to `mentions` and pollute the graph silently. If a needed relation is missing, extend the controlled table deliberately.

## 2. Naming conventions

Node ids are normalized (`concept:lower-case-hyphenated`), but the *label* is what users see. Keep labels canonical:

- **Full official name first, abbreviation as alias**: label `FlashAttention`, alias `FA` — not the reverse. Frontmatter `aliases:` is the merge mechanism; the label is the display name.
- **Singular, no version suffix in the concept name**: `bert` the concept vs. `bert-base-uncased` the specific artifact. If versions matter scientifically (BERT vs. BERT-large ablations), make them separate nodes linked by `extends`, not one node with a changelog in the label.
- **No year in labels**: year belongs in paper metadata, not in `transformer-2017`. The graph-rag temporal narration reads years from paper nodes.
- **Datasets keep their canonical capitalization** (`ImageNet`, not `imagenet`); wikilink resolution is case-insensitive on stems, but labels feed DOT/Mermaid rendering.
- **One language per vault for concept labels.** Mixed-language labels for the same concept (`attention mechanism` + `attention`) create duplicate nodes that alias-merge cannot reliably fix. Pick the language of the majority of notes; keep the other in `aliases:`.

## 3. Granularity decisions: one concept or several?

The hardest recurring judgment call. Use these tests:

**Split into two nodes when:**
- The two candidates have **different edge sets**: e.g. "dropout" as a regularizer vs. "MC dropout" as an uncertainty-estimation method — different `evaluates-on` and `improves-on` neighbors → split.
- One **evolved from** the other and papers claim improvements specifically against one (`improves-on` needs distinct endpoints).
- A claim would be **true of one and false of the other** ("X outperforms Y" where Y = v1 but not v2).

**Keep one node when:**
- Every paper uses the terms interchangeably; the split would be editorializing, not reflecting the literature.
- The distinction lives entirely inside one paper's ablation (record it in the note body, not the graph).
- You cannot find an evidence anchor that uses the finer-grained term distinctly.

**The "hub test" for over-merging**: if a node accumulates > ~30 `mentions` edges and its neighbors clearly cluster into groups that never co-occur, it is probably two concepts merged. Split by re-reading the evidence quotes and assigning each a sub-node.

**The "orphan test" for over-splitting**: if a fine-grained node has ≤ 2 edges and its only difference from the parent is a qualifier ("fast X", "large-scale X"), fold it into the parent as an alias or a note-body detail.

## 4. Ontology evolution and migration rules

Ontologies drift as the vault grows. Rules for changing them without corrupting existing facts:

1. **Additions are free.** New relation in `KNOWN_RELATIONS`, new node type — no migration needed; old graphs still validate.
2. **Renames need an alias period.** To rename relation `uses` → `adopts`: add `adopts`, run a scan listing all `uses` edges (use `--csv` and filter), rewrite frontmatter blocks, then remove `uses`. Never rename in place while old declarations remain — half the edges silently degrade to `mentions`.
3. **Type changes are per-note edits.** Changing a node's `type:` frontmatter is local and safe; but changing the *meaning* of a type (e.g. redefining `topic` to exclude areas) requires re-typing all members — do a `--stats` census first to count the blast radius.
4. **Splitting a node**: create the new note with its own `type:`/frontmatter, then edit each *incoming* frontmatter `graph:` block that should now point at the new node (evidence quotes tell you which), then delete the old node's outgoing relations. Keep the old node as a stub with `aliases:` pointing nowhere and a `see: [[new-node]]` line until the next full rebuild is verified clean.
5. **Deprecating a relation**: mark it in the schema doc first, run one release cycle where new proposals must not use it, migrate existing edges, then drop it from `KNOWN_RELATIONS`.
6. **Record decisions**: keep an `ontology.md` note in the vault (excluded from concept typing — give it `type: note`) listing custom types, relations, and each migration with date. This is the changelog that makes the graph maintainable by a future session.
7. **Verify after every migration**: re-run `build_graph.py` and diff warnings before/after. A migration that increases `unknown-relation` or `missing-evidence` warnings is not done.

## 5. Anti-patterns

- ❌ Type-per-paper-design (`type: transformer-variant`) — types are roles, not taxonomies of instances.
- ❌ Relations that duplicate node typing (`is-a`, `instance-of` as edges) — that's what `type:` is for; hierarchy belongs in `topic` grouping or note folder structure.
- ❌ Bidirectional synonyms as two relations (`improves-on` + `improved-by`) — pick one direction; inverse queries are derived, not stored.
- ❌ Encoding negation in the predicate (`does-not-improve-on`) — use `contradicts` with evidence.
- ❌ Letting the ontology grow past ~15 relations; beyond that, proposers stop distinguishing them and everything collapses to `uses`.
