#!/usr/bin/env python3
"""Generate an Obsidian-excalidraw-plugin compatible .excalidraw.md scene.

Purpose: turn a small declarative JSON (nodes + edges) into a hand-drawn-style
schematic that opens directly in Obsidian (excalidraw-plugin) or imports into
excalidraw.com. Handles the fiddly parts: Text Elements section ids, bound
container text, arrow bindings, and a simple layered auto-layout.

Dependencies: none (Python 3.8+ stdlib only).

Input JSON:
  {
    "nodes": [{"id": "a", "label": "Data Loader", "x": 0, "y": 0}, ...],
    "edges": [{"from": "a", "to": "b", "label": "reads"}, ...]
  }
  x/y are optional; omitted nodes get an automatic layered layout (topological
  depth from edges, grid fallback for cycles). Extra per-node keys "color"
  (backgroundColor) and "shape" ("rectangle"|"ellipse"|"diamond") are honored.

CLI:
  python3 excalidraw_gen.py scene.json --out arch.excalidraw.md [--seed 42]
  python3 excalidraw_gen.py scene.json --out arch.svg   # simple SVG fallback

Output: an .excalidraw.md file (frontmatter `excalidraw-plugin: parsed`,
`# Excalidraw Data` with `## Text Elements` + `## Drawing` JSON block wrapped
in %% comments), or a plain SVG when the output path ends in .svg.
"""

import argparse
import json
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NODE_W, NODE_H = 160.0, 60.0
GAP_X, GAP_Y = 80.0, 70.0
FONT_SIZE = 16
STROKE = "#1e1e1e"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("scene", help="input JSON with nodes/edges")
    p.add_argument("--out", required=True, help="output .excalidraw.md (or .svg)")
    p.add_argument("--seed", type=int, default=42, help="seed for excalidraw element jitter")
    p.add_argument("--roughness", type=float, default=1.0, help="0 = clean lines, 1 = hand-drawn")
    return p.parse_args()


def auto_layout(nodes, edges):
    """Assign x/y to nodes lacking coordinates: layered by longest-path depth."""
    ids = [n["id"] for n in nodes]
    deps = {i: set() for i in ids}
    for e in edges:
        if e["from"] in deps and e["to"] in deps:
            deps[e["to"]].add(e["from"])
    depth = {}

    def depth_of(i, stack):
        if i in depth:
            return depth[i]
        if i in stack:  # cycle: break it
            return 0
        stack.add(i)
        d = 1 + max((depth_of(p, stack) for p in deps[i]), default=-1)
        stack.discard(i)
        depth[i] = d
        return d

    for i in ids:
        depth_of(i, set())
    columns = {}
    for i in ids:
        columns.setdefault(depth[i], []).append(i)
    for i in ids:
        depth[i]  # ensure computed
    for n in nodes:
        if "x" in n and "y" in n:
            continue
        col = depth[n["id"]]
        row = columns[col].index(n["id"])
        n["x"], n["y"] = col * (NODE_W + GAP_X), row * (NODE_H + GAP_Y)


def base_element(eid, etype, x, y, w, h, rng, **extra):
    el = {
        "id": eid, "type": etype, "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": STROKE, "backgroundColor": "transparent",
        "fillStyle": "hachure", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": extra.pop("roughness", 1), "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": {"type": 3},
        "seed": rng.randint(1, 2**31 - 1), "version": 1, "versionNonce": rng.randint(1, 2**31 - 1),
        "isDeleted": False, "boundElements": [], "updated": 1, "link": None, "locked": False,
    }
    el.update(extra)
    return el


