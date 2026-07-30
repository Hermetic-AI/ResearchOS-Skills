#!/usr/bin/env python3
"""Create a protected dataset evidence inventory without copying or downloading data."""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION="0.1.0"
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", action="append", required=True, help="dataset file; repeatable")
    p.add_argument("--license", action="append", default=[], help="license/terms source or identifier; repeatable")
    p.add_argument("--version-source", action="append", default=[], help="dataset version/DOI/release source; repeatable")
    p.add_argument("--out", required=True);p.add_argument("--force",action="store_true");p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}");a=p.parse_args(argv)
    try:
        out=Path(a.out).resolve()
        if out.exists() and not a.force: raise ValueError("output exists; use --force only for a revised inventory")
        files=[]
        for raw in a.data:
            path=Path(raw).resolve(strict=True)
            if not path.is_file(): raise ValueError(f"--data must be a file: {path}")
            files.append({"path":str(path),"bytes":path.stat().st_size,"sha256":digest(path)})
        payload={"schema_version":"1.0.0","artifact_type":"dataset-evidence-inventory","created_at":datetime.now(timezone.utc).isoformat(),"tool_version":VERSION,"datasets":files,"license_or_terms_sources":a.license,"version_sources":a.version_source,"warnings":["Inventory only: file presence, checksum, and supplied sources do not prove redistribution permission, consent, or suitability for the claimed use."]}
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(payload,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError) as e: print(f"error: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
