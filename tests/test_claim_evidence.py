import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "literature-reader" / "scripts" / "audit_claim_evidence.py"
ENVIRONMENT = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


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


def provenance(locator: str) -> dict:
    return {"created_by": "test", "sources": [{"kind": "file", "locator": locator}]}


def write_note(path: Path, quote: str, method: str = "native-text", verification: str = "exact-match") -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "artifact_type": "paper-note",
                "paper": {"title": "Evidence Paper", "doi": None, "year": 2024, "authors": ["A. Author"]},
                "research_question": "Does the method improve accuracy?",
                "method": "Controlled comparison",
                "contributions": ["Reports an improvement"],
                "limitations": ["Single dataset"],
                "claims": [
                    {
                        "id": "finding-primary",
                        "claim_type": "finding",
                        "text": "The method improved accuracy by five points.",
                        "support_level": "direct",
                        "evidence": [
                            {
                                "source": "paper.pdf",
                                "page": 2,
                                "section": "Results",
                                "quote": quote,
                                "extraction_method": method,
                                "verification": verification,
                            }
                        ],
                    }
                ],
                "provenance": provenance("paper.pdf"),
            }
        ),
        encoding="utf-8",
    )


def write_extraction(path: Path, method: str = "native-text") -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "artifact_type": "pdf-extraction",
                "input": {"kind": "file", "locator": "paper.pdf", "checksum": "sha256:abc"},
                "page_count": 2,
                "selected_pages": [2],
                "pages": [
                    {
                        "page_number": 2,
                        "extraction_method": method,
                        "layout": "ocr-reading-order" if method == "ocr" else "single",
                        "character_count": 66,
                        "text": "Results\nThe method improved accuracy by five points compared with baseline.",
                    }
                ],
                "tables": [],
                "captions": [],
                "supplementary_mentions": [],
                "warnings": [],
                "provenance": provenance("paper.pdf"),
            }
        ),
        encoding="utf-8",
    )


def validate_artifact(path: Path, artifact_type: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_artifact.py"), str(path), "--type", artifact_type],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_exact_page_quote_passes_and_report_validates(tmp_path: Path):
    note, extraction, report = tmp_path / "note.json", tmp_path / "extraction.json", tmp_path / "audit.json"
    write_note(note, "The method improved accuracy by five points compared with baseline.")
    write_extraction(extraction)

    result = run_cli(note, "--extraction", extraction, "--out", report)
    assert result.returncode == 0, result.stderr
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "pass"
    assert payload["claim_count"] == payload["anchored_claim_count"] == payload["exact_match_count"] == 1
    validate_artifact(note, "paper-note")
    validate_artifact(report, "evidence-audit")


def test_wrong_quote_fails_but_still_writes_auditable_report(tmp_path: Path):
    note, extraction, report = tmp_path / "note.json", tmp_path / "extraction.json", tmp_path / "audit.json"
    write_note(note, "A result that is not on the cited page.")
    write_extraction(extraction)

    result = run_cli(note, "--extraction", extraction, "--out", report)
    assert result.returncode == 1
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "fail"
    assert any(finding["code"] == "quote-not-found" for finding in payload["findings"])
    validate_artifact(report, "evidence-audit")


def test_unverified_ocr_warns_or_fails_in_strict_mode(tmp_path: Path):
    note, extraction = tmp_path / "note.json", tmp_path / "extraction.json"
    write_note(
        note,
        "The method improved accuracy by five points compared with baseline.",
        method="ocr",
        verification="unverified",
    )
    write_extraction(extraction, method="ocr")

    warning = run_cli(note, "--extraction", extraction)
    assert warning.returncode == 0
    assert json.loads(warning.stdout)["status"] == "warning"

    strict = run_cli(note, "--extraction", extraction, "--strict-ocr")
    assert strict.returncode == 1
    assert json.loads(strict.stdout)["status"] == "fail"


def test_report_overwrite_and_source_paths_are_protected(tmp_path: Path):
    note, extraction, report = tmp_path / "note.json", tmp_path / "extraction.json", tmp_path / "audit.json"
    write_note(note, "The method improved accuracy by five points compared with baseline.")
    write_extraction(extraction)
    assert run_cli(note, "--extraction", extraction, "--out", report).returncode == 0
    original = report.read_text(encoding="utf-8")
    assert run_cli(note, "--extraction", extraction, "--out", report).returncode != 0
    assert report.read_text(encoding="utf-8") == original
    assert run_cli(note, "--extraction", extraction, "--out", report, "--force").returncode == 0

    note_text = note.read_text(encoding="utf-8")
    assert run_cli(note, "--out", note, "--force").returncode != 0
    assert note.read_text(encoding="utf-8") == note_text
