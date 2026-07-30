#!/usr/bin/env python3
"""Add a single relation to a note's frontmatter `graph:` list.

Purpose
-------
Hand-editing YAML frontmatter is error-prone (quoting, indentation). This
CLI appends one relation declaration to a note, idempotently: if an item
with the same relation+target already exists, nothing is changed. The
emitted YAML stays compatible with the minimal parser in build_graph.py:
values containing double quotes or backslashes are wrapped in single
quotes (with '' escaping), everything else in double quotes.

Dependencies: Python 3.8+ standard library only (no third-party packages).

CLI usage
---------
    python3 add_relation.py --note notes/a.md --relation cites \
        --target "[[some-note]]" --quote "evidence text" [--line 42] [--dry-run]

    --note       Note file to edit (created frontmatter block if missing).
    --relation   Controlled relation name (see KNOWN_RELATIONS below).
    --target     Wikilink "[[name]]", "@citekey", or explicit id
                 ("note:/concept:/paper:...").
    --quote      Verbatim evidence quote from the note body (required).
    --line       Optional body line number of the evidence.
    --dry-run    Print the resulting frontmatter block without writing.
"""

import argparse
import re
import sys
from pathlib import Path

KNOWN_RELATIONS = {
    "mentions", "cites", "uses", "uses-dataset", "evaluates-on",
    "improves-on", "outperforms", "extends", "implements",
    "supports", "contradicts",
}

FRONTMATTER_DELIM = "---"


def yaml_value(value):
    """Emit a quoted YAML scalar safe for build_graph.py's minimal parser.
    Single-quoted style is used whenever the value contains a double quote
    or a backslash (single quotes need no backslash escaping; a literal
    single quote becomes '')."""
    text = str(value)
    if '"' in text or "\\" in text:
        return "'" + text.replace("'", "''") + "'"
    return f'"{text}"'


def relation_block(relation, target, quote, line=None):
    lines = ["  - relation: " + relation,
             "    target: " + yaml_value(target),
             "    evidence:"]
    if line is not None:
        lines.append(f"      line: {line}")
    lines.append("      quote: " + yaml_value(quote))
    return lines


def split_note(text):
    """Return (frontmatter_lines_or_None, body_lines)."""
    lines = text.splitlines()
    if lines and lines[0].strip() == FRONTMATTER_DELIM:
        for i in range(1, len(lines)):
            if lines[i].strip() == FRONTMATTER_DELIM:
                return lines[1:i], lines[i + 1:]
    return None, lines


def graph_block_span(fm_lines):
    """Locate the `graph:` block. Returns (start, end) or None."""
    for i, line in enumerate(fm_lines):
        if re.match(r"^graph:\s*$", line):
            end = i + 1
            while end < len(fm_lines):
                stripped = fm_lines[end]
                if stripped.strip() and not stripped.startswith((" ", "\t")):
                    break
                end += 1
            return i, end
    return None


def already_declared(fm_lines, relation, target):
    """True if a graph item with the same relation+target exists."""
    span = graph_block_span(fm_lines)
    if not span:
        return False
    block = "\n".join(fm_lines[span[0]:span[1]])
    for chunk in block.split("- relation: "):
        chunk = chunk.lstrip()
        if not chunk:
            continue
        if chunk.split(None, 1)[0] != relation:
            continue
        if re.search(r"target:\s*[\"']?" + re.escape(str(target))
                     + r"[\"']?\s*$", chunk, re.MULTILINE):
            return True
    return False


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to GBK
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Idempotently append one relation to a note's "
                    "frontmatter graph: list.")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--note", required=True, help="note file to edit")
    parser.add_argument("--relation", required=True,
                        help="relation name, one of: "
                             + ", ".join(sorted(KNOWN_RELATIONS)))
    parser.add_argument("--target", required=True,
                        help='wikilink "[[name]]", "@citekey", or explicit id')
    parser.add_argument("--quote", required=True,
                        help="verbatim evidence quote from the note body")
    parser.add_argument("--line", type=int, default=None,
                        help="optional body line number of the evidence")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the change without writing")
    args = parser.parse_args(argv)

    if args.relation not in KNOWN_RELATIONS:
        print(f"error: unknown relation '{args.relation}' "
              f"(known: {', '.join(sorted(KNOWN_RELATIONS))})",
              file=sys.stderr)
        return 2

    path = Path(args.note)
    if not path.is_file():
        print(f"error: note not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    fm_lines, body_lines = split_note(text)
    if fm_lines is None:
        fm_lines = []

    if already_declared(fm_lines, args.relation, args.target):
        print(f"already declared: {args.relation} -> {args.target} "
              f"in {path} (no change)", file=sys.stderr)
        return 0

    block = relation_block(args.relation, args.target, args.quote, args.line)
    span = graph_block_span(fm_lines)
    if span:
        fm_lines[span[1]:span[1]] = block
    else:
        fm_lines.extend(["graph:"] + block)

    new_lines = ([FRONTMATTER_DELIM] + fm_lines + [FRONTMATTER_DELIM]
                 + body_lines)
    if args.dry_run:
        print("\n".join(new_lines))
        print("[dry-run: not written]", file=sys.stderr)
        return 0
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"added: {args.relation} -> {args.target} in {path}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
