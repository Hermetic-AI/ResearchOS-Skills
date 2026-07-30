#!/usr/bin/env python3
"""Parse patent family data, compute timelines, and rank closest prior art.

Reads a ``prior-art-search-ledger`` (or a dedicated family JSON) and, for each
patent family, computes a priority/publication timeline, identifies the closest
prior art by date proximity and claims-token overlap, and emits a family-tree
visualization as indented text and, optionally, a Mermaid flowchart.

This is research support: it does not assess novelty, claim construction,
infringement, freedom-to-operate, or legal relevance, and every conclusion must
be escalated to qualified counsel.

Dependencies: none (Python 3.8+ standard library only).

Input shapes (auto-detected):
    * A ``prior-art-search-ledger`` with ``patent_records`` and ``family_links``.
    * A dedicated family file: ``{"families": [{"family_id": "...", "members": [...]}]}``.
      Each member needs at least ``pub_number`` and ``filing_date``; ``claims``
      (list of strings) and ``priority_date`` improve the analysis.

CLI usage:
    python patent_family.py --ledger prior-art-ledger.json --out family-report.json

    python patent_family.py --ledger prior-art-ledger.json --out family-report.json \\
        --mermaid-out family-tree.mmd --cutoff-date 2024-01-01
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

VERSION = "0.1.0"


def _parse_iso(value):
    """Parse a YYYY-MM-DD date, returning a ``date`` or None when absent/invalid.

    Idempotent: passes through values that are already ``date`` objects so
    ``_normalize_member`` can be applied repeatedly without losing data.
    """
    if isinstance(value, date):
        return value
    if not value or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def _to_date(entry, *keys):
    """Return the first parseable date found under ``keys`` in ``entry``."""
    for key in keys:
        parsed = _parse_iso(entry.get(key))
        if parsed:
            return parsed
    return None


def load_families(path):
    """Load and normalize family data from a ledger or a dedicated family file.

    Returns a list of families, each ``{"family_id": str, "members": [...]}``.
    Members are normalized to carry ``pub_number``, ``title``, ``jurisdiction``,
    ``filing_date`` (date), ``priority_date`` (date), ``publication_date`` (date),
    ``status``, and ``claims`` (list[str]).
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    artifact_type = raw.get("artifact_type")

    if artifact_type == "prior-art-search-ledger":
        records = raw.get("patent_records") or []
        links = raw.get("family_links") or []
        by_number = {r.get("pub_number"): r for r in records if r.get("pub_number")}
        families: dict[str, dict] = {}
        for link in links:
            fid = link.get("family_id") or link.get("family") or "unfiled"
            member_numbers = link.get("members") or link.get("pub_numbers") or []
            members = [by_number[n] for n in member_numbers if n in by_number]
            families.setdefault(fid, {"family_id": fid, "members": []})
            existing = {m.get("pub_number") for m in families[fid]["members"]}
            for member in members:
                if member.get("pub_number") not in existing:
                    families[fid]["members"].append(member)
                    existing.add(member.get("pub_number"))
        # Records not mentioned in any family_link each form a singleton family.
        for rec in records:
            if not any(rec.get("pub_number") in (l.get("members") or l.get("pub_numbers") or [])
                       for l in links):
                fid = rec.get("pub_number") or "unfiled"
                families.setdefault(fid, {"family_id": fid, "members": []})
                families[fid]["members"].append(rec)
        return list(families.values())

    families_raw = raw.get("families") if isinstance(raw, dict) else raw
    if not isinstance(families_raw, list):
        raise ValueError("input must be a prior-art-ledger or a {families:[...]} file")
    return families_raw


def _normalize_member(member):
    """Normalize a raw member dict into a consistent shape."""
    claims = member.get("claims") or []
    if isinstance(claims, str):
        claims = [claims]
    return {
        "pub_number": member.get("pub_number") or member.get("number") or "",
        "title": member.get("title") or "",
        "jurisdiction": member.get("jurisdiction") or _jurisdiction_from_number(member.get("pub_number")),
        "filing_date": _to_date(member, "filing_date", "filed"),
        "priority_date": _to_date(member, "priority_date", "priority", "earliest_priority"),
        "publication_date": _to_date(member, "publication_date", "published", "grant_date"),
        "status": member.get("status") or "",
        "claims": [str(c) for c in claims],
    }


