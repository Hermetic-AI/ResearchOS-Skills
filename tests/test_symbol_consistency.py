"""Tests for the --symbols flag of paper-writing-assistant/scripts/consistency_audit.py."""
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "paper-writing-assistant" / "scripts" / "consistency_audit.py"
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


def write_tex(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_newcommand_used_is_not_flagged(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\newcommand{\\loss}{L}\n"
        "\\begin{document}\n"
        "The loss $\\loss$ is defined.\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "used.tex", src)
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    symbols = report["symbols"]
    assert "loss" in symbols["defined_commands"]
    assert "loss" not in symbols["unused_commands"]
    assert "loss" not in symbols["undefined_commands_used"]


def test_newcommand_unused_is_reported(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\newcommand{\\loss}{L}\n"
        "\\newcommand{\\unusedsym}{U}\n"
        "\\begin{document}\n"
        "The loss $\\loss$ is defined.\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "unused.tex", src)
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    symbols = report["symbols"]
    assert "unusedsym" in symbols["defined_commands"]
    assert "unusedsym" in symbols["unused_commands"]
    assert "loss" not in symbols["unused_commands"]


def test_undefined_command_is_reported(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "Use $\\mycustom$ here.\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "undef.tex", src)
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    symbols = report["symbols"]
    assert "mycustom" in symbols["undefined_commands_used"]
    assert "mycustom" not in symbols["defined_commands"]


def test_builtin_commands_not_flagged(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "See \\cite{foo} and $\\alpha + \\beta = \\ref{eq:x}$.\n"
        "\\begin{equation}\n"
        "  \\label{eq:x}\n"
        "  \\sum_{i} \\int f\n"
        "\\end{equation}\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "builtin.tex", src)
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    symbols = report["symbols"]
    for builtin in ("cite", "ref", "alpha", "beta", "label", "eq", "sum", "int"):
        assert builtin not in symbols["undefined_commands_used"], builtin


def test_equation_ref_and_label_consistency(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "\\begin{equation}\n"
        "  \\label{eq:foo}\n"
        "  a = b\n"
        "\\end{equation}\n"
        "See \\eqref{eq:foo} and \\eqref{eq:missing}.\n"
        "\\begin{equation}\n"
        "  \\label{eq:bar}\n"
        "  c = d\n"
        "\\end{equation}\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "eq.tex", src)
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    symbols = report["symbols"]
    assert "foo" in symbols["equation_labels"]
    assert "bar" in symbols["equation_labels"]
    assert "foo" in symbols["equation_refs"]
    assert "missing" in symbols["equation_refs"]
    assert "missing" in symbols["dangling_equation_refs"]
    assert "foo" not in symbols["dangling_equation_refs"]
    assert "bar" in symbols["unused_equation_labels"]
    assert "foo" not in symbols["unused_equation_labels"]


def test_notation_variants_detected(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "$\\mathbf{x}$ is a vector.\n"
        "Let $\\vec{x}$ denote the same.\n"
        "$y$ is plain.\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "not.tex", src)
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    symbols = report["symbols"]
    variants = symbols["notation_variants"]
    assert isinstance(variants, list)
    match = next((v for v in variants if v["variable"] == "x"), None)
    assert match is not None, variants
    assert "\\mathbf{x}" in match["forms"]
    assert "\\vec{x}" in match["forms"]
    # line numbers should be present and non-empty
    assert match["locations"]
    # y has only one form -> not a variant
    assert not any(v["variable"] == "y" for v in variants)


def test_no_symbols_flag_backward_compat(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\newcommand{\\loss}{L}\n"
        "\\begin{document}\n"
        "The loss $\\loss$ is defined and \\mycustom too.\n"
        "\\end{document}\n"
    )
    path = write_tex(tmp_path, "compat.tex", src)
    r = run_cli(str(path))
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    assert "symbols" not in report
    # existing findings still present
    assert "findings" in report
    assert "labels" in report["findings"]


def test_markdown_symbols_empty(tmp_path):
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\nSome text with ABC.\n", encoding="utf-8")
    r = run_cli(str(path), "--symbols")
    assert r.returncode == 0, r.stderr
    report = json.loads(r.stdout)
    assert report["symbols"] == {}
    # markdown findings still present
    assert "findings" in report
    assert "abbreviations_used" in report["findings"]
