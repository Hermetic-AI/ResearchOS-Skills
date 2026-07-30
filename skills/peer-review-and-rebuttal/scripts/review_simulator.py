#!/usr/bin/env python3
"""Generate structured review templates and score reporting-guideline compliance.

Purpose:
    A zero-dependency helper for the peer-review and rebuttal phase. It (1)
    produces a structured review skeleton tailored to a target venue (journal,
    conference, preprint) with standard sections, (2) checks a manuscript
    against reporting-guideline checklists (CONSORT for RCTs, STROBE for
    observational studies, PRISMA for systematic reviews) and produces a
    compliance score with item-level findings, and (3) emits a review template
    combining the venue structure and checklist results. It does not fabricate
    reviewer comments or replace actual expert review.

Dependencies:
    None (Python 3.8+ standard library only).

CLI usage:
    python3 review_simulator.py --mode template --venue journal --out review.json
    python3 review_simulator.py --mode checklist --guideline consort --manuscript manuscript.md \\
        --sections "title,abstract,methods,results" --out checklist.json
    python3 review_simulator.py --mode full --venue conference --guideline strobe \\
        --manuscript manuscript.md --sections "title,methods" --out review.json

    Common options: --force  --version

Venue choices: journal | conference | preprint | grant
Guideline choices: consort | strobe | prisma

Manuscript input: a Markdown/plain-text file. Sections is a comma-separated
    list of section names present in the manuscript (used to locate checklist
    items). The checklist scans the text for keywords tied to each guideline
    item and reports present/absent/partial.

Output format:
    A JSON artifact with the review template, checklist findings, and a
    compliance score (fraction of applicable items addressed). Every artifact
    carries schema_version, artifact_type, tool_version, and warnings.
    Exit code 0 on success, 1 on bad input.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

VERSION = "0.1.0"

# --- Venue templates ----------------------------------------------------------

VENUE_TEMPLATES = {
    "journal": {
        "name": "Journal peer review",
        "sections": [
            {"id": "summary", "title": "Summary of the work",
             "prompt": "In 3-5 sentences, summarize the question, approach, and claimed contribution."},
            {"id": "significance", "title": "Significance and novelty",
             "prompt": "What is new? Why does it matter? How does it relate to existing literature?"},
            {"id": "strengths", "title": "Major strengths",
             "prompt": "List the most compelling aspects of the work."},
            {"id": "major_issues", "title": "Major issues",
             "prompt": "List concerns that affect the validity or interpretation of the claims. For each, state the claim, the problem, and a concrete remedy."},
            {"id": "minor_issues", "title": "Minor issues",
             "prompt": "List presentation, clarification, or reproducibility points that do not affect the main conclusions."},
            {"id": "reproducibility", "title": "Reproducibility",
             "prompt": "Are data, code, methods, and analysis plan sufficient to reproduce the results?"},
            {"id": "recommendation", "title": "Recommendation",
             "prompt": "Accept / Minor revision / Major revision / Reject, with justification."},
        ],
    },
    "conference": {
        "name": "Conference peer review",
        "sections": [
            {"id": "summary", "title": "Summary",
             "prompt": "Summarize the problem, method, and results in a short paragraph."},
            {"id": "clarity", "title": "Clarity of presentation",
             "prompt": "Is the paper well organized and understandable?"},
            {"id": "technical_correctness", "title": "Technical correctness",
             "prompt": "Are the methods sound and the claims supported by evidence?"},
            {"id": "novelty", "title": "Novelty and significance",
             "prompt": "Does the work advance the field beyond prior art?"},
            {"id": "evaluation", "title": "Experimental evaluation",
             "prompt": "Are baselines, metrics, and ablations adequate and fairly reported?"},
            {"id": "questions", "title": "Questions for authors",
             "prompt": "List specific questions whose answers could change your evaluation."},
            {"id": "score", "title": "Overall assessment",
             "prompt": "Reject / Borderline / Accept, with confidence level."},
        ],
    },
    "preprint": {
        "name": "Preprint open review",
        "sections": [
            {"id": "summary", "title": "Summary",
             "prompt": "Briefly describe the work and its context."},
            {"id": "core_claims", "title": "Core claims and evidence",
             "prompt": "Map each central claim to the evidence offered."},
            {"id": "methods", "title": "Methods and transparency",
             "prompt": "Are methods described in sufficient detail? Are data/code shared?"},
            {"id": "suggestions", "title": "Constructive suggestions",
             "prompt": "Offer concrete, respectful suggestions for improvement."},
        ],
    },
    "grant": {
        "name": "Grant / funding review",
        "sections": [
            {"id": "significance", "title": "Significance",
             "prompt": "Does the project address an important problem?"},
            {"id": "innovation", "title": "Innovation",
             "prompt": "Does the project challenge existing paradigms or use novel approaches?"},
            {"id": "investigator", "title": "Investigator and environment",
             "prompt": "Are the team and institutional support appropriate?"},
            {"id": "approach", "title": "Approach and feasibility",
             "prompt": "Are the methods sound, with alternative strategies and milestones?"},
            {"id": "impact", "title": "Expected impact",
             "prompt": "What is the likely contribution if successful?"},
        ],
    },
}

# --- Reporting guideline checklists ------------------------------------------

# Each item: id, label, and keyword groups. An item is "present" if any group
# has all its keywords found in the manuscript text (case-insensitive).

CONSORT_ITEMS = [
    {"id": "1a", "label": "Identification as a randomised trial in the title",
     "groups": [["randomised", "title"], ["randomized", "title"]]},
    {"id": "1b", "label": "Structured summary",
     "groups": [["background", "methods", "results", "conclusions"]]},
    {"id": "2a", "label": "Scientific background and rationale",
     "groups": [["background"], ["rationale"]]},
    {"id": "2b", "label": "Specific objectives or hypotheses",
     "groups": [["objective"], ["hypothesis"]]},
    {"id": "3a", "label": "Description of trial design",
     "groups": [["trial design"], ["parallel", "design"]]},
    {"id": "4a", "label": "Eligibility criteria",
     "groups": [["eligibility"], ["inclusion criteria"], ["exclusion criteria"]]},
    {"id": "5", "label": "Interventions",
     "groups": [["intervention"], ["treatment", "group"]]},
    {"id": "6a", "label": "Pre-specified outcomes",
     "groups": [["primary outcome"], ["secondary outcome"], ["outcome measure"]]},
    {"id": "7a", "label": "Sample size determination",
     "groups": [["sample size"], ["power calculation"], ["sample-size"]]},
    {"id": "8a", "label": "Randomisation method",
     "groups": [["randomisation"], ["randomization"], ["randomly assigned"]]},
    {"id": "9", "label": "Allocation concealment",
     "groups": [["allocation concealment"], ["concealed"]]},
    {"id": "10", "label": "Blinding",
     "groups": [["blind"], ["masked"], ["double-blind"]]},
    {"id": "11", "label": "Statistical methods",
     "groups": [["statistical"], ["analysis"], ["regression"]]},
    {"id": "12a", "label": "Participant flow",
     "groups": [["enrolled"], ["randomised", "allocated"], ["flow"]]},
    {"id": "13", "label": "Recruitment dates",
     "groups": [["recruitment"], ["enrolment period"], ["recruited"]]},
    {"id": "14", "label": "Baseline data",
     "groups": [["baseline"], ["characteristics"]]},
    {"id": "15", "label": "Numbers analysed",
     "groups": [["analysed"], ["analyzed"], ["intention-to-treat"]]},
    {"id": "16", "label": "Outcomes and estimation",
     "groups": [["result"], ["mean difference"], ["odds ratio"], ["hazard ratio"]]},
    {"id": "17", "label": "Harms",
     "groups": [["harms"], ["adverse events"], ["side effects"]]},
    {"id": "18", "label": "Limitations",
     "groups": [["limitation"], ["weakness"]]},
    {"id": "19", "label": "Registration and protocol",
     "groups": [["registered"], ["trial registration"], ["protocol"]]},
    {"id": "20", "label": "Funding",
     "groups": [["funding"], ["grant"], ["supported by"]]},
]

STROBE_ITEMS = [
    {"id": "1", "label": "Study design in title/abstract",
     "groups": [["cohort"], ["cross-sectional"], ["case-control"], ["observational"]]},
    {"id": "2", "label": "Scientific background and rationale",
     "groups": [["background"], ["rationale"]]},
    {"id": "3", "label": "Objectives",
     "groups": [["objective"], ["aim"], ["purpose"]]},
    {"id": "4", "label": "Study design elements",
     "groups": [["study design"], ["design"]]},
    {"id": "5", "label": "Setting, locations, dates",
     "groups": [["setting"], ["recruitment"], ["period"]]},
    {"id": "6", "label": "Eligibility criteria and selection",
     "groups": [["eligibility"], ["inclusion"], ["exclusion"]]},
    {"id": "7", "label": "Outcome and predictor definitions",
     "groups": [["outcome"], ["predictor"], ["exposure"], ["variable"]]},
    {"id": "8", "label": "Data sources and measurement",
     "groups": [["data source"], ["measurement"], ["assessed"]]},
    {"id": "9", "label": "Bias",
     "groups": [["bias"], ["confounding"], ["selection bias"]]},
    {"id": "10", "label": "Study size",
     "groups": [["sample size"], ["participants"]]},
    {"id": "11", "label": "Quantitative variable handling",
     "groups": [["continuous"], ["categorical"], ["grouped"]]},
    {"id": "12", "label": "Statistical methods",
     "groups": [["statistical"], ["regression"], ["analysis"]]},
    {"id": "13", "label": "Participants and descriptive data",
     "groups": [["participants"], ["baseline"], ["characteristics"]]},
    {"id": "14", "label": "Outcome data and main results",
     "groups": [["result"], ["outcome"], ["prevalence"], ["incidence"]]},
    {"id": "15", "label": "Sensitivity analyses",
     "groups": [["sensitivity"], ["robust"]]},
    {"id": "16", "label": "Limitations",
     "groups": [["limitation"], ["weakness"]]},
    {"id": "17", "label": "Interpretation and caution",
     "groups": [["interpretation"], ["caution"], ["generalizability"]]},
    {"id": "18", "label": "Funding and role of funders",
     "groups": [["funding"], ["grant"], ["conflict of interest"]]},
]

PRISMA_ITEMS = [
    {"id": "1", "label": "Identification as a systematic review",
     "groups": [["systematic review"], ["meta-analysis"]]},
    {"id": "2", "label": "Structured abstract",
     "groups": [["background", "methods", "results"]]},
    {"id": "3", "label": "Rationale and registration",
     "groups": [["rationale"], ["registered"], ["protocol"]]},
    {"id": "4", "label": "PICOS eligibility criteria",
     "groups": [["population"], ["eligibility"], ["inclusion criteria"]]},
    {"id": "5", "label": "Information sources",
     "groups": [["database"], ["pubmed"], ["embase"], ["search"]]},
    {"id": "6", "label": "Full search strategy",
     "groups": [["search strategy"], ["boolean"], ["search string"]]},
    {"id": "7", "label": "Study selection process",
     "groups": [["screening"], ["title/abstract"], ["full text"]]},
    {"id": "8", "label": "Risk of bias assessment",
     "groups": [["risk of bias"], ["quality assessment"], ["robbins"]]},
    {"id": "9", "label": "Data extraction",
     "groups": [["data extraction"], ["extracted"]]},
    {"id": "10", "label": "Effect measures",
     "groups": [["effect size"], ["odds ratio"], ["risk ratio"], ["mean difference"]]},
    {"id": "11", "label": "Synthesis methods",
     "groups": [["meta-analysis"], ["pooled"], ["heterogeneity"]]},
    {"id": "12", "label": "Heterogeneity (I², Q)",
     "groups": [["i²"], ["i2"], ["heterogeneity"], ["q statistic"]]},
    {"id": "13", "label": "Publication bias",
     "groups": [["publication bias"], ["funnel plot"], ["egger"]]},
    {"id": "14", "label": "Study characteristics and results",
     "groups": [["study characteristics"], ["included studies"]]},
    {"id": "15", "label": "Risk of bias across studies",
     "groups": [["publication bias"], ["small-study"]]},
    {"id": "16", "label": "Summary of evidence and limitations",
     "groups": [["summary of evidence"], ["limitation"], ["grade"]]},
    {"id": "17", "label": "Funding",
     "groups": [["funding"], ["grant"]]},
]

GUIDELINES = {
    "consort": {"name": "CONSORT (RCTs)", "items": CONSORT_ITEMS},
    "strobe": {"name": "STROBE (observational)", "items": STROBE_ITEMS},
    "prisma": {"name": "PRISMA (systematic reviews)", "items": PRISMA_ITEMS},
}


# --- Checklist scoring --------------------------------------------------------

def score_checklist(manuscript_text, items, sections=None):
    text = manuscript_text.lower()
    section_text = text
    findings = []
    present = 0
    for item in items:
        matched = False
        for group in item["groups"]:
            if all(keyword.lower() in section_text for keyword in group):
                matched = True
                break
        status = "present" if matched else "absent"
        if matched:
            present += 1
        findings.append({
            "id": item["id"],
            "label": item["label"],
            "status": status,
        })
    applicable = len(items)
    score = present / applicable if applicable else 0.0
    return findings, present, applicable, score


# --- I/O helpers -------------------------------------------------------------

def ensure_output_path(path, protected, force=False):
    resolved = os.path.abspath(path)
    if resolved in {os.path.abspath(item) for item in protected}:
        raise SystemExit(f"error: output path must not replace an input file: {path}")
    if os.path.exists(resolved) and not force:
        raise SystemExit(f"error: output exists: {path}; use --force to replace a derived artifact")


def write_json(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --- Main --------------------------------------------------------------------

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    ap.add_argument("--mode", choices=["template", "checklist", "full"], required=True)
    ap.add_argument("--venue", choices=list(VENUE_TEMPLATES), help="review venue (template/full)")
    ap.add_argument("--guideline", choices=list(GUIDELINES), help="reporting guideline (checklist/full)")
    ap.add_argument("--manuscript", help="manuscript text file (checklist/full)")
    ap.add_argument("--sections", help="comma-separated section names present in manuscript")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--force", action="store_true", help="replace existing derived outputs")
    args = ap.parse_args(argv)

    try:
        if args.mode == "template":
            if not args.venue:
                raise ValueError("--venue is required for --mode template")
            template = VENUE_TEMPLATES[args.venue]
            ensure_output_path(args.out, [], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "review-template",
                "tool_version": VERSION,
                "venue": args.venue,
                "template": template,
                "warnings": [
                    "This is a review skeleton only; it does not contain actual reviewer comments or an expert assessment.",
                ],
            }
            write_json(args.out, artifact)
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

        if args.mode == "checklist" or args.mode == "full":
            if not args.guideline or not args.manuscript:
                raise ValueError("--guideline and --manuscript are required for checklist/full")
            source = Path(args.manuscript).resolve(strict=True)
            text = source.read_text(encoding="utf-8")
            sections = [s.strip() for s in args.sections.split(",") if s.strip()] if args.sections else []
            guideline = GUIDELINES[args.guideline]
            findings, present, applicable, score = score_checklist(text, guideline["items"], sections)
            ensure_output_path(args.out, [str(source)], args.force)
            artifact = {
                "schema_version": "1.0.0",
                "artifact_type": "reporting-guideline-checklist",
                "tool_version": VERSION,
                "source": str(source),
                "guideline": guideline["name"],
                "compliance_score": score,
                "items_present": present,
                "items_applicable": applicable,
                "findings": findings,
                "warnings": [
                    "Compliance is scored by keyword presence only; it does not verify the quality, correctness, or completeness of reporting.",
                    "A high score does not replace expert review or confirm adherence to the full guideline.",
                ],
            }
            if args.mode == "full":
                if not args.venue:
                    raise ValueError("--venue is required for --mode full")
                artifact["venue"] = args.venue
                artifact["review_template"] = VENUE_TEMPLATES[args.venue]
                artifact["artifact_type"] = "review-with-checklist"
            write_json(args.out, artifact)
            print(json.dumps(artifact, ensure_ascii=False, indent=2))
            return 0

    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
