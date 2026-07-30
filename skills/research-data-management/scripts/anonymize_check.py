#!/usr/bin/env python3
"""Check a dataset for potential direct identifiers and quasi-identifiers.

Flags columns whose names match common direct-identifier patterns (name, email,
phone, address, ssn, id, ...) and reports uniqueness risk for quasi-identifiers.
Read-only: never modifies data.
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
VERSION = "0.1.0"
DIRECT_PATTERNS = [re.compile(p, re.I) for p in [
    r"^(name|fullname|full_name|firstname|lastname|given_name|family_name)$",
    r"^(email|e[-_]?mail)$", r"^(phone|tel|mobile|fax)$",
    r"^(address|street|city|zip|postal|country|state|province)$",
    r"^(ssn|social[-_]?security|national[-_]?id|passport)$",
    r"^(date[-_]?of[-_]?birth|dob|birth[-_]?date)$",
    r"^(ip[-_]?address|ip)$", r"^(_?id|uuid|guid)$",
]]


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        r = getattr(s, "reconfigure", None)
        if r:
            r(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv_file")
    p.add_argument("--quasi", default="zip,birth_date,gender", help="comma-separated quasi-identifier column names")
    p.add_argument("--uniqueness-threshold", type=float, default=0.9,
                   help="flag if fraction of unique rows exceeds this")
    p.add_argument("--pretty", action="store_true")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    a = p.parse_args(argv)
    try:
        path = Path(a.csv_file).resolve(strict=True)
        quasi_cols = [c.strip() for c in a.quasi.split(",") if c.strip()]
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            headers = list(reader.fieldnames or [])
            rows = list(reader)
        direct_flags = [h for h in headers if any(pat.search(h) for pat in DIRECT_PATTERNS)]
        quasi_uniqueness = {}
        for col in quasi_cols:
            if col not in headers:
                continue
            vals = [r[col] for r in rows]
            uniq = len(set(vals)) / len(vals) if vals else 0
            quasi_uniqueness[col] = {"unique_ratio": round(uniq, 4),
                                      "risk": "high" if uniq > a.uniqueness_threshold else "low"}
        report = {
            "schema_version": "1.0.0", "artifact_type": "anonymization-screen",
            "tool_version": VERSION, "file": str(path),
            "rows": len(rows), "columns": len(headers),
            "direct_identifier_columns": direct_flags,
            "quasi_identifier_risk": quasi_uniqueness,
            "warnings": ["Screen only: flags patterns; does not measure k-anonymity/l-diversity/t-closeness.",
                         "Final anonymization decisions require a human expert and domain rules."],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2 if a.pretty else None))
        return 0
    except (OSError, ValueError, csv.Error) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
