import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8"))
PROVENANCE = {"created_by": "test", "sources": [{"kind": "user", "locator": "fixture"}]}


VALID = {
    "paper_note": {
        "paper": {"title": "T"},
        "research_question": "Q",
        "method": "M",
        "contributions": [],
        "limitations": [],
        "claims": [{
            "id": "claim-1",
            "claim_type": "finding",
            "text": "Finding",
            "support_level": "direct",
            "evidence": [{"source": "paper.pdf", "page": 1, "quote": "evidence", "extraction_method": "native-text", "verification": "exact-match"}],
        }],
    },
    "literature_matrix": {"dimensions": ["method"], "papers": ["p1"], "rows": []},
    "research_gap": {"candidates": [{"statement": "S", "gap_type": "method", "feasibility": "caution"}]},
    "design_brief": {"hypothesis": "H", "variables": [], "treatments": [], "experimental_unit": "subject"},
    "analysis_plan": {"outcomes": ["score"], "comparisons": [], "planned_models": ["t-test"], "alpha": 0.05},
    "preregistration_manifest": {"study_id": "s1", "title": "Study", "protocol_version": "1.0.0", "registration_status": "draft", "frozen_at": None, "source_spec": {"kind": "file", "locator": "study.json"}, "files": [{"path": f"file-{i}", "sha256": "a" * 64, "bytes": 0} for i in range(4)], "unresolved": []},
    "sequential_design_plan": {"study_id": "s1", "family_alpha": 0.05, "sidedness": "two-sided", "multiplicity": {"method": "bonferroni"}, "endpoints": [{"id": "primary", "local_alpha": 0.05, "looks": []}], "sequential": {"spending": "none", "information_fractions": [1.0]}, "stopping_rules": {}, "adaptations": [], "simulation_plan": None, "warnings": []},
    "cleaning_manifest": {"input": {"kind": "file", "locator": "raw.csv"}, "output": {"kind": "file", "locator": "clean.csv"}, "steps": []},
    "stat_results": {"alpha": 0.05, "results": [{"id": "primary", "test": "Welch t", "statistic": 2.1, "p_value": 0.04}]},
    "competing_risk_estimate": {"time_column": "time", "status_column": "status", "group_column": None, "causes": [1], "groups": [{"group": "all", "cause": 1, "n": 2, "events": 1, "estimates": [{"time": 1, "cumulative_incidence": 0.5, "standard_error": 0.2}]}], "warnings": []},
    "time_series_forecast": {"date_column": "date", "value_column": "y", "frequency": "MS", "order": [1,0,0], "seasonal_order": [0,0,0,0], "trend": "c", "nobs": 10, "missing": 0, "converged": True, "aic": 1.0, "bic": 2.0, "coefficients": [], "forecast": [], "warnings": []},
    "resampling_estimate": {"method": "bootstrap", "statistic": "mean", "point_estimate": 1.0, "confidence_interval": [0.5, 1.5], "p_value": None, "n_resamples": 100, "seed": 0, "warnings": []},
    "bayesian_estimate": {"model": "beta-binomial", "prior": {}, "arms": {}, "contrast": "a-b", "posterior_mean": 0.1, "credible_interval": [-0.1, 0.3], "probability_greater_than_zero": 0.8, "n_draws": 100, "seed": 0, "warnings": []},
    "model_diagnostics": {"formula": "y ~ x", "family": "ols", "nobs": 10, "vif": [], "influence": [], "warnings": []},
    "sensitivity_analysis": {"estimand": "delta", "observed_effect": 0.1, "observed_standard_error": 0.2, "missing_fraction": 0.1, "scenarios": [{}, {}], "warnings": []},
    "imputation_manifest": {"input": {"kind": "file", "locator": "raw.csv"}, "output": {"kind": "file", "locator": "completed.csv"}, "method": "mice", "iterations": 2, "columns": ["x", "y"], "missing_before": {"x": 1}, "missing_after": {"x": 0}, "warnings": []},
    "data_dictionary": {"input": {"kind": "file", "locator": "data.tsv"}, "input_format": "tsv", "rows": 2, "columns": [{"name": "x", "dtype": "int64", "missing": 0, "nonmissing": 2, "unique": 2, "example_values": ["1", "2"]}], "warnings": []},
    "figure_manifest": {"figure_id": "fig1", "outputs": ["fig1.svg"], "data_sources": [{"kind": "file", "locator": "data.csv"}]},
    "pdf_extraction": {
        "input": {"kind": "file", "locator": "paper.pdf"},
        "page_count": 1,
        "selected_pages": [1],
        "pages": [{"page_number": 1, "extraction_method": "native-text", "layout": "single", "character_count": 4, "text": "text"}],
        "tables": [],
        "captions": [],
        "supplementary_mentions": [],
        "warnings": [],
    },
    "bibliography_audit": {
        "entries": [],
        "clusters": [],
        "integrity_alerts": [],
        "summary": {"entry_count": 0, "invalid_identifier_count": 0, "cluster_count": 0, "integrity_alert_count": 0, "online_checked": False},
        "warnings": [],
    },
    "bibliography_library": {"items": [], "warnings": []},
    "bibliography_conversion": {
        "source_format": "bibtex",
        "target_format": "ris",
        "record_count": 1,
        "input": {"kind": "file", "locator": "library.bib"},
        "output": {"kind": "file", "locator": "library.ris"},
        "warnings": [],
    },
    "evidence_audit": {
        "note": {"kind": "file", "locator": "note.json"},
        "extraction": None,
        "claim_count": 1,
        "anchored_claim_count": 1,
        "exact_match_count": 0,
        "status": "warning",
        "findings": [],
        "warnings": ["no extraction supplied"],
    },
    "literature_batch": {
        "source_root": "corpus",
        "output_root": "derived",
        "checkpoint": "derived/batch-state.json",
        "items": [],
        "summary": {"total": 0},
        "warnings": [],
    },
    "reproduction_card": {"repository_commit": "abc123", "environment": {}, "comparisons": [{"metric": "accuracy", "verdict": "match"}]},
}


@pytest.mark.parametrize("definition,payload", VALID.items())
def test_minimal_artifact_contract(definition, payload):
    artifact_type = definition.replace("_", "-")
    instance = {"schema_version": "1.0.0", "artifact_type": artifact_type, "provenance": PROVENANCE, **payload}
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]}
    jsonschema.Draft202012Validator(wrapper).validate(instance)


def test_contract_rejects_wrong_artifact_type():
    instance = {"schema_version": "1.0.0", "artifact_type": "wrong", "provenance": PROVENANCE, **VALID["stat_results"]}
    wrapper = {"$schema": SCHEMA["$schema"], "$ref": "#/$defs/stat_results", "$defs": SCHEMA["$defs"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(wrapper).validate(instance)


def test_every_public_contract_has_a_minimal_fixture():
    infrastructure = {"source", "provenance", "evidence_anchor", "artifact_header"}
    assert set(SCHEMA["$defs"]) - infrastructure == set(VALID)
