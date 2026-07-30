#!/usr/bin/env python3
"""End-to-end test harness for the md2latex Markdown -> TeX pipeline.

Two modes:

* ``--self-test`` runs a built-in suite of smoke conversions (heading, list,
  table, math, figure, footnote, theorem, definition list, cross-ref) and
  asserts the generated ``.tex`` contains the expected LaTeX constructs.
  Works WITHOUT a LaTeX toolchain.
* ``--fixtures <dir>`` reads ``<stem>.md`` / ``<stem>.expected.tex`` pairs from
  a directory, runs the converter, and diffs the output against the expected
  ``.tex``. With ``--compile`` (and a detected ``xelatex``/``pdflatex``) it
  also attempts compilation and reports ``passed``/``failed``/``unavailable``.

Zero dependencies (Python stdlib only). Deterministic. Outputs a JSON report
with ``schema_version``/``artifact_type``/``tool_version``/``warnings``.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


VERSION = "0.1.0"
SCRIPT = Path(__file__).resolve().parent / "md2latex.py"
ENV = {"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}

# ---------------------------------------------------------- self-test fixtures

SELF_TEST_FIXTURES: list[tuple[str, str, list[str]]] = [
    ("heading", "# Introduction\n", [r"\section{Introduction}"]),
    ("list", "- a\n- b\n- c\n", [r"\begin{itemize}", r"\item a", r"\end{itemize}"]),
    ("table", "| A | B |\n|---|---|\n| 1 | 2 |\n",
     [r"\begin{table}", r"\toprule", r"\end{tabularx}", r"\end{table}"]),
    ("math", "Display:\n\n$$\na^2 + b^2 = c^2\n$$\n",
     [r"\begin{equation}", r"a^2 + b^2 = c^2", r"\end{equation}"]),
    ("figure", "![Result](result.pdf)\n",
     [r"\begin{figure}", r"\includegraphics", r"\label{fig:result}", r"\end{figure}"]),
    ("footnote", "Claim[^1].\n\n[^1]: A note.\n",
     [r"\footnote{A~note.}"]),  # ~ = LaTeX non-breaking space
    ("theorem", "::: {.theorem #thm:pyth}\n$a^2+b^2=c^2$.\n:::\n",
     [r"\begin{theorem}", r"\label{thm:pyth}", r"\end{theorem}", r"\usepackage{amsthm}"]),
    ("definition_list", "Term\n:   Definition.\n",
     [r"\begin{description}", r"\item[Term]", r"\end{description}"]),
    ("cross_ref", "See [@sec:methods].\n",
     [r"\ref{sec:methods}"]),
]


def detect_latex_compiler() -> str | None:
    for compiler in ("xelatex", "pdflatex"):
        if shutil.which(compiler):
            return compiler
    return None


def run_md2latex(src: Path, out: Path, extra_args: list[str],
                 compile_flag: bool = False) -> dict:
    """Invoke md2latex.py and return its JSON report plus raw stdout/stderr."""
    cmd = [sys.executable, str(SCRIPT), str(src), "-o", str(out), "--force"]
    if compile_flag:
        cmd.append("--compile")
    cmd.extend(extra_args)
    env = {**os.environ, **ENV}
    started = time.time()
    run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", env=env, timeout=120, check=False)
    duration = time.time() - started
    report: dict = {"returncode": run.returncode, "duration": duration}
    try:
        report["json"] = json.loads(run.stdout)
    except (json.JSONDecodeError, ValueError):
        report["json"] = None
    report["stdout"] = run.stdout
    report["stderr"] = run.stderr
    return report


def run_self_test(compile_flag: bool) -> dict:
    results = []
    overall_ok = True
    with tempfile.TemporaryDirectory(prefix="md2latex_e2e_") as tmp_name:
        tmp = Path(tmp_name)
        for name, md_text, expected_fragments in SELF_TEST_FIXTURES:
            src = tmp / f"{name}.md"
            out = tmp / f"{name}.tex"
            src.write_text(md_text, encoding="utf-8")
            extra = ["--cross-ref"] if name == "cross_ref" else []
            info = run_md2latex(src, out, extra, compile_flag=compile_flag)
            tex = out.read_text(encoding="utf-8") if out.exists() else ""
            missing = [frag for frag in expected_fragments if frag not in tex]
            ok = info["returncode"] == 0 and not missing
            overall_ok = overall_ok and ok
            results.append({
                "fixture": name,
                "ok": ok,
                "returncode": info["returncode"],
                "missing_fragments": missing,
                "compile": info.get("json", {}).get("compile") if info.get("json") else None,
            })
    return {
        "mode": "self-test",
        "ok": overall_ok,
        "fixtures": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["ok"]),
            "failed": sum(1 for r in results if not r["ok"]),
        },
    }


def run_fixtures(fixtures_dir: Path, compile_flag: bool) -> dict:
    md_files = sorted(fixtures_dir.glob("*.md"))
    if not md_files:
        return {"mode": "fixtures", "ok": False,
                "error": f"no .md fixtures in {fixtures_dir}", "fixtures": []}
    results = []
    overall_ok = True
    with tempfile.TemporaryDirectory(prefix="md2latex_e2e_") as tmp_name:
        tmp = Path(tmp_name)
        for md in md_files:
            expected = md.with_suffix(".expected.tex")
            if not expected.exists():
                results.append({"fixture": md.stem, "ok": False,
                                "error": f"missing {expected.name}"})
                overall_ok = False
                continue
            out = tmp / md.with_suffix(".tex").name
            info = run_md2latex(md, out, [], compile_flag=compile_flag)
            actual = out.read_text(encoding="utf-8") if out.exists() else ""
            expected_text = expected.read_text(encoding="utf-8")
            if actual == expected_text:
                diff = []
                match = True
            else:
                match = False
                diff = list(difflib.unified_diff(
                    expected_text.splitlines(), actual.splitlines(),
                    fromfile=f"expected/{expected.name}", tofile=f"actual/{out.name}",
                    lineterm=""))
            ok = info["returncode"] == 0 and match
            overall_ok = overall_ok and ok
            results.append({
                "fixture": md.stem, "ok": ok, "returncode": info["returncode"],
                "match": match, "diff": diff,
                "compile": info.get("json", {}).get("compile") if info.get("json") else None,
            })
    return {
        "mode": "fixtures",
        "ok": overall_ok,
        "fixtures": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["ok"]),
            "failed": sum(1 for r in results if not r["ok"]),
        },
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--self-test", action="store_true",
                   help="run built-in smoke conversions (no LaTeX required)")
    p.add_argument("--fixtures", type=Path, metavar="DIR",
                   help="directory of <stem>.md + <stem>.expected.tex pairs")
    p.add_argument("--compile", action="store_true",
                   help="attempt LaTeX compilation when a toolchain is available")
    p.add_argument("--out", type=Path,
                   help="write the JSON report here (default: stdout only)")
    p.add_argument("--force", action="store_true",
                   help="replace an existing --out file")
    args = p.parse_args(argv)
    if not args.self_test and not args.fixtures:
        p.error("either --self-test or --fixtures DIR is required")
    if args.self_test and args.fixtures:
        p.error("--self-test and --fixtures are mutually exclusive")

    warnings: list[str] = []
    if args.compile:
        compiler = detect_latex_compiler()
        if compiler is None:
            warnings.append(
                "no LaTeX toolchain (xelatex/pdflatex) on PATH; "
                "--compile will report 'unavailable' per fixture")

    if args.self_test:
        report = run_self_test(args.compile)
    else:
        if not args.fixtures.is_dir():
            p.error(f"--fixtures must be a directory: {args.fixtures}")
        report = run_fixtures(args.fixtures, args.compile)

    report["compile_requested"] = bool(args.compile)
    report["latex_compiler"] = detect_latex_compiler() if args.compile else None
    if warnings:
        report.setdefault("warnings", []).extend(warnings)

    artifact = {
        "schema_version": "1.0.0",
        "artifact_type": "md2latex-e2e-test",
        "tool_version": VERSION,
        "ok": report.get("ok", False),
        "report": report,
        "warnings": report.get("warnings", []),
    }
    payload = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    sys.stdout.write(payload)
    if args.out:
        out = args.out
        if out.exists() and not args.force:
            print(f"error: output exists: {out}; use --force to replace it",
                  file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(f"written: {out}", file=sys.stderr)
    return 0 if report.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
