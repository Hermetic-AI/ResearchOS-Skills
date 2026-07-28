# Graph Schema — Controlled Ontology

The graph is a property graph over Markdown notes. **The fact source is the notes themselves** (files + frontmatter); the JSON/DOT output of `build_graph.py` is a rebuildable projection, never the source of truth.

## 1. Node types

| Type | Meaning | Typical origin |
| --- | --- | --- |
| `paper` | A cited publication (DOI, `@citekey`, `\cite{key}`) | citation syntax, `type: paper` frontmatter |
| `method` | A technique/model/algorithm (e.g. FlashAttention, LoRA) | concept note with `type: method` |
| `dataset` | A dataset or benchmark corpus (e.g. ImageNet, MMLU) | `type: dataset` |
| `task` | An evaluation task/problem (e.g. machine translation) | `type: task` |
| `metric` | An evaluation metric (e.g. BLEU, perplexity) | `type: metric` |
| `topic` | A research area/theme that groups the above (e.g. efficient attention) | `type: topic` |
| `note` | A plain literature/reading note (default for any scanned `.md`) | fallback type |

Typing rules (in priority order):

1. Explicit `type:` field in the note's frontmatter wins.
2. A wikilink/citation *target* node gets its type from the target note's frontmatter if that note exists.
3. Heuristic fallback: DOI-shaped or `@citekey` targets → `paper`; everything else → `note`/`concept` until the user assigns a type.

Node identity: `note:<vault-relative path>` for files, `paper:<citekey or normalized DOI>` for papers, `concept:<lowercased name>` for concept targets. Merge case variants, plural/singular, and frontmatter `aliases:` entries into one node — but only after user confirmation.

## 2. Built-in relation table

Only these predicates are allowed. Unknown relations must degrade to `mentions` — never invent new predicates on the fly.

| Relation | From → To | Meaning | Deterministic? |
| --- | --- | --- | --- |
| `mentions` | note/paper → any | `[[wikilink]]` reference | ✅ syntax-derived |
| `cites` | note/paper → paper | `@citekey` or `\cite{key}` | ✅ syntax-derived |
| `uses` | paper/note → method/dataset | uses the method or dataset | ❌ explicit/proposal only |
| `uses-dataset` | paper/note → dataset | trains/evaluates on the dataset | ❌ |
| `evaluates-on` | paper/note → task/metric | reports results on task/metric | ❌ |
| `improves-on` | method/paper → method/paper | is a direct improvement of | ❌ |
| `outperforms` | method/paper → method/paper | beats on some metric (metric should appear in evidence) | ❌ |
| `extends` | method → method | generalizes/extends | ❌ |
| `implements` | repo/note → paper/method | provides an implementation | ❌ |
| `supports` / `contradicts` | paper/note → paper/note | evidential stance | ❌, evidence mandatory |

Deterministic relations are auto-confirmed from syntax position. All ❌ relations must either come from an explicit frontmatter declaration or from the AI proposal → user approval pipeline (§4).

## 3. Evidence anchors (mandatory)

Every relation edge carries an evidence record:

```json
{
  "source": "notes/flash-attention.md",
  "line": 42,
  "quote": "FlashAttention improves on standard attention by IO-aware tiling..."
}
```

- Deterministic edges: evidence is the syntax position (file + line of the wikilink/citation). `build_graph.py` generates this automatically.
- Frontmatter-declared edges: the `evidence` field is **required**. Edges missing it are still emitted but flagged in the warnings report — treat them as incomplete and ask the user to fill in the anchor.
- AI-proposed edges: must quote a verbatim snippet. A proposal without a quote is rejected before it ever reaches the user.

## 4. Frontmatter declaration format

Semantic relations that cannot be inferred from syntax live in the note's frontmatter under `graph:`:

```yaml
---
type: method
aliases: [FA, Flash Attention]
graph:
  - relation: improves-on
    target: "[[multi-head-attention]]"
    evidence:
      line: 42
      quote: "FlashAttention improves on standard attention by IO-aware tiling"
    note: direct improvement claim
  - relation: evaluates-on
    target: "[[perplexity]]"
    evidence:
      line: 87
      quote: "we report perplexity on WikiText-103"
---
```

- `target` may be a `[[wikilink]]`, `@citekey`, or a bare node id (`concept:...`, `paper:...`).
- `evidence.line` refers to a line in the *same file*; `evidence.quote` is a verbatim substring of that line's neighborhood. The script warns when the quote cannot be found in the file (stale evidence).
- AI approval flow: propose → user approves → the agent writes the block above into frontmatter → re-run `build_graph.py`. The agent never writes relations anywhere else.

## 5. Validation checklist (what the script warns about)

- Frontmatter relation missing `evidence` → **error-level warning**.
- `evidence.quote` not found in source file → stale-evidence warning.
- Unknown relation name → degraded to `mentions` + warning.
- Wikilink target with no matching file → placeholder node + unresolved warning.
- Duplicate edges (same from/to/relation/source) → deduplicated silently.
