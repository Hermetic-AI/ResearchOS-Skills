#!/usr/bin/env python3
"""Generate likely defense questions, simulate Q&A, and audit a defense brief.

Reads a ``thesis-defense-brief`` and produces three things:

1. **Likely examiner questions** derived from the declared research question,
   contributions, limitations, and methods. Each question carries a difficulty
   level (foundational / methodological / critical) and the evidence a prepared
   answer should cite. This is a preparation aid, not a prediction of the real
   examination.
2. **Timing audit**: given a slide count and a target duration, it flags decks
   that are too dense or too sparse and estimates per-slide minutes.
3. **Contribution-evidence coverage**: every declared contribution should link
   to at least one evidence entry; gaps are reported as findings.

The script writes a JSON defense-QA report to ``--out`` and prints it to stdout.

Dependencies: none (Python 3.8+ standard library only).

CLI usage:
    python defense_qa.py --brief defense-brief.json --slides 20 --minutes 30 \\
        --out defense-qa.json

    # Restrict generated questions to a maximum difficulty:
    python defense_qa.py --brief defense-brief.json --slides 15 --minutes 20 \\
        --max-difficulty methodological --out defense-qa.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

# Difficulty tiers, ordered least to most demanding.
DIFFICULTY_ORDER = ["foundational", "methodological", "critical"]
DIFFICULTY_WEIGHT = {name: i for i, name in enumerate(DIFFICULTY_ORDER)}

# Minutes-per-slide heuristics for a spoken defense.
MIN_PER_SLIDE_FLOOR = 0.75   # faster than this and the deck feels rushed
MIN_PER_SLIDE_CEIL = 3.0     # slower than this and the talk drags


def _text(item):
    """Extract a human-readable label from a brief entry of varied shape."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return (item.get("title") or item.get("text") or item.get("id")
                or item.get("contribution") or json.dumps(item, ensure_ascii=False))
    return str(item)


def _evidence_labels(brief):
    """Return the set of evidence location strings declared in the brief."""
    labels = []
    for entry in brief.get("evidence_ledger") or []:
        if isinstance(entry, str):
            labels.append(entry)
        elif isinstance(entry, dict):
            loc = entry.get("location") or entry.get("source") or entry.get("chapter")
            if loc:
                labels.append(str(loc))
    return labels


def generate_questions(brief, max_difficulty):
    """Build likely examiner questions from brief content, capped by difficulty."""
    cap = DIFFICULTY_WEIGHT.get(max_difficulty, DIFFICULTY_WEIGHT["critical"])
    questions = []
    rq = brief.get("research_question")
    if rq:
        questions.append({
            "difficulty": "foundational",
            "topic": "research question",
            "question": f"Why was the research question '{rq}' framed this way rather than an alternative formulation?",
            "expected_evidence": "motivation, scope boundaries, and rejected alternatives",
        })
        questions.append({
            "difficulty": "methodological",
            "topic": "research question",
            "question": f"What would change in the methodology if the research question were narrowed or broadened?",
            "expected_evidence": "design rationale and sensitivity of results to the question scope",
        })

    for item in brief.get("contributions") or []:
        label = _text(item)
        if not label:
            continue
        questions.append({
            "difficulty": "foundational",
            "topic": "contribution",
            "question": f"State the core claim behind '{label}' and the result that supports it.",
            "expected_evidence": "the primary result, its effect size, and its location",
        })
        questions.append({
            "difficulty": "methodological",
            "topic": "contribution",
            "question": f"Which assumptions does '{label}' depend on, and how were they checked?",
            "expected_evidence": "assumption list, diagnostics, and robustness checks",
        })
        questions.append({
            "difficulty": "critical",
            "topic": "contribution",
            "question": f"What is the strongest alternative explanation for the result behind '{label}'?",
            "expected_evidence": "threats to validity and the analyses that rule them out",
        })

    for item in brief.get("limitations") or []:
        label = _text(item)
        if not label:
            continue
        questions.append({
            "difficulty": "methodological",
            "topic": "limitation",
            "question": f"How does '{label}' limit the generalizability of the findings?",
            "expected_evidence": "scope conditions and affected claims",
        })
        questions.append({
            "difficulty": "critical",
            "topic": "limitation",
            "question": f"If you could redo the work, how would you mitigate '{label}'?",
            "expected_evidence": "concrete follow-up design or analysis",
        })

    return [q for q in questions if DIFFICULTY_WEIGHT[q["difficulty"]] <= cap]


