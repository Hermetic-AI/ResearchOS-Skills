#!/usr/bin/env python3
"""Profile a paper's code repository for reproduction planning (zero-dependency).

Purpose
    Scan a cloned repository and emit a structural profile that feeds the
    `analyze` step of the reproduction pipeline:
      - entry-point candidates (Python, R, Julia, MATLAB/Octave, Make, shell)
      - dependency manifests found (which files, not their contents)
      - config files (yaml/json/toml/cfg under config-like names)
      - data directory references (dir names and path strings that look like datasets)
      - run commands extracted from README code blocks (best-effort heuristics)

Dependencies
    Python 3 standard library only. No third-party packages, no randomness.

CLI
    python3 repo_probe.py <repo_dir> [--pretty] [--readme-max-bytes 200000]

Output (JSON to stdout)
    {
      "repo_dir": "...",
      "runtime_hints":       [{"runtime": "R", "evidence": "renv.lock"}, ...],
      "dependency_manifests": ["requirements.txt", ...],
      "config_files":       ["configs/base.yaml", ...],
      "data_references":    [{"path": "data/", "kind": "directory"}, ...],
      "readme_commands":    [{"file": "README.md", "command": "python train.py ..."}, ...],
      "notes":              ["..."]
    }
    Entries are ordered by heuristic confidence; verify by reading before use.

This tool only *suggests*. Per pipeline.md step 2, a human/agent must read the
README and the entry script itself before trusting any candidate.
"""

import json
import re
import sys
from pathlib import Path

ENTRY_NAMES = {
    "train.py", "main.py", "run.py", "eval.py", "evaluate.py", "test.py",
    "train_val.py", "finetune.py", "pretrain.py",
}
NON_PYTHON_ENTRY_SUFFIXES = {".r": "R script", ".jl": "Julia script", ".m": "MATLAB/Octave script"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env",
             ".tox", ".mypy_cache", "dist", "build", "egg-info"}
MANIFEST_NAMES = {
    "requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.py",
    "setup.cfg", "environment.yml", "environment.yaml", "Pipfile",
    "Pipfile.lock", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "Makefile", "tox.ini", "poetry.lock", "uv.lock", "flake.nix", "shell.nix",
    "renv.lock", "DESCRIPTION", "Project.toml", "Manifest.toml", "JuliaProject.toml",
    "JuliaManifest.toml", "startup.m", "matlab.prj",
}
CONFIG_EXT = {".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"}
DATA_HINT = re.compile(r"^(data|datasets?|corpus|images?|raw|input|inputs)$", re.I)
CODE_FENCE = re.compile(r"```(?:bash|sh|shell|console|zsh)?\s*\n(.*?)```", re.S)
CMD_START = re.compile(r"^(?:\$\s*)?(python\d?(?:\.\d+)?|torchrun|accelerate\s+launch|"
                       r"deepspeed|make|bash|sh|\.?/?[\w\-./]+\.sh|docker|conda|pip|npm|"
                       r"uv|poetry|nix(?:\s+develop)?|Rscript|R\s+CMD|julia|matlab|octave)\b",
                       re.I)


def walk(root):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in rel.parts):
            continue
        yield p, rel


def find_entries(root, files):
    out = []
    for p, rel in files:
        if p.is_dir():
            continue
        name = p.name
        if name in ENTRY_NAMES:
            out.append({"path": str(rel), "why": "well-known entry filename"})
        elif name in ("Makefile",) or (name.endswith(".sh") and len(rel.parts) <= 2):
            out.append({"path": str(rel), "why": "build/run script"})
        elif p.suffix.lower() in NON_PYTHON_ENTRY_SUFFIXES and len(rel.parts) <= 2:
            out.append({"path": str(rel), "why": NON_PYTHON_ENTRY_SUFFIXES[p.suffix.lower()]})
    return out


def find_manifests(files):
    return [str(rel) for p, rel in files
            if p.is_file() and (p.name in MANIFEST_NAMES or p.name.startswith("requirements"))]


