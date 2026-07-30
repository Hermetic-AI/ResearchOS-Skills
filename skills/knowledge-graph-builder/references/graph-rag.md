# Graph-Guided Lineage Tracing (Graph RAG)

How to turn the built graph into a research-lineage narrative without hallucinating structure that is not in the notes.

## 1. Pipeline: recall → expand → prune → narrate

### Step 1 — Seed recall

Map the user's question to seed nodes:

- Exact/id match first: node id, note title, alias.
- Then case-insensitive substring match over labels and aliases.
- If several candidates tie, list them and let the user pick; do not guess.
- If nothing matches, say so — do not substitute a "close enough" concept from general knowledge.

### Step 2 — Budgeted layer-by-layer expansion

Expand from seeds along **whitelisted relations only** (`uses`, `uses-dataset`, `evaluates-on`, `improves-on`, `outperforms`, `extends`, `implements`, `supports`, `contradicts`, plus `cites` for papers). Plain `mentions` edges are noise for lineage — exclude them unless the user asks for a co-mention map.

Budgets (defaults, adjust to graph size):

- Depth: 1 hop by default, max 2 hops on explicit request.
- Per-layer cap: 25 edges; global cap: 100 nodes / 200 edges.
- Order each layer by evidence quality (typed relation > citation > mention) then by paper year if available; truncate the tail and record `truncated: true`.

### Step 3 — Prune

- Drop nodes with no evidence-anchored relation to any seed.
- Drop duplicate paths; keep the shortest evidence-bearing path per node.
- For high-degree hubs (e.g. a popular dataset), keep only edges whose evidence mentions the seed context.

### Step 4 — Narrate

Write the lineage in English (user-facing), structured as:

1. **Main line** (time/evolution-ordered improves-on/extends chain) — each hop stated as "A improves on B at X (evidence: file:line cited text)".
2. **Branches** (parallel methods, different task/dataset combinations).
3. **Controversies/gaps** (contradicts edges, insufficient-evidence spots).

Rules:

- **Every claim cites its evidence anchor** (`filename:line` or `PDF page/chapter` + brief cited text + verification state). A claim without an anchor is deleted, not softened.
- When the subgraph is sparse or contradictory, say "graph evidence insufficient" and list which relation is missing — propose Stage-3 relation proposals to fill the gap, but never fill it from general knowledge.
- Mark derived-from-graph vs. user-approved-proposal relations if both appear.

## 2. Answering "how did X evolve" — worked pattern

1. Seed = the method node X.
2. Backward chain: follow incoming `improves-on`/`extends` to ancestors (roots of the lineage).
3. Forward chain: outgoing same relations to descendants.
4. Attach `uses-dataset`/`evaluates-on` leaves at each chain node for context.
5. Sort by paper year when available; note where year is missing and ordering is inferred from relation direction only.

## 3. Comparative mode — finding the divergence points of two research lines

For "when/why did route A and route B diverge" questions. Goal: locate the **divergence node** — the last common ancestor — and the **discriminating edges** that separate the two lines.

1. **Anchor both lines**: seed nodes A and B (usually two methods or two topics). If the user names the lines loosely ("efficiency camp vs accuracy camp"), first resolve each to concrete nodes — refuse to run the comparison on vibes.
2. **Trace ancestors of each seed** along `improves-on`/`extends` (incoming direction), depth ≤ 4. Two node sets `anc(A)`, `anc(B)`.
3. **Intersection = shared heritage**. The divergence point is the intersection node closest to the seeds (measured by shortest-path hops). If the intersection is empty, the two lines are independent in this graph — report that as the finding, with the caveat that a missing edge, not a true independence, may be the cause (check for a co-cited survey or a shared dataset hub that hints at an undocumented link).
4. **Discriminating edges**: edges incident on the post-divergence nodes of each line that differ in kind — e.g. line A's nodes carry `uses-dataset → ImageNet` while line B's carry `uses-dataset → internal-corpus`. These are the *reasons* for the split as recorded in the notes; rank them by how many nodes on each side share them.
5. **Narrate** (English): common ancestor → divergence node (evidence anchor) → discriminating choices of each route after divergence (2–3 edges per side, with evidence) → current state (whether the latest nodes of the two lines have `outperforms`/`contradicts` cross-edges — if yes the two lines are still in direct competition, if no they have gone their separate ways).

Rules: every divergence claim cites the edge evidence; if the "split" rests on a single unapproved proposal edge, say so and downgrade the confidence; do not import the real-world reason for a split (compute cost, licensing) unless a note's evidence anchor states it.

## 4. Temporal narration — year-ordered evolution stories

For "tell the evolution of X over time". The graph has no intrinsic time; years come from paper nodes (frontmatter `year:` field, or parse from citekey like `@smith2021foo`). Methods/datasets inherit the year of the earliest paper that `uses`/`implements` them.

1. Extract the lineage subgraph (§2 steps 2–4).
2. **Assign years**: paper nodes → their `year`; concept nodes → min year of adjacent papers; nodes with no inferable year go into an "unknown era" bucket at the end — do not guess from model knowledge.
3. **Sort and bucket**: ascending year; within a year, order by dependency direction (`improves-on` source after target — a 2021 paper cannot improve a 2022 one; if the edges say it does, flag the inconsistency rather than silently reordering).
4. **Write the narrative** as year-bucketed paragraphs: "**2017**: Transformer proposed (evidence…). **2018**: BERT extends Transformer…" Each sentence cites its anchor. Where two nodes share a year and no edge orders them, present them as parallel developments — never invent a sequence.
5. **Call out temporal anomalies**: a method whose earliest citing paper is 5+ years after its lineage neighbors (possible revival — worth a sentence); a dense cluster in one year (field inflection point); a gap of several years with no nodes (either a real lull or a vault coverage gap — check `--stats` and say which).

## 5. Community / cluster analysis (conceptual)

The zero-dependency script does not run community detection, but you can reason about clusters directly from the JSON:

- **What a "community" means here**: a set of nodes more densely connected *to each other* (via whitelisted relations, ignoring `mentions`) than to the rest of the graph. In a literature graph these typically correspond to subfields or problem camps.
- **Cheap detection without libraries**: use `--stats` connected components (components = the coarsest clustering — two components mean two literatures that never cite each other in this vault); for finer structure, take a high-degree hub's ego-network at depth 1 and look for neighbor sets that overlap heavily across hubs (two hubs sharing > 50% of neighbors are likely one community with two names — check for a missed alias merge).
- **Hub-vs-bridge distinction**: high *within-cluster* degree = hub (defines the subfield); edges *between* clusters = bridges (usually survey papers, shared datasets, or transfer methods). Bridges are the most valuable nodes for survey writing — they are where cross-field claims live. Identify them from the `--csv` edge export by finding edges whose endpoints belong to different components of the `improves-on`-only subgraph.
- **Report clusters in English** as: cluster naming (using the highest-degree topic/method node within the cluster) / size / core hub / bridge nodes / evidence strength (proportion of intra-cluster edges that are frontmatter-declared — a low-proportion cluster is a signal that "you think it's one field but the graph has no evidence for it").
- For serious community detection (Louvain etc.), export `--csv` and let the user load it into Gephi/Cytoscape — do not reimplement it here.

## 6. Anti-patterns

- ❌ Using `mentions` co-occurrence to claim "A improves on B".
- ❌ Expanding unbounded BFS over a citation hub and dumping the whole subgraph.
- ❌ Narrating a smooth story over missing edges — gaps must be surfaced as gaps.
- ❌ Treating unapproved proposals as graph facts.
