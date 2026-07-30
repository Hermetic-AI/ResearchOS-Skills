#!/usr/bin/env python3
"""Build a typed concept graph from Markdown notes and paper-note JSON.

Purpose
-------
Scans a notes vault and extracts:
  - [[wikilink]] references (incl. [[target|alias]] and [[target#heading]]),
    skipping fenced code blocks and inline code
  - @citekey citations (pandoc style) and \\cite{key1,key2} (LaTeX style)
  - explicit frontmatter `graph:` relation declarations, each of which must
    carry an `evidence` anchor (line + verbatim quote)
  - schema-versioned ResearchOS `paper-note` JSON claims with page/section,
    extraction-method, and verification provenance preserved on graph edges

Emits a nodes/edges JSON projection, optionally a Graphviz DOT file, and a
warnings report flagging relations that lack required evidence, stale
evidence quotes, unknown relation names, and unresolved wikilink targets.

Dependencies: Python 3.8+ standard library only (no third-party packages).

CLI usage
---------
    python3 build_graph.py <notes_dir> [-o graph.json] [--dot graph.dot]
                           [--warnings warnings.md] [--quiet]

    notes_dir        Directory to scan recursively for Markdown notes and
                     ResearchOS paper-note JSON files.
                     Optional when --query is given (standalone subgraph
                     extraction from an existing graph JSON).
    -o/--out         JSON output path (default: stdout).
    --dot            Also write a Graphviz DOT visualization to this path.
    --warnings       Write a Markdown warnings report to this path
                     (default: warnings are printed to stderr).
    --quiet          Suppress the summary printed to stderr.
    --stats          Add detailed statistics to the JSON output
                     (degree distribution, isolated nodes, connected
                     components) and print a readable summary to stderr.
    --csv PREFIX     Export Gephi/Cytoscape-compatible CSV files:
                     PREFIX.nodes.csv (Id,Label,Type) and
                     PREFIX.edges.csv (Source,Target,Relation).
    --query GRAPH    Standalone mode: load an existing graph JSON instead
                     of scanning notes_dir, and extract a subgraph.
    --seed NODE      Seed node id for --query (repeatable). Matching is
                     exact id first, then case-insensitive label/alias
                     substring; ambiguous matches are listed and refused.
    --depth N        BFS depth for --query (default 1, max 4).
    --relations LIST Comma-separated relation whitelist for --query
                     (default: all relations).

Output format (JSON)
--------------------
    {
      "nodes": [{"id": "note:notes/a.md", "type": "method",
                 "label": "...", "path": "notes/a.md"}, ...],
      "edges": [{"from": "...", "to": "...", "relation": "uses",
                 "origin": "parser|frontmatter",
                 "evidence": {"source": "...", "line": 42, "quote": "..."}},
                 ...],
      "warnings": [{"level": "error|warning", "kind": "...",
                    "message": "...", "source": "...", "line": 12}, ...],
      "stats": {"files": 3, "nodes": 8, "edges": 11, "errors": 0}
    }
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\[\]|#]+)(?:#[^\[\]|]*)?(?:\|[^\[\]]*)?\]\]")
CITEKEY_RE = re.compile(r"(?<![\w/.-])@([A-Za-z][\w:.-]*\w)")
LATEX_CITE_RE = re.compile(r"\\cite[tp]?\*?\{([^}]+)\}")
DOI_RE = re.compile(r"^(?:https?://doi\.org/)?10\.\d{4,9}/\S+$", re.IGNORECASE)

KNOWN_RELATIONS = {
    "mentions", "cites", "uses", "uses-dataset", "evaluates-on",
    "improves-on", "outperforms", "extends", "implements",
    "supports", "contradicts",
}
NODE_TYPES = {"paper", "claim", "method", "dataset", "task", "metric", "topic", "note"}
SKIP_DIRS = {".git", ".researchos", "node_modules", ".obsidian"}
CLAIM_TYPES = {"research-question", "method", "finding", "contribution", "limitation", "interpretation"}
SUPPORT_LEVELS = {"direct", "partial", "context-only"}
EXTRACTION_METHODS = {"native-text", "ocr", "human-transcription", "visual"}
VERIFICATION_STATES = {"exact-match", "human-verified", "unverified"}
CLAIM_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def validate_paper_note_contract(payload):
    """Return compact zero-dependency contract violations for paper-note v1."""
    issues = []
    if payload.get("schema_version") != "1.0.0":
        issues.append("schema_version must be 1.0.0")
    paper = payload.get("paper")
    if not isinstance(paper, dict) or not isinstance(paper.get("title"), str) or not paper["title"].strip():
        issues.append("paper.title is required")
    elif not isinstance(paper.get("authors", []), list):
        issues.append("paper.authors must be an array")
    for field in ("research_question", "method"):
        if not isinstance(payload.get(field), str):
            issues.append(f"{field} must be a string")
    for field in ("contributions", "limitations"):
        if not isinstance(payload.get(field), list):
            issues.append(f"{field} must be an array")
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict) or not isinstance(provenance.get("created_by"), str) or not provenance.get("created_by"):
        issues.append("provenance.created_by is required")
    elif not isinstance(provenance.get("sources"), list):
        issues.append("provenance.sources must be an array")
    claims = payload.get("claims")
    if not isinstance(claims, list) or not claims:
        issues.append("at least one claim is required")
        return issues
    seen = set()
    for position, claim in enumerate(claims):
        prefix = f"claim {position}"
        if not isinstance(claim, dict):
            issues.append(f"{prefix} must be an object")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not CLAIM_ID_RE.fullmatch(claim_id):
            issues.append(f"{prefix}.id is missing or invalid")
        elif claim_id in seen:
            issues.append(f"duplicate claim id '{claim_id}'")
        else:
            seen.add(claim_id)
        if claim.get("claim_type") not in CLAIM_TYPES:
            issues.append(f"{prefix}.claim_type is invalid")
        if not isinstance(claim.get("text"), str) or not claim["text"].strip():
            issues.append(f"{prefix}.text is required")
        if claim.get("support_level") not in SUPPORT_LEVELS:
            issues.append(f"{prefix}.support_level is invalid")
        evidence_items = claim.get("evidence")
        if not isinstance(evidence_items, list) or not evidence_items:
            issues.append(f"{prefix}.evidence must contain at least one anchor")
            continue
        for evidence_index, evidence in enumerate(evidence_items):
            evidence_prefix = f"{prefix}.evidence {evidence_index}"
            if not isinstance(evidence, dict):
                issues.append(f"{evidence_prefix} must be an object")
                continue
            if not isinstance(evidence.get("source"), str) or not evidence["source"].strip():
                issues.append(f"{evidence_prefix}.source is required")
            quote = evidence.get("quote")
            if not isinstance(quote, str) or not quote.strip() or len(quote) > 500:
                issues.append(f"{evidence_prefix}.quote must be 1-500 characters")
            if evidence.get("page") is None and not evidence.get("section"):
                issues.append(f"{evidence_prefix} needs page or section")
            if evidence.get("extraction_method") not in EXTRACTION_METHODS:
                issues.append(f"{evidence_prefix}.extraction_method is invalid")
            if evidence.get("verification") not in VERIFICATION_STATES:
                issues.append(f"{evidence_prefix}.verification is invalid")
    return issues


# ---------------------------------------------------------------- frontmatter

def split_frontmatter(text):
    """Return (frontmatter_lines, body_lines). Both keep original line numbers
    implicitly: body_lines starts right after the closing '---'."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1 :]
    return [], lines