def find_runtime_hints(files):
    """Return evidence-based runtime hints; never infer an executable command."""
    evidence = {
        "Docker": {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"},
        "Nix": {"flake.nix", "shell.nix"},
        "Poetry": {"poetry.lock"}, "uv": {"uv.lock"},
        "R": {"renv.lock", "DESCRIPTION"},
        "Julia": {"Project.toml", "Manifest.toml", "JuliaProject.toml", "JuliaManifest.toml"},
        "MATLAB/Octave": {"startup.m", "matlab.prj"},
    }
    names = {p.name for p, _ in files if p.is_file()}
    return [
        {"runtime": runtime, "evidence": marker}
        for runtime, markers in evidence.items()
        for marker in sorted(markers & names)
    ]


def find_configs(files):
    return [rel.as_posix() for p, rel in files
            if p.is_file() and p.suffix.lower() in CONFIG_EXT
            and ("config" in str(rel).lower() or len(rel.parts) <= 1)]


def find_data_refs(root, files):
    refs = []
    for p, rel in files:
        if p.is_dir() and DATA_HINT.match(p.name):
            refs.append({"path": str(rel) + "/", "kind": "directory"})
    # path-like strings inside README and shell/python entry files
    for p, rel in files:
        if p.is_file() and p.name.lower() in ("readme.md", "readme.rst", "readme.txt", "readme"):
            for m in re.finditer(r"([\w\-./]*(?:data|datasets?)/[\w\-./]+)",
                                 p.read_text(encoding="utf-8", errors="replace")):
                refs.append({"path": m.group(1), "kind": f"referenced in {rel}"})
    seen, out = set(), []
    for r in refs:
        if r["path"] not in seen:
            seen.add(r["path"])
            out.append(r)
    return out[:30]


def extract_readme_commands(root, files, max_bytes):
    cmds = []
    for p, rel in files:
        if not (p.is_file() and p.name.lower().startswith("readme")):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")[:max_bytes]
        for block in CODE_FENCE.findall(text):
            for line in block.splitlines():
                line = line.strip()
                if CMD_START.match(line) and not line.startswith(("pip install", "conda install")):
                    cmds.append({"file": str(rel), "command": line})
        # also bare "$ python ..." lines outside fences
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("$ ") and CMD_START.match(s) and len(s) > 8:
                cmds.append({"file": str(rel), "command": s})
    seen, out = set(), []
    for c in cmds:
        if c["command"] not in seen:
            seen.add(c["command"])
            out.append(c)
    return out[:40]


def main(argv):
    if "--version" in argv[1:]:
        print("repo_probe.py 0.1.0")
        return 0
    if len(argv) >= 2 and argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if len(argv) < 2:
        print("error: provide a repository directory; use --help for usage", file=sys.stderr)
        return 2
    repo = Path(argv[1])
    pretty = "--pretty" in argv[2:]
    max_bytes = 200_000
    if "--readme-max-bytes" in argv:
        i = argv.index("--readme-max-bytes")
        if i + 1 >= len(argv):
            print("error: --readme-max-bytes requires a value", file=sys.stderr)
            return 2
        max_bytes = int(argv[i + 1])
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2

    files = [(p, rel) for p, rel in walk(repo) if len(rel.parts) <= 4]
    notes = []
    result = {
        "repo_dir": str(repo),
        "entry_candidates": find_entries(repo, files),
        "dependency_manifests": find_manifests(files),
        "runtime_hints": find_runtime_hints(files),
        "config_files": find_configs(files)[:40],
        "data_references": find_data_refs(repo, files),
        "readme_commands": extract_readme_commands(repo, files, max_bytes),
        "notes": notes,
    }
    if not result["dependency_manifests"]:
        notes.append("no dependency manifest found — deps must be inferred from imports/CI")
    if not result["entry_candidates"] and not result["readme_commands"]:
        notes.append("no entry point candidates — read the README/paper manually")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
