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
  Nodes grow around their center to fit multi-line labels ("\n"), and edges
  between the same node pair fan out into curves so bidirectional flows stay
  readable. The SVG fallback renders all of the above (multi-line text,
  diamond shapes, boundary-attached curved edges, halo-backed edge labels).

CLI:
  python3 excalidraw_gen.py scene.json --out arch.excalidraw.md [--seed 42]
  python3 excalidraw_gen.py scene.json --out arch.svg   # simple SVG fallback

Output: an .excalidraw.md file (frontmatter `excalidraw-plugin: parsed`,
`# Excalidraw Data` with `## Text Elements` + `## Drawing` JSON block wrapped
in %% comments), or a plain SVG when the output path ends in .svg.
"""

import argparse
import json
import math
import os
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
SUBTEXT = "#495057"  # secondary line color for multi-line labels


def label_lines(label):
    """Split a node/edge label into display lines."""
    return [ln for ln in str(label).split("\n") if ln.strip()] or [""]


def line_px(line, fs=FONT_SIZE):
    """Rough pixel width of one text line (proportional-font estimate)."""
    wide = sum(1 for ch in line if ord(ch) > 0x2E7F)
    return (len(line) - wide) * fs * 0.60 + wide * fs


def node_size(node):
    """(w, h) for a node, grown to fit its label; never smaller than the defaults."""
    lines = label_lines(node["label"])
    w = max(NODE_W * 0.75, max(line_px(ln) for ln in lines) + 36)
    h = max(NODE_H * 0.85, len(lines) * FONT_SIZE * 1.3 + 22)
    if node.get("shape") == "diamond":
        # text must fit inside the inscribed ellipse-ish region
        w *= 1.45
        h *= 1.6
    return w, h


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.add_argument("scene", help="input JSON with nodes/edges")
    p.add_argument("--out", required=True, help="output .excalidraw.md (or .svg)")
    p.add_argument("--force", action="store_true", help="replace an existing output file")
    p.add_argument("--seed", type=int, default=42, help="seed for excalidraw element jitter")
    p.add_argument("--roughness", type=float, default=1.0, help="0 = clean lines, 1 = hand-drawn")
    return p.parse_args()


def auto_layout(nodes, edges, size_of):
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
    placed = {n["id"] for n in nodes if "x" in n and "y" in n}
    col_x, acc = {}, 0.0
    for col in sorted(columns):
        col_x[col] = acc
        acc += max(size_of[i][0] for i in columns[col]) + GAP_X
    for n in nodes:
        if "x" in n and "y" in n:
            continue
        col = depth[n["id"]]
        col_nodes = columns[col]
        row = col_nodes.index(n["id"])
        y = sum(size_of[i][1] + GAP_Y for i in col_nodes[:row])
        n["x"], n["y"] = col_x[col], y
    # Grow hand-placed nodes around their original center so layouts stay put.
    for n in nodes:
        if n["id"] not in placed:
            continue
        w, h = size_of[n["id"]]
        cx, cy = n["x"] + NODE_W / 2, n["y"] + NODE_H / 2
        n["x"], n["y"] = cx - w / 2, cy - h / 2


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
    size_of = {n["id"]: node_size(n) for n in nodes}
    auto_layout(nodes, edges, size_of)
    elements, texts = [], []
    node_by_id = {}
    for n in nodes:
        eid, tid = f"node-{n['id']}", f"text-{n['id']}"
        shape = n.get("shape", "rectangle")
        w, h = size_of[n["id"]]
        rect = base_element(eid, shape, float(n["x"]), float(n["y"]), w, h, rng,
                            roughness=roughness, backgroundColor=n.get("color", "transparent"))
        if shape != "rectangle":
            rect["roundness"] = {"type": 2}
        label = n["label"]
        lines = label_lines(label)
        tw = max(max(line_px(ln) for ln in lines), 10)
        th = len(lines) * FONT_SIZE * 1.25
        text = base_element(tid, "text", float(n["x"]) + (w - tw) / 2,
                            float(n["y"]) + (h - th) / 2, tw, th, rng,
                            roughness=roughness, text=label, fontSize=FONT_SIZE, fontFamily=1,
                            textAlign="center", verticalAlign="middle", containerId=eid,
                            originalText=label, lineHeight=1.25, baseline=18)
        rect["boundElements"] = [{"id": tid, "type": "text"}]
        elements += [rect, text]
        texts.append((tid, label))
        node_by_id[n["id"]] = rect

    def boundary_point(el, tx, ty):
        """Point where the line center->target exits the node shape."""
        cx, cy = el["x"] + el["width"] / 2, el["y"] + el["height"] / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            dx = 1.0
        w2, h2 = el["width"] / 2, el["height"] / 2
        if el["type"] == "ellipse":
            t = 1.0 / (math.hypot(dx / w2, dy / h2) or 1.0)
        elif el["type"] == "diamond":
            t = 1.0 / ((abs(dx) / w2 + abs(dy) / h2) or 1.0)
        else:  # rectangle
            t = min(w2 / abs(dx) if dx else float("inf"),
                    h2 / abs(dy) if dy else float("inf"))
        return cx + dx * t, cy + dy * t

    # Group edges by unordered node pair to fan out bidirectional/parallel edges.
    groups = {}
    for i, e in enumerate(edges):
        groups.setdefault(frozenset((e["from"], e["to"])), []).append(i)

    for i, e in enumerate(edges):
        a, b = node_by_id.get(e["from"]), node_by_id.get(e["to"])
        if not a or not b:
            print(f"warning: edge {e!r} references unknown node, skipped", file=sys.stderr)
            continue
        aid = f"arrow-{i}"
        ac = (a["x"] + a["width"] / 2, a["y"] + a["height"] / 2)
        bc = (b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
        x1, y1 = boundary_point(a, *bc)
        x2, y2 = boundary_point(b, *ac)
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy) or 1.0
        # left-of-travel unit perpendicular
        px, py = -dy / dist, dx / dist
        mates = groups[frozenset((e["from"], e["to"]))]
        bend = 0.0 if len(mates) == 1 else 0.16 + 0.10 * mates.index(i)
        cxp, cyp = (x1 + x2) / 2 + px * bend * dist, (y1 + y2) / 2 + py * bend * dist
        points = [[0, 0], [x2 - x1, y2 - y1]] if bend == 0 else \
            [[0, 0], [cxp - x1, cyp - y1], [x2 - x1, y2 - y1]]
        arrow = base_element(aid, "arrow", x1, y1, abs(x2 - x1), abs(y2 - y1), rng,
                             roughness=roughness,
                             points=points,
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
            efs = FONT_SIZE - 2
            tw = max(line_px(ln, efs) for ln in label_lines(label))
            # label sits at the curve midpoint, nudged off the stroke
            if bend:
                lx_c = 0.25 * x1 + 0.5 * cxp + 0.25 * x2
                ly_c = 0.25 * y1 + 0.5 * cyp + 0.25 * y2
            else:
                lx_c, ly_c = (x1 + x2) / 2, (y1 + y2) / 2
            lift = efs * 0.9 if bend == 0 else efs * 0.55
            lx, ly = lx_c + px * lift - tw / 2, ly_c + py * lift - efs * 0.7
            elements.append(base_element(tid, "text", lx, ly, tw, efs * 1.25, rng,
                                         roughness=roughness, text=label, fontSize=efs,
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
    # Text Elements contract: one line per entry, "label ^id" — flatten newlines.
    text_lines = "\n".join(f"{' '.join(label.splitlines())} ^{tid}" for tid, label in texts)
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


def _svg_label(cx, cy, label, fs, edge=False):
    """Multi-line SVG <text>: first line full-size, following lines smaller/gray."""
    lines = label_lines(label)
    step = fs * 1.3
    y0 = cy - (len(lines) - 1) * step / 2
    out = []
    for k, ln in enumerate(lines):
        size = fs if k == 0 else max(fs - 3, 10)
        fill = STROKE if k == 0 else SUBTEXT
        weight = ' font-weight="600"' if k == 0 and not edge else ""
        out.append(f'<text x="{cx:.1f}" y="{y0 + k * step:.1f}" font-size="{size}" '
                   f'text-anchor="middle" dominant-baseline="central" fill="{fill}"{weight}>'
                   f'{esc(ln)}</text>')
    return out


def write_svg(path, elements, texts):
    margin = 24.0
    min_x = min(e["x"] for e in elements) - margin
    min_y = min(e["y"] for e in elements) - margin
    max_x = max(e["x"] + e["width"] for e in elements) + margin
    max_y = max(e["y"] + e["height"] for e in elements) + margin
    for e in elements:  # bent arrows can overshoot their bounding box
        if e["type"] == "arrow" and len(e["points"]) > 2:
            cx, cy = e["x"] + e["points"][1][0], e["y"] + e["points"][1][1]
            min_x, min_y = min(min_x, cx - margin), min(min_y, cy - margin)
            max_x, max_y = max(max_x, cx + margin), max(max_y, cy + margin)
    w, h = max_x - min_x, max_y - min_y
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="{min_x:.1f} {min_y:.1f} {w:.1f} {h:.1f}" font-family="sans-serif">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{STROKE}"/></marker></defs>',
    ]
    shapes, labels = [], []
    for e in elements:
        if e["type"] == "rectangle":
            fill = e["backgroundColor"] if e["backgroundColor"] != "transparent" else "white"
            shapes.append(f'<rect x="{e["x"]:.1f}" y="{e["y"]:.1f}" width="{e["width"]:.1f}" '
                          f'height="{e["height"]:.1f}" rx="8" fill="{fill}" stroke="{STROKE}" '
                          f'stroke-width="1.5"/>')
        elif e["type"] == "ellipse":
            fill = e["backgroundColor"] if e["backgroundColor"] != "transparent" else "white"
            shapes.append(f'<ellipse cx="{e["x"] + e["width"] / 2:.1f}" cy="{e["y"] + e["height"] / 2:.1f}" '
                          f'rx="{e["width"] / 2:.1f}" ry="{e["height"] / 2:.1f}" fill="{fill}" '
                          f'stroke="{STROKE}" stroke-width="1.5"/>')
        elif e["type"] == "diamond":
            cx, cy = e["x"] + e["width"] / 2, e["y"] + e["height"] / 2
            fill = e["backgroundColor"] if e["backgroundColor"] != "transparent" else "white"
            pts = f'{cx:.1f},{e["y"]:.1f} {e["x"] + e["width"]:.1f},{cy:.1f} ' \
                  f'{cx:.1f},{e["y"] + e["height"]:.1f} {e["x"]:.1f},{cy:.1f}'
            shapes.append(f'<polygon points="{pts}" fill="{fill}" stroke="{STROKE}" '
                          f'stroke-width="1.5" stroke-linejoin="round"/>')
        elif e["type"] == "arrow":
            pts = [(e["x"] + p[0], e["y"] + p[1]) for p in e["points"]]
            if len(pts) > 2:
                d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f} Q {pts[1][0]:.1f} {pts[1][1]:.1f} ' \
                    f'{pts[2][0]:.1f} {pts[2][1]:.1f}'
                shapes.append(f'<path d="{d}" fill="none" stroke="{STROKE}" stroke-width="1.5" '
                              f'marker-end="url(#arrow)"/>')
            else:
                shapes.append(f'<line x1="{pts[0][0]:.1f}" y1="{pts[0][1]:.1f}" x2="{pts[1][0]:.1f}" '
                              f'y2="{pts[1][1]:.1f}" stroke="{STROKE}" stroke-width="1.5" '
                              f'marker-end="url(#arrow)"/>')
        elif e["type"] == "text":
            labels.append(e)
    parts += shapes
    for e in labels:  # labels on top; edge labels get a white halo for legibility
        cx, cy = e["x"] + e["width"] / 2, e["y"] + e["height"] / 2
        fs = e["fontSize"]
        if e["id"].startswith("text-edge-"):
            bw = max(line_px(ln, fs) for ln in label_lines(e["text"])) + 10
            bh = fs + 6
            parts.append(f'<rect x="{cx - bw / 2:.1f}" y="{cy - bh / 2:.1f}" width="{bw:.1f}" '
                         f'height="{bh:.1f}" rx="4" fill="white" fill-opacity="0.88"/>')
        parts += _svg_label(cx, cy, e["text"], fs, edge=e["id"].startswith("text-edge-"))
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main():
    args = parse_args()
    if os.path.abspath(args.out) == os.path.abspath(args.scene):
        sys.exit("output must not replace the scene JSON input")
    if os.path.exists(args.out) and not args.force:
        sys.exit(f"output exists: {args.out}; use --force to replace it")
    with open(args.scene, encoding="utf-8") as f:
        scene = json.load(f)
    elements, texts = build_elements(scene, args.seed, args.roughness)
    if not elements:
        sys.exit("scene has no nodes — nothing to draw")
    if args.out.endswith(".svg"):
        write_svg(args.out, elements, texts)
    else:
        write_excalidraw_md(args.out, elements, texts)
    print(f"wrote {args.out} ({len(elements)} elements, {len(texts)} text elements)")


if __name__ == "__main__":
    main()
