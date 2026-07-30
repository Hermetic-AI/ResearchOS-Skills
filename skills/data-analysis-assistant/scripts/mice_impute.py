#!/usr/bin/env python3
"""Create one reproducible MICE-imputed CSV and an imputation-manifest artifact.

Only numeric columns are eligible. This utility produces a single completed data set;
use an analysis model that pools multiple imputed data sets when inferential pooling is
required.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


VERSION = "0.1.0"


def fail(message: str) -> None:
    raise ValueError(message)


def parse_columns(value: str | None) -> list[str] | None:
    if value is None:
        return None
    columns = [part.strip() for part in value.split(",") if part.strip()]
    if not columns:
        fail("--columns must name at least one column")
    if len(set(columns)) != len(columns):
        fail("--columns contains duplicates")
    return columns


def derived_manifest_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.mice-manifest.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", help="input CSV; it is never modified")
    parser.add_argument("--out", required=True, help="new completed CSV path")
    parser.add_argument("--manifest-out", help="new imputation-manifest JSON path")
    parser.add_argument("--columns", help="comma-separated numeric columns; default: numeric columns with missing values")
    parser.add_argument("--iterations", type=int, default=10, help="MICE update cycles (default: 10)")
    parser.add_argument("--seed", type=int, default=20260729, help="random seed recorded in the manifest")
    parser.add_argument("--force", action="store_true", help="replace existing derived output/manifest; never the input")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)

    try:
        if args.iterations < 1:
            fail("--iterations must be at least 1")
        import numpy as np
        import pandas as pd
        from statsmodels.imputation.mice import MICEData

        source = Path(args.data).resolve(strict=True)
        output = Path(args.out).resolve()
        manifest_path = Path(args.manifest_out).resolve() if args.manifest_out else derived_manifest_path(output)
        if source == output:
            fail("--out must differ from the input; raw input protection is active")
        if not args.force and (output.exists() or manifest_path.exists()):
            fail("output or manifest already exists; choose new paths to avoid overwriting derived data")
        frame = pd.read_csv(source)
        requested = parse_columns(args.columns)
        numeric = [column for column in frame.columns if pd.api.types.is_numeric_dtype(frame[column])]
        columns = requested or [column for column in numeric if frame[column].isna().any()]
        missing_columns = [column for column in columns if column not in frame.columns]
        non_numeric = [column for column in columns if column in frame.columns and column not in numeric]
        if missing_columns:
            fail(f"unknown columns: {', '.join(missing_columns)}")
        if non_numeric:
            fail(f"MICE input must be numeric: {', '.join(non_numeric)}")
        if len(columns) < 2:
            fail("MICE requires at least two numeric eligible columns; select additional predictors")
        before = {column: int(frame[column].isna().sum()) for column in columns}
        if not any(before.values()):
            fail("selected columns contain no missing values")
        if any(frame[column].notna().sum() < 2 for column in columns):
            fail("each selected column needs at least two observed values")

        np.random.seed(args.seed)
        imputer = MICEData(frame[columns].copy())
        imputer.update_all(n_iter=args.iterations)
        completed = frame.copy()
        completed.loc[:, columns] = imputer.data.loc[:, columns]
        after = {column: int(completed[column].isna().sum()) for column in columns}
        if any(after.values()):
            fail("MICE did not complete all selected missing values; inspect the selected predictors")
        completed.to_csv(output, index=False)
        manifest = {
            "schema_version": "1.0.0",
            "artifact_type": "imputation-manifest",
            "provenance": {
                "created_by": "data-analysis-assistant/mice_impute.py",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "tool_version": VERSION,
                "command": " ".join(sys.argv),
                "seed": args.seed,
                "sources": [{"kind": "file", "locator": str(source)}],
                "warnings": [],
            },
            "input": {"kind": "file", "locator": str(source)},
            "output": {"kind": "file", "locator": str(output)},
            "method": "statsmodels-mice predictive mean matching",
            "iterations": args.iterations,
            "columns": columns,
            "missing_before": before,
            "missing_after": after,
            "warnings": [
                "This artifact is one completed data set, not pooled multiple-imputation inference.",
                "Assess the missingness mechanism and include outcome/predictors appropriate to the analysis before treating MAR as plausible.",
            ],
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except (FileNotFoundError, OSError, ValueError, ImportError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
