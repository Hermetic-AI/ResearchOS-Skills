#!/usr/bin/env python3
"""Convert research bibliographies among JSON, BibTeX, RIS, and EndNote XML."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.1.0"
FORMATS = ("researchos-json", "csl-json", "bibtex", "ris", "endnote-xml")
TYPE_TO_BIB = {
    "article-journal": "article",
    "book": "book",
    "chapter": "incollection",
    "paper-conference": "inproceedings",
    "thesis": "phdthesis",
    "report": "techreport",
    "webpage": "online",
    "preprint": "unpublished",
}
BIB_TO_TYPE = {value: key for key, value in TYPE_TO_BIB.items()}
RIS_TO_TYPE = {
    "JOUR": "article-journal",
    "BOOK": "book",
    "CHAP": "chapter",
    "CPAPER": "paper-conference",
    "CONF": "paper-conference",
    "THES": "thesis",
    "RPRT": "report",
    "ELEC": "webpage",
    "UNPB": "preprint",
}
TYPE_TO_RIS = {value: key for key, value in RIS_TO_TYPE.items()}
TYPE_TO_RIS["paper-conference"] = "CPAPER"
TYPE_TO_ENDNOTE = {
    "article-journal": ("Journal Article", "17"),
    "book": ("Book", "6"),
    "chapter": ("Book Section", "5"),
    "paper-conference": ("Conference Proceedings", "10"),
    "thesis": ("Thesis", "32"),
    "report": ("Report", "27"),
    "webpage": ("Web Page", "12"),
    "preprint": ("Unpublished Work", "34"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("input", help="source bibliography")
    parser.add_argument("--from", dest="source_format", choices=("auto", *FORMATS), default="auto")
    parser.add_argument("--to", dest="target_format", choices=FORMATS, required=True)
    parser.add_argument("--out", required=True, help="converted bibliography output")
    parser.add_argument(
        "--manifest-out",
        help="conversion manifest (default: <out>.manifest.json)",
    )
    parser.add_argument("--force", action="store_true", help="replace existing output files")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when a record lacks both title and scholarly identifier",
    )
    return parser


def clean(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def parse_year(value: Any) -> int | None:
    match = re.search(r"\b(1[5-9]\d{2}|20\d{2}|2100)\b", str(value or ""))
    return int(match.group(1)) if match else None


def normalize_doi(value: Any) -> str | None:
    text = clean(value)
    if not text:
        return None
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi\s*:\s*)", "", text, flags=re.I)
    return text.rstrip(".,;").lower()


def author_from_string(value: str) -> dict[str, str]:
    value = clean(value) or ""
    if "," in value:
        family, given = [part.strip() for part in value.split(",", 1)]
        return {"family": family, "given": given}
    parts = value.split()
    if len(parts) >= 2:
        return {"family": parts[-1], "given": " ".join(parts[:-1])}
    return {"literal": value}


def author_to_string(author: dict[str, Any]) -> str:
    if author.get("literal"):
        return str(author["literal"])
    family, given = clean(author.get("family")), clean(author.get("given"))
    return ", ".join(part for part in (family, given) if part) or "Unknown"


def canonical_item(raw: dict[str, Any], index: int) -> dict[str, Any]:
    authors = raw.get("authors") or raw.get("author") or []
    normalized_authors = []
    for author in authors if isinstance(authors, list) else [authors]:
        if isinstance(author, dict):
            normalized_authors.append(
                {
                    key: value
                    for key, value in {
                        "family": clean(author.get("family") or author.get("lastName")),
                        "given": clean(author.get("given") or author.get("firstName")),
                        "literal": clean(author.get("literal") or author.get("name")),
                    }.items()
                    if value
                }
            )
        elif clean(author):
            normalized_authors.append(author_from_string(str(author)))
    item_type = clean(raw.get("type") or raw.get("itemType")) or "article-journal"
    aliases = {
        "journalarticle": "article-journal",
        "conferencepaper": "paper-conference",
        "booksection": "chapter",
        "thesis": "thesis",
        "preprint": "preprint",
    }
    item_type = aliases.get(item_type.replace("-", "").casefold(), item_type)
    keywords = raw.get("keywords") or raw.get("keyword") or raw.get("tags") or []
    if isinstance(keywords, str):
        keywords = [part.strip() for part in re.split(r"[;,]", keywords) if part.strip()]
    normalized_keywords = []
    for keyword in keywords:
        if isinstance(keyword, dict):
            keyword = keyword.get("tag")
        if clean(keyword):
            normalized_keywords.append(clean(keyword))
    extra = str(raw.get("extra") or "")
    extra_pmid = re.search(r"\bPMID\s*:\s*(\d{1,9})\b", extra, re.I)
    extra_arxiv = re.search(r"\barXiv\s*:\s*([^\s;]+)", extra, re.I)
    archive_arxiv = (
        raw.get("archive_location") or raw.get("archive-location")
        if str(raw.get("archive") or "").casefold() == "arxiv"
        else None
    )
    return {
        "id": clean(raw.get("id") or raw.get("key")) or f"item-{index + 1}",
        "type": item_type,
        "title": clean(raw.get("title")),
        "authors": normalized_authors,
        "year": parse_year(raw.get("year") or raw.get("issued") or raw.get("date")),
        "container_title": clean(raw.get("container_title") or raw.get("container-title") or raw.get("publicationTitle") or raw.get("journal")),
        "volume": clean(raw.get("volume")),
        "issue": clean(raw.get("issue")),
        "pages": clean(raw.get("pages") or raw.get("page")),
        "doi": normalize_doi(raw.get("doi") or raw.get("DOI")),
        "pmid": clean(raw.get("pmid") or raw.get("PMID") or (extra_pmid.group(1) if extra_pmid else None)),
        "arxiv_id": clean(raw.get("arxiv_id") or raw.get("arxiv") or raw.get("eprint") or archive_arxiv or (extra_arxiv.group(1) if extra_arxiv else None)),
        "url": clean(raw.get("url") or raw.get("URL")),
        "abstract": clean(raw.get("abstract") or raw.get("abstractNote")),
        "keywords": normalized_keywords,
        "citation_key": clean(raw.get("citation_key") or raw.get("citation-key")),
    }


def parse_json_source(text: str) -> list[dict[str, Any]]:
    payload = json.loads(text)
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        records = payload["items"]
    elif isinstance(payload, dict) and isinstance(payload.get("entries"), list):
        records = payload["entries"]
    elif isinstance(payload, list):
        records = [record.get("data", record) if isinstance(record, dict) else record for record in payload]
    else:
        raise ValueError("JSON must contain items/entries or be an array")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("every JSON bibliography record must be an object")
    csl_records = []
    for record in records:
        if isinstance(record.get("data"), dict):
            record = record["data"]
        if "creators" in record and "author" not in record and "authors" not in record:
            record = {
                **record,
                "authors": [creator for creator in record.get("creators", []) if creator.get("creatorType", "author") == "author"],
            }
        csl_records.append(record)
    return csl_records


def split_bibtex_entries(text: str) -> list[tuple[str, str, str]]:
    entries = []
    position = 0
    while True:
        match = re.search(r"@(\w+)\s*([\{(])\s*([^,\s]+)\s*,", text[position:], re.I)
        if not match:
            break
        start = position + match.start()
        body_start = position + match.end()
        opener = match.group(2)
        closer = "}" if opener == "{" else ")"
        depth, quoted, escaped = 1, False, False
        cursor = body_start
        while cursor < len(text):
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted:
                if char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
                    if depth == 0:
                        break
            cursor += 1
        if depth != 0:
            raise ValueError(f"unclosed BibTeX entry near byte {start}")
        entries.append((match.group(1).lower(), match.group(3), text[body_start:cursor]))
        position = cursor + 1
    return entries


def split_bibtex_fields(body: str) -> dict[str, str]:
    fields = {}
    position = 0
    while position < len(body):
        match = re.search(r"([A-Za-z][\w-]*)\s*=\s*", body[position:])
        if not match:
            break
        name = match.group(1).lower()
        cursor = position + match.end()
        if cursor >= len(body):
            break
        if body[cursor] in '{"':
            opener = body[cursor]
            closer = "}" if opener == "{" else '"'
            cursor += 1
            start, depth, escaped = cursor, 1, False
            while cursor < len(body):
                char = body[cursor]
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif opener == "{" and char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
                    if depth == 0:
                        break
                cursor += 1
            fields[name] = clean(body[start:cursor]) or ""
            position = cursor + 1
        else:
            end = body.find(",", cursor)
            end = len(body) if end < 0 else end
            fields[name] = clean(body[cursor:end]) or ""
            position = end + 1
    return fields


def parse_bibtex(text: str) -> list[dict[str, Any]]:
    records = []
    for entry_type, key, body in split_bibtex_entries(text):
        fields = split_bibtex_fields(body)
        records.append(
            {
                "id": key,
                "citation_key": key,
                "type": BIB_TO_TYPE.get(entry_type, "article-journal"),
                "title": fields.get("title"),
                "authors": [author_from_string(value) for value in re.split(r"\s+and\s+", fields.get("author", ""), flags=re.I) if clean(value)],
                "year": fields.get("year"),
                "container_title": fields.get("journal") or fields.get("booktitle"),
                "volume": fields.get("volume"),
                "issue": fields.get("number"),
                "pages": fields.get("pages"),
                "doi": fields.get("doi"),
                "pmid": fields.get("pmid"),
                "arxiv_id": fields.get("eprint"),
                "url": fields.get("url"),
                "abstract": fields.get("abstract"),
                "keywords": fields.get("keywords"),
            }
        )
    if not records:
        raise ValueError("no BibTeX entries found")
    return records


def parse_ris(text: str) -> list[dict[str, Any]]:
    records, current = [], {}
    last_tag = None
    for line in text.splitlines():
        match = re.match(r"^([A-Z0-9]{2})\s{0,2}-\s?(.*)$", line)
        if match:
            tag, value = match.groups()
            if tag == "TY":
                current = {"TY": [value]}
            elif tag == "ER":
                if current:
                    records.append(current)
                current, last_tag = {}, None
                continue
            else:
                current.setdefault(tag, []).append(value)
            last_tag = tag
        elif line[:1].isspace() and current and last_tag:
            current[last_tag][-1] += " " + line.strip()
    if current:
        records.append(current)
    if not records:
        raise ValueError("no RIS records found")
    return [
        {
            "type": RIS_TO_TYPE.get((record.get("TY") or ["JOUR"])[0], "article-journal"),
            "title": ((record.get("TI") or record.get("T1") or [None])[0]),
            "authors": [author_from_string(author) for author in record.get("AU", [])],
            "year": ((record.get("PY") or record.get("Y1") or [None])[0]),
            "container_title": ((record.get("JO") or record.get("JF") or record.get("T2") or [None])[0]),
            "volume": (record.get("VL") or [None])[0],
            "issue": (record.get("IS") or [None])[0],
            "pages": (record.get("SP") or [None])[0],
            "doi": (record.get("DO") or [None])[0],
            "pmid": (record.get("AN") or [None])[0],
            "arxiv_id": (record.get("C3") or [None])[0],
            "url": (record.get("UR") or [None])[0],
            "abstract": (record.get("AB") or [None])[0],
            "keywords": record.get("KW", []),
            "citation_key": (record.get("ID") or [None])[0],
        }
        for record in records
    ]


def child_text(parent: ET.Element, path: str) -> str | None:
    element = parent.find(path)
    return clean("".join(element.itertext())) if element is not None else None


def parse_endnote_xml(text: str) -> list[dict[str, Any]]:
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise ValueError("DOCTYPE and ENTITY declarations are not accepted")
    root = ET.fromstring(text)
    records = []
    for record in root.findall(".//record"):
        ref_type = record.find("ref-type")
        name = (ref_type.get("name", "") if ref_type is not None else "").casefold()
        item_type = next((kind for kind, (label, _) in TYPE_TO_ENDNOTE.items() if label.casefold() == name), "article-journal")
        records.append(
            {
                "id": child_text(record, "rec-number"),
                "type": item_type,
                "title": child_text(record, "titles/title"),
                "authors": [author_from_string(clean("".join(author.itertext())) or "") for author in record.findall("contributors/authors/author")],
                "year": child_text(record, "dates/year"),
                "container_title": child_text(record, "titles/secondary-title"),
                "volume": child_text(record, "volume"),
                "issue": child_text(record, "number"),
                "pages": child_text(record, "pages"),
                "doi": child_text(record, "electronic-resource-num"),
                "pmid": child_text(record, "accession-num"),
                "arxiv_id": child_text(record, "label"),
                "url": child_text(record, "urls/related-urls/url"),
                "abstract": child_text(record, "abstract"),
                "keywords": [clean("".join(keyword.itertext())) for keyword in record.findall("keywords/keyword") if clean("".join(keyword.itertext()))],
            }
        )
    if not records:
        raise ValueError("no EndNote XML records found")
    return records


def detect_format(path: Path, text: str) -> str:
    suffix = path.suffix.lower()
    if suffix == ".bib" or re.search(r"@\w+\s*[\{(]", text):
        return "bibtex"
    if suffix == ".ris" or re.search(r"(?m)^TY\s{0,2}-", text):
        return "ris"
    if suffix == ".xml" or text.lstrip().startswith("<"):
        return "endnote-xml"
    payload = json.loads(text)
    if isinstance(payload, dict) and payload.get("artifact_type") == "bibliography-library":
        return "researchos-json"
    return "csl-json"


def assign_citation_keys(items: list[dict[str, Any]]) -> None:
    used = set()
    for item in items:
        base = clean(item.get("citation_key"))
        if not base:
            author = item["authors"][0].get("family") if item.get("authors") else "item"
            title_word = next(iter(re.findall(r"[A-Za-z0-9]+", item.get("title") or "work")), "work")
            base = f"{author or 'item'}{item.get('year') or 'nd'}{title_word}"
        base = re.sub(r"[^A-Za-z0-9_:-]", "", base) or f"item{len(used) + 1}"
        candidate, suffix = base, 0
        while candidate.casefold() in used:
            suffix += 1
            candidate = base + chr(ord("a") + suffix - 1) if suffix <= 26 else f"{base}{suffix}"
        used.add(candidate.casefold())
        item["citation_key"] = candidate
        item["id"] = clean(item.get("id")) or candidate


def render_researchos(items: list[dict[str, Any]], source: Path, warnings: list[str]) -> str:
    artifact = {
        "schema_version": "1.0.0",
        "artifact_type": "bibliography-library",
        "items": items,
        "warnings": warnings,
        "provenance": {
            "created_by": "literature-reader/scripts/convert_bibliography.py",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "command": " ".join(["convert_bibliography.py", *sys.argv[1:]]),
            "seed": None,
            "sources": [{"kind": "file", "locator": str(source.resolve()), "checksum": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()}],
            "warnings": warnings,
        },
    }
    return json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"


def render_csl(items: list[dict[str, Any]]) -> str:
    payload = []
    for item in items:
        record = {
            "id": item["citation_key"],
            "type": item["type"],
            "title": item["title"],
            "author": item["authors"],
            "issued": {"date-parts": [[item["year"]]]} if item["year"] else None,
            "container-title": item["container_title"],
            "volume": item["volume"],
            "issue": item["issue"],
            "page": item["pages"],
            "DOI": item["doi"],
            "PMID": item["pmid"],
            "archive": "arXiv" if item["arxiv_id"] else None,
            "archive_location": item["arxiv_id"],
            "URL": item["url"],
            "abstract": item["abstract"],
            "keyword": ", ".join(item["keywords"]) if item["keywords"] else None,
        }
        payload.append({key: value for key, value in record.items() if value not in (None, [], "")})
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_bibtex(items: list[dict[str, Any]]) -> str:
    blocks = []
    for item in items:
        fields = {
            "title": item["title"],
            "author": " and ".join(author_to_string(author) for author in item["authors"]),
            "year": item["year"],
            "journal" if item["type"] == "article-journal" else "booktitle": item["container_title"],
            "volume": item["volume"],
            "number": item["issue"],
            "pages": item["pages"],
            "doi": item["doi"],
            "pmid": item["pmid"],
            "eprint": item["arxiv_id"],
            "archivePrefix": "arXiv" if item["arxiv_id"] else None,
            "url": item["url"],
            "abstract": item["abstract"],
            "keywords": ", ".join(item["keywords"]) if item["keywords"] else None,
        }
        lines = [f"@{TYPE_TO_BIB.get(item['type'], 'misc')}{{{item['citation_key']},"]
        active = [(name, value) for name, value in fields.items() if value not in (None, "")]
        for index, (name, value) in enumerate(active):
            comma = "," if index < len(active) - 1 else ""
            lines.append(f"  {name} = {{{value}}}{comma}")
        lines.append("}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def render_ris(items: list[dict[str, Any]]) -> str:
    records = []
    for item in items:
        lines = [f"TY  - {TYPE_TO_RIS.get(item['type'], 'GEN')}", f"ID  - {item['citation_key']}"]
        mapping = (
            ("TI", item["title"]), ("PY", item["year"]), ("JO", item["container_title"]),
            ("VL", item["volume"]), ("IS", item["issue"]), ("SP", item["pages"]),
            ("DO", item["doi"]), ("AN", item["pmid"]), ("C3", item["arxiv_id"]),
            ("UR", item["url"]), ("AB", item["abstract"]),
        )
        lines.extend(f"AU  - {author_to_string(author)}" for author in item["authors"])
        lines.extend(f"{tag}  - {value}" for tag, value in mapping if value not in (None, ""))
        lines.extend(f"KW  - {keyword}" for keyword in item["keywords"])
        lines.append("ER  -")
        records.append("\n".join(lines))
    return "\n\n".join(records) + "\n"


def add_text(parent: ET.Element, tag: str, value: Any) -> None:
    if value not in (None, "", []):
        ET.SubElement(parent, tag).text = str(value)


def render_endnote(items: list[dict[str, Any]]) -> str:
    root = ET.Element("xml")
    records = ET.SubElement(root, "records")
    for position, item in enumerate(items, start=1):
        record = ET.SubElement(records, "record")
        add_text(record, "rec-number", position)
        name, code = TYPE_TO_ENDNOTE.get(item["type"], ("Generic", "13"))
        ref_type = ET.SubElement(record, "ref-type", {"name": name})
        ref_type.text = code
        contributors = ET.SubElement(record, "contributors")
        authors = ET.SubElement(contributors, "authors")
        for author in item["authors"]:
            add_text(authors, "author", author_to_string(author))
        titles = ET.SubElement(record, "titles")
        add_text(titles, "title", item["title"])
        add_text(titles, "secondary-title", item["container_title"])
        dates = ET.SubElement(record, "dates")
        add_text(dates, "year", item["year"])
        for tag, value in (("volume", item["volume"]), ("number", item["issue"]), ("pages", item["pages"]), ("electronic-resource-num", item["doi"]), ("accession-num", item["pmid"]), ("label", item["arxiv_id"]), ("abstract", item["abstract"])):
            add_text(record, tag, value)
        if item["keywords"]:
            keywords = ET.SubElement(record, "keywords")
            for keyword in item["keywords"]:
                add_text(keywords, "keyword", keyword)
        if item["url"]:
            urls = ET.SubElement(record, "urls")
            related = ET.SubElement(urls, "related-urls")
            add_text(related, "url", item["url"])
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def convert(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    source = Path(args.input)
    if source.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("input exceeds the 50 MiB safety limit")
    text = source.read_text(encoding="utf-8-sig")
    source_format = detect_format(source, text) if args.source_format == "auto" else args.source_format
    parsers = {
        "researchos-json": parse_json_source,
        "csl-json": parse_json_source,
        "bibtex": parse_bibtex,
        "ris": parse_ris,
        "endnote-xml": parse_endnote_xml,
    }
    raw_items = parsers[source_format](text)
    items = [canonical_item(item, index) for index, item in enumerate(raw_items)]
    warnings = []
    for index, item in enumerate(items):
        if not item["title"] and not any((item["doi"], item["pmid"], item["arxiv_id"])):
            message = f"item {index}: missing title and scholarly identifier"
            if args.strict:
                raise ValueError(message)
            warnings.append(message)
    assign_citation_keys(items)
    renderers = {
        "researchos-json": lambda: render_researchos(items, source, warnings),
        "csl-json": lambda: render_csl(items),
        "bibtex": lambda: render_bibtex(items),
        "ris": lambda: render_ris(items),
        "endnote-xml": lambda: render_endnote(items),
    }
    rendered = renderers[args.target_format]()
    manifest = {
        "schema_version": "1.0.0",
        "artifact_type": "bibliography-conversion",
        "source_format": source_format,
        "target_format": args.target_format,
        "record_count": len(items),
        "input": {"kind": "file", "locator": str(source.resolve()), "checksum": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()},
        "output": {"kind": "file", "locator": str(Path(args.out).resolve()), "checksum": "sha256:" + hashlib.sha256(rendered.encode("utf-8")).hexdigest()},
        "warnings": warnings,
        "provenance": {
            "created_by": "literature-reader/scripts/convert_bibliography.py",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "command": " ".join(["convert_bibliography.py", *sys.argv[1:]]),
            "seed": None,
            "sources": [{"kind": "file", "locator": str(source.resolve()), "checksum": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()}],
            "warnings": warnings,
        },
    }
    return rendered, manifest


def validate_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    source, output = Path(args.input), Path(args.out)
    manifest = Path(args.manifest_out) if args.manifest_out else Path(str(output) + ".manifest.json")
    if not source.is_file():
        raise ValueError(f"input not found: {source}")
    if not output.parent.is_dir() or not manifest.parent.is_dir():
        raise ValueError("output and manifest parent directories must already exist")
    resolved = [source.resolve(), output.resolve(), manifest.resolve()]
    if len(set(resolved)) != len(resolved):
        raise ValueError("input, output, and manifest paths must be distinct")
    existing = [path for path in (output, manifest) if path.exists()]
    if existing and not args.force:
        raise ValueError(f"output exists: {existing[0]}; use --force to replace it")
    return source, output, manifest


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, output, manifest_path = validate_paths(args)
        rendered, manifest = convert(args)
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    output.write_text(rendered, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written: {output}", file=sys.stderr)
    print(f"written: {manifest_path}", file=sys.stderr)
    print(json.dumps({"output": str(output), "manifest": str(manifest_path), "records": manifest["record_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
