"""Tests for md2latex cross-references, image attributes, longtable, and
merged cells."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "md2latex" / "scripts" / "md2latex.py"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def convert(md_text, tmp_path, *flags):
    src = tmp_path / "in.md"
    out = tmp_path / "out.tex"
    src.write_text(md_text, encoding="utf-8")
    cmd = [sys.executable, str(SCRIPT), str(src), "-o", str(out), "--force", *flags]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=ENV, timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    return out.read_text(encoding="utf-8")


# ------------------------------------------------------------- cross-references

def test_heading_gets_label(tmp_path):
    tex = convert("# Hello World\n", tmp_path, "--cross-ref")
    assert r"\label{sec:hello-world}" in tex


def test_cross_ref_rendered(tmp_path):
    tex = convert("See [@sec:methods].\n", tmp_path, "--cross-ref")
    assert r"\ref{sec:methods}" in tex
    # must not be treated as a citation
    assert r"\cite" not in tex


def test_figure_cross_ref(tmp_path):
    tex = convert("As shown in [@fig:result].\n", tmp_path, "--cross-ref")
    assert r"\ref{fig:result}" in tex


def test_cross_ref_disabled_by_default(tmp_path):
    tex = convert("See [@sec:methods].\n", tmp_path)
    # without --cross-ref, [@sec:methods] is treated as a citation
    assert r"\cite{sec:methods}" in tex
    assert r"\ref" not in tex


def test_figure_autolabel(tmp_path):
    tex = convert("![Result](r.png)\n", tmp_path)
    assert r"\label{fig:result}" in tex


# ------------------------------------------------------------- image attributes

def test_image_with_width_attribute(tmp_path):
    tex = convert("![Chart](chart.pdf){width=0.6\\textwidth}\n", tmp_path)
    assert r"\includegraphics[width=0.6\textwidth]{chart.pdf}" in tex


def test_image_with_multiple_attributes(tmp_path):
    tex = convert("![Chart](c.pdf){width=5cm height=3cm}\n", tmp_path)
    assert "width=5cm" in tex
    assert "height=3cm" in tex


def test_image_without_attributes_keeps_default(tmp_path):
    tex = convert("![Chart](c.pdf)\n", tmp_path)
    assert r"\includegraphics[width=0.8\linewidth]{c.pdf}" in tex


# --------------------------------------------------------------- longtable

def test_longtable_environment(tmp_path):
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    tex = convert(md, tmp_path, "--long-table")
    assert r"\begin{longtable}" in tex
    assert r"\end{longtable}" in tex
    assert r"\usepackage{longtable}" in tex
    # longtable is not a float
    assert r"\begin{table}" not in tex


def test_longtable_repeats_header(tmp_path):
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    tex = convert(md, tmp_path, "--long-table")
    # header repeated in \endhead for page continuation
    assert r"\endfirsthead" in tex
    assert r"\endhead" in tex


def test_float_table_is_default(tmp_path):
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    tex = convert(md, tmp_path)
    assert r"\begin{table}" in tex
    assert "longtable" not in tex


# ------------------------------------------------------------- merged cells

def test_multicolumn_passthrough(tmp_path):
    md = "| A | B |\n|---|---|\n| \\multicolumn{2}{c}{X} |\n"
    tex = convert(md, tmp_path)
    assert r"\multicolumn{2}{c}{X}" in tex


def test_multirow_passthrough(tmp_path):
    md = "| A | B |\n|---|---|\n| \\multirow{2}{*}{X} | y |\n"
    tex = convert(md, tmp_path)
    assert r"\multirow{2}{*}{X}" in tex
    assert r"\usepackage{multirow}" in tex
