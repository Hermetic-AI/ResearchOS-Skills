#!/usr/bin/env python3
"""Parse Python dependency manifests into one unified dependency list (JSON).

Purpose
    Scan a repository directory for dependency declarations and emit a
    normalized manifest. Supported sources:
      - requirements*.txt   (pip requirement specifiers, one per line)
      - pyproject.toml      (PEP 621: [project] dependencies + optional-dependencies)
      - setup.cfg           ([options] install_requires / extras_require)
      - setup.py            (regex-extracted install_requires=[...] list)
      - Pipfile             ([packages] / [dev-packages], line-based)
      - environment.yml     (conda: name, dependencies incl. nested pip section)

    Native environment evidence is reported but not parsed: Poetry/uv locks,
    Nix, R, Julia, MATLAB/Octave, Docker and Make. Review those files with
    their native tooling; this script never executes package managers.

    Each entry is tagged with the file it came from, so conflicts between
    sources are visible instead of silently merged.

Dependencies
    Python 3.11+ (uses stdlib tomllib). No third-party packages.

CLI
    python3 parse_deps.py <repo_dir> [--pretty] [--export requirements.txt] [--force]

    --export PATH  additionally writes a pip-installable requirements.txt
    to PATH: one "name<specifier>" per dependency (duplicates merged by
    first-seen specifier; conflicts still reported in JSON, not resolved).
    Existing exports are protected unless --force is explicit.

Output (JSON to stdout)
    {
      "repo_dir": "...",
      "sources_found": ["requirements.txt", ...],
      "python_requires": "...",          // from PEP 621 if present, else null
      "conda_env_name": "...",           // from environment.yml if present, else null
      "dependencies": [
        {"name": "torch", "specifier": ">=2.0", "extras": [],
         "source": "requirements.txt", "kind": "pip"},
        ...
      ],
      "conflicts": [                     // same name, differing specifiers across entries
        {"name": "torch", "specifiers": [{"specifier": ">=2.0", "source": "..."}]}
      ]
    }
"""

import json
import re
import sys
import tomllib
from pathlib import Path

NAME_FROM_SPEC = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(\[[^\]]*\])?\s*(.*)$")

ENVIRONMENT_EVIDENCE = {
    "poetry.lock": "Poetry", "uv.lock": "uv", "flake.nix": "Nix",
    "shell.nix": "Nix", "renv.lock": "R", "DESCRIPTION": "R",
    "Project.toml": "Julia", "Manifest.toml": "Julia", "startup.m": "MATLAB/Octave",
    "matlab.prj": "MATLAB", "Dockerfile": "Docker", "Makefile": "Make",
}


def norm_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirement_line(line):
    """Parse one PEP 508-ish line into (name, extras, specifier)."""
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith(("-", "git+", "http://", "https://")):
        return None
    line = line.split(";", 1)[0].strip()  # drop environment markers
    m = NAME_FROM_SPEC.match(line)
    if not m:
        return None
    name, extras, spec = m.group(1), m.group(2), m.group(3).strip()
    extras = [e.strip() for e in extras[1:-1].split(",")] if extras else []
    if spec and not spec.startswith(("=", ">", "<", "!", "~", "(")):
        return None
    return name, extras, spec.strip("() ")


def entry(name, extras, specifier, source, kind):
    return {
        "name": norm_name(name),
        "specifier": specifier or "",
        "extras": extras,
        "source": source,
        "kind": kind,
    }


def parse_requirements_txt(path):
    out = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parsed = parse_requirement_line(raw)
        if parsed:
            name, extras, spec = parsed
            out.append(entry(name, extras, spec, path.name, "pip"))
    return out


