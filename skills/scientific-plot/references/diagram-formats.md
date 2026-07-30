# Diagram Formats — Excalidraw, Mermaid, Graphviz, PlantUML

## .excalidraw.md (Obsidian excalidraw-plugin)

File skeleton produced by `scripts/excalidraw_gen.py`:

```markdown
---
excalidraw-plugin: parsed
tags: [excalidraw]
---

# Excalidraw Data

## Text Elements
Node label ^textElementId

## Drawing
```json
{"type": "excalidraw", "version": 2, "source": "...",
 "elements": [...], "appState": {...}, "files": {}}
```
%%
```

Key points:

- The `## Text Elements` section lists every text element as `text content ^elementId` — the `^id` is an Obsidian block reference and **must match** the element `id` in the JSON, or the plugin regenerates/mangles text.
- The JSON block is wrapped in `%% ... %%` comments so reading mode hides it.
- Element essentials: `id` (string), `type` (`rectangle` | `arrow` | `text`), `x`, `y`, `width`, `height`, `angle: 0`, `strokeColor`, `backgroundColor`, `fillStyle` (`hachure` for hand-drawn), `strokeWidth: 1`, `roughness: 1`, `opacity: 100`, `seed` (int — pass `--seed` for reproducible jitter), `isDeleted: false`, `boundElements` (arrows on shapes), `groupIds: []`, `link: null`.
- Text elements: `fontSize` (20 default), `fontFamily` (1 = Virgil hand-drawn, 2 = Helvetica, 3 = Cascadia), `text`, `textAlign`, `verticalAlign`, `containerId` (id of the rectangle the text is bound to — the rectangle must list the text id in `boundElements` with `type: "text"`).
- Arrows: `points: [[0,0],[dx,dy]]` relative to x/y; `startBinding: {elementId, focus, gap}`, `endBinding: {...}`; the bound shapes must list the arrow id in their `boundElements` with `type: "arrow"`.
- The generator handles all of the above; hand-edit only for touch-ups, and keep Text Elements and JSON ids in sync.

## SVG fallback

`--out fig.svg` renders the same scene as plain SVG (no Excalidraw needed). The renderer handles:

- **Multi-line labels**: `\n` in node/edge labels becomes stacked lines (first line bold, later lines smaller/gray) — raw `\n` inside `<text>` would collapse into one overflowing line, so never emit unsplit text.
- **Node auto-sizing**: shapes grow around their center to fit the label (min 120×52), so hand-placed `x`/`y` layouts stay put. Leave ≥ ~100 px between node edges for edge labels, or short edges will look cramped.
- **Shapes**: `rectangle`, `ellipse`, `diamond` are all rendered (diamond as polygon). Edges attach at the shape boundary along the center-to-center direction, not just left/right midpoints.
- **Bidirectional / parallel edges**: edges sharing a node pair are fanned out as quadratic curves (bend 0.16 + 0.10 per extra edge) with labels placed at the curve midpoint, so `A→B` and `B→A` no longer overlap.
- **Edge labels**: drawn 2 pt smaller with a white halo rect behind, so they stay legible over strokes.

Keep it under ~40 elements; beyond that, use tier-3 code-as-diagram.

**Exporting PDF / high-res PNG without a renderer**: the generator itself stays zero-dependency (SVG only). When a browser is available, reuse it as the renderer — Edge/Chrome headless works offline:

```bash
# vector PDF (journal submission)
msedge --headless=new --print-to-pdf=fig.pdf --no-pdf-header-footer file:///abs/path/fig.svg
# 300-DPI-class PNG (Word / slides) — 3x scale factor
msedge --headless=new --screenshot=fig.png --force-device-scale-factor=3 \
  --window-size=1600,1100 file:///abs/path/fig.svg
```

(On Windows use the full path, e.g. `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"`; on macOS/Linux substitute `google-chrome`.) Always deliver SVG + PDF; PNG alone is not submission-grade.

## Mermaid patterns and pitfalls

Headers: `flowchart TD|LR`, `sequenceDiagram`, `erDiagram`, `gantt`, `classDiagram`, `stateDiagram-v2`.

- Node labels containing `()`, `[]`, `{}` or spaces **must be quoted**: `A["f(x)"]` not `A[f(x)]`.
- Edge labels: `A -->|label| B`; pipe syntax breaks if the label contains `|`.
- `graph TD` is legacy but still valid; prefer `flowchart TD`.
- Subgraphs need `end`; every `subgraph X` must close.
- sequenceDiagram: arrows are `->>` (solid) / `-->>` (dashed), participants via `participant A as Alice`.
- Render: `npx -y @mermaid-js/mermaid-cli -i in.mmd -o out.svg` (needs network + puppeteer on first run).

## Graphviz DOT patterns and pitfalls

- Header: `digraph G { ... }` (directed) or `graph G { ... }`.
- Statements end with `;` or newline; braces must balance.
- Labels with spaces/punctuation need quotes: `a [label="Load Data"];`.
- Common attributes: `rankdir=LR;`, `node [shape=box, style=rounded];`.
- Edge: `a -> b [label="reads"];` (`--` in undirected graphs).
- Render: `dot -Tsvg in.dot -o out.svg` (also `neato`, `fdp` for other layouts).

## PlantUML (optional, source only)

- Must open `@startuml` and close `@enduml`.
- This environment has no renderer; the user renders locally (plantuml.jar, VS Code plugin, or plantuml.com server). Say so when delivering.
