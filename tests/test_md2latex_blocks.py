"""Tests for md2latex block-level extensions: footnotes, definition lists,
fenced-div theorem/proof environments, and regression for existing constructs.

Zero-dependency: invokes the converter via subprocess and asserts on the
generated .tex text.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "md2latex" / "scripts" / "md2latex.py"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def convert(md_text, tmp_path, **extra_args):
    src = tmp_path / "in.md"
    out = tmp_path / "out.tex"
    src.write_text(md_text, encoding="utf-8")
    cmd = [sys.executable, str(SCRIPT), str(src), "-o", str(out), "--force", *extra_args]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=ENV, timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    return out.read_text(encoding="utf-8")


# ---------------------------------------------------------------- footnotes

def test_footnote_rendered(tmp_path):
    tex = convert("Claim needs a note[^1].\n\n[^1]: The footnote text.\n", tmp_path)
    # script inserts ~ (LaTeX non-breaking space) between words inside \footnote{}
    assert r"\footnote{The~footnote~text.}" in tex
    # definition line must not appear as body text
    assert "[^1]" not in tex


def test_multiple_footnotes(tmp_path):
    tex = convert("A[^1] and B[^2].\n\n[^1]: First.\n[^2]: Second.\n", tmp_path)
    assert r"\footnote{First.}" in tex
    assert r"\footnote{Second.}" in tex


def test_undefined_footnote_left_literal(tmp_path):
    # [^missing] has no definition -> not treated as a footnote (no crash).
    # The "^" is a LaTeX special char so it gets escaped; the key property is
    # that no \footnote{} is emitted for the undefined id.
    tex = convert("See [^missing] for detail.\n", tmp_path)
    assert r"\footnote" not in tex
    assert "missing" in tex


def test_footnote_definition_removed_from_body(tmp_path):
    tex = convert("Body[^a].\n\n[^a]: Note.\n\nMore text.\n", tmp_path)
    # the definition line text should not appear as a paragraph
    lines = [l for l in tex.splitlines() if l.strip()]
    assert not any(l.strip() == "[^a]: Note." for l in lines)


# ------------------------------------------------------------- definition list

def test_definition_list_rendered(tmp_path):
    md = "Term\n:   Its definition.\n"
    tex = convert(md, tmp_path)
    assert r"\begin{description}" in tex
    assert r"\item[Term]" in tex
    assert "Its~definition." in tex  # ~ = LaTeX non-breaking space
    assert r"\end{description}" in tex


def test_multiple_definitions(tmp_path):
    md = "Apple\n:   A fruit.\n\nBanana\n:   Another fruit.\n"
    tex = convert(md, tmp_path)
    assert r"\item[Apple]" in tex
    assert r"\item[Banana]" in tex
    assert tex.count(r"\begin{description}") == 2


# ------------------------------------------------------------- fenced divs

def test_theorem_with_label(tmp_path):
    md = "::: {.theorem #thm:main}\nLet $x>0$. Then $x^2>0$.\n:::\n"
    tex = convert(md, tmp_path)
    assert r"\begin{theorem}" in tex
    assert r"\label{thm:main}" in tex
    assert r"\end{theorem}" in tex
    assert r"\usepackage{amsthm}" in tex


def test_proof_environment(tmp_path):
    tex = convert("::: proof\nFollows from axioms.\n:::\n", tmp_path)
    assert r"\begin{proof}" in tex
    assert r"\end{proof}" in tex


def test_bare_env_name(tmp_path):
    md = "::: lemma\nA useful lemma.\n:::\n"
    tex = convert(md, tmp_path)
    assert r"\begin{lemma}" in tex
    assert r"\end{lemma}" in tex


def test_custom_environment(tmp_path):
    # unknown env name still emitted as a generic environment
    md = "::: {.note}\nSomething to note.\n:::\n"
    tex = convert(md, tmp_path)
    assert r"\begin{note}" in tex
    assert r"\end{note}" in tex


def test_fenced_div_missing_closer_tolerated(tmp_path):
    # no closing ::: -> body runs to EOF, should not crash
    md = "::: {.remark\nThis remark never closes.\n"
    tex = convert(md, tmp_path)
    assert r"\begin{remark}" in tex


# ------------------------------------------------------------- regression

def test_existing_heading_table_unchanged(tmp_path):
    md = "# Title\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"
    tex = convert(md, tmp_path)
    assert r"\section{Title}" in tex
    assert r"\toprule" in tex
    # no spurious packages
    assert "amsthm" not in tex
    assert "description" not in tex


def test_footnote_in_table_header(tmp_path):
    md = "| Col[^1] |\n|---|\n| x |\n\n[^1]: A column note.\n"
    tex = convert(md, tmp_path)
    assert r"\footnote{A~column~note.}" in tex
