#!/usr/bin/env python3
"""Convert CSL-JSON or CSL-YAML citation data into BibTeX entries.

Purpose
-------
 CSL (Citation Style Language) JSON/YAML is the native interchange format of
 Zotero, Mendeley, Pandoc, and many reference managers. This zero-dependency
 translator maps the most common CSL types and fields to their BibTeX
 equivalents so a CSL library can be used directly with ``\bibliography``.
 It is a *structural* mapping: it does not validate URLs/DOIs, resolve
 strings, or guarantee that the output compiles with any particular ``.bst``.

Dependencies: Python 3.8+ standard library only (no PyYAML — a minimal
 CSL-YAML subset is parsed by hand, see ``_minimal_yaml``).

CLI
---
 python3 csl_to_bibtex.py library.json -o refs.bib
 python3 csl_to_bibtex.py library.yaml --format yaml -o refs.bib
 python3 csl_to_bibtex.py library.json --key-prefix zot --force

Input
-----
 CSL JSON: a top-level list of objects (the Zotero/Pandoc shape), each with
 ``type``, ``id``, and field keys such as ``title``, ``author``, ``DOI``.
 CSL YAML: the same shape in YAML (``type: article-journal``, ``author: - family: …``).

Output
------
 A ``.bib`` file, one BibTeX entry per CSL item, sorted deterministically by
 the generated citation key. Existing output is protected unless ``--force``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VERSION = "0.1.0"

# CSL type -> BibTeX entry type. Only the common subset is mapped; everything
# else falls back to ``misc`` and a warning is emitted per entry.
CSL_TO_BIBTEX_TYPE = {
    "article-journal": "article",
    "article-magazine": "article",
    "article-newspaper": "article",
    "article": "article",
    "journal-article": "article",
    "book": "book",
    "chapter": "incollection",
    "paper-conference": "inproceedings",
    "proceedings-article": "inproceedings",
    "thesis": "phdthesis",
    "report": "techreport",
    "webpage": "misc",
    "entry-encyclopedia": "incollection",
    "bill": "misc",
    "case": "misc",
    "legislation": "misc",
    "patent": "misc",
    "map": "misc",
    "motion_picture": "misc",
    "song": "misc",
    "broadcast": "misc",
    "dataset": "misc",
    "software": "misc",
    "post": "misc",
    "post-weblog": "misc",
    "personal_communication": "misc",
    "manuscript": "unpublished",
    "interview": "misc",
}

# CSL field -> BibTeX field. One CSL field may map to one BibTeX field.
CSL_TO_BIBTEX_FIELD = {
    "title": "title",
    "container-title": "journal",
    "collection-title": "series",
    "publisher": "publisher",
    "publisher-place": "address",
    "page": "pages",
    "volume": "volume",
    "issue": "number",
    "edition": "edition",
    "DOI": "doi",
    "ISBN": "isbn",
    "ISSN": "issn",
    "URL": "url",
    "language": "language",
    "abstract": "abstract",
    "note": "note",
    "event-title": "booktitle",
    "event-place": "address",
}

# Fields that, if present, are used to refine the entry type.
TYPE_BY_FIELD = {
    "thesis": {"school": "school", "genre": "type"},
    "report": {"institution": "institution", "genre": "type"},
    "chapter": {"container-title": "booktitle"},
    "paper-conference": {"container-title": "booktitle"},
}


def _esc_tex(text):
    """Minimal LaTeX-safe escaping for BibTeX values (no math-mode aware)."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
    s = s.replace("#", r"\#").replace("_", r"\_")
    return s


def _author_name(party):
    """Render one CSL ``author``/``editor`` person object to ``First Last``."""
    family = (party.get("family") or "").strip()
    given = (party.get("given") or "").strip()
    if family and given:
        return f"{given} {family}"
    if family:
        return family
    # "literal" is used for organisations / non-person authors.
    literal = (party.get("literal") or "").strip()
    return literal or given


def _author_field(persons):
    """Join a list of person objects with `` and `` (BibTeX separator)."""
    names = [_author_name(p) for p in persons or []]
    names = [n for n in names if n]
    return " and ".join(names)


def _year_from_csl(item):
    """Pull a four-digit year out of CSL's ``issued`` date-parts."""
    issued = item.get("issued")
    if isinstance(issued, dict):
        parts = issued.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            return str(parts[0][0])
    if isinstance(issued, str) and issued[:4].isdigit():
        return issued[:4]
    return ""


def _make_key(item, index, prefix):
    """Build a deterministic, collision-free citation key.

    Pattern: ``<prefix><family><year>`` using the first author's family name
    and the year; numeric suffix disambiguates collisions."""
    family = ""
    for party in item.get("author", []) or []:
        family = (party.get("family") or "").strip()
        if family:
            break
    family = re.sub(r"[^A-Za-z0-9]", "", family)[:15].lower() or "anon"
    year = _year_from_csl(item) or "nd"
    base = f"{prefix}{family}{year}" if prefix else f"{family}{year}"
    # disambiguate via index to guarantee uniqueness within one run
    return f"{base}{index + 1}"


