#!/usr/bin/env python3
"""Validate a declared remote-dataset manifest without downloading anything.

Input JSON is a list or ``{"datasets": [...]}``. Each record requires an
``id`` and ``url`` and should state ``license_or_terms`` and ``version``.
Optional ``sha256`` is syntax-checked only. This is provenance planning, not
permission verification, accessibility checking, or checksum verification.

Usage: python3 remote_data_manifest.py manifest.json [--pretty]
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from urllib.parse import urlparse

VERSION="0.1.0"; SHA256=re.compile(r"^[0-9a-fA-F]{64}$")

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("manifest");p.add_argument("--pretty",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
    try:
        raw=json.loads(Path(a.manifest).read_text(encoding="utf-8")); rows=raw.get("datasets") if isinstance(raw,dict) else raw
        if not isinstance(rows,list): raise ValueError("manifest must be a list or object with datasets list")
        ids=set(); findings=[]
        for n,row in enumerate(rows,1):
            if not isinstance(row,dict): findings.append({"row":n,"severity":"error","issue":"record is not an object"});continue
            identifier=str(row.get("id","")).strip(); url=str(row.get("url","")).strip()
            if not identifier: findings.append({"row":n,"severity":"error","issue":"missing id"})
            elif identifier in ids: findings.append({"row":n,"id":identifier,"severity":"error","issue":"duplicate id"})
            ids.add(identifier)
            if urlparse(url).scheme not in {"https","http","s3","gs","doi"}: findings.append({"row":n,"id":identifier,"severity":"error","issue":"url needs http(s), s3, gs, or doi scheme"})
            for field in ("license_or_terms","version"):
                if not str(row.get(field," ")).strip(): findings.append({"row":n,"id":identifier,"severity":"warning","issue":f"missing {field}"})
            checksum=row.get("sha256")
            if checksum and not SHA256.fullmatch(str(checksum)): findings.append({"row":n,"id":identifier,"severity":"error","issue":"sha256 must be 64 hexadecimal characters"})
        report={"schema_version":"1.0.0","artifact_type":"remote-dataset-manifest-audit","tool_version":VERSION,"manifest":str(Path(a.manifest).resolve()),"records":len(rows),"findings":findings,"warnings":["Offline audit only: URLs were not contacted and supplied checksums were not verified.","A declared license/terms source does not prove access, consent, redistribution permission, or dataset suitability."]}
        print(json.dumps(report,ensure_ascii=False,indent=2 if a.pretty else None));return 0
    except (OSError,ValueError,json.JSONDecodeError) as e: print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
