#!/usr/bin/env python3
"""Create an auditable, registry-neutral preregistration and SAP package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


VERSION = "0.1.0"
OUTPUT_NAMES = (
    "design-brief.json",
    "analysis-plan.json",
    "preregistration.md",
    "statistical-analysis-plan.md",
    "preregistration-manifest.json",
)
REQUIRED = (
    "study_id", "title", "hypothesis", "experimental_unit", "variables",
    "treatments", "outcomes", "comparisons", "planned_models", "alpha",
)


def _read_spec(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"input does not exist or is not a file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON input: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("input root must be a JSON object")
    missing = [key for key in REQUIRED if key not in payload]
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))
    for key in ("variables", "treatments", "outcomes", "comparisons", "planned_models"):
        if not isinstance(payload[key], list):
            raise ValueError(f"{key} must be an array")
    if not isinstance(payload["alpha"], (int, float)) or isinstance(payload["alpha"], bool) or not 0 < payload["alpha"] < 1:
        raise ValueError("alpha must be a number strictly between 0 and 1")
    if not isinstance(payload["study_id"], str) or not payload["study_id"].strip():
        raise ValueError("study_id must be a non-empty string")
    return payload


def _todo_paths(value, prefix="$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(_todo_paths(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_todo_paths(child, f"{prefix}[{index}]"))
    elif isinstance(value, str) and "_TODO_" in value:
        found.append(prefix)
    return found


def _source(path: Path) -> dict:
    return {
        "kind": "file",
        "locator": str(path),
        "checksum": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _provenance(source: dict, created_at: str, command: str) -> dict:
    return {
        "created_by": "experiment-designer/create_preregistration.py",
        "created_at": created_at,
        "tool_version": VERSION,
        "command": command,
        "sources": [source],
        "warnings": [],
    }


def _as_text(value) -> str:
    if value is None:
        return "_TODO_"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _bullet(values: list, empty="_TODO_") -> str:
    return "\n".join(f"- {_as_text(value)}" for value in values) if values else f"- {empty}"


def _render_preregistration(spec: dict, status: str, protocol_version: str) -> str:
    controls = spec.get("controls", [])
    return f"""# Preregistration: {spec['title']}

- Study ID: `{spec['study_id']}`
- Protocol version: `{protocol_version}`
- Status: `{status}`
- Registration target: `{spec.get('registration_target', 'registry-neutral')}`

## Research question and hypothesis

{_as_text(spec.get('research_question'))}

**Hypothesis:** {_as_text(spec['hypothesis'])}

## Design and experimental unit

- Design: {_as_text(spec.get('design_type'))}
- Experimental unit: {_as_text(spec['experimental_unit'])}
- Sampling: {_as_text(spec.get('sampling'))}
- Sample-size rationale: {_as_text(spec.get('sample_size_rationale'))}

## Variables

{_bullet(spec['variables'])}

## Treatments and controls

{_bullet(spec['treatments'])}

### Controls

{_bullet(controls)}

## Allocation, masking, and data collection

- Randomization: {_as_text(spec.get('randomization'))}
- Blinding/masking: {_as_text(spec.get('blinding'))}
- Measurements: {_as_text(spec.get('measurements'))}
- Data management: {_as_text(spec.get('data_management'))}

## Outcomes and confirmatory comparisons

### Outcomes

{_bullet(spec['outcomes'])}

### Comparisons

{_bullet(spec['comparisons'])}

## Exclusions, missing data, and deviations

- Inclusion criteria: {_as_text(spec.get('inclusion_criteria'))}
- Exclusion criteria: {_as_text(spec.get('exclusion_criteria'))}
- Missing-data policy: {_as_text(spec.get('missing_data'))}
- Protocol deviations: {_as_text(spec.get('deviation_policy'))}

## Ethics, conflicts, and sharing

- Ethics/consent: {_as_text(spec.get('ethics'))}
- Conflicts of interest: {_as_text(spec.get('conflicts'))}
- Data/code sharing: {_as_text(spec.get('sharing'))}

## Unresolved decisions

{_bullet(spec.get('open_questions', []), empty='None recorded')}
"""


def _render_sap(spec: dict, status: str, protocol_version: str) -> str:
    return f"""# Statistical Analysis Plan: {spec['title']}

- Study ID: `{spec['study_id']}`
- Protocol version: `{protocol_version}`
- Status: `{status}`
- Family-wise alpha: `{spec['alpha']}`

## Estimands

{_bullet(spec.get('estimands', []))}

## Outcomes

{_bullet(spec['outcomes'])}

## Confirmatory comparisons

{_bullet(spec['comparisons'])}

## Planned models

{_bullet(spec['planned_models'])}

## Covariates and transformations

- Covariates: {_as_text(spec.get('covariates'))}
- Transformations: {_as_text(spec.get('transformations'))}

## Multiplicity

{_as_text(spec.get('multiplicity'))}

## Analysis populations, exclusions, and missing data

- Analysis populations: {_as_text(spec.get('analysis_populations'))}
- Exclusions: {_as_text(spec.get('exclusion_criteria'))}
- Missing-data handling: {_as_text(spec.get('missing_data'))}

