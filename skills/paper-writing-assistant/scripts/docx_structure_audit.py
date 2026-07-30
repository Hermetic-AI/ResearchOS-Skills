#!/usr/bin/env python3
"""Inspect structural DOCX evidence: style inheritance, theme, sections, headers and footers.

The tool is read-only and uses the Python standard library. It inventories XML
parts and style ``basedOn`` chains; it does not calculate Word's final
effective formatting, pagination, field values, or rendered header/footer text.

Usage: python3 docx_structure_audit.py manuscript.docx [--pretty]
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "0.1.0"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def attr(element, name):
    return element.get(W + name) if element is not None else None


def audit(path: Path) -> dict:
    if path.suffix.lower() != ".docx":
        raise ValueError("input must be a .docx file")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        try:
            document = ET.fromstring(archive.read("word/document.xml"))
        except KeyError as exc:
            raise ValueError("DOCX has no word/document.xml") from exc
        styles = ET.fromstring(archive.read("word/styles.xml")) if "word/styles.xml" in names else None
    style_parent = {}
    if styles is not None:
        for style in styles.findall(W + "style"):
            style_id = attr(style, "styleId")
            parent = style.find(W + "basedOn")
            if style_id:
                style_parent[style_id] = attr(parent, "val")
    chains, cycles = {}, []
    for style_id in sorted(style_parent):
        chain, seen, current = [], set(), style_id
        while current:
            if current in seen:
                cycles.append(style_id); break
            seen.add(current); chain.append(current); current = style_parent.get(current)
        chains[style_id] = chain
    sections = list(document.iter(W + "sectPr"))
    header_refs = sum(1 for section in sections for _ in section.findall(W + "headerReference"))
    footer_refs = sum(1 for section in sections for _ in section.findall(W + "footerReference"))
    return {
        "schema_version": "1.0.0", "artifact_type": "docx-structure-audit", "tool_version": VERSION,
        "document": str(path.resolve()),
        "parts": {
            "theme_present": "word/theme/theme1.xml" in names,
            "header_parts": sorted(name for name in names if name.startswith("word/header") and name.endswith(".xml")),
            "footer_parts": sorted(name for name in names if name.startswith("word/footer") and name.endswith(".xml")),
        },
        "sections": {"count": len(sections), "header_references": header_refs, "footer_references": footer_refs},
        "styles": {"present": styles is not None, "count": len(style_parent), "based_on_chains": chains, "cycles": sorted(set(cycles))},
        "warnings": [
            "Style chains show declared inheritance only; Word theme/default/style precedence is not fully resolved.",
            "Header/footer part presence and references do not prove their rendered content or section applicability.",
            "Pagination, page-number fields, final fonts, and layout require Word/PDF rendering verification.",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(audit(Path(args.document)), ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