def parse_pyproject(path):
    data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    project = data.get("project", {})
    deps, python_requires = [], project.get("requires-python")
    for raw in project.get("dependencies", []):
        parsed = parse_requirement_line(raw)
        if parsed:
            name, extras, spec = parsed
            deps.append(entry(name, extras, spec, path.name, "pip"))
    for group, items in project.get("optional-dependencies", {}).items():
        for raw in items:
            parsed = parse_requirement_line(raw)
            if parsed:
                name, extras, spec = parsed
                e = entry(name, extras, spec, f"{path.name} [optional:{group}]", "pip")
                deps.append(e)
    return deps, python_requires


def parse_setup_cfg(path):
    """Parse [options] install_requires / extras_require from setup.cfg (stdlib configparser; tolerant of odd lines)."""
    import configparser

    cfg = configparser.ConfigParser()
    try:
        cfg.read_string(path.read_text(encoding="utf-8", errors="replace"))
    except configparser.Error:
        return []
    deps = []
    for raw in cfg.get("options", "install_requires", fallback="").splitlines():
        parsed = parse_requirement_line(raw)
        if parsed:
            name, extras, spec = parsed
            deps.append(entry(name, extras, spec, path.name, "pip"))
    if cfg.has_section("options.extras_require"):
        for group in cfg.options("options.extras_require"):
            for raw in cfg.get("options.extras_require", group).splitlines():
                parsed = parse_requirement_line(raw)
                if parsed:
                    name, extras, spec = parsed
                    deps.append(entry(name, extras, spec, f"{path.name} [extra:{group}]", "pip"))
    return deps