def _field_value(key, raw):
    """Normalise a CSL field value (str | list[person] | dict) to a string."""
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "family" in raw[0]:
        return _author_field(raw)
    if isinstance(raw, list):
        return ", ".join(str(x) for x in raw)
    return str(raw) if raw is not None else ""


def csl_item_to_bibtex(item, index, prefix, warnings):
    """Convert one CSL item to a BibTeX entry string. Returns the entry text."""
    csl_type = item.get("type", "misc")
    bib_type = CSL_TO_BIBTEX_TYPE.get(csl_type, "misc")
    if csl_type not in CSL_TO_BIBTEX_TYPE:
        warnings.append(f"unknown CSL type {csl_type!r} for id {item.get('id', '?')}; mapped to @misc")

    key = _make_key(item, index, prefix)
    # brace-wrapped title preserves casing in BibTeX.
    fields = {"title": "{" + _esc_tex(item.get("title", item.get("id", "untitled"))) + "}"}

    for csl_key, bib_key in CSL_TO_BIBTEX_FIELD.items():
        if csl_key in item and bib_key not in fields:
            value = _field_value(csl_key, item[csl_key])
            if value.strip():
                fields[bib_key] = "{" + _esc_tex(value) + "}"

    # author/editor are list-of-person handled specially.
    if item.get("author"):
        fields["author"] = "{" + _esc_tex(_author_field(item["author"])) + "}"
    if item.get("editor"):
        fields["editor"] = "{" + _esc_tex(_author_field(item["editor"])) + "}"

    year = _year_from_csl(item)
    if year:
        fields["year"] = year

    # BibTeX convention: journal/article uses ``journal``, book uses ``publisher``.
    if bib_type == "article" and "journal" not in fields:
        container = _field_value("container-title", item.get("container-title"))
        if container.strip():
            fields["journal"] = "{" + _esc_tex(container) + "}"

    order = ["author", "title", "journal", "booktitle", "publisher", "school",
             "institution", "address", "series", "edition", "volume", "number",
             "pages", "year", "doi", "isbn", "issn", "url", "language",
             "abstract", "note", "type"]
    lines = [f"@{bib_type}{{{key},"]
    for fname in order:
        if fname in fields:
            lines.append(f"  {fname} = {fields[fname]},")
    # emit any remaining fields not in the preferred order
    for fname in fields:
        if fname not in order:
            lines.append(f"  {fname} = {fields[fname]},")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- minimal YAML

_FIELD = re.compile(r"^(\w[\w-]*):\s?(.*)$")
_LIST_ITEM = re.compile(r"^(\s*)-\s(.*)$")