def simulate_qa(questions, brief):
    """Attach a prepared-answer skeleton to each question (no real answers).

    The skeleton records the question's difficulty, the kind of evidence a
    strong answer should cite, and a placeholder response the candidate must
    fill with verified thesis content. It never fabricates an answer.
    """
    evidence = _evidence_labels(brief)
    simulated = []
    for q in questions:
        simulated.append({
            "difficulty": q["difficulty"],
            "topic": q["topic"],
            "question": q["question"],
            "expected_evidence": q["expected_evidence"],
            "candidate_prepared_response": None,
            "suggested_evidence_locations": evidence[:3],
            "status": "open",
        })
    return simulated


def audit_timing(slides, minutes):
    """Check slide density against a target duration; return findings + metrics."""
    findings = []
    if not slides or slides < 1:
        findings.append({"check": "timing", "issue": "slide count must be >= 1"})
        return findings, {"slides": slides, "minutes": minutes, "minutes_per_slide": None}
    if minutes is None or minutes <= 0:
        findings.append({"check": "timing", "issue": "minutes must be > 0"})
        return findings, {"slides": slides, "minutes": minutes, "minutes_per_slide": None}

    mps = minutes / slides
    metrics = {"slides": slides, "minutes": minutes,
               "minutes_per_slide": round(mps, 2)}
    if mps < MIN_PER_SLIDE_FLOOR:
        findings.append({
            "check": "timing", "issue": "deck feels rushed",
            "detail": f"{mps:.2f} min/slide is below the {MIN_PER_SLIDE_FLOOR} floor",
        })
    elif mps > MIN_PER_SLIDE_CEIL:
        findings.append({
            "check": "timing", "issue": "deck may drag",
            "detail": f"{mps:.2f} min/slide exceeds the {MIN_PER_SLIDE_CEIL} ceiling",
        })
    return findings, metrics


def audit_coverage(brief):
    """Report contributions that lack a linked evidence entry."""
    findings = []
    evidence = _evidence_labels(brief)
    for item in brief.get("contributions") or []:
        label = _text(item)
        if not label:
            continue
        linked = isinstance(item, dict) and (
            item.get("evidence") or item.get("location") or item.get("source"))
        if not linked and not evidence:
            findings.append({
                "check": "coverage", "topic": "contribution",
                "contribution": label,
                "issue": "no evidence linked to this contribution and no evidence_ledger entries",
            })
        elif not linked:
            findings.append({
                "check": "coverage", "topic": "contribution",
                "contribution": label,
                "issue": "contribution has no direct evidence link; attach a location",
            })
    return findings


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--brief", required=True, help="path to a thesis-defense-brief JSON file")
    p.add_argument("--slides", type=int, default=0, help="number of defense slides")
    p.add_argument("--minutes", type=int, default=0, help="target defense duration in minutes")
    p.add_argument("--max-difficulty", choices=DIFFICULTY_ORDER, default="critical",
                   help="cap on question difficulty (default critical = all)")
    p.add_argument("--out", required=True, help="output defense-QA report")
    p.add_argument("--force", action="store_true", help="replace an existing --out file")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    a = p.parse_args(argv)

    try:
        src = Path(a.brief).resolve(strict=True)
        out = Path(a.out).resolve()
        if out == src:
            raise ValueError("--out must differ from --brief")
        if out.exists() and not a.force:
            raise ValueError("output exists; use --force only for a revised QA report")

        brief = json.loads(src.read_text(encoding="utf-8-sig"))
        if brief.get("artifact_type") != "thesis-defense-brief":
            raise ValueError("--brief must be a thesis-defense-brief artifact")

        questions = generate_questions(brief, a.max_difficulty)
        simulated = simulate_qa(questions, brief)
        timing_findings, timing_metrics = audit_timing(a.slides, a.minutes)
        coverage_findings = audit_coverage(brief)
        all_findings = timing_findings + coverage_findings

        report = {
            "schema_version": "1.0.0",
            "artifact_type": "thesis-defense-qa",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "brief": str(src),
            "max_difficulty": a.max_difficulty,
            "timing": timing_metrics,
            "questions": simulated,
            "question_count": len(simulated),
            "findings": all_findings,
            "ready_for_human_review": not all_findings,
            "warnings": [
                "Preparation aid only: generated questions are not predictions of the "
                "real examination, and candidate_prepared_response is a placeholder the "
                "candidate must fill with verified thesis content. Never present a "
                "fabricated answer as one's own.",
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
