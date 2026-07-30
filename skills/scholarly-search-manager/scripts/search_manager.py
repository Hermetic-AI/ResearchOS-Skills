#!/usr/bin/env python3
"""Manage scholarly search queries, deduplicate results, and exchange formats.

Purpose:
    A zero-dependency (stdlib only) helper for the discovery phase of a
    literature review. It (1) formats a structured query into database-specific
    search strings (PubMed, Crossref, Semantic Scholar) via urllib-ready
    templates, (2) deduplicates a local result list by normalized DOI then by
    normalized title/year, and (3) exports a local library to RIS, BibTeX, or
    CSV. It never performs network calls on its own; online queries require the
    user's explicit authorization and the target service's terms.

Dependencies:
    None (Python 3.8+ standard library only).

CLI usage:
    # 1. Build database-specific search strings from a structured query.
    python3 search_manager.py --mode plan --query query.json --out search-plan.json

    # 2. Deduplicate a local result list (DOI first, then title/year).
    python3 search_manager.py --mode dedupe --library results.json --out deduped.json

    # 3. Export a local library to RIS / BibTeX / CSV.
    python3 search_manager.py --mode export --library library.json --format ris --out library.ris
    python3 search_manager.py --mode export --library library.json --format bib --out library.bib
    python3 search_manager.py --mode export --library library.json --format csv --out library.csv

    Common options: --force  --version
    Export-only   : --format ris|bib|csv  (default ris)

Query file format (for --mode plan):
    {
      "question": "...",
      "concepts": [
        {"term": "synapse", "synonyms": ["synaptic"], "pubmed_field": "tiab"},
        {"term": "plasticity", "synonyms": []}
      ],
      "filters": {"pubmed": {"dates": "2018:2024", "species": "humans"}}
    }

Output format:
    --mode plan   -> search-plan.json  (per-database formatted strings + provenance)
    --mode dedupe -> deduped.json      (canonical items + duplicate_clusters)
    --mode export -> target file (RIS/BibTeX/CSV) + a JSON manifest on stdout
    Every JSON artifact carries schema_version, artifact_type, tool_version,
    and warnings. Exit code 0 on success, 1 on bad input.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

VERSION = "0.1.0"

# Normalization helpers -------------------------------------------------------

_DOI_PREFIX_RE = re.compile(r"^https?://(?:dx\.)?doi\.org/", re.IGNORECASE)
_DOI_SCHEME_RE = re.compile(r"^doi:\s*", re.IGNORECASE)


def normalize_doi(value):
    if value is None:
        return ""
    cleaned = _DOI_PREFIX_RE.sub("", str(value).strip())
    cleaned = _DOI_SCHEME_RE.sub("", cleaned)
    return cleaned.lower()


def normalize_title(value):
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def strip_markup(text):
    if text is None:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


# Search-string formatting ----------------------------------------------------

def _or_join(terms):
    terms = [t for t in terms if str(t).strip()]
    if not terms:
        return ""
    if len(terms) == 1:
        return str(terms[0]).strip()
    return "(" + " OR ".join(f'"{t}"' if " " in str(t) else str(t) for t in terms) + ")"


def _pubmed_string(concept):
    field = concept.get("pubmed_field") or "tiab"
    terms = [concept.get("term", "")] + concept.get("synonyms", [])
    return f'"{concept.get("term", "")}"[{field}]' if not concept.get("synonyms") else (
        _or_join(terms) + f"[{field}]"
    )


def build_search_plan(query):
    concepts = query.get("concepts") or []
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("query must contain a non-empty 'concepts' list")

    pubmed_groups = []
    generic_groups = []
    for concept in concepts:
        if not isinstance(concept, dict) or not str(concept.get("term", "")).strip():
            raise ValueError("every concept needs a non-empty 'term'")
        pubmed_groups.append(_pubmed_string(concept))
        terms = [concept["term"]] + concept.get("synonyms", [])
        generic_groups.append(_or_join(terms))

    pubmed_clause = " AND ".join(pubmed_groups)
    generic_clause = " AND ".join(generic_groups)
    filters = query.get("filters") or {}
    pubmed_filters = filters.get("pubmed") or {}
    pubmed_suffix = ""
    if pubmed_filters.get("dates"):
        pubmed_suffix += f' AND ("{pubmed_filters["dates"]}"[Date - Publication])'
    if pubmed_filters.get("species"):
        pubmed_suffix += f' AND {pubmed_filters["species"]}[MeSH Terms]'

    plan = {
        "question": query.get("question", ""),
        "databases": {
            "pubmed": {
                "search_string": pubmed_clause + pubmed_suffix,
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=" + quote(pubmed_clause + pubmed_suffix),
                "notes": "MeSH/field-tagged; run manually and record retrieval date.",
            },
            "crossref": {
                "search_string": generic_clause,
                "url": "https://search.crossref.org/?q=" + quote(generic_clause),
                "notes": "Free-text query; no field tags.",
            },
            "semantic_scholar": {
                "search_string": generic_clause,
                "url": "https://api.semanticscholar.org/graph/v1/paper/search?query=" + quote(generic_clause),
                "notes": "API call requires user authorization and rate-limit handling.",
            },
        },
    }
    return plan


# Deduplication ---------------------------------------------------------------

def deduplicate(items):
    if not isinstance(items, list):
        raise ValueError("library must be a JSON list of records")
    doi_buckets = {}
    title_buckets = {}
    unresolved = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"item {idx} is not an object")
        doi = normalize_doi(item.get("doi"))
        if doi:
            doi_buckets.setdefault("doi:" + doi, []).append((idx, item))
            continue
        title_key = normalize_title(item.get("title"))
        year = str(item.get("year", "")).strip()
        if title_key:
            title_buckets.setdefault("title-year:" + title_key + ":" + year, []).append((idx, item))
        else:
            unresolved.append((idx, item))

    canonical = []
    clusters = []
    seen_indexes = set()

    def _emit(bucket):
        best = max(bucket, key=lambda pair: sum(
            bool(pair[1].get(field)) for field in ("doi", "title", "authors", "abstract", "year")))[1]
        canonical.append(best)
        if len(bucket) > 1:
            clusters.append({
                "key": bucket_key,
                "canonical_index": items.index(best),
                "member_indexes": [i for i, _ in bucket],
                "action": "review-and-merge-metadata; do-not-delete-automatically",
            })
        seen_indexes.update(i for i, _ in bucket)

    for bucket_key, bucket in doi_buckets.items():
        _emit(bucket)
    for bucket_key, bucket in title_buckets.items():
        _emit(bucket)
    for idx, item in unresolved:
        canonical.append(item)
        seen_indexes.add(idx)

    warnings = []
    if unresolved:
        warnings.append(f"{len(unresolved)} record(s) lacked DOI and title; kept as-is, review manually.")
    warnings.append("Title/year clusters are candidates, not proof of duplicates. Review authors, version, and identifiers before merging.")
    return canonical, clusters, warnings


# Format export ---------------------------------------------------------------

def _ris_line(tag, value):
    if value in (None, "", []):
        return ""
    return f"{tag}  - {value}\n"


def _ris_authors(value):
    if isinstance(value, list):
        return [str(a) for a in value if str(a).strip()]
    return [str(value)] if value else []


def to_ris(items):
    chunks = []
    for n, row in enumerate(items, 1):
        if not isinstance(row, dict):
            raise ValueError(f"item {n} is not an object")
        chunk = "TY  - JOUR\n"
        for author in _ris_authors(row.get("authors")):
            chunk += _ris_line("AU", author)
        chunk += _ris_line("TI", row.get("title"))
        chunk += _ris_line("PY", row.get("year"))
        chunk += _ris_line("JO", row.get("journal") or row.get("container_title"))
        chunk += _ris_line("VL", row.get("volume"))
        chunk += _ris_line("IS", row.get("issue"))
        chunk += _ris_line("SP", row.get("pages"))
        chunk += _ris_line("DO", row.get("doi"))
        chunk += _ris_line("UR", row.get("url"))
        chunk += _ris_line("AB", row.get("abstract"))
        chunk += "ER  - \n\n"
        chunks.append(chunk)
    return "".join(chunks)


def _bib_escape(value):
    value = strip_markup(str(value))
    return value.replace("&", "\\&")


def to_bibtex(items):
    entries = []
    for n, row in enumerate(items, 1):
        if not isinstance(row, dict):
            raise ValueError(f"item {n} is not an object")
        key = re.sub(r"[^a-zA-Z0-9]", "", str(row.get("authors", [[]])[0] if row.get("authors") else "ref"))[:12]
        key = (key or "ref") + str(row.get("year", ""))
        authors = " and ".join(_ris_authors(row.get("authors"))) if row.get("authors") else ""
        fields = [
            f"  title = {{{_bib_escape(row.get('title', ''))}}}",
            f"  year = {{{row.get('year', '')}}}",
            f"  journal = {{{_bib_escape(row.get('journal') or row.get('container_title', ''))}}}",
        ]
        if row.get("doi"):
            fields.append(f"  doi = {{{row['doi']}}}")
        if row.get("volume"):
            fields.append(f"  volume = {{{row['volume']}}}")
        if authors:
            fields.insert(1, f"  author = {{{_bib_escape(authors)}}}")
        entries.append(f"@article{{{key},\n" + ",\n".join(fields) + ",\n}")
    return "\n\n".join(entries) + "\n"


def to_csv(items):
    fields = ["title", "authors", "year", "journal", "doi", "url", "abstract"]
    rows = []
    for n, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ValueError(f"item {n} is not an object")
        row = dict(item)
        if isinstance(row.get("authors"), list):
            row["authors"] = "; ".join(str(a) for a in row["authors"])
        rows.append(row)
    return fields, rows


# I/O helpers -----------------------------------------------------------------

def load_json(path):
    source = Path(path).resolve(strict=True)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"], source
    if isinstance(payload, list):
        return payload, source
    raise ValueError("input must be a JSON list or an object with an 'items' list")


def ensure_output_path(path, protected, force=False):
    resolved = os.path.abspath(path)
    if resolved in {os.path.abspath(item) for item in protected}:
        raise SystemExit(f"error: output path must not replace an input file: {path}")
    if os.path.exists(resolved) and not force:
        raise SystemExit(f"error: output exists: {path}; use --force to replace a derived artifact")


def write_text(path, text):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


# Main ------------------------------------------------------------------------

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    ap.add_argument("--mode", choices=["plan", "dedupe", "export"], required=True)
    ap.add_argument("--query", help="query.json (for --mode plan)")
    ap.add_argument("--library", help="local library JSON (for --mode dedupe/export)")
    ap.add_argument("--format", choices=["ris", "bib", "csv"], default="ris")
    ap.add_argument("--out", required=True, help="output path")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs")
    args = ap.parse_args(argv)

    try:
        if args.mode == "plan":
            if not args.query:
                raise ValueError("--query is required for --mode plan")
            query = json.loads(Path(args.query).resolve(strict=True).read_text(encoding="utf-8"))
            plan = build_search_plan(query)
            ensure_output_path(args.out, [args.query], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "search-plan",
                "tool_version": VERSION,
                "source_query": str(Path(args.query).resolve()),
                "plan": plan,
                "warnings": [
                    "Search strings are templates only. Online queries require user authorization and the target service's terms.",
                    "Record retrieval date, database, and exact filters for an auditable search log.",
                ],
            }
            write_text(args.out, json.dumps(artifact, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

        if args.mode == "dedupe":
            if not args.library:
                raise ValueError("--library is required for --mode dedupe")
            items, source = load_json(args.library)
            canonical, clusters, warnings = deduplicate(items)
            ensure_output_path(args.out, [str(source)], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "search-library",
                "tool_version": VERSION,
                "input": str(source),
                "input_count": len(items),
                "output_count": len(canonical),
                "items": canonical,
                "duplicate_clusters": clusters,
                "warnings": warnings,
            }
            write_text(args.out, json.dumps(artifact, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

        # export
        if not args.library:
            raise ValueError("--library is required for --mode export")
        items, source = load_json(args.library)
        ensure_output_path(args.out, [str(source)], args.force)
        manifest = {
            "schema_version": "1.0.0",
            "artifact_type": f"{args.format}-export",
            "tool_version": VERSION,
            "input": str(source),
            "output": str(Path(args.out).resolve()),
            "records": len(items),
            "warnings": [
                "Offline format conversion only: fields were not identifier-verified or normalized against a citation style.",
            ],
        }
        if args.format == "ris":
            write_text(args.out, to_ris(items))
        elif args.format == "bib":
            write_text(args.out, to_bibtex(items))
        else:
            fields, rows = to_csv(items)
            with open(args.out, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