def build_elements(scene, seed, roughness):
    rng = random.Random(seed)
    nodes = scene.get("nodes", [])
    edges = scene.get("edges", [])
    auto_layout(nodes, edges)
    elements, texts = [], []
    node_by_id = {}
    for n in nodes:
        eid, tid = f"node-{n['id']}", f"text-{n['id']}"
        shape = n.get("shape", "rectangle")
        rect = base_element(eid, shape, float(n["x"]), float(n["y"]), NODE_W, NODE_H, rng,
                            roughness=roughness, backgroundColor=n.get("color", "transparent"))
        if shape != "rectangle":
            rect["roundness"] = {"type": 2}
        label = n["label"]
        tw = max(len(label) * FONT_SIZE * 0.6, 10)
        text = base_element(tid, "text", float(n["x"]) + (NODE_W - tw) / 2,
                            float(n["y"]) + (NODE_H - FONT_SIZE * 1.25) / 2, tw, FONT_SIZE * 1.25, rng,
                            roughness=roughness, text=label, fontSize=FONT_SIZE, fontFamily=1,
                            textAlign="center", verticalAlign="middle", containerId=eid,
                            originalText=label, lineHeight=1.25, baseline=18)
        rect["boundElements"] = [{"id": tid, "type": "text"}]
        elements += [rect, text]
        texts.append((tid, label))
        node_by_id[n["id"]] = rect
    for i, e in enumerate(edges):
        a, b = node_by_id.get(e["from"]), node_by_id.get(e["to"])
        if not a or not b:
            print(f"warning: edge {e!r} references unknown node, skipped", file=sys.stderr)
            continue
        aid = f"arrow-{i}"
        x1, y1 = a["x"] + a["width"], a["y"] + a["height"] / 2
        x2, y2 = b["x"], b["y"] + b["height"] / 2
        if x2 < x1:  # backwards edge: attach left/right instead
            x1, y1 = a["x"], a["y"] + a["height"] / 2
            x2, y2 = b["x"] + b["width"], b["y"] + b["height"] / 2
        arrow = base_element(aid, "arrow", x1, y1, abs(x2 - x1), abs(y2 - y1), rng,
                             roughness=roughness,
                             points=[[0, 0], [x2 - x1, y2 - y1]],
                             lastCommittedPoint=None,
                             startBinding={"elementId": a["id"], "focus": 0, "gap": 2},
                             endBinding={"elementId": b["id"], "focus": 0, "gap": 2},
                             startArrowhead=None, endArrowhead="arrow")
        a["boundElements"].append({"id": aid, "type": "arrow"})
        b["boundElements"].append({"id": aid, "type": "arrow"})
        elements.append(arrow)
        if e.get("label"):
            tid = f"text-edge-{i}"
            label = e["label"]
            tw = len(label) * FONT_SIZE * 0.55
            lx, ly = (x1 + x2) / 2 - tw / 2, (y1 + y2) / 2 - FONT_SIZE
            elements.append(base_element(tid, "text", lx, ly, tw, FONT_SIZE * 1.25, rng,
                                         roughness=roughness, text=label, fontSize=FONT_SIZE,
                                         fontFamily=1, textAlign="center", verticalAlign="top",
                                         containerId=None, originalText=label, lineHeight=1.25,
                                         baseline=18))
            texts.append((tid, label))
    return elements, texts


def write_excalidraw_md(path, elements, texts):
    doc = {
        "type": "excalidraw", "version": 2,
        "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.0.0",
        "elements": elements,
        "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }
    text_lines = "\n".join(f"{label} ^{tid}" for tid, label in texts)
    content = (
        "---\n"
        "excalidraw-plugin: parsed\n"
        "tags: [excalidraw]\n"
        "---\n"
        "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==\n\n"
        "# Excalidraw Data\n\n"
        "## Text Elements\n"
        f"{text_lines}\n\n"
        "%%\n"
        "## Drawing\n"
        "```json\n"
        f"{json.dumps(doc, indent=2)}\n"
        "```\n"
        "%%\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_svg(path, elements, texts):
    shapes = {e["id"]: e for e in elements}
    max_x = max(e["x"] + e["width"] for e in elements) + 20
    max_y = max(e["y"] + e["height"] for e in elements) + 20
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{max_x:.0f}" height="{max_y:.0f}" '
        f'viewBox="0 0 {max_x:.0f} {max_y:.0f}" font-family="sans-serif">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#1e1e1e"/></marker></defs>',
    ]
    for e in elements:
        if e["type"] == "rectangle":
            fill = e["backgroundColor"] if e["backgroundColor"] != "transparent" else "white"
            parts.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["width"]}" height="{e["height"]}" '
                         f'rx="6" fill="{fill}" stroke="#1e1e1e" stroke-width="1.5"/>')
        elif e["type"] == "ellipse":
            parts.append(f'<ellipse cx="{e["x"] + e["width"] / 2}" cy="{e["y"] + e["height"] / 2}" '
                         f'rx="{e["width"] / 2}" ry="{e["height"] / 2}" fill="white" '
                         f'stroke="#1e1e1e" stroke-width="1.5"/>')
        elif e["type"] == "arrow":
            (x1, y1), (x2, y2) = (e["x"], e["y"]), (e["x"] + e["points"][1][0], e["y"] + e["points"][1][1])
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1e1e1e" '
                         f'stroke-width="1.5" marker-end="url(#arrow)"/>')
        elif e["type"] == "text":
            parts.append(f'<text x="{e["x"] + e["width"] / 2}" y="{e["y"] + e["height"] / 2}" '
                         f'font-size="{e["fontSize"]}" text-anchor="middle" '
                         f'dominant-baseline="middle">{esc(e["text"])}</text>')
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main():
    args = parse_args()
    with open(args.scene, encoding="utf-8") as f:
        scene = json.load(f)
    elements, texts = build_elements(scene, args.seed, args.roughness)
    if args.out.endswith(".svg"):
        write_svg(args.out, elements, texts)
    else:
        write_excalidraw_md(args.out, elements, texts)
    print(f"wrote {args.out} ({len(elements)} elements, {len(texts)} text elements)")


if __name__ == "__main__":
    main()
