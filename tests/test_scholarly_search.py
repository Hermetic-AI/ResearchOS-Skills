import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "scholarly-search-manager" / "scripts" / "search_manager.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_plan_builds_database_strings(tmp_path):
    query = tmp_path / "query.json"
    query.write_text(json.dumps({
        "question": "synaptic plasticity and memory",
        "concepts": [
            {"term": "synaptic plasticity", "synonyms": ["neural plasticity"], "pubmed_field": "tiab"},
            {"term": "memory", "synonyms": []},
        ],
        "filters": {"pubmed": {"dates": "2018:2024", "species": "humans"}},
    }), encoding="utf-8")
    out = tmp_path / "plan.json"
    result = run("--mode", "plan", "--query", str(query), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == "1.0.0"
    assert artifact["artifact_type"] == "search-plan"
    assert "tool_version" in artifact
    assert "warnings" in artifact
    plan = artifact["plan"]
    assert "synaptic plasticity" in plan["databases"]["pubmed"]["search_string"]
    assert "memory" in plan["databases"]["pubmed"]["search_string"]
    assert "2018:2024" in plan["databases"]["pubmed"]["search_string"]
    assert "pubmed.ncbi.nlm.nih.gov" in plan["databases"]["pubmed"]["url"]
    assert "OR" in plan["databases"]["crossref"]["search_string"]


def test_plan_requires_concepts(tmp_path):
    query = tmp_path / "query.json"
    query.write_text(json.dumps({"question": "x", "concepts": []}), encoding="utf-8")
    out = tmp_path / "plan.json"
    result = run("--mode", "plan", "--query", str(query), "--out", str(out))
    assert result.returncode == 1
    assert "concepts" in result.stderr


def test_dedupe_by_doi_and_title(tmp_path):
    library = tmp_path / "library.json"
    library.write_text(json.dumps([
        {"doi": "10.1/a", "title": "Memory and Plasticity", "year": 2020, "authors": ["A"]},
        {"doi": "https://doi.org/10.1/a", "title": "Memory and Plasticity", "year": 2020, "authors": ["A"]},
        {"title": "Memory and Plasticity", "year": 2020},
        {"title": "Unrelated Work", "year": 2021, "authors": ["B"]},
    ]), encoding="utf-8")
    out = tmp_path / "deduped.json"
    result = run("--mode", "dedupe", "--library", str(library), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "search-library"
    assert artifact["input_count"] == 4
    # items 1+2 share a DOI (1 cluster); item 3 is a title/year candidate; item 4 is unique
    assert artifact["output_count"] == 3
    assert len(artifact["duplicate_clusters"]) == 1
    assert artifact["duplicate_clusters"][0]["member_indexes"] == [0, 1]


def test_export_ris_bib_csv(tmp_path):
    library = tmp_path / "library.json"
    library.write_text(json.dumps({"items": [
        {"title": "Paper One", "authors": ["A. Smith", "B. Lee"], "year": 2020,
         "journal": "J Mem", "doi": "10.1/one", "abstract": "About memory."},
    ]}), encoding="utf-8")
    ris = tmp_path / "library.ris"
    bib = tmp_path / "library.bib"
    csv_out = tmp_path / "library.csv"
    assert run("--mode", "export", "--library", str(library), "--format", "ris", "--out", str(ris)).returncode == 0
    assert run("--mode", "export", "--library", str(library), "--format", "bib", "--out", str(bib)).returncode == 0
    assert run("--mode", "export", "--library", str(library), "--format", "csv", "--out", str(csv_out)).returncode == 0
    assert "TY  - JOUR" in ris.read_text(encoding="utf-8")
    assert "AU  - A. Smith" in ris.read_text(encoding="utf-8")
    assert "@article{" in bib.read_text(encoding="utf-8")
    csv_rows = list(__import__("csv").DictReader(csv_out.open(encoding="utf-8")))
    assert csv_rows[0]["title"] == "Paper One"


def test_output_protected_without_force(tmp_path):
    library = tmp_path / "library.json"
    library.write_text(json.dumps({"items": [{"title": "T", "year": 2020}]}), encoding="utf-8")
    out = tmp_path / "library.ris"
    first = run("--mode", "export", "--library", str(library), "--format", "ris", "--out", str(out))
    assert first.returncode == 0
    second = run("--mode", "export", "--library", str(library), "--format", "ris", "--out", str(out))
    assert second.returncode == 1
    assert "--force" in second.stderr


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
