import os
import ast
import subprocess
import sys
import tomllib
from pathlib import Path

from tools.validate_skills import skill_directories


ROOT = Path(__file__).resolve().parents[1]
PROJECT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def test_all_python_clis_support_help_and_version():
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    failures = []
    for skill in skill_directories(ROOT):
        for script in sorted((skill / "scripts").glob("*.py")):
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
                timeout=15,
                check=False,
            )
            if result.returncode != 0:
                failures.append(f"{script.relative_to(ROOT)}: exit {result.returncode}")
            version = subprocess.run(
                [sys.executable, str(script), "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
                timeout=15,
                check=False,
            )
            if version.returncode != 0 or PROJECT_VERSION not in version.stdout:
                failures.append(
                    f"{script.relative_to(ROOT)} --version: exit {version.returncode}, output={version.stdout!r}"
                )
    assert failures == []


def test_stat_help_version_and_adjust_do_not_require_site_packages():
    script = ROOT / "skills" / "data-analysis-assistant" / "scripts" / "stat_test.py"
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
    for args in (
        ("--help",),
        ("--version",),
        ("--test", "adjust", "--method", "holm", "--pvalues", "0.01,0.04"),
    ):
        result = subprocess.run(
            [sys.executable, "-S", str(script), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=15,
            check=False,
        )
        assert result.returncode == 0, result.stderr


def test_file_writing_clis_declare_force_for_overwrite():
    output_options = {"-o", "--out", "--artifact-out", "--manifest-out", "--dot", "--warnings", "--csv", "--overlay", "--report"}
    failures = []
    for skill in skill_directories(ROOT):
        for script in sorted((skill / "scripts").glob("*.py")):
            tree = ast.parse(script.read_text(encoding="utf-8"))
            declared = set()
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr != "add_argument":
                    continue
                declared.update(
                    arg.value for arg in node.args
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                )
            if declared & output_options and "--force" not in declared:
                failures.append(str(script.relative_to(ROOT)))
    assert failures == []


def test_manual_dump_and_export_clis_implement_force_guard():
    scripts = [
        ROOT / "skills" / "paper-writing-assistant" / "scripts" / "docx_text.py",
        ROOT / "skills" / "paper-writing-assistant" / "scripts" / "md_text.py",
        ROOT / "skills" / "reproduction-assistant" / "scripts" / "parse_deps.py",
    ]
    for script in scripts:
        assert '"--force"' in script.read_text(encoding="utf-8")


def test_invalid_cli_usage_is_nonzero_and_reports_on_stderr():
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
    failures = []
    for skill in skill_directories(ROOT):
        for script in sorted((skill / "scripts").glob("*.py")):
            result = subprocess.run(
                [sys.executable, str(script), "--definitely-invalid-option"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
                timeout=15,
                check=False,
            )
            if result.returncode == 0 or not result.stderr.strip():
                failures.append(
                    f"{script.relative_to(ROOT)}: exit={result.returncode}, stderr={result.stderr!r}"
                )
    assert failures == []