def parse_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        if value[0] == '"':
            # YAML double-quoted scalars use backslash escapes; unescape the
            # common ones so evidence quotes match the raw note body.
            inner = (inner.replace('\\\\', '\x00')
                          .replace('\\"', '"')
                          .replace('\\n', '\n')
                          .replace('\\t', '\t')
                          .replace('\x00', '\\'))
        else:
            # In single-quoted scalars '' is an escaped single quote.
            inner = inner.replace("''", "'")
        return inner
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part) for part in inner.split(",")]
    return value


def parse_frontmatter(fm_lines):
    """Minimal indentation-based parser for the subset of YAML this skill
    uses: top-level scalar keys, inline lists, and a `graph:` list of maps
    with a nested `evidence:` map. Returns a dict."""
    meta = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):  # stray indented line outside a block
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if key == "graph" and not rest:
            items, i = parse_graph_list(fm_lines, i + 1)
            meta["graph"] = items
            continue
        meta[key] = parse_scalar(rest)
        i += 1
    return meta


def parse_graph_list(lines, start):
    """Parse a '- relation: ...' list indented under `graph:`. Returns
    (items, next_line_index)."""
    items = []
    i = start
    current = None
    in_evidence = False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0:  # block ended
            break
        if stripped.startswith("- "):
            current = {}
            items.append(current)
            in_evidence = False
            stripped = stripped[2:].strip()
            if stripped:
                key, _, value = stripped.partition(":")
                current[key.strip()] = parse_scalar(value)
        elif current is not None:
            key, _, value = stripped.partition(":")
            key, value = key.strip(), value.strip()
            if key == "evidence" and not value:
                current["evidence"] = {}
                in_evidence = True
            elif in_evidence and indent >= 6:
                current["evidence"][key] = parse_scalar(value)
            else:
                in_evidence = False
                current[key] = parse_scalar(value)
        i += 1
    return items, i


