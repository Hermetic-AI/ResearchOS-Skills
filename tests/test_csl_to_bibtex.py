"""Tests for md2latex/csl_to_bibtex.py (CSL-JSON/YAML -> BibTeX) and the
markdown_project_audit.py --rewrite-plan extension."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CSL = ROOT / "skills" / "md2latex" / "scripts" / "csl_to_bibtex.py"
AUDIT = ROOT / "skills" / "md2latex" / "scripts" / "markdown_project_audit.py"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run_csl(*args):
    return subprocess.run([sys.executable, str(CSL), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=ENV, timeout=30, check=False)


# ---------------------------------------------------------- CSL-JSON -> BibTeX

def test_json_article_fields(tmp_path):
    lib = tmp_path / "lib.json"
    lib.write_text(json.dumps([{
        "type": "article-journal", "id": "doe2024",
        "title": "A Study", "author": [{"family": "Doe", "given": "J."}],
        "issued": {"date-parts": [[2024]]},
        "container-title": "J. Examples", "volume": "1", "page": "1-10",
        "DOI": "10.1234/x",
    }]), encoding="utf-8")
    out = tmp_path / "refs.bib"
    result = run_csl(str(lib), "-o", str(out), "--force")
    assert result.returncode == 0, result.stderr
    bib = out.read_text(encoding="utf-8")
    assert "@article{" in bib
    assert "author = {J. Doe}" in bib
    assert "title = {A Study}" in bib
    assert "journal = {J. Examples}" in bib
    assert "year = 2024" in bib
    assert "doi = {10.1234/x}" in bib


def test_json_book_with_isbn(tmp_path):
    lib = tmp_path / "lib.json"
    lib.write_text(json.dumps([{
        "type": "book", "id": "smith2020", "title": "Examples & More",
        "author": [{"family": "Smith", "given": "B."}],
        "issued": {"date-parts": [[2020]]}, "publisher": "Press", "ISBN": "123",
    }]), encoding="utf-8")
    out = tmp_path / "refs.bib"
    assert run_csl(str(lib), "-o", str(out), "--force").returncode == 0
    bib = out.read_text(encoding="utf-8")
    assert "@book{" in bib
    assert r"\&" in bib  # & must be escaped


def test_json_unknown_type_maps_to_misc(tmp_path):
    lib = tmp_path / "lib.json"
    lib.write_text(json.dumps([{"type": "painting", "id": "x", "title": "Art"}]), encoding="utf-8")
    out = tmp_path / "refs.bib"
    result = run_csl(str(lib), "-o", str(out), "--force")
    assert result.returncode == 0
    bib = out.read_text(encoding="utf-8")
    assert "@misc{" in bib
    assert "unknown CSL type" in result.stderr


def test_key_prefix(tmp_path):
    lib = tmp_path / "lib.json"
    lib.write_text(json.dumps([{"type": "book", "id": "a", "title": "T", "author": [{"family": "Lee", "given": "K."}]}]), encoding="utf-8")
    out = tmp_path / "refs.bib"
    run_csl(str(lib), "--key-prefix", "zot", "-o", str(out), "--force")
    bib = out.read_text(encoding="utf-8")
    assert "zotlee" in bib


def test_output_protected(tmp_path):
    lib = tmp_path / "lib.json"
    lib.write_text(json.dumps([{"type": "book", "id": "a", "title": "T"}]), encoding="utf-8")
    out = tmp_path / "refs.bib"
    out.write_text("existing", encoding="utf-8")
    result = run_csl(str(lib), "-o", str(out))
    assert result.returncode != 0
    assert out.read_text(encoding="utf-8") == "existing"


# ---------------------------------------------------------- CSL-YAML -> BibTeX

def test_yaml_article(tmp_path):
    lib = tmp_path / "lib.yaml"
    lib.write_text("- type: article-journal\n  id: w2023\n  title: YAML Paper\n"
                  "  author:\n    - family: Wang\n      given: L.\n"
                  "  container-title: YAML J\n  DOI: 10.5678/y\n", encoding="utf-8")
    out = tmp_path / "refs.bib"
    result = run_csl(str(lib), "-o", str(out), "--force")
    assert result.returncode == 0, result.stderr
    bib = out.read_text(encoding="utf-8")
    assert "@article{" in bib
    assert "author = {L. Wang}" in bib
    assert "title = {YAML Paper}" in bib


def test_yaml_multiple_authors(tmp_path):
    lib = tmp_path / "lib.yaml"
    lib.write_text("- type: paper-conference\n  id: z2022\n  title: DL\n"
                  "  author:\n    - family: Zhang\n      given: Q.\n"
                  "    - family: Chen\n      given: M.\n"
                  "  container-title: Proc. EX\n", encoding="utf-8")
    out = tmp_path / "refs.bib"
    run_csl(str(lib), "-o", str(out), "--force")
    bib = out.read_text(encoding="utf-8")
    assert "Q. Zhang and M. Chen" in bib
    assert "@inproceedings{" in bib


# ---------------------------------------------------------- project audit

def test_audit_rewrite_plan_without_flag(tmp_path):
    (tmp_path / "main.md").write_text("![a](img.png)\n", encoding="utf-8")
    (tmp_path / "img.png").touch()
    result = subprocess.run([sys.executable, str(AUDIT), str(tmp_path)],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=ENV, timeout=30, check=False)
    report = json.loads(result.stdout)
    assert report["rewrite_plan"] == []


def test_audit_rewrite_plan_reports_missing(tmp_path):
    (tmp_path / "main.md").write_text("![a](missing.png)\n", encoding="utf-8")
    result = subprocess.run([sys.executable, str(AUDIT), str(tmp_path), "--rewrite-plan"],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=ENV, timeout=30, check=False)
    report = json.loads(result.stdout)
    assert len(report["missing_or_outside_resources"]) == 1
    assert report["missing_or_outside_resources"][0]["path"] == "missing.png"
