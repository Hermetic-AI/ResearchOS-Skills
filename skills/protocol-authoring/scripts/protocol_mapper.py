#!/usr/bin/env python3
"""Map a study protocol to a reporting guideline and draft a registration summary.

Reads a ``research-protocol`` and:

1. **Maps the design to a reporting guideline** — CONSORT (randomized trials),
   SPIRIT (trial protocols), STROBE (observational studies), PRISMA (systematic
   reviews / meta-analyses), or ARRIVE (animal/preclinical work) — by scoring the
   declared design and populated fields against keyword signals.
2. **Generates a compliance checklist** for the mapped guideline, marking each
   item against the protocol fields that satisfy it.
3. **Produces a registration-ready summary** shaped for ClinicalTrials.gov or
   OSF, pulling the populated fields each registry expects.

The script writes a JSON mapping report to ``--out`` and prints it to stdout.
It does not submit a registration, guarantee completeness, or replace the
governing guideline's official checklist.

Dependencies: none (Python 3.8+ standard library only).

CLI usage:
    python protocol_mapper.py --protocol protocol.json --registry clinicaltrials.gov \\
        --out protocol-mapping.json

    python protocol_mapper.py --protocol protocol.json --registry osf \\
        --out protocol-mapping.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

# Guideline definitions: id, human name, scoring keywords, the protocol fields
# that satisfy each checklist item, and the registry it primarily serves.
GUIDELINES = [
    {
        "id": "consort",
        "name": "CONSORT (randomized parallel-group trials)",
        "keywords": ["randomised", "randomized", "rct", "trial", "intervention",
                      "parallel", "placebo", "control arm", "random allocation"],
        "checklist": [
            {"item": "title_and_abstract", "fields": ["title", "objectives"]},
            {"item": "background_and_rationale", "fields": ["objectives", "hypotheses"]},
            {"item": "design_and_eligibility", "fields": ["population_and_eligibility"]},
            {"item": "interventions", "fields": ["procedures"]},
            {"item": "outcomes", "fields": ["outcomes_and_estimands"]},
            {"item": "sample_size", "fields": ["sample_size_evidence"]},
            {"item": "randomization_and_blinding", "fields": ["procedures"]},
            {"item": "statistical_methods", "fields": ["analysis_artifacts"]},
            {"item": "participant_flow", "fields": ["monitoring_and_stopping"]},
            {"item": "harms_and_limitations", "fields": ["amendments_and_deviations"]},
            {"item": "registration_and_protocol", "fields": ["ethics_and_registration"]},
            {"item": "funding_and_conflicts", "fields": ["ethics_and_registration"]},
        ],
    },
    {
        "id": "spirit",
        "name": "SPIRIT (trial protocols)",
        "keywords": ["protocol", "trial protocol", "intervention", "randomized",
                      "randomised", "rct", "clinical trial"],
        "checklist": [
            {"item": "administrative_information", "fields": ["title", "ethics_and_registration"]},
            {"item": "background_and_rationale", "fields": ["objectives", "hypotheses"]},
            {"item": "objectives_and_hypotheses", "fields": ["objectives", "hypotheses"]},
            {"item": "trial_design", "fields": ["population_and_eligibility", "procedures"]},
            {"item": "eligibility", "fields": ["population_and_eligibility"]},
            {"item": "interventions", "fields": ["procedures"]},
            {"item": "outcomes_and_estimands", "fields": ["outcomes_and_estimands"]},
            {"item": "sample_size", "fields": ["sample_size_evidence"]},
            {"item": "allocation_and_blinding", "fields": ["procedures"]},
            {"item": "data_collection_and_management", "fields": ["data_governance"]},
            {"item": "statistical_analysis", "fields": ["analysis_artifacts"]},
            {"item": "monitoring_and_stopping", "fields": ["monitoring_and_stopping"]},
            {"item": "ethics_and_dissemination", "fields": ["ethics_and_registration"]},
            {"item": "amendments_and_deviations", "fields": ["amendments_and_deviations"]},
        ],
    },
    {
        "id": "strobe",
        "name": "STROBE (observational studies)",
        "keywords": ["cohort", "case-control", "cross-sectional", "observational",
                      "longitudinal", "retrospective", "prospective", "survey",
                      "registry study"],
        "checklist": [
            {"item": "title_and_abstract", "fields": ["title", "objectives"]},
            {"item": "background_and_rationale", "fields": ["objectives", "hypotheses"]},
            {"item": "study_design", "fields": ["population_and_eligibility", "procedures"]},
            {"item": "setting_and_participants", "fields": ["population_and_eligibility"]},
            {"item": "variables_and_estimands", "fields": ["outcomes_and_estimands"]},
            {"item": "data_sources_and_measurement", "fields": ["procedures", "data_governance"]},
            {"item": "bias_and_confounding", "fields": ["analysis_artifacts"]},
            {"item": "sample_size", "fields": ["sample_size_evidence"]},
            {"item": "quantitative_methods", "fields": ["analysis_artifacts"]},
            {"item": "participants_and_descriptive", "fields": ["population_and_eligibility"]},
            {"item": "outcome_data", "fields": ["outcomes_and_estimands"]},
            {"item": "main_results", "fields": ["outcomes_and_estimands", "analysis_artifacts"]},
            {"item": "sensitivity_and_limitations", "fields": ["amendments_and_deviations"]},
            {"item": "interpretation_and_generalisability", "fields": ["objectives"]},
            {"item": "funding_and_conflicts", "fields": ["ethics_and_registration"]},
        ],
    },
    {
        "id": "prisma",
        "name": "PRISMA (systematic reviews and meta-analyses)",
        "keywords": ["systematic review", "meta-analysis", "meta analysis",
                      "literature review", "scoping review", "evidence synthesis"],
        "checklist": [
            {"item": "title_and_abstract", "fields": ["title", "objectives"]},
            {"item": "rationale_and_objectives", "fields": ["objectives", "hypotheses"]},
            {"item": "eligibility_criteria", "fields": ["population_and_eligibility"]},
            {"item": "information_sources", "fields": ["procedures"]},
            {"item": "search_strategy", "fields": ["procedures"]},
            {"item": "selection_process", "fields": ["procedures"]},
            {"item": "data_collection", "fields": ["data_governance"]},
            {"item": "study_risk_of_bias", "fields": ["analysis_artifacts"]},
            {"item": "synthesis_and_effects", "fields": ["outcomes_and_estimands", "analysis_artifacts"]},
            {"item": "reporting_bias_and_certainty", "fields": ["amendments_and_deviations"]},
            {"item": "registration_and_protocol", "fields": ["ethics_and_registration"]},
            {"item": "funding_and_conflicts", "fields": ["ethics_and_registration"]},
        ],
    },
    {
        "id": "arrive",
        "name": "ARRIVE (animal / preclinical research)",
        "keywords": ["animal", "in vivo", "preclinical", "rodent", "mouse", "rat",
                      "animal model", "laboratory animal"],
        "checklist": [
            {"item": "title_and_abstract", "fields": ["title", "objectives"]},
            {"item": "introduction_and_objectives", "fields": ["objectives", "hypotheses"]},
            {"item": "ethical_statement_and_housing", "fields": ["ethics_and_registration"]},
            {"item": "study_design_and_randomization", "fields": ["procedures"]},
            {"item": "experimental_animals", "fields": ["population_and_eligibility"]},
            {"item": "procedures_and_interventions", "fields": ["procedures"]},
            {"item": "outcome_measures", "fields": ["outcomes_and_estimands"]},
            {"item": "sample_size", "fields": ["sample_size_evidence"]},
            {"item": "statistical_methods", "fields": ["analysis_artifacts"]},
            {"item": "results_and_adverse_events", "fields": ["monitoring_and_stopping"]},
            {"item": "interpretation_and_limitations", "fields": ["amendments_and_deviations"]},
            {"item": "funding_and_conflicts", "fields": ["ethics_and_registration"]},
        ],
    },
]


def _field_populated(protocol, field):
    """True when a protocol field exists and is non-empty."""
    value = protocol.get(field)
    if value is None:
        return False
    if isinstance(value, (list, dict)):
        return bool(value)
    return bool(str(value).strip())


def map_guideline(protocol):
    """Score each guideline against the protocol and return the best match.

    Scoring sums keyword hits in the design string plus a bonus for each
    checklist item whose fields are populated, so a design keyword match is
    reinforced by structural completeness. Returns the guideline with the
    highest score (ties broken by list order) and the winning score.
    """
    design = str(protocol.get("design") or "").lower()
    best, best_score = GUIDELINES[0], -1
    for guideline in GUIDELINES:
        keyword_hits = sum(1 for kw in guideline["keywords"] if kw in design)
        field_hits = sum(1 for item in guideline["checklist"]
                         if _field_populated(protocol, item["fields"][0]))
        score = keyword_hits * 3 + field_hits
        if score > best_score:
            best, best_score = guideline, score
    return best, best_score


def build_checklist(protocol, guideline):
    """Mark each checklist item satisfied/partial/missing from protocol fields."""
    rows = []
    for item in guideline["checklist"]:
        populated = sum(1 for field in item["fields"] if _field_populated(protocol, field))
        if populated == len(item["fields"]):
            status = "satisfied"
        elif populated > 0:
            status = "partial"
        else:
            status = "missing"
        rows.append({"item": item["item"], "status": status,
                     "fields": item["fields"]})
    return rows


def registration_summary(protocol, registry, guideline):
    """Shape populated protocol fields into a registry-ready summary."""
    summary = {
        "registry": registry,
        "mapped_guideline": guideline["id"],
        "title": protocol.get("title") or None,
        "design": protocol.get("design") or None,
        "objectives": protocol.get("objectives") or [],
        "population": protocol.get("population_and_eligibility") or {},
        "interventions_or_exposures": protocol.get("procedures") or [],
        "outcomes": protocol.get("outcomes_and_estimands") or [],
        "eligibility": protocol.get("population_and_eligibility") or {},
        "sample_size_evidence": protocol.get("sample_size_evidence") or [],
        "analysis_plan": protocol.get("analysis_artifacts") or [],
        "ethics_and_registration": protocol.get("ethics_and_registration") or [],
        "data_governance": protocol.get("data_governance") or [],
    }
    if registry == "clinicaltrials.gov":
        summary["registry_fields"] = {
            "brief_title": protocol.get("title"),
            "study_type": "Interventional" if guideline["id"] in ("consort", "spirit") else "Observational",
            "condition": protocol.get("population_and_eligibility"),
            "intervention_name": protocol.get("procedures"),
            "primary_outcome": protocol.get("outcomes_and_estimands"),
            "eligibility_criteria": protocol.get("population_and_eligibility"),
        }
    elif registry == "osf":
        summary["registry_fields"] = {
            "title": protocol.get("title"),
            "description": protocol.get("objectives"),
            "category": "analysis" if guideline["id"] == "prisma" else "project",
            "tags": [guideline["id"], protocol.get("design")],
        }
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--protocol", required=True, help="path to a research-protocol JSON file")
    p.add_argument("--registry", choices=("clinicaltrials.gov", "osf"), default="clinicaltrials.gov",
                   help="target registry for the registration summary (default clinicaltrials.gov)")
    p.add_argument("--out", required=True, help="output mapping report")
    p.add_argument("--force", action="store_true", help="replace an existing --out file")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    a = p.parse_args(argv)

    try:
        src = Path(a.protocol).resolve(strict=True)
        out = Path(a.out).resolve()
        if out == src:
            raise ValueError("--out must differ from --protocol")
        if out.exists() and not a.force:
            raise ValueError("output exists; use --force only for a revised mapping")

        protocol = json.loads(src.read_text(encoding="utf-8-sig"))
        if protocol.get("artifact_type") != "research-protocol":
            raise ValueError("--protocol must be a research-protocol artifact")

        guideline, score = map_guideline(protocol)
        checklist = build_checklist(protocol, guideline)
        summary = registration_summary(protocol, a.registry, guideline)
        missing = sum(1 for row in checklist if row["status"] == "missing")

        report = {
            "schema_version": "1.0.0",
            "artifact_type": "protocol-guideline-mapping",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "protocol": str(src),
            "registry": a.registry,
            "mapped_guideline": guideline["id"],
            "guideline_name": guideline["name"],
            "match_score": score,
            "checklist": checklist,
            "checklist_items": len(checklist),
            "missing_items": missing,
            "registration_summary": summary,
            "ready_for_human_review": missing == 0,
            "warnings": [
                "Mapping is heuristic: confirm the matched guideline against the study's "
                "actual design and the governing reporting standard. This does not submit a "
                "registration, guarantee checklist completeness, or replace the official "
                "guideline checklist.",
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
