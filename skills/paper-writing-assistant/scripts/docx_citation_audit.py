#!/usr/bin/env python3
"""Audit author-year citation *candidates* and Word field semantics in a DOCX.

This zero-dependency tool reads Word XML only.  It reports visible-text
author-year candidates and the presence/count of common Zotero/Word field
markers. It now also parses Word ``CITATION`` field *instructions* (raw
``instrText``) and the rendered RESULT text between the field begin/end
markers.  Parsing the instruction is still heuristic — it does not perform
live Word field resolution, does not validate bibliography semantics, and
cannot see what Word actually displays after an update.

Usage: python3 docx_citation_audit.py manuscript.docx [--pretty] [--fields]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "0.1.0"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PAREN_CITATION = re.compile(r"\(([^()]{0,160}?(?:19|20)\d{2}[a-z]?(?:[^()]*)?)\)")
YEAR = re.compile(r"\b(?:19|20)\d{2}[a-z]?\b")
def paragraph_texts(document: ET.Element) -> list[str]:
    return ["".join(node.text or "" for node in p.iter(W + "t")).strip()
            for p in document.iter(W + "p")]


def _run_text(run: ET.Element) -> str:
    return "".join(t.text or "" for t in run.iter(W + "t"))


def parse_citation_instruction(instr: str) -> dict:
    """Parse a raw CITATION field instruction text.

    Returns the citation key (best effort) and any recognized ``\\switch``
    arguments.  The key is the first non-switch token after ``CITATION``;
    quoted keys ``"key"`` have their quotes stripped.  Unknown switches are
    reported under ``other_switches`` so the caller can see them.

    Word writes switches as a backslash + single letter followed by an
    optional whitespace-separated argument (e.g. ``\\l 1033``).  The argument
    is therefore the *next* token whenever that token is not itself a switch.
    """
    recognized = {"l", "m", "p", "t"}
    text = instr.strip()
    tokens = text.split()
    # Strip a leading CITATION/REF/NOTEREF keyword if present.
    if tokens and tokens[0].upper() in {"CITATION", "REF", "NOTEREF", "BIBLIOGRAPHY", "TOC"}:
        tokens = tokens[1:]
    key = None
    switches: dict[str, list[str]] = {}
    other: list[str] = []
    rest: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        # A switch is a backslash followed by a single letter: \l \m \p \t ...
        if token.startswith("\\") and len(token) >= 2 and token[1].isalpha() and len(token) == 2:
            name = token[1]
            value = ""
            # The argument, if any, is the next token — unless that token is
            # itself a switch, in which case this switch takes no argument.
            if index + 1 < len(tokens) and not tokens[index + 1].startswith("\\"):
                value = tokens[index + 1]
                index += 1
            switches.setdefault(name, []).append(value)
            if name not in recognized:
                other.append(token)
        elif key is None:
            key = token.strip('"').strip("'")
        else:
            rest.append(token)
        index += 1
    return {
        "key": key,
        "switches": switches,
        "recognized_switches": sorted(switches.keys()),
        "suppress_author": "m" in switches,
        "has_locale": "l" in switches,
        "has_page": "p" in switches,
        "has_title": "t" in switches,
        "other_switches": other,
        "remainder": rest,
    }


def _document_order(root: ET.Element) -> list[ET.Element]:
    """Return every element under *root* in document (depth-first) order."""
    out: list[ET.Element] = []
    stack: list[ET.Element] = list(reversed(list(root)))
    while stack:
        element = stack.pop()
        out.append(element)
        if len(element):
            stack.extend(reversed(list(element)))
    return out


def resolve_fields(document: ET.Element) -> list[dict]:
    """Walk the document body and collect CITATION field instances.

    Two shapes are handled:

    * **Simple fields** — ``<w:fldSimple w:instr="...">...</w:fldSimple>``: the
      instruction is the ``w:instr`` attribute and the displayed text is the
      concatenated ``w:t`` content inside the field element.
    * **Complex fields** — ``<w:fldChar w:fldCharType="begin"/>`` ...
      ``<w:fldChar w:fldCharType="end"/>``: the instruction lives in the
      first ``<w:instrText>`` after the begin marker; the displayed text is
      the concatenated ``w:t`` on ``w:r`` elements between begin and end.

    Only fields whose instruction starts with ``CITATION`` (case-insensitive)
    are reported; this keeps the output focused on author-year citations while
    still exposing the raw text for transparency.
    """
    # Simple fields first.
    simple_fields: dict[ET.Element, dict] = {}
    for fld in document.iter(W + "fldSimple"):
        instr = (fld.get(W + "instr") or "").strip()
        if not instr.upper().startswith("CITATION"):
            continue
        simple_fields[fld] = {
            "kind": "fldSimple",
            "instruction": instr,
            "parsed": parse_citation_instruction(instr),
            "displayed": _run_text(fld),
        }

    # Complex fields: sweep every element in document order, tracking the most
    # recent begin marker.  Skip any subtree rooted at a fldSimple so we do not
    # double-count simple fields.
    resolved: list[dict] = list(simple_fields.values())
    simple_roots = set(id(fld) for fld in simple_fields)
    pending_instruction: str | None = None
    pending_runs: list[ET.Element] = []
    pending_began = False
    for element in _document_order(document):
        if id(element) in simple_roots:
            # Skip the entire fldSimple subtree for the complex sweep.
            continue
        tag = element.tag
        if tag == W + "fldChar":
            ftype = element.get(W + "fldCharType")
            if ftype == "begin":
                pending_instruction = None
                pending_runs = []
                pending_began = True
            elif ftype == "end" and pending_began:
                instr = (pending_instruction or "").strip()
                displayed = "".join(_run_text(r) for r in pending_runs)
                if instr.upper().startswith("CITATION"):
                    resolved.append({
                        "kind": "fldChar",
                        "instruction": instr,
                        "parsed": parse_citation_instruction(instr),
                        "displayed": displayed,
                    })
                pending_began = False
                pending_instruction = None
                pending_runs = []
        elif pending_began and tag == W + "instrText":
            pending_instruction = "".join(element.itertext())
        elif pending_began and tag == W + "r":
            pending_runs.append(element)
    return resolved


def audit(path: Path, include_fields: bool = False) -> dict:
    if path.suffix.lower() != ".docx":
        raise ValueError("input must be a .docx file")
    with zipfile.ZipFile(path) as archive:
        try:
            document_raw = archive.read("word/document.xml")
        except KeyError as exc:
            raise ValueError("DOCX has no word/document.xml") from exc
        document = ET.fromstring(document_raw)
        field_text = "\n".join(
            archive.read(name).decode("utf-8", errors="replace")
            for name in archive.namelist() if name.startswith("word/") and name.endswith(".xml")
        )
    candidates = []
    for number, text in enumerate(paragraph_texts(document), 1):
        for match in PAREN_CITATION.finditer(text):
            candidate = match.group(0)
            if YEAR.search(candidate):
                candidates.append({"paragraph": number, "text": candidate})
    markers = {
        "zotero_csl_citation": field_text.count("ADDIN ZOTERO_ITEM CSL_CITATION"),
        "mendeley_citation": field_text.count("ADDIN MENDELEY_CITATION"),
        "word_citation_field": field_text.count(" CITATION "),
    }
    resolved = resolve_fields(document) if include_fields else None
    warnings = [
        "Heuristic only: parentheses containing a year can be prose, a range, or a citation.",
        "Field-marker counts do not expose citation semantics or prove bibliography coverage.",
        "Citation-field parsing extracts the raw instruction text (instrText/instr) and the "
        "rendered RESULT text between field markers; it does not perform live Word resolution.",
        "The displayed text is whatever was last saved in the DOCX and may be stale if fields "
        "have not been updated in Word.",
    ]
    if include_fields:
        warnings.append(
            "Field parsing is heuristic: nested fields, collapsed results, or protected "
            "fields may be missed or misread."
        )
    result = {
        "schema_version": "1.1.0", "artifact_type": "docx-citation-screen",
        "tool_version": VERSION, "document": str(path.resolve()),
        "visible_author_year_candidates": candidates,
        "field_marker_counts": markers,
        "warnings": warnings,
    }
    if include_fields:
        result["resolved_fields"] = resolved
        result["resolved_field_count"] = len(resolved)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--fields", action="store_true",
                        help="also parse CITATION field instructions and rendered text")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(audit(Path(args.document), include_fields=args.fields),
                         ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
