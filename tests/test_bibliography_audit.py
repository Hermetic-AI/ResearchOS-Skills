import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "literature-reader" / "scripts" / "audit_bibliography.py"
ENVIRONMENT = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def load_module():
    spec = importlib.util.spec_from_file_location("researchos_bibliography_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )


def test_identifier_normalization_and_api_parsers(monkeypatch):
    module = load_module()
    assert module.normalize_doi("https://doi.org/10.1000/ABC.1") == "10.1000/abc.1"
    assert module.normalize_arxiv("arXiv:2401.12345v3") == ("2401.12345", 3)
    assert module.normalize_arxiv("hep-th/9901001v2") == ("hep-th/9901001", 2)
    assert module.normalize_pmid("https://pubmed.ncbi.nlm.nih.gov/12345678/") == "12345678"

    crossref = {
        "message": {
            "DOI": "10.1000/ABC.1",
            "title": ["A paper"],
            "update-to": [
                {"type": "retraction", "source": "retraction-watch", "record-id": 42}
            ],
        }
    }
    monkeypatch.setattr(
        module,
        "request_bytes",
        lambda url, email, timeout: json.dumps(crossref).encode("utf-8"),
    )
    record = module.crossref_lookup("10.1000/abc.1", "contact@example.org", 5)
    assert record["canonical_doi"] == "10.1000/abc.1"
    assert record["updates"][0]["type"] == "retraction"

    atom = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
      <entry><id>http://arxiv.org/abs/2401.12345v3</id><updated>2026-01-01T00:00:00Z</updated>
      <title>A versioned paper</title><arxiv:doi>10.1000/ABC.1</arxiv:doi></entry>
    </feed>"""
    monkeypatch.setattr(module, "request_bytes", lambda url, email, timeout: atom)
    arxiv = module.arxiv_lookup(["2401.12345"], "contact@example.org", 5)
    assert arxiv["2401.12345"]["latest_returned_version"] == 3
    assert arxiv["2401.12345"]["doi"] == "10.1000/abc.1"

    pubmed = {
        "result": {
            "uids": ["12345678"],
            "12345678": {
                "title": "A retracted paper",
                "pubtype": ["Journal Article", "Retracted Publication"],
                "articleids": [{"idtype": "doi", "value": "10.1000/ABC.1"}],
            },
        }
    }
    monkeypatch.setattr(
        module,
        "request_bytes",
        lambda url, email, timeout: json.dumps(pubmed).encode("utf-8"),
    )
    record = module.pubmed_lookup(["12345678"], "contact@example.org", 5)["12345678"]
    assert record["doi"] == "10.1000/abc.1"
    assert "Retracted Publication" in record["publication_types"]
    assert module.redacted_command(["metadata.json", "--online", "--email", "secret@example.org"])[-10:] == "<redacted>"


def test_offline_audit_deduplicates_versions_and_reads_retraction_index(tmp_path: Path):
    source = tmp_path / "metadata.json"
    source.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "title": "Reproducible Models for Science",
                        "authors": ["Smith, Jane"],
                        "year": 2024,
                        "doi": "https://doi.org/10.1000/ABC.1",
                    },
                    {
                        "title": "Reproducible Models for Science",
                        "authors": ["Smith, J."],
                        "year": 2024,
                        "doi": "10.1000/abc.1",
                    },
                    {
                        "title": "A Versioned Preprint",
                        "authors": ["Lee, A."],
                        "year": 2023,
                        "arxiv_id": "2301.12345v1",
                    },
                    {
                        "title": "A Versioned Preprint",
                        "authors": ["Lee, A."],
                        "year": 2023,
                        "arxiv_id": "2301.12345v3",
                    },
                    {"title": "Broken identifier", "doi": "not-a-doi"},
                ]
            }
        ),
        encoding="utf-8",
    )
    index = tmp_path / "retractions.csv"
    index.write_text(
        "Record ID,RetractionNature,RetractionDate,OriginalPaperDOI,OriginalPaperPubMedID\n"
        "77,Retraction,2025-01-02,10.1000/abc.1,\n",
        encoding="utf-8",
    )
    output = tmp_path / "audit.json"

    result = run_cli(source, "--retraction-index", index, "--out", output)
    assert result.returncode == 0, result.stderr
    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert artifact["summary"] == {
        "entry_count": 5,
        "invalid_identifier_count": 1,
        "cluster_count": 2,
        "integrity_alert_count": 2,
        "online_checked": False,
    }
    assert artifact["clusters"][0]["canonical_entry"] == 0
    version_cluster = next(
        cluster for cluster in artifact["clusters"] if cluster["classification"] == "version-family"
    )
    assert version_cluster["canonical_entry"] == 3
    assert all(alert["severity"] == "critical" for alert in artifact["integrity_alerts"])

    validation = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_artifact.py"), str(output), "--type", "bibliography-audit"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )
    assert validation.returncode == 0, validation.stderr

    protected = run_cli(source, "--retraction-index", index, "--out", output)
    assert protected.returncode != 0
    forced = run_cli(source, "--retraction-index", index, "--out", output, "--force")
    assert forced.returncode == 0, forced.stderr


def test_online_requires_contact_email_and_output_never_replaces_input(tmp_path: Path):
    source = tmp_path / "metadata.json"
    original = '[{"title": "Paper"}]\n'
    source.write_text(original, encoding="utf-8")

    missing_email = run_cli(source, "--online")
    assert missing_email.returncode != 0
    assert "--email" in missing_email.stderr

    same_output = run_cli(source, "--out", source, "--force")
    assert same_output.returncode != 0
    assert source.read_text(encoding="utf-8") == original


def test_extract_metadata_preserves_arxiv_version_and_pmid(tmp_path: Path):
    source = tmp_path / "references.txt"
    source.write_text(
        "Smith, J. A sufficiently descriptive paper title. Journal, 2024. "
        "arXiv:2401.12345v2. PMID: 12345678.\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "skills" / "literature-reader" / "scripts" / "extract_metadata.py"), str(source)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    entry = json.loads(result.stdout)["entries"][0]
    assert entry["arxiv_id"] == "2401.12345"
    assert entry["arxiv_version"] == 2
    assert entry["pmid"] == "12345678"