# ------------------------------------------------------------------ scanning

def strip_code_lines(body_lines):
    """Return a list of (line_index, text) with fenced code block contents and
    inline code removed, preserving original line numbers (1-based)."""
    out = []
    in_fence = False
    for idx, line in enumerate(body_lines, start=1):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append((idx, re.sub(r"`[^`]*`", "", line)))
    return out


def normalize_concept_id(name):
    return "concept:" + re.sub(r"\s+", "-", name.strip().lower())


def paper_id_for(key):
    return "paper:" + key.strip().lower()


class GraphBuilder:
    def __init__(self, root):
        self.root = root
        self.nodes = {}
        self.edges = []
        self.warnings = []
        self.file_paths = {}  # lowercase stem / relative path -> rel path
        self.files_scanned = 0

    def warn(self, level, kind, message, source=None, line=None):
        self.warnings.append(
            {"level": level, "kind": kind, "message": message,
             "source": source, "line": line}
        )

    def add_node(self, node_id, ntype, label, path=None):
        existing = self.nodes.get(node_id)
        if existing:
            # Upgrade a placeholder with a real file-backed node.
            if existing.get("placeholder") and path:
                existing.update({"type": ntype, "label": label, "path": path})
                existing.pop("placeholder", None)
            return existing
        node = {"id": node_id, "type": ntype, "label": label}
        if path:
            node["path"] = path
        else:
            node["placeholder"] = True
        self.nodes[node_id] = node
        return node

    def add_edge(self, frm, to, relation, origin, evidence):
        key = (
            frm, to, relation, evidence.get("source"), evidence.get("page"),
            evidence.get("section"), evidence.get("line"), evidence.get("quote"),
        )
        for edge in self.edges:
            edge_key = (
                edge["from"], edge["to"], edge["relation"],
                edge["evidence"].get("source"), edge["evidence"].get("page"),
                edge["evidence"].get("section"), edge["evidence"].get("line"),
                edge["evidence"].get("quote"),
            )
            if edge_key == key:
                return
        self.edges.append({"from": frm, "to": to, "relation": relation,
                           "origin": origin, "evidence": evidence})

    # ------------------------------------------------------------- per file

    def scan_file(self, path):
        rel = path.relative_to(self.root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self.warn("warning", "read-error", f"cannot read file: {exc}", rel)
            return
        self.files_scanned += 1

        fm_lines, body_lines = split_frontmatter(text)
        meta = parse_frontmatter(fm_lines)
        fm_offset = len(text.splitlines()) - len(body_lines)  # lines before body

        ntype = str(meta.get("type", "note")).strip().lower()
        if ntype not in NODE_TYPES:
            self.warn("warning", "unknown-node-type",
                      f"unknown type '{ntype}', falling back to 'note'", rel)
            ntype = "note"
        title = meta.get("title") or path.stem
        source_id = f"note:{rel}"
        self.add_node(source_id, ntype, str(title), path=rel)
        aliases = meta.get("aliases") or []
        if isinstance(aliases, list):
            self.nodes[source_id]["aliases"] = [str(a) for a in aliases]

        self.file_paths[rel.lower()] = rel
        self.file_paths[path.stem.lower()] = rel

        code_free = strip_code_lines(body_lines)
        self.extract_links(code_free, source_id, rel, fm_offset)
        # Evidence quotes must be found in the body only; the frontmatter
        # itself always contains the quote, which would mask staleness.
        self.extract_frontmatter_relations(meta.get("graph") or [], source_id,
                                           rel, "\n".join(body_lines))

    def scan_paper_note(self, path):
        rel = path.relative_to(self.root).as_posix()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            if path.name.endswith(".paper-note.json"):
                self.warn("error", "invalid-paper-note-json",
                          f"cannot parse paper-note JSON: {exc}", rel)
            return
        if not isinstance(payload, dict) or payload.get("artifact_type") != "paper-note":
            return
        self.files_scanned += 1
        contract_issues = validate_paper_note_contract(payload)
        if contract_issues:
            for issue in contract_issues:
                self.warn("error", "invalid-paper-note", issue, rel)
            return
        paper = payload.get("paper")
        claims = payload.get("claims")

        title = str(paper["title"]).strip()
        doi = str(paper.get("doi") or "").strip().lower()
        if doi:
            paper_node_id = paper_id_for(doi)
        else:
            identity = json.dumps(
                [title.casefold(), paper.get("year"), paper.get("authors") or []],
                ensure_ascii=False,
                sort_keys=True,
            )
            paper_node_id = "paper-note:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
        paper_node = self.add_node(paper_node_id, "paper", title, path=rel)
        paper_node.update({
            "schema_version": payload["schema_version"],
            "artifact_type": "paper-note",
            "year": paper.get("year"),
            "authors": paper.get("authors") or [],
        })
        if doi:
            paper_node["doi"] = doi
        sources = paper_node.setdefault("source_artifacts", [])
        if rel not in sources:
            sources.append(rel)
        self.file_paths[rel.lower()] = rel
        self.file_paths[path.stem.lower()] = rel

        seen_claim_ids = set()
        for position, claim in enumerate(claims):
            if not isinstance(claim, dict):
                self.warn("error", "invalid-paper-claim",
                          f"claim {position} must be an object", rel)
                continue
            local_id = str(claim.get("id") or "").strip()
            text = str(claim.get("text") or "").strip()
            evidence_items = claim.get("evidence")
            if not local_id or not text or not isinstance(evidence_items, list) or not evidence_items:
                self.warn("error", "invalid-paper-claim",
                          f"claim {position} requires id, text, and evidence", rel)
                continue
            if local_id in seen_claim_ids:
                self.warn("error", "duplicate-paper-claim",
                          f"duplicate claim id '{local_id}'", rel)
                continue
            seen_claim_ids.add(local_id)
            safe_local_id = re.sub(r"[^a-z0-9._-]+", "-", local_id.casefold()).strip("-")
            claim_node_id = f"claim:{paper_node_id}:{safe_local_id}"
            claim_node = self.add_node(claim_node_id, "claim", text, path=rel)
            claim_node.update({
                "claim_id": local_id,
                "claim_type": claim.get("claim_type"),
                "support_level": claim.get("support_level"),
                "paper": paper_node_id,
            })
            for evidence_index, evidence in enumerate(evidence_items):
                if not isinstance(evidence, dict) or not evidence.get("source") or not evidence.get("quote"):
                    self.warn("error", "invalid-claim-evidence",
                              f"claim '{local_id}' evidence {evidence_index} lacks source/quote", rel)
                    continue
                if evidence.get("page") is None and not evidence.get("section"):
                    self.warn("error", "invalid-claim-evidence",
                              f"claim '{local_id}' evidence {evidence_index} lacks page/section", rel)
                    continue
                preserved = {
                    key: evidence[key]
                    for key in (
                        "source", "page", "section", "line", "quote",
                        "extraction_method", "verification",
                    )
                    if key in evidence
                }
                self.add_edge(paper_node_id, claim_node_id, "supports",
                              "paper-note", preserved)

    def extract_links(self, code_free, source_id, rel, fm_offset):
        for body_idx, line in code_free:
            line_no = fm_offset + body_idx
            for m in WIKILINK_RE.finditer(line):
                target = m.group(1).strip()
                if not target:
                    continue
                evidence = {"source": rel, "line": line_no,
                            "quote": line.strip()[:200]}
                if DOI_RE.match(target):
                    pid = paper_id_for(target)
                    self.add_node(pid, "paper", target)
                    self.add_edge(source_id, pid, "cites", "parser", evidence)
                    continue
                hit = self.file_paths.get(target.lower())
                if hit:
                    target_id = f"note:{hit}"
                    label = target
                else:
                    target_id = normalize_concept_id(target)
                    label = target
                if target_id not in self.nodes:
                    node = self.add_node(target_id, "note", label)
                    if not hit:
                        self.warn("warning", "unresolved-wikilink",
                                  f"wikilink target '{target}' has no matching "
                                  f"file; kept as placeholder node", rel, line_no)
                        node["unresolved"] = True
                self.add_edge(source_id, target_id, "mentions", "parser", evidence)
            for m in CITEKEY_RE.finditer(line):
                key = m.group(1)
                pid = paper_id_for(key)
                self.add_node(pid, "paper", key)
                self.add_edge(source_id, pid, "cites", "parser",
                              {"source": rel, "line": line_no,
                               "quote": line.strip()[:200]})
            for m in LATEX_CITE_RE.finditer(line):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if not key:
                        continue
                    pid = paper_id_for(key)
                    self.add_node(pid, "paper", key)
                    self.add_edge(source_id, pid, "cites", "parser",
                                  {"source": rel, "line": line_no,
                                   "quote": line.strip()[:200]})

    def extract_frontmatter_relations(self, items, source_id, rel, full_text):
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            relation = str(item.get("relation", "")).strip()
            target = str(item.get("target", "")).strip()
            if not relation or not target:
                self.warn("error", "malformed-relation",
                          "frontmatter graph item missing relation/target", rel)
                continue
            if relation not in KNOWN_RELATIONS:
                self.warn("warning", "unknown-relation",
                          f"unknown relation '{relation}' degraded to "
                          f"'mentions'", rel)
                relation = "mentions"

            wm = WIKILINK_RE.search(target)
            if wm:
                name = wm.group(1).strip()
                hit = self.file_paths.get(name.lower())
                target_id = f"note:{hit}" if hit else normalize_concept_id(name)
                self.add_node(target_id, "note", name)
            elif target.startswith("@"):
                target_id = paper_id_for(target[1:])
                self.add_node(target_id, "paper", target[1:])
            elif target.startswith(("note:", "concept:", "paper:")):
                target_id = target
                self.add_node(target_id, "note", target.split(":", 1)[1])
            else:
                target_id = normalize_concept_id(target)
                self.add_node(target_id, "note", target)

            evidence = item.get("evidence")
            if not isinstance(evidence, dict) or not evidence:
                self.warn("error", "missing-evidence",
                          f"relation '{relation}' -> '{target}' lacks a "
                          f"required evidence anchor", rel)
                evidence = {"source": rel}
            else:
                evidence = dict(evidence)
                evidence.setdefault("source", rel)
                quote = evidence.get("quote")
                if quote and str(quote) not in full_text:
                    self.warn("warning", "stale-evidence",
                              f"evidence quote for '{relation}' -> '{target}' "
                              f"not found in file text", rel)
                if "line" in evidence:
                    try:
                        evidence["line"] = int(evidence["line"])
                    except (TypeError, ValueError):
                        evidence.pop("line")
            self.add_edge(source_id, target_id, relation, "frontmatter",
                          evidence)

    # --------------------------------------------------------------- driver

    def build(self):
        md_files = sorted(
            p for p in self.root.rglob("*.md")
            if not any(part in SKIP_DIRS or part.startswith(".")
                       for part in p.relative_to(self.root).parts[:-1])
        )
        # Pre-register file paths so forward wikilinks resolve.
        for p in md_files:
            rel = p.relative_to(self.root).as_posix()
            self.file_paths[rel.lower()] = rel
            self.file_paths[p.stem.lower()] = rel
        for p in md_files:
            self.scan_file(p)
        json_files = sorted(
            p for p in self.root.rglob("*.json")
            if not any(part in SKIP_DIRS or part.startswith(".")
                       for part in p.relative_to(self.root).parts[:-1])
        )
        for p in json_files:
            self.scan_paper_note(p)
        # Second pass: concept placeholders that actually match a file stem.
        for node in list(self.nodes.values()):
            if node.get("unresolved"):
                stem = node["label"].strip().lower()
                if stem in self.file_paths:
                    node["path"] = self.file_paths[stem]
                    node.pop("unresolved", None)
                    node.pop("placeholder", None)
        return self

    def to_dict(self):
        errors = sum(1 for w in self.warnings if w["level"] == "error")
        return {
            "nodes": sorted(self.nodes.values(), key=lambda n: n["id"]),
            "edges": sorted(self.edges,
                            key=lambda e: (e["from"], e["to"], e["relation"])),
            "warnings": self.warnings,
            "stats": {"files": self.files_scanned,
                      "nodes": len(self.nodes),
                      "edges": len(self.edges),
                      "errors": errors},
        }

    def to_dot(self):
        shapes = {"paper": "box", "claim": "note", "method": "ellipse", "dataset": "cylinder",
                  "task": "diamond", "metric": "hexagon", "topic": "octagon",
                  "note": "note"}
        lines = ["digraph knowledge_graph {",
                 "  rankdir=LR;",
                 "  node [fontname=\"Helvetica\"];"]
        for node in sorted(self.nodes.values(), key=lambda n: n["id"]):
            shape = shapes.get(node["type"], "ellipse")
            label = node["label"].replace('"', '\\"')
            attrs = f'label="{label}", shape={shape}'
            if node.get("unresolved"):
                attrs += ', style=dashed, color=red'
            lines.append(f'  "{node["id"]}" [{attrs}];')
        for edge in self.edges:
            style = "solid" if edge["origin"] == "frontmatter" else "dashed"
            lines.append(
                f'  "{edge["from"]}" -> "{edge["to"]}" '
                f'[label="{edge["relation"]}", style={style}];')
        lines.append("}")
        return "\n".join(lines) + "\n"

    def warnings_markdown(self):
        lines = ["# build_graph warnings", ""]
        if not self.warnings:
            lines.append("No warnings.")
        for w in self.warnings:
            loc = w["source"] or ""
            if w.get("line"):
                loc += f":{w['line']}"
            icon = "ERROR" if w["level"] == "error" else "warn"
            lines.append(f"- **[{icon}] {w['kind']}** {loc} — {w['message']}")
        return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ analysis

def detailed_stats(nodes, edges):
    """Degree distribution, isolated nodes, and undirected connected
    components for a graph dict's nodes/edges lists."""
    degree = {n["id"]: {"in": 0, "out": 0} for n in nodes}
    adjacency = {n["id"]: set() for n in nodes}
    for e in edges:
        frm, to = e["from"], e["to"]
        if frm not in degree or to not in degree:
            continue
        degree[frm]["out"] += 1
        degree[to]["in"] += 1
        adjacency[frm].add(to)
        adjacency[to].add(frm)

    totals = {nid: d["in"] + d["out"] for nid, d in degree.items()}
    distribution = {}
    for total in totals.values():
        distribution[total] = distribution.get(total, 0) + 1
    isolated = sorted(nid for nid, total in totals.items() if total == 0)

    seen = set()
    components = []
    for nid in adjacency:
        if nid in seen:
            continue
        stack, members = [nid], []
        seen.add(nid)
        while stack:
            cur = stack.pop()
            members.append(cur)
            for nxt in adjacency[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        components.append(sorted(members))
    components.sort(key=len, reverse=True)

    top_hubs = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:10]
    return {
        "degree": {nid: {"in": d["in"], "out": d["out"],
                         "total": d["in"] + d["out"]}
                   for nid, d in sorted(degree.items())},
        "degree_distribution": {str(k): distribution[k]
                                for k in sorted(distribution)},
        "isolated_nodes": isolated,
        "connected_components": [{"size": len(c), "nodes": c}
                                 for c in components],
        "top_hubs": [{"id": nid, "degree": total} for nid, total in top_hubs],
    }


def stats_summary(detailed):
    lines = ["-- detailed stats --"]
    dist = detailed["degree_distribution"]
    lines.append("degree distribution (degree: node count): "
                 + ", ".join(f"{k}: {v}" for k, v in dist.items()))
    comps = detailed["connected_components"]
    lines.append(f"connected components: {len(comps)} "
                 f"(sizes: {', '.join(str(c['size']) for c in comps[:10])})")
    lines.append(f"isolated nodes ({len(detailed['isolated_nodes'])}): "
                 + (", ".join(detailed["isolated_nodes"][:15]) or "none"))
    lines.append("top hubs: " + (", ".join(
        f"{h['id']}({h['degree']})" for h in detailed["top_hubs"][:5])
        or "none"))
    return "\n".join(lines)


def write_csv(nodes, edges, prefix):
    """Write Gephi/Cytoscape-compatible nodes/edges CSV pair."""
    import csv

    def esc(value):
        return "" if value is None else str(value)

    with open(prefix + ".nodes.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Id", "Label", "Type", "Path"])
        for n in sorted(nodes, key=lambda n: n["id"]):
            writer.writerow([esc(n["id"]), esc(n.get("label")),
                             esc(n.get("type")), esc(n.get("path"))])
    with open(prefix + ".edges.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Source", "Target", "Relation", "Origin",
                         "EvidenceSource", "EvidenceLine"])
        for e in sorted(edges, key=lambda e: (e["from"], e["to"],
                                              e["relation"])):
            ev = e.get("evidence") or {}
            writer.writerow([esc(e["from"]), esc(e["to"]), esc(e["relation"]),
                             esc(e.get("origin")), esc(ev.get("source")),
                             esc(ev.get("line"))])


