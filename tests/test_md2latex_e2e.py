"""Tests for md2latex/scripts/md2latex_e2e_test.py — the end-to-end test
harness for the Markdown -> TeX pipeline.

Covers:
1. --self-test runs built-in smoke conversions and checks expected LaTeX
   constructs in the output (no LaTeX install needed).
2. --fixtures matches expected .tex for a simple fixture.
3. --compile with no LaTeX installed reports "unavailable" (not an error).
4. --compile with LaTeX (if present) reports passed/failed.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "md2latex" / "scripts" / "md2latex_e2e_test.py"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run_e2e(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=ENV, timeout=120, check=False,
    )


def test_self_test_passes_without_latex(tmp_path):
    out = tmp_path / "report.json"
    result = run_e2e("--self-test", "--out", str(out), "--force")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == "1.0.0"
    assert artifact["artifact_type"] == "md2latex-e2e-test"
    assert artifact["tool_version"]
    report = artifact["report"]
    assert report["mode"] == "self-test"
    assert report["ok"] is True
    assert report["summary"]["total"] >= 9
    assert report["summary"]["passed"] == report["summary"]["total"]
    assert report["summary"]["failed"] == 0
    # every fixture must have run and reported ok=True
    for fixture in report["fixtures"]:
        assert fixture["ok"] is True, fixture
        assert fixture["missing_fragments"] == [], fixture


def test_fixtures_mode_matches_expected(tmp_path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    md = fixtures / "simple.md"
    expected = fixtures / "simple.expected.tex"
    md.write_text("# Title\n\nSome text.\n", encoding="utf-8")
    # run the converter once to get the actual expected output
    conv = ROOT / "skills" / "md2latex" / "scripts" / "md2latex.py"
    out_tex = tmp_path / "probe.tex"
    subprocess.run(
        [sys.executable, str(conv), str(md), "-o", str(out_tex), "--force"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=ENV, timeout=30, check=True,
    )
    expected.write_text(out_tex.read_text(encoding="utf-8"), encoding="utf-8")

    out = tmp_path / "report.json"
    result = run_e2e("--fixtures", str(fixtures), "--out", str(out), "--force")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    report = artifact["report"]
    assert report["mode"] == "fixtures"
    assert report["ok"] is True
    assert report["summary"]["total"] == 1
    assert report["summary"]["passed"] == 1
    fixture_report = report["fixtures"][0]
    assert fixture_report["fixture"] == "simple"
    assert fixture_report["match"] is True
    assert fixture_report["diff"] == []


def test_fixtures_mode_reports_mismatch(tmp_path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    md = fixtures / "broken.md"
    expected = fixtures / "broken.expected.tex"
    md.write_text("# Real Title\n", encoding="utf-8")
    expected.write_text("% intentionally wrong expected output\n", encoding="utf-8")

    out = tmp_path / "report.json"
    result = run_e2e("--fixtures", str(fixtures), "--out", str(out), "--force")
    assert result.returncode != 0
    artifact = json.loads(out.read_text(encoding="utf-8"))
    report = artifact["report"]
    assert report["ok"] is False
    assert report["summary"]["failed"] == 1
    fixture_report = report["fixtures"][0]
    assert fixture_report["match"] is False
    assert fixture_report["diff"]  # non-empty diff


def test_compile_without_latex_reports_unavailable(tmp_path):
    # Force the "no LaTeX" branch by ensuring neither xelatex nor pdflatex is
    # on PATH for this subprocess. We do that by overriding PATH to a custom
    # empty-ish directory containing only the essentials.
    empty_bin = tmp_path / "empty_bin"
    empty_bin.mkdir()
    # Windows: keep System32 so python still works; remove typical LaTeX dirs.
    custom_path = str(empty_bin)
    if sys.platform == "win32":
        # On Windows we need at least the system DLL directory; use a minimal
        # PATH that excludes common LaTeX install roots.
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        custom_path = os.pathsep.join([str(empty_bin),
                                      os.path.join(system_root, "System32")])
    env = {**ENV, "PATH": custom_path}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--self-test", "--compile"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=120, check=False,
    )
    # self-test conversion itself passes; compile is unavailable
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout)
    report = artifact["report"]
    assert report["compile_requested"] is True
    assert report["latex_compiler"] is None
    # warning about missing toolchain
    assert any("no LaTeX toolchain" in w for w in report.get("warnings", []))
    # every fixture's compile status is "unavailable"
    for fixture in report["fixtures"]:
        assert fixture["compile"]["status"] == "unavailable"


def test_compile_with_latex_if_present(tmp_path):
    # Skip (do not fail) if no LaTeX toolchain is installed.
    has_latex = shutil.which("xelatex") or shutil.which("pdflatex")
    if not has_latex:
        pytest.skip("no LaTeX toolchain (xelatex/pdflatex) on PATH")
    out = tmp_path / "report.json"
    result = run_e2e("--self-test", "--compile", "--out", str(out), "--force")
    # We don't assert returncode: compilation may fail on some fixtures (e.g.
    # cross-ref-only body without a full document). We DO assert the report
    # structure is correct and compile status is one of the allowed values.
    artifact = json.loads(out.read_text(encoding="utf-8"))
    report = artifact["report"]
    assert report["compile_requested"] is True
    assert report["latex_compiler"] in {"xelatex", "pdflatex"}
    for fixture in report["fixtures"]:
        assert fixture["compile"]["status"] in {"passed", "failed", "unavailable"}


def test_version_flag():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--version"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=ENV, timeout=10, check=False,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_output_protected(tmp_path):
    out = tmp_path / "report.json"
    out.write_text("sentinel", encoding="utf-8")
    result = run_e2e("--self-test", "--out", str(out))
    assert result.returncode != 0
    assert out.read_text(encoding="utf-8") == "sentinel"