def _jurisdiction_from_number(pub_number):
    """Best-effort two-letter jurisdiction from a publication number prefix."""
    if not pub_number or not isinstance(pub_number, str):
        return ""
    prefix = re.match(r"^([A-Z]{2})", pub_number.upper())
    return prefix.group(1) if prefix else ""


def compute_timeline(members):
    """Compute a timeline summary for a family's members (normalized inline)."""
    members = [_normalize_member(m) for m in members]
    if not members:
        return None
    filing_dates = [m["filing_date"] for m in members if m["filing_date"]]
    priority_dates = [m["priority_date"] for m in members if m["priority_date"]]
    pub_dates = [m["publication_date"] for m in members if m["publication_date"]]
    earliest_priority = min(priority_dates) if priority_dates else None
    latest_filing = max(filing_dates) if filing_dates else None
    latest_pub = max(pub_dates) if pub_dates else None
    span_days = (latest_filing - earliest_priority).days if (latest_filing and earliest_priority) else None
    return {
        "member_count": len(members),
        "jurisdictions": sorted({m["jurisdiction"] for m in members if m["jurisdiction"]}),
        "earliest_priority": earliest_priority.isoformat() if earliest_priority else None,
        "latest_filing": latest_filing.isoformat() if latest_filing else None,
        "latest_publication": latest_pub.isoformat() if latest_pub else None,
        "family_span_days": span_days,
        "statuses": sorted({m["status"] for m in members if m["status"]}),
    }


def _tokenize(text):
    """Lowercased alphanumeric tokens, for crude claims-overlap scoring."""
    return set(re.findall(r"[A-Za-z0-9]+", text.lower()))


def claims_overlap(claims_a, claims_b):
    """Jaccard similarity over claim-token sets; 0.0 when either side is empty."""
    tokens_a = set()
    tokens_b = set()
    for c in claims_a:
        tokens_a |= _tokenize(c)
    for c in claims_b:
        tokens_b |= _tokenize(c)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def rank_prior_art(families, target_claims, cutoff_date):
    """Rank every family member as candidate prior art against a target.

    Candidates must have a priority/filing date on or before ``cutoff_date``.
    They are scored by date proximity to the cutoff (closer is stronger) and by
    claims-token overlap with ``target_claims``. Returns a sorted list (best
    first) with the components of the score exposed for counsel review.
    """
    cutoff = _parse_iso(cutoff_date)
    candidates = []
    for family in families:
        for member in family.get("members") or []:
            norm = _normalize_member(member)
            anchor = norm["priority_date"] or norm["filing_date"]
            if anchor is None or (cutoff is not None and anchor > cutoff):
                continue
            proximity = None
            if cutoff is not None:
                proximity = max((cutoff - anchor).days, 0)
            overlap = claims_overlap(target_claims, norm["claims"])
            score = (proximity or 0) / 365.0 + overlap * 10.0
            candidates.append({
                "family_id": family.get("family_id"),
                "pub_number": norm["pub_number"],
                "title": norm["title"],
                "jurisdiction": norm["jurisdiction"],
                "anchor_date": anchor.isoformat(),
                "cutoff_date": cutoff.isoformat() if cutoff else None,
                "days_before_cutoff": proximity,
                "claims_overlap": round(overlap, 3),
                "score": round(score, 3),
            })
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


def render_family_tree(families):
    """Render an indented text family tree grouped by family then by date."""
    lines = []
    for family in families:
        lines.append(f"Family: {family.get('family_id')}")
        ordered = sorted(family.get("members") or [],
                          key=lambda m: _normalize_member(m)["filing_date"] or date.max)
        for member in ordered:
            norm = _normalize_member(member)
            date_str = norm["filing_date"].isoformat() if norm["filing_date"] else "?"
            lines.append(f"  - {norm['pub_number']} ({norm['jurisdiction']}) "
                         f"filed {date_str} [{norm['status'] or 'unknown'}]")
        lines.append("")
    return "\n".join(lines).rstrip("\n")


