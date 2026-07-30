#!/usr/bin/env python3
"""Inspect or convert CSV, TSV, JSON records, XLSX, and Parquet research data."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


VERSION = "0.1.0"
FORMATS = {".csv": "csv", ".tsv": "tsv", ".json": "json", ".xlsx": "xlsx", ".parquet": "parquet"}


def infer(path: Path) -> str:
    try:
        return FORMATS[path.suffix.lower()]
    except KeyError as error:
        raise ValueError("supported extensions: .csv, .tsv, .json, .xlsx, .parquet") from error


def read_frame(path: Path, sheet: str | None):
    import pandas as pd
    kind = infer(path)
    if kind == "csv": return pd.read_csv(path), kind
    if kind == "tsv": return pd.read_csv(path, sep="\t"), kind
    if kind == "json": return pd.read_json(path), kind
    if kind == "xlsx": return pd.read_excel(path, sheet_name=sheet or 0), kind
    return pd.read_parquet(path), kind


def source(path: Path): return {"kind": "file", "locator": str(path)}


def refuse_existing(path: Path, force: bool) -> None:
    if path.exists() and not force: raise ValueError(f"output exists: {path}; choose a new path or use --force")


def dictionary(frame, input_path: Path, input_format: str, command: str):
    columns = []
    for name in frame.columns:
        series = frame[name]
        columns.append({"name": str(name), "dtype": str(series.dtype), "missing": int(series.isna().sum()), "nonmissing": int(series.notna().sum()), "unique": int(series.nunique(dropna=True)), "example_values": [str(value) for value in series.dropna().head(3).tolist()]})
    return {"schema_version":"1.0.0", "artifact_type":"data-dictionary", "provenance":{"created_by":"data-analysis-assistant/tabular_io.py", "created_at":datetime.now(timezone.utc).isoformat(), "tool_version":VERSION, "command":command, "seed":None, "sources":[source(input_path)], "warnings":[]}, "input":source(input_path), "input_format":input_format, "rows":int(len(frame)), "columns":columns, "warnings":["Inferred types and example values are a profile, not a semantic codebook. Confirm units, permitted values, and missing-value meanings with the study protocol."]}


def write_frame(frame, path: Path, sheet: str | None):
    kind = infer(path)
    if kind == "csv": frame.to_csv(path, index=False)
    elif kind == "tsv": frame.to_csv(path, index=False, sep="\t")
    elif kind == "json": frame.to_json(path, orient="records", indent=2)
    elif kind == "xlsx": frame.to_excel(path, index=False, sheet_name=sheet or "data")
    else: frame.to_parquet(path, index=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subs = parser.add_subparsers(dest="mode", required=True)
    for name in ("inspect", "convert"):
        sub = subs.add_parser(name); sub.add_argument("data"); sub.add_argument("--sheet", help="XLSX sheet name (default: first)")
        sub.add_argument("--force", action="store_true", help="replace an existing derived output; never the input")
    subs.choices["inspect"].add_argument("--dictionary-out", required=True)
    subs.choices["convert"].add_argument("--out", required=True, help="new output with a supported extension")
    subs.choices["convert"].add_argument("--dictionary-out", help="optional new data-dictionary JSON")
    args = parser.parse_args(argv)
    try:
        input_path = Path(args.data).resolve(strict=True); frame, input_format = read_frame(input_path, args.sheet)
        if args.mode == "inspect":
            target = Path(args.dictionary_out).resolve(); refuse_existing(target, args.force)
            artifact = dictionary(frame, input_path, input_format, " ".join(sys.argv))
            target.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(artifact, ensure_ascii=False, indent=2)); return 0
        output = Path(args.out).resolve()
        if output == input_path: raise ValueError("--out must differ from the source; raw input protection is active")
        refuse_existing(output, args.force); infer(output)
        dictionary_path = Path(args.dictionary_out).resolve() if args.dictionary_out else None
        if dictionary_path:
            if dictionary_path == output: raise ValueError("--dictionary-out must differ from --out")
            refuse_existing(dictionary_path, args.force)
        write_frame(frame, output, args.sheet)
        artifact = dictionary(frame, input_path, input_format, " ".join(sys.argv))
        artifact["output"] = source(output)
        if dictionary_path:
            dictionary_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(artifact, ensure_ascii=False, indent=2)); return 0
    except (ImportError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
