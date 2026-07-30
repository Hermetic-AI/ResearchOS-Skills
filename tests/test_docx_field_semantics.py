"""Tests for DOCX field semantics and effective-style computation.

Covers the two roadmap gaps for ``paper-writing-assistant``:
  1. Word author-year field instruction parsing (``docx_citation_audit.py``).
  2. Final effective style computation (``docx_inspect.py``).

Fixtures are minimal valid OOXML DOCX archives built in-memory with the
standard library only.  Namespace constants follow the project convention:
``w`` for WordprocessingML, ``r`` for relationships.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CITATION_SCRIPT = ROOT / "skills" / "paper-writing-assistant" / "scripts" / "docx_citation_audit.py"
INSPECT_SCRIPT = ROOT / "skills" / "paper-writing-assistant" / "scripts" / "docx_inspect.py"
ENVIRONMENT = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml"
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml"
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
                Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
                Target="word/document.xml"/>
</Relationships>
"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""

SETTINGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
</w:settings>
"""


def _run_cli(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )


class DocxBuilder:
    """Build a minimal valid DOCX archive in memory.

    Supply the raw XML strings for ``word/document.xml`` and
    ``word/styles.xml``; the builder fills in the boilerplate parts
    (``[Content_Types].xml``, ``_rels/.rels``, ``word/_rels/document.xml.rels``,
    ``word/settings.xml``) so fixtures stay focused on the XML under test.
    """

    def __init__(self, document_xml: str, styles_xml: str) -> None:
        self.document_xml = document_xml
        self.styles_xml = styles_xml

    def write(self, path: Path) -> None:
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/_rels/document.xml.rels", DOC_RELS)
            archive.writestr("word/settings.xml", SETTINGS)
            archive.writestr("word/document.xml", self.document_xml)
            archive.writestr("word/styles.xml", self.styles_xml)


# ---------------------------------------------------------------------------
# Fixture XML fragments
# ---------------------------------------------------------------------------

STYLES_WITH_INHERITANCE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体"/>
        <w:sz w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:line="360" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体"/>
      <w:sz w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:b/>
      <w:sz w:val="32"/>
      <w:rFonts w:eastAsia="黑体"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="BodyText">
    <w:name w:val="Body Text"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:spacing w:line="480" w:lineRule="auto"/>
      <w:ind w:firstLineChars="200"/>
    </w:pPr>
  </w:style>
</w:styles>
"""

STYLES_MINIMAL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
</w:styles>
"""

DOCUMENT_WITH_FIELDS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:t>Prior work established the baseline (</w:t></w:r>
      <w:r>
        <w:fldChar w:fldCharType="begin"/>
      </w:r>
      <w:r>
        <w:instrText> CITATION Doe2024 \\l 1033 \\p 5 </w:instrText>
      </w:r>
      <w:r>
        <w:fldChar w:fldCharType="separate"/>
      </w:r>
      <w:r>
        <w:t>Doe, 2024, p.5</w:t>
      </w:r>
      <w:r>
        <w:fldChar w:fldCharType="end"/>
      </w:r>
      <w:r><w:t>).</w:t></w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:fldSimple w:instr="CITATION Smith2023 \\l 1033 \\m">
          <w:r><w:t>(Smith, 2023)</w:t></w:r>
        </w:fldSimple>
      </w:r>
    </w:p>
    <w:p>
      <w:r><w:t>正文段落正文段落正文段落。</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
