from pathlib import Path

from tools.validate_skills import skill_directories, validate_repository


ROOT = Path(__file__).resolve().parents[1]


def test_expected_skills_are_discovered():
    names = {path.name for path in skill_directories(ROOT)}
    assert names == {
        "academic-presentation-poster",
        "biomedical-research",
        "causal-inference-assistant",
        "chemistry-research",
        "data-analysis-assistant",
        "experiment-designer",
        "knowledge-graph-builder",
        "literature-reader",
        "machine-learning-research",
        "materials-research",
        "md2latex",
        "paper-writing-assistant",
        "patent-prior-art-search",
        "peer-review-and-rebuttal",
        "protocol-authoring",
        "qualitative-research-assistant",
        "reproduction-assistant",
        "research-data-management",
        "research-integrity-and-ethics",
        "research-project-orchestrator",
        "research-proposal-and-grant",
        "research-software-quality",
        "scholarly-search-manager",
        "scientific-plot",
        "social-science-research",
        "survey-and-psychometrics",
        "systematic-review-meta-analysis",
        "thesis-defense-assistant",
        "researchos",
    }


def test_repository_structure_is_valid():
    assert validate_repository(ROOT) == []