def render_mermaid(families):
    """Render a Mermaid flowchart of family members and their date order."""
    lines = ["flowchart TD"]
    nodes: dict[str, str] = {}
    for family in families:
        ordered = sorted(family.get("members") or [],
                          key=lambda m: _normalize_member(m)["filing_date"] or date.max)
        prev_id = None
        for member in ordered:
            norm = _normalize_member(member)
            node_id = re.sub(r"[^A-Za-z0-9]", "_", norm["pub_number"]) or "unknown"
            nodes.setdefault(node_id, norm["pub_number"])
            label = f"{norm['pub_number']}<br/>{norm['jurisdiction']} {norm['filing_date'] or '?'}"
            lines.append(f"    {node_id}[\"{label}\"]")
            if prev_id:
                lines.append(f"    {prev_id} --> {node_id}")
            prev_id = node_id
    if not nodes:
        lines.append("    empty[\"No family members\"]")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger", default=None, help="path to a prior-art-search-ledger JSON file")
    p.add_argument("--family-file", default=None,
                   help="path to a dedicated family JSON file (alternative to --ledger)")
    p.add_argument("--target-claims", default=None,
                   help="path to a JSON list of claim strings to score overlap against")
    p.add_argument("--cutoff-date", default=None,
                   help="YYYY-MM-DD cutoff; only members on/before it are prior-art candidates")
    p.add_argument("--mermaid-out", default=None,
                   help="optional path to write a Mermaid family-tree flowchart")
    p.add_argument("--out", required=True, help="output family-analysis report")
    p.add_argument("--force", action="store_true", help="replace an existing --out file")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    a = p.parse_args(argv)

    if not a.ledger and not a.family_file:
        print("error: supply --ledger or --family-file", file=sys.stderr)
        return 1

    try:
        src = Path(a.ledger or a.family_file).resolve(strict=True)
        out = Path(a.out).resolve()
        if out == src:
            raise ValueError("--out must differ from the input file")
        if out.exists() and not a.force:
            raise ValueError("output exists; use --force only for a revised report")

        families = load_families(src)
        for family in families:
            if not family.get("family_id"):
                family["family_id"] = "unfiled"

        target_claims = []
        if a.target_claims:
            target_claims = json.loads(Path(a.target_claims).read_text(encoding="utf-8-sig"))
            if not isinstance(target_claims, list):
                raise ValueError("--target-claims must be a JSON list of strings")

        timelines = []
        for family in families:
            timeline = compute_timeline(family["members"])
            if timeline:
                timeline["family_id"] = family["family_id"]
                timelines.append(timeline)

        ranked = rank_prior_art(families, target_claims, a.cutoff_date)
        tree_text = render_family_tree(families)

        if a.mermaid_out:
            mermaid_path = Path(a.mermaid_out).resolve()
            if mermaid_path == src:
                raise ValueError("--mermaid-out must differ from the input file")
            if mermaid_path.exists() and not a.force:
                raise ValueError("mermaid output exists; use --force to replace it")
            mermaid_path.write_text(render_mermaid(families) + "\n", encoding="utf-8")

        report = {
            "schema_version": "1.0.0",
            "artifact_type": "patent-family-analysis",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "source": str(src),
            "family_count": len(families),
            "member_count": sum(len(f["members"]) for f in families),
            "timelines": timelines,
            "prior_art_ranking": ranked,
            "closest_prior_art": ranked[0] if ranked else None,
            "family_tree": tree_text,
            "ready_for_human_review": bool(ranked),
            "warnings": [
                "Research support only: date proximity and claims-token overlap are crude "
                "signals, not a novelty, obviousness, infringement, freedom-to-operate, or "
                "patentability conclusion. Escalate every conclusion to qualified counsel.",
            ],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: force UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