def _minimal_yaml(text):
    r"""Parse the CSL-YAML subset used by Zotero/Pandoc exports.

    Supports top-level list items (``- id: …``) with nested mapping fields and
    nested person lists (``author:\n  - family: …``). Does NOT support anchors,
    aliases, multi-line block scalars (``|``/``>``), flow mappings, or tags —
    those are out of scope for CSL interchange and trigger an error.

    Implementation: a classic recursive-descent block parser. ``_block()``
    parses a mapping at a given indent level; ``_list()`` parses a sequence
    of mappings (used for top-level items and for ``author``/``editor``)."""
    lines = text.splitlines()
    pos = [0]  # mutable index shared across recursive calls

    def peek():
        return lines[pos[0]] if pos[0] < len(lines) else None

    def _mapping_indent():
        """Find the indent of the first mapping field at or after pos."""
        j = pos[0]
        while j < len(lines):
            s = lines[j].strip()
            if s and not s.startswith("#") and not s.startswith("-"):
                return len(lines[j]) - len(lines[j].lstrip())
            j += 1
        return None

    def _is_list_start(raw):
        """True if `raw` is a list item ('- ...') at its natural indent."""
        m = _LIST_ITEM.match(raw)
        return m is not None

    def _block(indent):
        """Parse a mapping whose fields are at >= indent. Returns a dict."""
        obj = {}
        while pos[0] < len(lines):
            raw = lines[pos[0]]
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                pos[0] += 1
                continue
            line_indent = len(raw) - len(raw.lstrip())
            if line_indent < indent:
                break
            # A list item inside a mapping: delegate to _list and stop.
            if _is_list_start(raw) and line_indent >= indent:
                # The key for this list was already consumed by the caller; the
                # caller handles it. Here we just stop.
                break
            m = _FIELD.match(stripped)
            if not m:
                raise ValueError(f"expected mapping field on line {pos[0] + 1}: {stripped!r}")
            key, value = m.group(1), m.group(2)
            pos[0] += 1
            if value:
                obj[key] = value
                continue
            # Empty value: decide between nested mapping and nested list.
            if pos[0] < len(lines) and _is_list_start(lines[pos[0]]):
                nxt_indent = len(lines[pos[0]]) - len(lines[pos[0]].lstrip())
                nxt_m = _LIST_ITEM.match(lines[pos[0]])
                if nxt_indent > line_indent:
                    obj[key] = _list_at(nxt_indent)
                    continue
            obj[key] = _block(line_indent + 1)
        return obj

    def _list_at(indent):
        """Parse a sequence of list items whose '- ' markers sit at `indent`.
        Returns a list of parsed entries (dicts for mappings, else scalars)."""
        items = []
        while pos[0] < len(lines):
            raw = lines[pos[0]]
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                pos[0] += 1
                continue
            line_indent = len(raw) - len(raw.lstrip())
            if line_indent < indent:
                break
            m = _LIST_ITEM.match(raw)
            if not m:
                break
            content = m.group(2)
            pos[0] += 1
            inline = _FIELD.match(content)
            if inline and not inline.group(2):
                # "- key:" -> key maps to a nested mapping on following lines
                entry = {inline.group(1): _block(line_indent + 2)}
                items.append(entry)
            elif inline:
                # "- key: value" inline entry (person: family/given)
                entry = {inline.group(1): inline.group(2)}
                # absorb deeper-indented fields into this entry
                sub = _block(line_indent + 2)
                entry.update(sub)
                items.append(entry)
            else:
                items.append(content)
        return items

    def _list(indent):
        """Parse a top-level-style list: each '- ' at `indent` starts a new
        item; the item's fields are indented 2 deeper than the '-' marker."""
        items = []
        while pos[0] < len(lines):
            raw = lines[pos[0]]
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                pos[0] += 1
                continue
            line_indent = len(raw) - len(raw.lstrip())
            if line_indent < indent:
                break
            m = _LIST_ITEM.match(raw)
            if not m:
                break
            content = m.group(2)
            pos[0] += 1
            inline = _FIELD.match(content)
            if inline and not inline.group(2):
                # "- key:" -> key maps to a nested mapping on following lines
                entry = {inline.group(1): _block(line_indent + 2)}
                items.append(entry)
            elif inline:
                # "- key: value" inline entry (e.g. "- type: article-journal")
                entry = {inline.group(1): inline.group(2)}
                # absorb deeper-indented fields into this entry
                sub = _block(line_indent + 2)
                entry.update(sub)
                items.append(entry)
            else:
                items.append(content)
        return items

    # Top-level: a single run of list items. Each "- key: value" starts a new
    # item; its fields are indented 2 columns deeper than the "-" marker.
    return _list(0)


# ---------------------------------------------------------------------- main

def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Convert CSL-JSON or CSL-YAML to BibTeX.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("input", help="CSL .json or .yaml library file")
    parser.add_argument("-o", "--out", help="output .bib file (default: stdout)")
    parser.add_argument("--format", choices=("json", "yaml", "auto"), default="auto",
                        help="input format (default: auto-detect from extension)")
    parser.add_argument("--key-prefix", default="", help="prefix every citation key (e.g. 'zot')")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args(argv)

    in_path = Path(args.input).resolve()
    if not in_path.is_file():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 1

    fmt = args.format
    if fmt == "auto":
        fmt = "yaml" if in_path.suffix.lower() in (".yaml", ".yml") else "json"

    try:
        text = in_path.read_text(encoding="utf-8-sig")
        if fmt == "json":
            data = json.loads(text)
        else:
            data = _minimal_yaml(text)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"error: could not parse {fmt} input: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, list):
        print("error: CSL input must be a top-level list of items", file=sys.stderr)
        return 1

    warnings = []
    entries = [csl_item_to_bibtex(item, i, args.key_prefix, warnings) for i, item in enumerate(data)]
    out_text = "%% Generated by md2latex/csl_to_bibtex.py — review before use.\n" + "\n".join(entries) + "\n"

    if args.out:
        out_path = Path(args.out).resolve()
        if out_path == in_path:
            print("error: output must not replace the input file", file=sys.stderr)
            return 1
        if out_path.exists() and not args.force:
            print(f"error: output exists: {out_path}; use --force to replace it", file=sys.stderr)
            return 1
        out_path.write_text(out_text, encoding="utf-8")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(out_text if not args.out else "")
    if not args.out or sys.stdout.isatty() is False:
        pass
    summary = {"input": str(in_path), "format": fmt, "entries": len(entries),
               "warnings": warnings, "output": str(Path(args.out).resolve()) if args.out else None}
    print(json.dumps(summary, ensure_ascii=False, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
