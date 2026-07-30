#!/usr/bin/env python3
"""Audit claim-level evidence anchors in a ResearchOS paper note."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("note", help="paper-note JSON")
    parser.add_argument(
        "--extraction",
        help="optional pdf-extraction JSON used for page/quote matching",
    )
    parser.add_argument("--out", help="write evidence-audit JSON here")
    parser.add_argument("--force", action="store_true", help="replace an existing --out file")
    parser.add_argument(
        "--strict-ocr",
        action="store_true",
        help="treat direct claims backed only by unverified OCR as errors",
    )
    return parser


def source(path: Path, note: str | None = None) -> dict[str, Any]:
    descriptor = {
        "kind": "file",
        "locator": str(path.resolve()),
        "checksum": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    if note:
        descriptor["note"] = note
    return descriptor


def normalized_text(value: Any) -> str:
    text = str(value or "").replace("\u00ad", "")
    return " ".join(text.split()).casefold()


def add_finding(
    findings: list[dict[str, Any]],
    severity: str,
    code: str,
    claim_id: str | None,
    message: str,
) -> None:
    findings.append(
        {"severity": severity, "code": code, "claim_id": claim_id, "message": message}
    )


def load_json(path: Path, expected_type: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    if payload.get("artifact_type") != expected_type:
        raise ValueError(f"{path} must have artifact_type {expected_type!r}")
    return payload


def audit_note(
    note: dict[str, Any],
    extraction: dict[str, Any] | None,
    strict_ocr: bool,
) -> tuple[list[dict[str, Any]], int, int]:
    findings: list[dict[str, Any]] = []
    claims = note.get("claims")
    if not isinstance(claims, list) or not claims:
        add_finding(findings, "error", "claims-missing", None, "paper-note must contain at least one claim")
        return findings, 0, 0

    pages = {}
    accepted_sources = set()
    if extraction:
        for page in extraction.get("pages", []):
            number = page.get("page_number")
            if not isinstance(number, int):
                add_finding(findings, "error", "invalid-extraction-page", None, "extraction page_number must be an integer")
            elif number in pages:
                add_finding(findings, "error", "duplicate-extraction-page", None, f"duplicate extraction page {number}")
            else:
                pages[number] = page
        locator = str((extraction.get("input") or {}).get("locator", ""))
        if locator:
            accepted_sources.update((locator, Path(locator).name))

    seen_ids = set()
    anchored_claims = 0
    exact_matches = 0
    quote_usage: dict[str, list[str]] = {}
    for position, claim in enumerate(claims):
        if not isinstance(claim, dict):
            add_finding(findings, "error", "invalid-claim", None, f"claim {position} must be an object")
            continue
        claim_id = str(claim.get("id") or f"claim-at-{position}")
        if claim_id in seen_ids:
            add_finding(findings, "error", "duplicate-claim-id", claim_id, "claim id is not unique")
        seen_ids.add(claim_id)
        evidence_list = claim.get("evidence")
        if not isinstance(evidence_list, list) or not evidence_list:
            add_finding(findings, "error", "evidence-missing", claim_id, "claim has no evidence anchor")
            continue
        anchored_claims += 1
        verified_for_direct = False
        for evidence_index, evidence in enumerate(evidence_list):
            if not isinstance(evidence, dict):
                add_finding(findings, "error", "invalid-evidence", claim_id, f"evidence {evidence_index} must be an object")
                continue
            quote = str(evidence.get("quote") or "").strip()
            if not quote:
                add_finding(findings, "error", "quote-missing", claim_id, "evidence quote is empty")
                continue
            if len(quote) > 500:
                add_finding(findings, "error", "quote-too-long", claim_id, "evidence quote exceeds 500 characters")
            quote_usage.setdefault(normalized_text(quote), []).append(claim_id)
            if evidence.get("page") is None and not evidence.get("section"):
                add_finding(findings, "error", "location-missing", claim_id, "evidence needs a PDF page or section")
            method = evidence.get("extraction_method")
            verification = evidence.get("verification")
            if method not in {"native-text", "ocr", "human-transcription", "visual"}:
                add_finding(findings, "error", "method-missing", claim_id, "evidence extraction_method is missing or invalid")
            if verification not in {"exact-match", "human-verified", "unverified"}:
                add_finding(findings, "error", "verification-missing", claim_id, "evidence verification is missing or invalid")
            if verification in {"exact-match", "human-verified"}:
                verified_for_direct = True
            if method == "ocr" and verification == "unverified":
                severity = "error" if strict_ocr and claim.get("support_level") == "direct" else "warning"
                add_finding(findings, severity, "unverified-ocr", claim_id, "OCR quote has not been checked against the page image")

            if extraction:
                evidence_source = str(evidence.get("source") or "")
                if evidence_source and accepted_sources and evidence_source not in accepted_sources and Path(evidence_source).name not in accepted_sources:
                    add_finding(findings, "warning", "source-mismatch", claim_id, "evidence source does not match the extraction input")
                page_number = evidence.get("page")
                if not isinstance(page_number, int):
                    add_finding(findings, "warning", "page-not-machine-verifiable", claim_id, "non-integer or missing PDF page cannot be matched automatically")
                    continue
                page = pages.get(page_number)
                if not page:
                    add_finding(findings, "error", "page-not-found", claim_id, f"PDF page {page_number} is absent from the extraction")
                    continue
                page_method = page.get("extraction_method")
                if method in {"native-text", "ocr"} and method != page_method:
                    add_finding(findings, "error", "method-mismatch", claim_id, f"anchor says {method}, extraction page says {page_method}")
                if normalized_text(quote) in normalized_text(page.get("text")):
                    exact_matches += 1
                    if verification == "unverified" and method == "native-text":
                        add_finding(findings, "notice", "exact-match-found", claim_id, "quote exactly matches normalized native page text; update verification after review")
                else:
                    add_finding(findings, "error", "quote-not-found", claim_id, f"quote not found on extracted PDF page {page_number}")
            elif verification == "exact-match":
                add_finding(findings, "warning", "exact-match-not-rechecked", claim_id, "no pdf-extraction artifact was supplied to recheck the exact match")

        if claim.get("support_level") == "direct" and not verified_for_direct:
            severity = "error" if strict_ocr else "warning"
            add_finding(findings, severity, "direct-claim-unverified", claim_id, "direct claim has no exact-match or human-verified anchor")

    for quote, claim_ids in quote_usage.items():
        if quote and len(set(claim_ids)) > 3:
            add_finding(findings, "warning", "overused-anchor", None, f"one quote is reused across {len(set(claim_ids))} claims")
    return findings, anchored_claims, exact_matches


def build_report(
    note_path: Path,
    extraction_path: Path | None,
    note: dict[str, Any],
    extraction: dict[str, Any] | None,
    strict_ocr: bool,
) -> dict[str, Any]:
    findings, anchored, exact_matches = audit_note(note, extraction, strict_ocr)
    severities = {finding["severity"] for finding in findings}
    status = "fail" if "error" in severities else "warning" if "warning" in severities else "pass"
    warnings = [finding["message"] for finding in findings if finding["severity"] == "warning"]
    sources = [source(note_path, "paper-note under audit")]
    if extraction_path:
        sources.append(source(extraction_path, "pdf-extraction used for quote matching"))
    return {
        "schema_version": "1.0.0",
        "artifact_type": "evidence-audit",
        "note": sources[0],
        "extraction": sources[1] if len(sources) > 1 else None,
        "claim_count": len(note.get("claims") or []),
        "anchored_claim_count": anchored,
        "exact_match_count": exact_matches,
        "status": status,
        "findings": findings,
        "warnings": warnings,
        "provenance": {
            "created_by": "literature-reader/scripts/audit_claim_evidence.py",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "command": " ".join(["audit_claim_evidence.py", *sys.argv[1:]]),
            "seed": None,
            "sources": sources,
            "warnings": warnings,
        },
    }


def validate_paths(args: argparse.Namespace) -> tuple[Path, Path | None, Path | None]:
    note_path = Path(args.note)
    extraction_path = Path(args.extraction) if args.extraction else None
    output = Path(args.out) if args.out else None
    inputs = [note_path, *([extraction_path] if extraction_path else [])]
    if any(not path.is_file() for path in inputs):
        missing = next(path for path in inputs if not path.is_file())
        raise ValueError(f"input not found: {missing}")
    if output:
        if any(output.resolve() == path.resolve() for path in inputs):
            raise ValueError("--out must not replace note or extraction input")
        if output.exists() and not args.force:
            raise ValueError(f"output exists: {output}; use --force to replace it")
        if not output.parent.is_dir():
            raise ValueError("output parent directory must already exist")
    return note_path, extraction_path, output


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        note_path, extraction_path, output = validate_paths(args)
        note = load_json(note_path, "paper-note")
        extraction = load_json(extraction_path, "pdf-extraction") if extraction_path else None
        report = build_report(note_path, extraction_path, note, extraction, args.strict_ocr)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(payload, end="")
    if output:
        output.write_text(payload, encoding="utf-8")
        print(f"written: {output}", file=sys.stderr)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
