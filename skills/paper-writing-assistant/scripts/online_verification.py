#!/usr/bin/env python3
"""Online DOI / journal metadata verification via the Crossref API.

For each DOI supplied on the command line (or parsed from a ``.bib`` file via
``--bibtex``), queries ``https://api.crossref.org/works/{doi}`` and compares
the returned metadata (title, journal/container, year, pages, authors)
against the local record. Reports match / mismatch per field, confidence, and
warnings.

Honesty warnings (always surfaced in the report):
  - Requires network access; results depend on Crossref data quality.
  - A Crossref hit does NOT prove the DOI is the right work for your claim.
  - Does not replace human verification.

Zero dependencies (Python stdlib only: ``urllib.request``). Deterministic given
a fixed inputs + live Crossref response. UTF-8 reconfigure for Windows consoles.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


VERSION = "0.1.0"
CROSSREF_WORKS = "https://api.crossref.org/works/"
DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
TOKEN_RE = re.compile(r"[^\w\s-]", re.UNICODE)


# --------------------------------------------------------------- DOI helpers

def normalize_doi(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi\s*:\s*)", "", text, flags=re.I)
    text = text.rstrip(".,;)").strip().lower()
    return text or None


def doi_syntax_valid(doi: str | None) -> bool:
    return doi is None or bool(DOI_RE.fullmatch(doi))


# --------------------------------------------------------------- BibTeX parse

def parse_bib_dois(path: Path) -> list[dict[str, Any]]:
    """Lightweight BibTeX parser: returns one record per entry with the key,
    type, and raw field values (author, title, year, journal, booktitle,
    pages, doi). Does not attempt full BibTeX tokenization — sufficient for
    DOI/journal verification."""
    text = path.read_text(encoding="utf-8-sig")
    records: list[dict[str, Any]] = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text, re.I):
        kind = match.group(1).lower()
        key = match.group(2)
        start = match.end()
        depth, end = 1, start
        while end < len(text) and depth:
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
            end += 1
        body = text[start:end - 1]
        fields: dict[str, str] = {}
        for fmatch in re.finditer(
            r"(\w+)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|\"((?:[^\"\\]|\\.)*)\"|(\w+))",
            body, re.S,
        ):
            name = fmatch.group(1).lower()
            value = fmatch.group(2) if fmatch.group(2) is not None else (
                fmatch.group(3) if fmatch.group(3) is not None else fmatch.group(4))
            # collapse whitespace
            value = re.sub(r"\s+", " ", value).strip()
            fields[name] = value
        doi = normalize_doi(fields.get("doi"))
        records.append({
            "key": key,
            "type": kind,
            "title": fields.get("title"),
            "author": fields.get("author"),
            "year": fields.get("year"),
            "journal": fields.get("journal") or fields.get("booktitle"),
            "pages": fields.get("pages"),
            "doi": doi,
            "doi_syntax_valid": doi_syntax_valid(doi),
        })
    return records


# --------------------------------------------------------------- Crossref

def fetch_crossref(doi: str, timeout: float, retries: int,
                   user_agent: str) -> dict[str, Any]:
    """Query Crossref for a single DOI. Returns a dict with at least a
    ``status`` key: ``"found"``, ``"not-found"``, ``"error"``, or
    ``"unavailable"`` (network). On ``"found"``, includes parsed metadata."""
    url = CROSSREF_WORKS + urllib.parse.quote(doi, safe="")
    last_error: str | None = None
    for attempt in range(max(1, retries)):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": user_agent, "Accept": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            message = payload.get("message", {})
            return _parse_crossref_message(message)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return {"status": "not-found", "http_status": 404}
            last_error = f"HTTP {error.code}"
        except urllib.error.URLError as error:
            # Network unavailable (no connection, DNS failure, ...) -> do not
            # keep retrying; report unavailable.
            return {"status": "unavailable", "message": str(error.reason)}
        except (OSError, ValueError, json.JSONDecodeError) as error:
            last_error = str(error)
    return {"status": "error", "message": last_error or "unknown error"}


def _parse_crossref_message(message: dict[str, Any]) -> dict[str, Any]:
    title_list = message.get("title") or []
    subtitle_list = message.get("subtitle") or []
    title = " ".join(title_list).strip()
    if subtitle_list:
        title = (title + ": " + " ".join(subtitle_list)).strip(": ")
    container_list = message.get("container-title") or []
    journal = " ".join(container_list).strip() if container_list else None
    short_container = message.get("short-container-title") or []
    if journal and short_container:
        short_first = " ".join(short_container).strip()
        if short_first and short_first.lower() != journal.lower():
            journal = f"{journal} (short: {short_first})"
    elif short_container and not journal:
        journal = " ".join(short_container).strip()
    year: int | None = None
    for key in ("published-print", "published-online", "published",
                "issued", "created"):
        part = message.get(key, {}).get("date-parts")
        if part and part[0] and part[0][0] is not None:
            try:
                year = int(part[0][0])
                break
            except (TypeError, ValueError):
                continue
    pages = message.get("page")
    authors_raw = message.get("author") or []
    authors = []
    for a in authors_raw:
        given = a.get("given") or ""
        family = a.get("family") or ""
        name = f"{given} {family}".strip()
        if name:
            authors.append(name)
    return {
        "status": "found",
        "doi": message.get("DOI"),
        "title": title or None,
        "journal": journal,
        "year": year,
        "pages": pages,
        "authors": authors,
        "type": message.get("type"),
    }


# --------------------------------------------------------------- comparison

def _normalize_text(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text


def _token_key(value: Any) -> set[str]:
    return {t for t in TOKEN_RE.sub(" ", _normalize_text(value).casefold()).split() if t}


def compare_fields(local: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
    """Compare a local BibTeX record against a Crossref record. Returns per-field
    match/mismatch with a coarse confidence level."""
    fields: dict[str, Any] = {}

    # title: token-set overlap (robust to casing/punctuation differences)
    local_title = _normalize_text(local.get("title"))
    remote_title = _normalize_text(remote.get("title"))
    if not local_title or not remote_title:
        fields["title"] = {"status": "missing",
                           "local": local_title or None,
                           "remote": remote_title or None}
    else:
        local_tokens = _token_key(local_title)
        remote_tokens = _token_key(remote_title)
        if local_tokens and remote_tokens:
            overlap = len(local_tokens & remote_tokens) / max(
                len(local_tokens), len(remote_tokens))
        else:
            overlap = 0.0
        fields["title"] = {
            "status": "match" if overlap >= 0.8 else "mismatch",
            "confidence": round(overlap, 3),
            "local": local_title,
            "remote": remote_title,
        }

    # year: exact integer match
    local_year = local.get("year")
    remote_year = remote.get("year")
    try:
        local_year_int = int(local_year) if local_year is not None else None
    except (TypeError, ValueError):
        local_year_int = None
    if local_year_int is None or remote_year is None:
        fields["year"] = {"status": "missing", "local": local_year,
                           "remote": remote_year}
    else:
        fields["year"] = {
            "status": "match" if local_year_int == remote_year else "mismatch",
            "local": local_year_int, "remote": remote_year,
        }

    # journal: token overlap (container-title is often abbreviated). The
    # remote may also carry supplemental info (e.g. "Journal (short: J.)"),
    # so accept a match when the local name is fully contained in the remote
    # token set OR token overlap is high enough.
    local_j = _normalize_text(local.get("journal"))
    remote_j = _normalize_text(remote.get("journal"))
    if not local_j or not remote_j:
        fields["journal"] = {"status": "missing", "local": local_j or None,
                             "remote": remote_j or None}
    else:
        lt, rt = _token_key(local_j), _token_key(remote_j)
        if lt and rt:
            overlap = len(lt & rt) / max(len(lt), len(rt))
            contained = lt <= rt  # every local token appears in remote
        else:
            overlap = 0.0
            contained = False
        matched = contained or overlap >= 0.7
        fields["journal"] = {
            "status": "match" if matched else "mismatch",
            "confidence": round(overlap, 3),
            "local": local_j, "remote": remote_j,
        }

    # pages: normalize dashes and whitespace, compare start page primarily
    def _page_start(value: str | None) -> str | None:
        if not value:
            return None
        cleaned = re.sub(r"\s+", "", str(value))
        cleaned = re.sub(r"[–—−]", "-", cleaned)
        return cleaned or None
    local_pages = _page_start(local.get("pages"))
    remote_pages = _page_start(remote.get("pages"))
    if not local_pages or not remote_pages:
        fields["pages"] = {"status": "missing", "local": local_pages,
                            "remote": remote_pages}
    else:
        same = local_pages == remote_pages
        if not same and "-" in local_pages and "-" in remote_pages:
            # compare only the start page when formatting differs
            same = local_pages.split("-")[0] == remote_pages.split("-")[0]
        fields["pages"] = {
            "status": "match" if same else "mismatch",
            "local": local_pages, "remote": remote_pages,
        }

    # authors: compare first-author family name (most discriminative)
    local_first = _first_author_family(local.get("author"))
    remote_first = _first_author_family(remote.get("authors"))
    if not local_first or not remote_first:
        fields["authors"] = {"status": "missing", "local": local_first,
                             "remote": remote_first}
    else:
        fields["authors"] = {
            "status": "match" if local_first == remote_first else "mismatch",
            "local": local_first, "remote": remote_first,
        }

    statuses = [f["status"] for f in fields.values()]
    mismatches = sum(1 for s in statuses if s == "mismatch")
    missing = sum(1 for s in statuses if s == "missing")
    if mismatches:
        overall = "mismatch"
    elif missing == len(statuses):
        overall = "missing"
    elif missing:
        overall = "partial"
    else:
        overall = "match"
    return {"fields": fields, "overall": overall,
            "mismatch_count": mismatches, "missing_count": missing}


def _first_author_family(value: Any) -> str | None:
    if not value:
        return None
    if isinstance(value, list):
        name = value[0] if value else ""
    else:
        # BibTeX "and"-separated list
        name = re.split(r"\s+and\s+", str(value), maxsplit=1, flags=re.I)[0]
    name = re.sub(r"[{}]", "", name).strip()
    if not name:
        return None
    if "," in name:
        family = name.split(",", 1)[0].strip()
    else:
        parts = name.split()
        family = parts[-1] if parts else name
    return re.sub(r"[^\w\s'-]", "", family).strip().casefold() or None


# --------------------------------------------------------------- main logic

def verify_doi(doi: str, timeout: float, retries: int,
               user_agent: str) -> dict[str, Any]:
    if not doi_syntax_valid(doi):
        return {"doi": doi, "doi_syntax_valid": False,
                "status": "invalid-syntax",
                "error": "DOI does not match the 10.xxxx/... syntax"}
    record = fetch_crossref(doi, timeout, retries, user_agent)
    return {"doi": doi, "doi_syntax_valid": True, "status": record["status"],
            "crossref": record}


def verify_bib(path: Path, timeout: float, retries: int,
               user_agent: str) -> dict[str, Any]:
    records = parse_bib_dois(path)
    results = []
    for rec in records:
        doi = rec.get("doi")
        if not doi:
            results.append({
                "key": rec["key"], "doi": None, "doi_syntax_valid": False,
                "status": "no-doi", "error": "no DOI in local record",
            })
            continue
        if not rec.get("doi_syntax_valid"):
            results.append({
                "key": rec["key"], "doi": doi, "doi_syntax_valid": False,
                "status": "invalid-syntax",
                "error": "DOI does not match the 10.xxxx/... syntax",
            })
            continue
        remote = fetch_crossref(doi, timeout, retries, user_agent)
        entry: dict[str, Any] = {
            "key": rec["key"], "doi": doi, "doi_syntax_valid": True,
            "status": remote["status"], "crossref": remote,
        }
        if remote.get("status") == "found":
            entry["comparison"] = compare_fields(rec, remote)
        results.append(entry)
    return {"source": str(path), "records": results}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--doi", action="append", default=[],
                   help="verify a single DOI (repeatable)")
    p.add_argument("--bibtex", type=Path,
                   help="verify every DOI found in a .bib file")
    p.add_argument("--out", type=Path,
                   help="write the JSON report here (default: stdout only)")
    p.add_argument("--force", action="store_true",
                   help="replace an existing --out file")
    p.add_argument("--timeout", type=float, default=15.0,
                   help="per-request HTTP timeout in seconds (default: 15)")
    p.add_argument("--retries", type=int, default=1,
                   help="retry count per DOI on transient errors (default: 1)")
    args = p.parse_args(argv)
    if not args.doi and not args.bibtex:
        p.error("at least one of --doi or --bibtex is required")
    if args.timeout <= 0 or args.timeout > 120:
        p.error("--timeout must be greater than 0 and at most 120 seconds")
    if args.retries < 1 or args.retries > 5:
        p.error("--retries must be between 1 and 5")

    user_agent = f"ResearchOS-Skills/online-verification {VERSION} (mailto:researchos-skills)"
    results: list[dict[str, Any]] = []
    network_unavailable = False
    for doi in args.doi:
        result = verify_doi(doi, args.timeout, args.retries, user_agent)
        if result.get("crossref", {}).get("status") == "unavailable":
            network_unavailable = True
        results.append(result)

    bib_report: dict[str, Any] | None = None
    if args.bibtex:
        if not args.bibtex.is_file():
            p.error(f"--bibtex file not found: {args.bibtex}")
        bib_report = verify_bib(args.bibtex, args.timeout, args.retries, user_agent)
        for rec in bib_report["records"]:
            if rec.get("crossref", {}).get("status") == "unavailable":
                network_unavailable = True

    warnings = [
        "Online verification depends on live Crossref data quality and availability.",
        "A Crossref hit does not prove the DOI is the correct work for your claim.",
        "This does not replace human verification of author, year, venue, and pages.",
    ]
    if network_unavailable:
        warnings.append(
            "Network unavailable during verification: some results are "
            "'unavailable'. Re-run with network access for those DOIs.")

    artifact = {
        "schema_version": "1.0.0",
        "artifact_type": "online-doi-verification",
        "tool_version": VERSION,
        "results": results,
        "bib_report": bib_report,
        "network_unavailable": network_unavailable,
        "warnings": warnings,
    }
    payload = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    sys.stdout.write(payload)
    if args.out:
        out = args.out
        if out == args.bibtex:
            print("error: --out must not replace the --bibtex input",
                  file=sys.stderr)
            return 2
        if out.exists() and not args.force:
            print(f"error: output exists: {out}; use --force to replace it",
                  file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(f"written: {out}", file=sys.stderr)
    # nonzero exit if any DOI errored / was unavailable
    any_problem = network_unavailable or any(
        r.get("status") in {"error", "invalid-syntax", "unavailable"}
        for r in results)
    if bib_report:
        any_problem = any_problem or any(
            r.get("status") in {"error", "invalid-syntax", "unavailable"}
            for r in bib_report["records"])
    return 2 if any_problem else 0


if __name__ == "__main__":
    raise SystemExit(main())