## Model diagnostics and sensitivity analyses

- Diagnostics: {_as_text(spec.get('diagnostics'))}
- Sensitivity analyses: {_as_text(spec.get('sensitivity_analyses'))}

## Interim analyses and stopping rules

{_as_text(spec.get('interim_and_stopping'))}

## Reporting

{_as_text(spec.get('reporting'))}

## Deviations from this plan

{_as_text(spec.get('deviation_policy'))}
"""


def _json_text(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def create_package(spec_path: Path, out_dir: Path, force: bool, freeze: bool, protocol_version: str, argv: list[str]) -> dict:
    spec_path = spec_path.resolve()
    out_dir = out_dir.resolve()
    if out_dir == spec_path or spec_path in out_dir.parents:
        raise ValueError("--out-dir must be a directory and cannot be inside the input file")
    targets = {name: out_dir / name for name in OUTPUT_NAMES}
    if spec_path in targets.values():
        raise ValueError("output must not replace the input specification")
    collisions = [str(path) for path in targets.values() if path.exists()]
    if collisions and not force:
        raise ValueError("outputs already exist; use --force to replace: " + ", ".join(collisions))

    spec = _read_spec(spec_path)
    todo_paths = sorted(set(_todo_paths(spec) + [f"$.open_questions[{i}]" for i, q in enumerate(spec.get("open_questions", [])) if q]))
    if freeze and todo_paths:
        raise ValueError("cannot freeze with unresolved decisions: " + ", ".join(todo_paths))

    status = "frozen" if freeze else "draft"
    created_at = datetime.now(timezone.utc).isoformat()
    source = _source(spec_path)
    command = " ".join(argv)
    provenance = _provenance(source, created_at, command)
    common = {"schema_version": "1.0.0", "provenance": provenance}
    design = {
        **common,
        "artifact_type": "design-brief",
        "study_id": spec["study_id"],
        "title": spec["title"],
        "hypothesis": spec["hypothesis"],
        "variables": spec["variables"],
        "treatments": spec["treatments"],
        "experimental_unit": spec["experimental_unit"],
        "design_type": spec.get("design_type"),
        "controls": spec.get("controls", []),
        "sampling": spec.get("sampling"),
        "randomization": spec.get("randomization"),
        "blinding": spec.get("blinding"),
        "measurements": spec.get("measurements"),
        "sample_size_rationale": spec.get("sample_size_rationale"),
        "open_questions": spec.get("open_questions", []),
    }
    analysis = {
        **common,
        "artifact_type": "analysis-plan",
        "study_id": spec["study_id"],
        "title": spec["title"],
        "estimands": spec.get("estimands", []),
        "outcomes": spec["outcomes"],
        "comparisons": spec["comparisons"],
        "planned_models": spec["planned_models"],
        "alpha": spec["alpha"],
        "multiplicity": spec.get("multiplicity"),
        "covariates": spec.get("covariates", []),
        "transformations": spec.get("transformations", []),
        "analysis_populations": spec.get("analysis_populations", []),
        "exclusion_criteria": spec.get("exclusion_criteria", []),
        "missing_data": spec.get("missing_data"),
        "diagnostics": spec.get("diagnostics", []),
        "sensitivity_analyses": spec.get("sensitivity_analyses", []),
        "interim_and_stopping": spec.get("interim_and_stopping"),
        "reporting": spec.get("reporting"),
        "open_questions": spec.get("open_questions", []),
    }
    contents = {
        "design-brief.json": _json_text(design),
        "analysis-plan.json": _json_text(analysis),
        "preregistration.md": _render_preregistration(spec, status, protocol_version),
        "statistical-analysis-plan.md": _render_sap(spec, status, protocol_version),
    }
    files = []
    for name, content in contents.items():
        files.append({
            "path": name,
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "bytes": len(content.encode("utf-8")),
        })
    manifest = {
        **common,
        "artifact_type": "preregistration-manifest",
        "study_id": spec["study_id"],
        "title": spec["title"],
        "protocol_version": protocol_version,
        "registration_status": status,
        "frozen_at": created_at if freeze else None,
        "source_spec": source,
        "files": files,
        "unresolved": todo_paths,
    }
    contents["preregistration-manifest.json"] = _json_text(manifest)
    for name in OUTPUT_NAMES:
        _write_atomic(targets[name], contents[name])
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--input", required=True, type=Path, help="structured study specification JSON")
    parser.add_argument("--out-dir", required=True, type=Path, help="new or dedicated package directory")
    parser.add_argument("--protocol-version", default="0.1.0", help="user-managed protocol version")
    parser.add_argument("--freeze", action="store_true", help="mark frozen; refuses all _TODO_ and open questions")
    parser.add_argument("--force", action="store_true", help="replace this command's known output files")
    args = parser.parse_args(argv)
    if not args.protocol_version.strip():
        parser.error("--protocol-version must not be empty")
    try:
        manifest = create_package(
            args.input, args.out_dir, args.force, args.freeze,
            args.protocol_version, [Path(sys.argv[0]).name, *(argv if argv is not None else sys.argv[1:])],
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
