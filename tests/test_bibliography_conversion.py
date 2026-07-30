import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "literature-reader" / "scripts" / "convert_bibliography.py"
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


@pytest.fixture
def zotero_json(tmp_path: Path) -> Path:
    source = tmp_path / "zotero.json"
    source.write_text(
        json.dumps(
            [
                {
                    "key": "ABCD1234",
                    "data": {
                        "key": "ABCD1234",
                        "itemType": "journalArticle",
                        "title": "Open Research Interchange",
                        "creators": [
                            {"creatorType": "author", "firstName": "Jane", "lastName": "Smith"},
                            {"creatorType": "author", "name": "ResearchOS Consortium"},
                        ],
                        "date": "2024-03-01",
                        "publicationTitle": "Journal of Open Tests",
                        "volume": "12",
                        "issue": "3",
                        "pages": "10-20",
                        "DOI": "10.1000/EXAMPLE.1",
                        "url": "https://example.org/paper",
                        "abstractNote": "A short user-supplied abstract.",
                        "tags": [{"tag": "open science"}, {"tag": "metadata"}],
                        "extra": "PMID: 12345678\narXiv: 2401.12345v2",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )
    return source


@pytest.mark.parametrize(
    "target,extension",
    [
        ("csl-json", ".json"),
        ("bibtex", ".bib"),
        ("ris", ".ris"),
        ("endnote-xml", ".xml"),
    ],
)
def test_zotero_round_trip_preserves_core_fields(
    tmp_path: Path, zotero_json: Path, target: str, extension: str
):
    converted = tmp_path / f"library{extension}"
    first = run_cli(zotero_json, "--to", target, "--out", converted)
    assert first.returncode == 0, first.stderr
    manifest = Path(str(converted) + ".manifest.json")
    validate_artifact(manifest, "bibliography-conversion")

    normalized = tmp_path / f"normalized-{target}.json"
    second = run_cli(converted, "--from", target, "--to", "researchos-json", "--out", normalized)
    assert second.returncode == 0, second.stderr
    validate_artifact(normalized, "bibliography-library")
    validate_artifact(Path(str(normalized) + ".manifest.json"), "bibliography-conversion")

    item = json.loads(normalized.read_text(encoding="utf-8"))["items"][0]
    assert item["title"] == "Open Research Interchange"
    assert item["doi"] == "10.1000/example.1"
    assert item["year"] == 2024
    assert item["authors"][0]["family"] == "Smith"
    assert item["pmid"] == "12345678"
    assert item["arxiv_id"] == "2401.12345v2"


def test_conversion_protects_both_output_files_and_source(tmp_path: Path, zotero_json: Path):
    output = tmp_path / "library.bib"
    first = run_cli(zotero_json, "--to", "bibtex", "--out", output)
    assert first.returncode == 0, first.stderr
    original_output = output.read_text(encoding="utf-8")

    protected = run_cli(zotero_json, "--to", "bibtex", "--out", output)
    assert protected.returncode != 0
    assert output.read_text(encoding="utf-8") == original_output

    forced = run_cli(zotero_json, "--to", "bibtex", "--out", output, "--force")
    assert forced.returncode == 0, forced.stderr
    source_text = zotero_json.read_text(encoding="utf-8")
    same_path = run_cli(zotero_json, "--to", "bibtex", "--out", zotero_json, "--force")
    assert same_path.returncode != 0
    assert zotero_json.read_text(encoding="utf-8") == source_text


def test_strict_mode_and_unsafe_xml_fail_cleanly(tmp_path: Path):
    incomplete = tmp_path / "incomplete.json"
    incomplete.write_text('[{"author": [{"literal": "Anonymous"}]}]', encoding="utf-8")
    result = run_cli(incomplete, "--to", "ris", "--out", tmp_path / "out.ris", "--strict")
    assert result.returncode != 0
    assert "missing title" in result.stderr

    xml = tmp_path / "unsafe.xml"
    xml.write_text(
        '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e "unsafe">]><xml><records/></xml>',
        encoding="utf-8",
    )
    result = run_cli(xml, "--to", "ris", "--out", tmp_path / "unsafe.ris")
    assert result.returncode != 0
    assert "DOCTYPE" in result.stderr
