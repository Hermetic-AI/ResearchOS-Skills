#!/usr/bin/env python3
"""Audit scholarly identifiers, retraction signals, duplicates, and versions.

The default audit is offline and deterministic. ``--online`` explicitly checks
Crossref, arXiv, and PubMed using their public APIs; a contact email is required
for responsible API identification. A missing database hit is never reported
as proof that a work is valid or unretracted.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.1.0"
DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
ARXIV_RE = re.compile(
    r"^(?P<base>(?:\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7}))"
    r"(?:v(?P<version>\d+))?$",
    re.IGNORECASE,
)
PMID_RE = re.compile(r"^[1-9]\d{0,8}$")
ATOM = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("input", help="extract_metadata JSON or a JSON list of bibliography entries")
    parser.add_argument("--out", help="write the bibliography-audit JSON here")
    parser.add_argument("--force", action="store_true", help="replace an existing --out file")
    parser.add_argument(
        "--online",
        action="store_true",
        help="query Crossref, arXiv, and PubMed (default: syntax checks only)",
    )
    parser.add_argument(
        "--email",
        help="contact email required for --online API identification; redacted from output",
    )
    parser.add_argument(
        "--retraction-index",
        help="optional local Crossref Retraction Watch CSV for offline integrity alerts",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout in seconds")
    parser.add_argument(
        "--title-threshold",
        type=float,
        default=0.92,
        help="normalized-title similarity used for probable duplicates",
    )
    return parser


def normalize_doi(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi\s*:\s*)", "", text, flags=re.I)
    return text.rstrip(".,;)").lower() or None


def normalize_arxiv(value: Any) -> tuple[str | None, int | None]:
    if value is None:
        return None, None
    text = str(value).strip()
    text = re.sub(r"^(?:https?://arxiv\.org/(?:abs|pdf)/|arxiv\s*:\s*)", "", text, flags=re.I)
    text = text.removesuffix(".pdf")
    match = ARXIV_RE.fullmatch(text)
    if not match:
        return text.lower() or None, None
    version = int(match.group("version")) if match.group("version") else None
    return match.group("base").lower(), version


def normalize_pmid(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    match = re.fullmatch(
        r"(?:(?:PMID\s*[:：]?\s*)|(?:https?://)?(?:www\.)?pubmed\.ncbi\.nlm\.nih\.gov/)?"
        r"(\d{1,9})/?",
        text,
        re.I,
    )
    return match.group(1) if match else None


def normalize_title(value: Any) -> str:
    text = str(value or "").casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def first_author_key(entry: dict[str, Any]) -> str | None:
    authors = entry.get("authors") or []
    if not authors:
        return None
    author = str(authors[0]).casefold().strip()
    if "," in author:
        return re.sub(r"\W+", "", author.split(",", 1)[0]) or None
    parts = re.findall(r"[\w'-]+", author, re.UNICODE)
    return re.sub(r"\W+", "", parts[-1]) if parts else None


def title_similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    a, b = normalize_title(left.get("title")), normalize_title(right.get("title"))
    if len(a) < 12 or len(b) < 12:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        a, b = self.find(left), self.find(right)
        if a != b:
            self.parent[b] = a


def normalize_entry(entry: dict[str, Any], index: int) -> dict[str, Any]:
    doi = normalize_doi(entry.get("doi"))
    arxiv, parsed_version = normalize_arxiv(entry.get("arxiv_id"))
    version = entry.get("arxiv_version")
    if version is None:
        version = parsed_version
    raw_pmid = entry.get("pmid")
    pmid = normalize_pmid(raw_pmid)
    if raw_pmid is not None and str(raw_pmid).strip() and pmid is None:
        pmid = str(raw_pmid).strip()
    return {
        **entry,
        "index": entry.get("index", index),
        "doi": doi,
        "arxiv_id": arxiv,
        "arxiv_version": int(version) if version is not None else None,
        "pmid": pmid,
    }


def load_entries(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    warnings = []
    if isinstance(payload, dict) and isinstance(payload.get("entries"), list):
        raw_entries = payload["entries"]
        warnings.extend(str(item) for item in payload.get("warnings", []))
    elif isinstance(payload, list):
        raw_entries = payload
    else:
        raise ValueError("input must be an extract_metadata object or a JSON list")
    if not all(isinstance(entry, dict) for entry in raw_entries):
        raise ValueError("every bibliography entry must be an object")
    return [normalize_entry(entry, index) for index, entry in enumerate(raw_entries)], warnings


def syntax_audit(entry: dict[str, Any]) -> dict[str, Any]:
    arxiv = entry.get("arxiv_id")
    return {
        "doi": {
            "value": entry.get("doi"),
            "syntax_valid": entry.get("doi") is None or bool(DOI_RE.fullmatch(entry["doi"])),
        },
        "arxiv": {
            "value": arxiv,
            "version": entry.get("arxiv_version"),
            "syntax_valid": arxiv is None or (
                bool(ARXIV_RE.fullmatch(arxiv))
                and (entry.get("arxiv_version") is None or entry["arxiv_version"] >= 1)
            ),
        },
        "pmid": {
            "value": entry.get("pmid"),
            "syntax_valid": entry.get("pmid") is None or bool(PMID_RE.fullmatch(entry["pmid"])),
        },
    }


def build_clusters(entries: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    union = UnionFind(len(entries))
    reasons: dict[tuple[int, int], list[str]] = {}
    for left in range(len(entries)):
        for right in range(left + 1, len(entries)):
            a, b = entries[left], entries[right]
            pair_reasons = []
            if a.get("doi") and a["doi"] == b.get("doi"):
                pair_reasons.append("same-doi")
            if a.get("pmid") and a["pmid"] == b.get("pmid"):
                pair_reasons.append("same-pmid")
            if a.get("arxiv_id") and a["arxiv_id"] == b.get("arxiv_id"):
                pair_reasons.append("same-arxiv-work")
            similarity = title_similarity(a, b)
            same_author = first_author_key(a) and first_author_key(a) == first_author_key(b)
            years = (a.get("year"), b.get("year"))
            close_year = not all(isinstance(year, int) for year in years) or abs(years[0] - years[1]) <= 2
            if similarity >= threshold and same_author and close_year:
                pair_reasons.append(f"probable-title-author-match:{similarity:.3f}")
            if similarity >= 0.85 and ((a.get("doi") and b.get("arxiv_id")) or (b.get("doi") and a.get("arxiv_id"))):
                pair_reasons.append(f"likely-preprint-publication-version:{similarity:.3f}")
            if pair_reasons:
                union.union(left, right)
                reasons[(left, right)] = pair_reasons

    groups: dict[int, list[int]] = {}
    for index in range(len(entries)):
        groups.setdefault(union.find(index), []).append(index)

    clusters = []
    for members in groups.values():
        if len(members) < 2:
            continue
        scores = {}
        for index in members:
            entry = entries[index]
            scores[index] = (
                100 if entry.get("doi") else 0,
                20 if entry.get("pmid") else 0,
                10 if entry.get("arxiv_id") else 0,
                entry.get("arxiv_version") or 0,
                sum(bool(entry.get(field)) for field in ("title", "authors", "year")),
                -index,
            )
        canonical = max(members, key=lambda item: scores[item])
        pair_evidence = []
        for (left, right), pair_reasons in reasons.items():
            if left in members and right in members:
                pair_evidence.append({"entries": [left, right], "reasons": pair_reasons})
        kinds = {reason.split(":", 1)[0] for pair in pair_evidence for reason in pair["reasons"]}
        clusters.append(
            {
                "cluster_id": f"cluster-{len(clusters) + 1:03d}",
                "members": members,
                "canonical_entry": canonical,
                "classification": "version-family" if "likely-preprint-publication-version" in kinds or "same-arxiv-work" in kinds else "probable-duplicate",
                "evidence": pair_evidence,
                "action": "review-and-merge-metadata; do-not-delete-automatically",
            }
        )
    return clusters


def load_retraction_index(path: Path) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_doi: dict[str, list[dict[str, str]]] = {}
    by_pmid: dict[str, list[dict[str, str]]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            record = {
                "nature": row.get("RetractionNature", "") or "Retraction",
                "date": row.get("RetractionDate", ""),
                "record_id": row.get("Record ID", ""),
                "source": "crossref-retraction-watch-csv",
            }
            for value in (row.get("OriginalPaperDOI") or "").split(";"):
                doi = normalize_doi(value)
                if doi and DOI_RE.fullmatch(doi):
                    by_doi.setdefault(doi, []).append(record)
            for value in (row.get("OriginalPaperPubMedID") or "").split(";"):
                pmid = normalize_pmid(value)
                if pmid and PMID_RE.fullmatch(pmid):
                    by_pmid.setdefault(pmid, []).append(record)
    return by_doi, by_pmid


def request_bytes(url: str, email: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"ResearchOS-Skills/{VERSION} (mailto:{email})",
            "Accept": "application/json, application/atom+xml, application/xml;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def crossref_lookup(doi: str, email: str, timeout: float) -> dict[str, Any]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    url += "?" + urllib.parse.urlencode({"mailto": email})
    message = json.loads(request_bytes(url, email, timeout))["message"]
    updates = []
    for update in message.get("update-to", []) or []:
        update_type = str(update.get("type", "")).lower()
        if update_type in {"retraction", "withdrawal", "expression-of-concern", "correction", "reinstatement"}:
            updates.append(
                {
                    "type": update_type,
                    "source": update.get("source", "crossref"),
                    "label": update.get("label"),
                    "record_id": update.get("record-id"),
                }
            )
    return {
        "status": "found",
        "canonical_doi": normalize_doi(message.get("DOI")),
        "title": (message.get("title") or [None])[0],
        "updates": updates,
    }


def arxiv_lookup(ids: list[str], email: str, timeout: float) -> dict[str, dict[str, Any]]:
    if not ids:
        return {}
    query = urllib.parse.urlencode({"id_list": ",".join(sorted(set(ids))), "max_results": len(set(ids))})
    root = ET.fromstring(request_bytes("https://export.arxiv.org/api/query?" + query, email, timeout))
    records = {}
    for entry in root.findall("atom:entry", ATOM):
        identifier = (entry.findtext("atom:id", default="", namespaces=ATOM).rsplit("/", 1)[-1])
        base, version = normalize_arxiv(identifier)
        if not base:
            continue
        records[base] = {
            "status": "found",
            "canonical_arxiv_id": base,
            "latest_returned_version": version,
            "title": " ".join(entry.findtext("atom:title", default="", namespaces=ATOM).split()),
            "doi": normalize_doi(entry.findtext("arxiv:doi", default="", namespaces=ATOM)),
            "updated": entry.findtext("atom:updated", default=None, namespaces=ATOM),
        }
    return records


def pubmed_lookup(ids: list[str], email: str, timeout: float) -> dict[str, dict[str, Any]]:
    if not ids:
        return {}
    query = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "id": ",".join(sorted(set(ids))),
            "retmode": "json",
            "tool": "researchos_skills",
            "email": email,
        }
    )
    payload = json.loads(
        request_bytes("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + query, email, timeout)
    )
    result = payload.get("result", {})
    records = {}
    for pmid in result.get("uids", []):
        item = result.get(pmid, {})
        records[pmid] = {
            "status": "found",
            "title": item.get("title"),
            "doi": normalize_doi(next((article_id.get("value") for article_id in item.get("articleids", []) if article_id.get("idtype") == "doi"), None)),
            "publication_types": item.get("pubtype", []),
        }
    return records


def alert_severity(nature: str) -> str:
    normalized = nature.casefold()
    if "retract" in normalized or "withdraw" in normalized:
        return "critical"
    if "concern" in normalized:
        return "warning"
    return "notice"


def redacted_command(argv: list[str]) -> str:
    redacted = list(argv)
    for index, token in enumerate(redacted[:-1]):
        if token == "--email":
            redacted[index + 1] = "<redacted>"
    return " ".join(["audit_bibliography.py", *redacted])


def run_online(entries: list[dict[str, Any]], audits: list[dict[str, Any]], email: str, timeout: float, warnings: list[str]) -> list[dict[str, Any]]:
    alerts = []
    arxiv_records: dict[str, dict[str, Any]] = {}
    pubmed_records: dict[str, dict[str, Any]] = {}
    valid_arxiv = [entry["arxiv_id"] for entry, audit in zip(entries, audits) if entry.get("arxiv_id") and audit["arxiv"]["syntax_valid"]]
    valid_pmids = [entry["pmid"] for entry, audit in zip(entries, audits) if entry.get("pmid") and audit["pmid"]["syntax_valid"]]
    try:
        arxiv_records = arxiv_lookup(valid_arxiv, email, timeout)
    except (OSError, ValueError, ET.ParseError) as error:
        warnings.append(f"arXiv verification unavailable: {error}")
    try:
        pubmed_records = pubmed_lookup(valid_pmids, email, timeout)
    except (OSError, ValueError) as error:
        warnings.append(f"PubMed verification unavailable: {error}")

    for index, (entry, audit) in enumerate(zip(entries, audits)):
        audit["online"] = {}
        doi = entry.get("doi")
        if doi and audit["doi"]["syntax_valid"]:
            try:
                record = crossref_lookup(doi, email, timeout)
            except urllib.error.HTTPError as error:
                record = {"status": "not-found" if error.code == 404 else "error", "http_status": error.code}
            except (OSError, ValueError, KeyError) as error:
                record = {"status": "error", "message": str(error)}
            audit["online"]["crossref"] = record
            for update in record.get("updates", []):
                alerts.append(
                    {
                        "entry": index,
                        "severity": alert_severity(update["type"]),
                        "nature": update["type"],
                        "source": update.get("source", "crossref"),
                        "record_id": update.get("record_id"),
                    }
                )
        arxiv = entry.get("arxiv_id")
        if arxiv and audit["arxiv"]["syntax_valid"]:
            audit["online"]["arxiv"] = arxiv_records.get(arxiv, {"status": "not-found"})
        pmid = entry.get("pmid")
        if pmid and audit["pmid"]["syntax_valid"]:
            record = pubmed_records.get(pmid, {"status": "not-found"})
            audit["online"]["pubmed"] = record
            publication_types = " ".join(map(str, record.get("publication_types", []))).casefold()
            if "retracted publication" in publication_types:
                alerts.append(
                    {"entry": index, "severity": "critical", "nature": "retracted-publication", "source": "pubmed"}
                )
    return alerts


def audit(args: argparse.Namespace) -> dict[str, Any]:
    input_path = Path(args.input)
    entries, warnings = load_entries(input_path)
    audits = [syntax_audit(entry) for entry in entries]
    alerts = []

    if args.retraction_index:
        by_doi, by_pmid = load_retraction_index(Path(args.retraction_index))
        for index, entry in enumerate(entries):
            matches = [*by_doi.get(entry.get("doi"), []), *by_pmid.get(entry.get("pmid"), [])]
            seen = set()
            for match in matches:
                key = (match.get("record_id"), match.get("nature"))
                if key in seen:
                    continue
                seen.add(key)
                alerts.append(
                    {
                        "entry": index,
                        "severity": alert_severity(match["nature"]),
                        **match,
                    }
                )
    if args.online:
        alerts.extend(run_online(entries, audits, args.email, args.timeout, warnings))

    invalid_count = 0
    for index, audit_item in enumerate(audits):
        for identifier, detail in audit_item.items():
            if identifier == "online":
                continue
            if detail["value"] is not None and not detail["syntax_valid"]:
                invalid_count += 1
                warnings.append(f"entry {index}: invalid {identifier} syntax: {detail['value']}")

    sources = [
        {
            "kind": "file",
            "locator": str(input_path.resolve()),
            "checksum": "sha256:" + hashlib.sha256(input_path.read_bytes()).hexdigest(),
        }
    ]
    if args.retraction_index:
        index_path = Path(args.retraction_index)
        sources.append(
            {
                "kind": "file",
                "locator": str(index_path.resolve()),
                "checksum": "sha256:" + hashlib.sha256(index_path.read_bytes()).hexdigest(),
                "note": "Crossref Retraction Watch-compatible CSV supplied by user",
            }
        )
    clusters = build_clusters(entries, args.title_threshold)
    return {
        "schema_version": "1.0.0",
        "artifact_type": "bibliography-audit",
        "entries": [
            {"entry": index, "metadata": entry, "identifier_audit": audits[index]}
            for index, entry in enumerate(entries)
        ],
        "clusters": clusters,
        "integrity_alerts": alerts,
        "summary": {
            "entry_count": len(entries),
            "invalid_identifier_count": invalid_count,
            "cluster_count": len(clusters),
            "integrity_alert_count": len(alerts),
            "online_checked": args.online,
        },
        "warnings": warnings,
        "provenance": {
            "created_by": "literature-reader/scripts/audit_bibliography.py",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "command": redacted_command(sys.argv[1:]),
            "seed": None,
            "sources": sources,
            "warnings": warnings,
        },
    }


def validate_args(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    if not input_path.is_file():
        raise ValueError(f"input not found: {input_path}")
    if args.online and not args.email:
        raise ValueError("--online requires --email for responsible API identification")
    if args.timeout <= 0 or args.timeout > 120:
        raise ValueError("--timeout must be greater than 0 and at most 120 seconds")
    if not 0.5 <= args.title_threshold <= 1:
        raise ValueError("--title-threshold must be between 0.5 and 1")
    protected = [input_path]
    if args.retraction_index:
        index_path = Path(args.retraction_index)
        if not index_path.is_file():
            raise ValueError(f"retraction index not found: {index_path}")
        protected.append(index_path)
    if args.out:
        output = Path(args.out)
        if any(output.resolve() == path.resolve() for path in protected):
            raise ValueError("--out must not replace an input or retraction-index file")
        if output.exists() and not args.force:
            raise ValueError(f"output exists: {output}; use --force to replace it")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validate_args(args)
        result = audit(args)
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(payload, end="")
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"written: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