def parse_setup_py(path):
    """Best-effort regex extraction of install_requires=[...] from setup.py.

    setup.py is executable code; we do NOT execute it. Only literal string
    items inside the first install_requires = [...] block are captured.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"install_requires\s*=\s*\[(.*?)\]", text, re.S)
    if not m:
        return []
    deps = []
    for raw in re.findall(r"""['"]([^'"]+)['"]""", m.group(1)):
        parsed = parse_requirement_line(raw)
        if parsed:
            name, extras, spec = parsed
            deps.append(entry(name, extras, spec, path.name, "pip"))
    return deps


PIPLINE = re.compile(r"""^([A-Za-z0-9_.\-]+)\s*=\s*(?:['"]([^'"]*)['"]|\{(.*)\})\s*$""")


def parse_pipfile(path):
    """Line-based parse of Pipfile [packages]/[dev-packages] (no toml dep)."""
    deps, section = [], None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]").strip().lower()
            continue
        if section not in ("packages", "dev-packages") or not line or line.startswith("#"):
            continue
        m = PIPLINE.match(line)
        if not m:
            continue
        name, ver, inline = m.group(1), m.group(2), m.group(3)
        if inline is not None:  # {version = "==1.0", ...} or {git = ...}
            vm = re.search(r"""version\s*=\s*['"]([^'"]+)['"]""", inline)
            ver = vm.group(1) if vm else ""
        spec = "" if ver in ("*", None) else ver
        if spec and not spec.startswith(("=", ">", "<", "!", "~")):
            spec = f"=={spec}"
        src = path.name if section == "packages" else f"{path.name} [dev-packages]"
        deps.append(entry(name, [], spec, src, "pip"))
    return deps


def parse_environment_yml(path):
    """Minimal line-based parse of conda environment.yml (no yaml dependency)."""
    deps, env_name, in_deps, in_pip = [], None, False, False
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line, stripped = raw, raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0 and stripped.startswith("name:"):
            env_name = stripped.split(":", 1)[1].strip()
        elif indent == 0:
            in_deps = stripped.startswith("dependencies:")
            in_pip = False
        elif in_deps and stripped.startswith("- pip:"):
            in_pip = True
        elif in_deps and stripped.startswith("- "):
            item = stripped[2:].strip()
            if in_pip and indent > 2:
                parsed = parse_requirement_line(item)
                if parsed:
                    name, extras, spec = parsed
                    deps.append(entry(name, extras, spec, path.name, "pip"))
            else:
                # back at conda-dependency indent: pip section (if any) is over
                in_pip = False
                # conda spec: "numpy=1.24" or "python=3.10" or plain "scipy"
                m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(.*)$", item)
                if m:
                    deps.append(entry(m.group(1), [], m.group(2).strip(), path.name, "conda"))
    return deps, env_name


def find_conflicts(deps):
    by_name = {}
    for d in deps:
        by_name.setdefault(d["name"], []).append(d)
    conflicts = []
    for name, items in sorted(by_name.items()):
        specs = {(i["specifier"], i["source"]) for i in items}
        if len({s for s, _ in specs}) > 1:
            conflicts.append(
                {
                    "name": name,
                    "specifiers": [
                        {"specifier": s, "source": src} for s, src in sorted(specs)
                    ],
                }
            )
    return conflicts


def export_requirements(deps, out_path):
    """Write a pip-installable requirements.txt: name<specifier>, first-seen
    specifier wins per package (conflicts stay visible in the JSON output)."""
    lines, seen = [], set()
    for d in deps:
        if d["kind"] != "pip" or d["name"] in seen:
            continue
        seen.add(d["name"])
        lines.append(f"{d['name']}{d['specifier']}")
    Path(out_path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def main(argv):
    if "--version" in argv[1:]:
        print("parse_deps.py 0.1.0")
        return 0
    if len(argv) >= 2 and argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if len(argv) < 2:
        print("error: provide a repository directory; use --help for usage", file=sys.stderr)
        return 2
    repo = Path(argv[1])
    rest = argv[2:]
    pretty = "--pretty" in rest
    export_path = None
    force = "--force" in rest
    if "--export" in rest:
        i = rest.index("--export")
        if i + 1 >= len(rest):
            print("error: --export requires a file path", file=sys.stderr)
            return 2
        export_path = rest[i + 1]
        if Path(export_path).exists() and not force:
            print(f"error: export exists: {export_path}; use --force to replace it",
                  file=sys.stderr)
            return 2
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    if export_path:
        dependency_sources = list(repo.glob("requirements*.txt"))
        dependency_sources.extend(
            repo / name
            for name in (
                "pyproject.toml",
                "setup.cfg",
                "setup.py",
                "Pipfile",
                "environment.yml",
                "environment.yaml",
            )
        )
        export_resolved = Path(export_path).resolve()
        if any(path.is_file() and path.resolve() == export_resolved for path in dependency_sources):
            print("error: --export must not replace a dependency source file", file=sys.stderr)
            return 2

    deps, sources, python_requires, conda_env_name = [], [], None, None
    for path in sorted(repo.glob("requirements*.txt")):
        deps += parse_requirements_txt(path)
        sources.append(path.name)
    pyproject = repo / "pyproject.toml"
    if pyproject.is_file():
        d, python_requires = parse_pyproject(pyproject)
        deps += d
        sources.append(pyproject.name)
    setup_cfg = repo / "setup.cfg"
    if setup_cfg.is_file():
        deps += parse_setup_cfg(setup_cfg)
        sources.append(setup_cfg.name)
    setup_py = repo / "setup.py"
    if setup_py.is_file():
        deps += parse_setup_py(setup_py)
        sources.append(setup_py.name)
    pipfile = repo / "Pipfile"
    if pipfile.is_file():
        deps += parse_pipfile(pipfile)
        sources.append(pipfile.name)
    for name in ("environment.yml", "environment.yaml"):
        env_yml = repo / name
        if env_yml.is_file():
            d, conda_env_name = parse_environment_yml(env_yml)
            deps += d
            sources.append(name)

    if export_path:
        export_requirements(deps, export_path)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    result = {
        "repo_dir": str(repo),
        "sources_found": sources,
        "python_requires": python_requires,
        "conda_env_name": conda_env_name,
        "environment_evidence": [
            {"runtime": runtime, "path": name, "parsed": False}
            for name, runtime in ENVIRONMENT_EVIDENCE.items()
            if (repo / name).is_file()
        ],
        "dependencies": deps,
        "conflicts": find_conflicts(deps),
        "exported": export_path,
    }
    print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
