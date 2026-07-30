import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "literature-reader" / "scripts" / "extract_pdf.py"


def load_module():
    spec = importlib.util.spec_from_file_location("researchos_extract_pdf", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_minimal_pdf(path: Path) -> None:
    stream = (
        b"BT /F1 12 Tf 72 720 Td (Research Evidence) Tj "
        b"0 -24 Td (Figure 1: Result overview) Tj "
        b"0 -24 Td (See supplementary material for details.) Tj ET"
    )
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(payload))
        payload.extend(f"{number} 0 obj\n".encode("ascii"))
        payload.extend(body)
        payload.extend(b"\nendobj\n")
    xref = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    payload.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode(
            "ascii"
        )
    )
    path.write_bytes(payload)


def test_page_selection_and_invalid_ranges():
    module = load_module()
    assert module.parse_page_spec("1-3,5,3", 6) == [1, 2, 3, 5]
    with pytest.raises(ValueError, match="descending"):
        module.parse_page_spec("4-2", 6)
    with pytest.raises(ValueError, match="outside"):
        module.parse_page_spec("7", 6)


def test_caption_supplement_and_two_column_detection():
    module = load_module()
    text = "Figure 2: Main finding\nSee Supplementary Material A."
    assert module.extract_captions(text, 3) == [
        {"page": 3, "label": "Figure 2", "kind": "figure", "text": "Main finding"}
    ]
    assert module.extract_supplement_mentions(text, 3)[0]["page"] == 3

    words = []
    for row in range(12):
        for x in (40, 340):
            words.append(
                {"text": f"w{row}", "x0": x, "x1": x + 30, "top": 60 + row * 20, "bottom": 72 + row * 20}
            )
    assert module.detect_two_columns(words, 600, 500)
    reconstructed, layout = module.words_to_text(words, 600, 500, "auto")
    assert layout == "two-column"
    assert reconstructed.count("w0") == 2


def test_pdf_extraction_schema_accepts_minimal_artifact():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        (ROOT / "schemas" / "researchos-artifacts.schema.json").read_text(encoding="utf-8")
    )
    artifact = {
        "schema_version": "1.0.0",
        "artifact_type": "pdf-extraction",
        "input": {"kind": "file", "locator": "paper.pdf", "checksum": "sha256:abc"},
        "page_count": 1,
        "selected_pages": [1],
        "pages": [
            {
                "page_number": 1,
                "extraction_method": "native-text",
                "layout": "single",
                "character_count": 4,
                "text": "text",
            }
        ],
        "tables": [],
        "captions": [],
        "supplementary_mentions": [],
        "warnings": [],
        "provenance": {
            "created_by": "extract_pdf.py",
            "created_at": "2026-07-29T00:00:00+00:00",
            "tool_version": "0.1.0",
            "command": "extract_pdf.py paper.pdf",
            "seed": None,
            "sources": [{"kind": "file", "locator": "paper.pdf"}],
            "warnings": [],
        },
    }
    wrapper = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/pdf_extraction",
        "$defs": schema["$defs"],
    }
    jsonschema.Draft202012Validator(wrapper).validate(artifact)


def test_pdf_extraction_and_schema(tmp_path: Path):
    pytest.importorskip("pdfplumber")
    source = tmp_path / "paper.pdf"
    output = tmp_path / "paper.json"
    markdown = tmp_path / "paper.md"
    write_minimal_pdf(source)
    environment = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
    }

    command = [
        sys.executable,
        str(SCRIPT),
        str(source),
        "--ocr",
        "never",
        "--out",
        str(output),
        "--markdown-out",
        str(markdown),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "pdf-extraction"
    assert artifact["pages"][0]["extraction_method"] == "native-text"
    assert "Research Evidence" in artifact["pages"][0]["text"]
    assert artifact["captions"][0]["label"] == "Figure 1"
    assert artifact["supplementary_mentions"]
    assert "## Page 1" in markdown.read_text(encoding="utf-8")

    protected = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=30,
        check=False,
    )
    assert protected.returncode != 0
    forced = subprocess.run(
        [*command, "--force"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=30,
        check=False,
    )
    assert forced.returncode == 0, forced.stderr

    try:
        import jsonschema  # noqa: F401
    except ImportError:
        return
    validation = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_artifact.py"), str(output), "--type", "pdf-extraction"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=30,
        check=False,
    )
    assert validation.returncode == 0, validation.stderr
