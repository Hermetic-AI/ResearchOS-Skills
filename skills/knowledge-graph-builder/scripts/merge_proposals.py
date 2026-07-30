#!/usr/bin/env python3
"""Merge user-approved AI relation proposals back into the knowledge graph.

Purpose
-------
Stage 3 of the knowledge-graph-builder workflow produces relation
*proposals* that the user approves or rejects. This script takes a proposals
JSON file and merges the approved entries into the fact source, either by:

  - (default) appending `graph:` relation blocks to each source note's
    YAML frontmatter, so the next `build_graph.py` run picks them up as
    deterministic facts; or
  - (--overlay) writing a standalone graph-overlay JSON (same edge shape as
    build_graph.py output, origin "proposal") without touching any note —
    useful for review or for tooling that consumes edges directly.

Only proposals with "status": "approved" are merged; every other status
("rejected", "pending", missing) is skipped and counted.

Dependencies: Python 3.8+ standard library only (no third-party packages).

CLI usage
---------
    python3 merge_proposals.py proposals.json --vault <notes_dir>
                               [--overlay overlay.json] [--dry-run]
                               [--report report.md] [--quiet]

    proposals.json   Proposals file, see format below.
    --vault          Notes vault root; required unless --overlay is used.
    --overlay        Write a graph-overlay JSON here instead of editing
                     note frontmatter.
    --dry-run        Print what would change without writing anything.
    --report         Write a Markdown merge report to this path.
    --quiet          Suppress the stderr summary.

Proposals JSON format
---------------------
    {
      "proposals": [
        {
          "source": "notes/flash-attention.md",   // vault-relative path
          "relation": "improves-on",              // controlled predicate
          "target": "[[multi-head-attention]]",   // wikilink/@citekey/id
          "evidence": {"line": 42, "quote": "..."},   // required
          "note": "direct improvement claim",     // optional
          "status": "approved"                    // gate: only this merges
        }
      ]
    }

Output
------
Frontmatter mode edits notes in place (a `graph:` list item per approved
proposal, deduplicated against existing declarations) and prints a summary.
Overlay mode writes {"edges": [...], "skipped": N} JSON.
Note: values containing double quotes or backslashes are emitted in
single-quoted YAML style (with '' escaping); everything else is
double-quoted, so quotes and backslashes round-trip intact.
"""

import argparse
import json
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


def proposal_block(proposal):
    lines = ["  - relation: " + proposal["relation"],
             "    target: " + yaml_value(proposal["target"])]
    evidence = proposal["evidence"]
    lines.append("    evidence:")
    if evidence.get("line") is not None:
        lines.append(f"      line: {int(evidence['line'])}")
    if evidence.get("quote"):
        lines.append("      quote: " + yaml_value(evidence["quote"]))
    if proposal.get("note"):
        lines.append("    note: " + yaml_value(proposal["note"]))
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
    """Locate the `graph:` block inside frontmatter lines. Returns
    (start_index, end_index) of the whole block, or None."""
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
        if re.search(r"target:\s*\"?" + re.escape(str(target)) + r"\"?\s*$",
                     chunk, re.MULTILINE):
            return True
    return False


def merge_into_note(path, proposals, dry_run):
    """Insert approved proposals into one note's frontmatter. Returns
    (inserted, skipped_duplicates)."""
    text = path.read_text(encoding="utf-8")
    fm_lines, body_lines = split_note(text)
    inserted = 0
    duplicates = 0

    if fm_lines is None:
        fm_lines = []
    for proposal in proposals:
        if already_declared(fm_lines, proposal["relation"],
                            proposal["target"]):
            duplicates += 1
            continue
        span = graph_block_span(fm_lines)
        block = proposal_block(proposal)
        if span:
            fm_lines[span[1]:span[1]] = block
        else:
            fm_lines.extend(["graph:"] + block)
        inserted += 1

    if not inserted or dry_run:
        return inserted, duplicates

    new_lines = ([FRONTMATTER_DELIM] + fm_lines + [FRONTMATTER_DELIM]
                 + body_lines)
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return inserted, duplicates