"""

DOCUMENT_PLAIN = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Hello world.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""


# ---------------------------------------------------------------------------
# 1. Author-year field instruction parsing
# ---------------------------------------------------------------------------

def test_citation_field_instruction_parses_key_and_switches(tmp_path: Path):
    docx = tmp_path / "f.docx"
    DocxBuilder(DOCUMENT_WITH_FIELDS, STYLES_MINIMAL).write(docx)

    result = _run_cli(CITATION_SCRIPT, docx, "--fields", "--pretty")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "resolved_fields" in payload
    # One complex field (CITATION Doe2024) and one simple field (CITATION Smith2023).
    assert payload["resolved_field_count"] == 2
    by_key = {f["parsed"]["key"]: f for f in payload["resolved_fields"]}
    assert "Doe2024" in by_key
    doe = by_key["Doe2024"]
    assert doe["kind"] == "fldChar"
    assert doe["parsed"]["has_locale"] is True
    assert doe["parsed"]["has_page"] is True
    assert doe["parsed"]["suppress_author"] is False
    assert doe["parsed"]["switches"].get("l") == ["1033"]
    assert doe["parsed"]["switches"].get("p") == ["5"]
    assert doe["displayed"] == "Doe, 2024, p.5"

    assert "Smith2023" in by_key
    smith = by_key["Smith2023"]
    assert smith["kind"] == "fldSimple"
    assert smith["parsed"]["suppress_author"] is True
    assert smith["displayed"] == "(Smith, 2023)"


# ---------------------------------------------------------------------------
# 2. Field displayed text extraction
# ---------------------------------------------------------------------------

def test_field_displayed_text_captured_between_markers(tmp_path: Path):
    docx = tmp_path / "f.docx"
    DocxBuilder(DOCUMENT_WITH_FIELDS, STYLES_MINIMAL).write(docx)

    result = _run_cli(CITATION_SCRIPT, docx, "--fields")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    displayed = {f["parsed"]["key"]: f["displayed"] for f in payload["resolved_fields"]}
    assert displayed["Doe2024"] == "Doe, 2024, p.5"
    assert displayed["Smith2023"] == "(Smith, 2023)"


# ---------------------------------------------------------------------------
# 3. Effective style computation
# ---------------------------------------------------------------------------

def test_effective_style_inherits_parent_properties(tmp_path: Path):
    docx = tmp_path / "f.docx"
    DocxBuilder(DOCUMENT_PLAIN, STYLES_WITH_INHERITANCE).write(docx)

    result = _run_cli(INSPECT_SCRIPT, docx, "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    eff = payload["effective_styles"]
    assert "Heading1" in eff
    h1 = eff["Heading1"]
    # Inherited from Normal: Times New Roman + 宋体.
    assert h1["run_properties"].get("font_ascii") == "Times New Roman"
    # Own overrides: bold + eastAsia 黑体 + size 16pt (w:sz=32).
    assert h1["run_properties"].get("bold") is True
    assert h1["run_properties"].get("font_eastasia") == "黑体"
    assert h1["run_properties"].get("size_pt") == 16.0
    assert h1["based_on"] == "Normal"

    # BodyText inherits Normal's font but overrides paragraph spacing.
    body = eff["BodyText"]
    assert body["run_properties"].get("font_ascii") == "Times New Roman"
    assert body["paragraph_properties"].get("line_spacing") == 2.0
    assert body["paragraph_properties"].get("indent_firstLineChars") == "200"


# ---------------------------------------------------------------------------
# 4. Document defaults parsed from docDefaults
# ---------------------------------------------------------------------------

def test_docdefaults_parsed_into_default_properties(tmp_path: Path):
    docx = tmp_path / "f.docx"
    DocxBuilder(DOCUMENT_PLAIN, STYLES_WITH_INHERITANCE).write(docx)

    result = _run_cli(INSPECT_SCRIPT, docx, "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["default_run_properties"].get("font_ascii") == "Times New Roman"
    assert payload["default_run_properties"].get("font_eastasia") == "宋体"
    assert payload["default_run_properties"].get("size_pt") == 12.0
    assert payload["default_paragraph_properties"].get("line_spacing") == 1.5
    # Legacy "defaults" key still present for backward compatibility.
    assert payload["defaults"].get("font_ascii") == "Times New Roman"


# ---------------------------------------------------------------------------
# 5. Backward compatibility: existing keys still present without new behavior
# ---------------------------------------------------------------------------

def test_citation_audit_without_fields_flag_unchanged(tmp_path: Path):
    docx = tmp_path / "f.docx"
    DocxBuilder(DOCUMENT_WITH_FIELDS, STYLES_MINIMAL).write(docx)

    result = _run_cli(CITATION_SCRIPT, docx)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    # Existing keys still present.
    for key in ("schema_version", "artifact_type", "tool_version", "document",
                "visible_author_year_candidates", "field_marker_counts", "warnings"):
        assert key in payload, f"missing key: {key}"
    # New keys absent unless --fields is passed.
    assert "resolved_fields" not in payload
    assert "resolved_field_count" not in payload


def test_inspect_legacy_keys_still_present(tmp_path: Path):
    docx = tmp_path / "f.docx"
    DocxBuilder(DOCUMENT_PLAIN, STYLES_WITH_INHERITANCE).write(docx)

    result = _run_cli(INSPECT_SCRIPT, docx, "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    for key in ("file", "defaults", "sections", "heading_styles", "body_sample", "captions"):
        assert key in payload, f"missing key: {key}"
    # New keys added alongside.
    assert "effective_styles" in payload
    assert "default_run_properties" in payload
    assert "default_paragraph_properties" in payload


# ---------------------------------------------------------------------------
# 6. Invalid / non-DOCX input -> error
# ---------------------------------------------------------------------------

def test_non_docx_input_rejected(tmp_path: Path):
    bogus = tmp_path / "not-a-docx.txt"
    bogus.write_text("this is not a docx", encoding="utf-8")

    result = _run_cli(CITATION_SCRIPT, bogus, "--fields")
    assert result.returncode != 0
    assert "docx" in result.stderr.lower()

    result = _run_cli(INSPECT_SCRIPT, bogus)
    assert result.returncode != 0
    assert "docx" in result.stderr.lower()


def test_corrupt_zip_rejected(tmp_path: Path):
    corrupt = tmp_path / "broken.docx"
    corrupt.write_bytes(b"PK\x03\x04garbage")

    result = _run_cli(CITATION_SCRIPT, corrupt, "--fields")
    assert result.returncode != 0

    result = _run_cli(INSPECT_SCRIPT, corrupt)
    assert result.returncode != 0


def test_missing_document_xml_rejected(tmp_path: Path):
    """A ZIP with the .docx extension but no word/document.xml must error."""
    docx = tmp_path / "empty.docx"
    with zipfile.ZipFile(docx, "w") as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)

    result = _run_cli(CITATION_SCRIPT, docx, "--fields")
    assert result.returncode != 0
    assert "document.xml" in result.stderr

    result = _run_cli(INSPECT_SCRIPT, docx)
    assert result.returncode != 0
    assert "document.xml" in result.stderr


# ---------------------------------------------------------------------------
# Direct unit coverage for the instruction parser (no fixture needed).
# ---------------------------------------------------------------------------

def test_parse_citation_instruction_unit():
    # Import the module to exercise the parser directly.
    import importlib.util

    spec = importlib.util.spec_from_file_location("citation_audit_mod", CITATION_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    parsed = module.parse_citation_instruction('CITATION Doe2024 \\l 1033 \\p 5')
    assert parsed["key"] == "Doe2024"
    assert parsed["switches"] == {"l": ["1033"], "p": ["5"]}
    assert parsed["has_locale"] is True
    assert parsed["has_page"] is True
    assert parsed["suppress_author"] is False

    parsed = module.parse_citation_instruction('CITATION "Smith2023" \\l 1033 \\m')
    assert parsed["key"] == "Smith2023"
    assert parsed["suppress_author"] is True

    parsed = module.parse_citation_instruction('CITATION Lee2022 \\t \\r 12')
    assert parsed["key"] == "Lee2022"
    assert parsed["has_title"] is True
    assert "r" in parsed["switches"]  # unrecognized switch still captured
