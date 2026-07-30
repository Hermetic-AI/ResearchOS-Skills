#!/usr/bin/env python3
"""Validate a ResearchOS JSON artifact against a named interchange contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "researchos-artifacts.schema.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--type", dest="artifact_type", required=True)
    args = parser.parse_args(argv)
    try:
        import jsonschema
    except ImportError:
        print('Install development dependencies with: python -m pip install -e ".[dev]"', file=sys.stderr)
        return 2
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    definition = args.artifact_type.replace("-", "_")
    if definition not in schema["$defs"]:
        choices = ", ".join(sorted(key.replace("_", "-") for key in schema["$defs"] if key not in {"source", "provenance", "evidence_anchor", "artifact_header"}))
        print(f"Unknown artifact type {args.artifact_type!r}. Choose one of: {choices}", file=sys.stderr)
        return 2
    instance = json.loads(args.artifact.read_text(encoding="utf-8"))
    wrapper = {"$schema": schema["$schema"], "$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]}
    errors = sorted(jsonschema.Draft202012Validator(wrapper).iter_errors(instance), key=lambda item: list(item.path))
    if errors:
        for error in errors:
            location = "/".join(str(part) for part in error.path) or "$"
            print(f"ERROR {location}: {error.message}", file=sys.stderr)
        return 1
    print(f"Valid {args.artifact_type} artifact: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