def resolve_seed(graph, seed_text):
    """Resolve a seed string to one node id. Returns (node_id, error)."""
    nodes = graph.get("nodes", [])
    for n in nodes:
        if n["id"] == seed_text:
            return n["id"], None
    needle = seed_text.lower()
    squashed = re.sub(r"[-\s_]", "", needle)
    hits = [n for n in nodes
            if needle in str(n.get("label", "")).lower()
            or squashed and squashed in re.sub(r"[-\s_]", "",
                                               str(n.get("label", "")).lower())
            or any(needle in str(a).lower() for a in n.get("aliases", []))]
    if not hits:
        return None, f"seed '{seed_text}' matched no node (exact id or label/alias substring)"
    ids = sorted(n["id"] for n in hits)
    if len(ids) > 1:
        return None, (f"seed '{seed_text}' is ambiguous, matched: "
                      + ", ".join(ids[:10]))
    return ids[0], None


def extract_subgraph(graph, seed_ids, depth, relations):
    """BFS over the graph (treated as undirected for reachability) from the
    seed ids, restricted to whitelisted relations. Returns a graph dict."""
    nodes_by_id = {n["id"]: n for n in graph.get("nodes", [])}
    edges = [e for e in graph.get("edges", [])
             if relations is None or e["relation"] in relations]
    adjacency = {}
    for e in edges:
        adjacency.setdefault(e["from"], []).append(e["to"])
        adjacency.setdefault(e["to"], []).append(e["from"])

    keep = set(seed_ids)
    frontier = set(seed_ids)
    for _ in range(depth):
        nxt = set()
        for nid in frontier:
            nxt.update(adjacency.get(nid, []))
        nxt -= keep
        keep |= nxt
        frontier = nxt

    sub_edges = [e for e in edges if e["from"] in keep and e["to"] in keep]
    return {
        "nodes": [nodes_by_id[nid] for nid in sorted(keep) if nid in nodes_by_id],
        "edges": sub_edges,
        "warnings": [],
        "stats": {"files": 0, "nodes": len(keep & set(nodes_by_id)),
                  "edges": len(sub_edges), "errors": 0},
        "query": {"seeds": sorted(seed_ids), "depth": depth,
                  "relations": sorted(relations) if relations else "all"},
    }


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to GBK
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Build a typed graph from Markdown notes and ResearchOS paper-note JSON.")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("notes_dir", nargs="?",
                        help="directory of Markdown notes and paper-note JSON")
    parser.add_argument("-o", "--out", help="JSON output path (default stdout)")
    parser.add_argument("--dot", help="write Graphviz DOT to this path")
    parser.add_argument("--warnings", help="write Markdown warnings report here")
    parser.add_argument("--quiet", action="store_true",
                        help="suppress stderr summary")
    parser.add_argument("--stats", action="store_true",
                        help="include detailed stats (degree distribution, "
                             "isolated nodes, connected components)")
    parser.add_argument("--csv", metavar="PREFIX",
                        help="export PREFIX.nodes.csv and PREFIX.edges.csv")
    parser.add_argument("--force", action="store_true",
                        help="replace existing derived output files")
    parser.add_argument("--query", metavar="GRAPH_JSON",
                        help="standalone mode: extract a subgraph from an "
                             "existing graph JSON instead of scanning notes")
    parser.add_argument("--seed", action="append", default=[],
                        help="seed node for --query (repeatable)")
    parser.add_argument("--depth", type=int, default=1,
                        help="BFS depth for --query (default 1, max 4)")
    parser.add_argument("--relations",
                        help="comma-separated relation whitelist for --query")
    args = parser.parse_args(argv)

    output_paths = [path for path in (args.out, args.dot, args.warnings) if path]
    if args.csv:
        output_paths += [args.csv + ".nodes.csv", args.csv + ".edges.csv"]
    if len({str(Path(path).resolve()) for path in output_paths}) != len(output_paths):
        print("error: graph output paths must be distinct", file=sys.stderr)
        return 2
    if args.query and any(Path(path).resolve() == Path(args.query).resolve() for path in output_paths):
        print("error: output must not replace the --query graph", file=sys.stderr)
        return 2
    existing = [path for path in output_paths if Path(path).exists()]
    if existing and not args.force:
        print(f"error: output exists: {existing[0]}; use --force to replace derived outputs",
              file=sys.stderr)
        return 2

    if args.query:
        try:
            graph = json.loads(Path(args.query).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"error: invalid JSON in {args.query}: {exc}",
                  file=sys.stderr)
            return 2
        if not args.seed:
            print("error: --query requires at least one --seed",
                  file=sys.stderr)
            return 2
        if not 1 <= args.depth <= 4:
            print("error: --depth must be between 1 and 4", file=sys.stderr)
            return 2
        relations = None
        if args.relations:
            relations = {r.strip() for r in args.relations.split(",")
                         if r.strip()}
        seed_ids = []
        for seed in args.seed:
            node_id, error = resolve_seed(graph, seed)
            if error:
                print(f"error: {error}", file=sys.stderr)
                return 2
            seed_ids.append(node_id)
        result = extract_subgraph(graph, seed_ids, args.depth, relations)
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
        if args.csv:
            write_csv(result["nodes"], result["edges"], args.csv)
        if not args.quiet:
            print(f"query: {len(seed_ids)} seed(s), depth {args.depth}, "
                  f"relations {sorted(relations) if relations else 'all'} -> "
                  f"{result['stats']['nodes']} nodes, "
                  f"{result['stats']['edges']} edges", file=sys.stderr)
        return 0

    if not args.notes_dir:
        print("error: notes_dir is required (unless --query is used)",
              file=sys.stderr)
        return 2
    root = Path(args.notes_dir).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    builder = GraphBuilder(root).build()
    result = builder.to_dict()

    if args.stats:
        detailed = detailed_stats(result["nodes"], result["edges"])
        result["detailed_stats"] = detailed

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    if args.dot:
        Path(args.dot).write_text(builder.to_dot(), encoding="utf-8")
    if args.warnings:
        Path(args.warnings).write_text(builder.warnings_markdown(),
                                       encoding="utf-8")
    if args.csv:
        write_csv(result["nodes"], result["edges"], args.csv)

    if not args.quiet:
        stats = result["stats"]
        by_type = {}
        for node in result["nodes"]:
            by_type[node["type"]] = by_type.get(node["type"], 0) + 1
        print(f"scanned {stats['files']} files -> "
              f"{stats['nodes']} nodes {by_type}, {stats['edges']} edges, "
              f"{len(result['warnings'])} warnings "
              f"({stats['errors']} errors)", file=sys.stderr)
        if args.stats:
            print(stats_summary(result["detailed_stats"]), file=sys.stderr)
        if not args.warnings:
            for w in result["warnings"]:
                loc = w["source"] or ""
                if w.get("line"):
                    loc += f":{w['line']}"
                print(f"  [{w['level']}] {w['kind']} {loc} — {w['message']}",
                      file=sys.stderr)

    return 1 if result["stats"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