def validate(proposal, index):
    problems = []
    for field in ("source", "relation", "target"):
        if not proposal.get(field):
            problems.append(f"proposal #{index}: missing '{field}'")
    if proposal.get("relation") and proposal["relation"] not in KNOWN_RELATIONS:
        problems.append(f"proposal #{index}: unknown relation "
                        f"'{proposal['relation']}'")
    evidence = proposal.get("evidence")
    if not isinstance(evidence, dict) or not evidence.get("quote"):
        problems.append(f"proposal #{index}: evidence with a verbatim "
                        f"'quote' is required")
    return problems


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to GBK
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Merge approved relation proposals into note frontmatter "
                    "or a graph-overlay JSON.")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("proposals", help="proposals JSON file")
    parser.add_argument("--vault", help="notes vault root")
    parser.add_argument("--overlay",
                        help="write graph-overlay JSON here instead of "
                             "editing notes")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change without writing")
    parser.add_argument("--report", help="write a Markdown merge report here")
    parser.add_argument("--force", action="store_true",
                        help="replace existing --overlay/--report files")
    parser.add_argument("--quiet", action="store_true",
                        help="suppress stderr summary")
    args = parser.parse_args(argv)

    outputs = [path for path in (args.overlay, args.report) if path]
    if len({str(Path(path).resolve()) for path in outputs}) != len(outputs):
        print("error: --overlay and --report must be different files", file=sys.stderr)
        return 2
    if any(Path(path).resolve() == Path(args.proposals).resolve() for path in outputs):
        print("error: output must not replace the proposals input", file=sys.stderr)
        return 2
    existing = [path for path in outputs if Path(path).exists()]
    if existing and not args.force:
        print(f"error: output exists: {existing[0]}; use --force to replace it",
              file=sys.stderr)
        return 2

    try:
        data = json.loads(Path(args.proposals).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"error: invalid JSON in {args.proposals}: {exc}",
              file=sys.stderr)
        return 2
    proposals = data if isinstance(data, list) else data.get("proposals", [])

    approved, skipped, invalid = [], 0, []
    for i, proposal in enumerate(proposals):
        if proposal.get("status") != "approved":
            skipped += 1
            continue
        problems = validate(proposal, i)
        if problems:
            invalid.extend(problems)
            continue
        approved.append(proposal)

    if invalid:
        for problem in invalid:
            print(f"error: {problem}", file=sys.stderr)
        return 2

    inserted_total, duplicates_total = 0, 0
    report_lines = ["# merge_proposals report", "",
                    f"- approved: {len(approved)}, skipped (not approved): "
                    f"{skipped}", ""]

    if args.overlay:
        edges = [{
            "from": f"note:{p['source']}",
            "to": p["target"],
            "relation": p["relation"],
            "origin": "proposal",
            "evidence": dict(p["evidence"], source=p["source"]),
        } for p in approved]
        overlay = {"edges": edges, "skipped": skipped}
        if not args.dry_run:
            Path(args.overlay).write_text(
                json.dumps(overlay, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
        inserted_total = len(edges)
        report_lines.append(f"Overlay mode: {len(edges)} edges -> "
                            f"`{args.overlay}`"
                            + (" (dry-run, not written)" if args.dry_run
                               else ""))
    else:
        if not args.vault:
            print("error: --vault is required unless --overlay is used",
                  file=sys.stderr)
            return 2
        vault = Path(args.vault).resolve()
        by_source = {}
        for p in approved:
            by_source.setdefault(p["source"], []).append(p)
        for source in sorted(by_source):
            path = vault / source
            if not path.is_file():
                print(f"error: source note not found: {source}",
                      file=sys.stderr)
                return 2
            inserted, duplicates = merge_into_note(path, by_source[source],
                                                   args.dry_run)
            inserted_total += inserted
            duplicates_total += duplicates
            report_lines.append(
                f"- `{source}`: {inserted} relation(s) merged"
                + (f", {duplicates} duplicate(s) skipped"
                   if duplicates else "")
                + (" (dry-run)" if args.dry_run else ""))

    report_lines += ["", f"**Total: {inserted_total} merged, "
                     f"{duplicates_total} duplicates skipped, "
                     f"{skipped} not-approved skipped.**"]
    if args.report:
        Path(args.report).write_text("\n".join(report_lines) + "\n",
                                     encoding="utf-8")

    if not args.quiet:
        print(f"merged {inserted_total} approved proposal(s) "
              f"({duplicates_total} duplicates, {skipped} not approved)"
              + (" [dry-run]" if args.dry_run else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
