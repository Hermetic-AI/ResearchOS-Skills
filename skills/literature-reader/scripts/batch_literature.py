#!/usr/bin/env python3
"""Process a literature corpus incrementally with resumable checkpoints."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.1.0"
DEFAULT_PATTERNS = ("*.pdf", "*.txt", "*.bib", "*.ris", "*.xml", "*.json")
SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("source", help="source corpus directory")
    parser.add_argument("--out-dir", required=True, help="existing, separate derived-output directory")
    parser.add_argument("--checkpoint", help="checkpoint JSON (default: <out-dir>/batch-state.json)")
    parser.add_argument("--force", action="store_true", help="update an existing checkpoint")
    parser.add_argument("--include", action="append", help="glob relative to source; repeatable")
    parser.add_argument("--exclude", action="append", default=[], help="exclusion glob; repeatable")
    parser.add_argument("--limit", type=int, help="process at most this many pending/changed files")
    parser.add_argument("--retry-failed", action="store_true", help="retry files that failed previously")
    parser.add_argument("--pdf-ocr", choices=["never", "auto", "always"], default="never")
    parser.add_argument("--max-file-mib", type=float, default=50.0)
    return parser


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_name(relative: str, kind: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(relative).stem).strip("-._") or "item"
    stem = stem[:48]
    suffix = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:10]
    return f"{stem}-{suffix}.{kind}.json"


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf-extraction"
    if suffix in {".txt", ".md"}:
        return "metadata-extraction"
    if suffix in {".bib", ".ris", ".xml", ".json"}:
        return "bibliography-library"
    return "unsupported"


def discover(source_root: Path, includes: list[str], excludes: list[str]) -> tuple[list[Path], list[str]]:
    files, warnings = [], []
    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source_root).as_posix()
        if any(part.startswith(".") for part in Path(relative).parts):
            continue
        if not any(fnmatch.fnmatch(relative, pattern) for pattern in includes):
            continue
        if any(fnmatch.fnmatch(relative, pattern) for pattern in excludes):
            continue
        try:
            path.resolve().relative_to(source_root.resolve())
        except ValueError:
            warnings.append(f"skipped source escaping corpus root: {relative}")
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(source_root).as_posix().casefold()), warnings


def run_command(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg"},
        timeout=300,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def atomic_write_text(path: Path, text: str) -> None:
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def process_file(
    source: Path,
    relative: str,
    kind: str,
    output: Path,
    pdf_ocr: str,
    allow_overwrite: bool,
) -> dict[str, Any]:
    if output.exists() and not allow_overwrite:
        return {
            "status": "failed",
            "error": "derived output already exists; use --force to replace it",
            "command": None,
            "stdout": "",
            "stderr": "",
        }
    if kind == "pdf-extraction":
        command = [
            sys.executable,
            str(SCRIPT_DIR / "extract_pdf.py"),
            str(source),
            "--ocr",
            pdf_ocr,
            "--out",
            str(output),
        ]
        if allow_overwrite:
            command.append("--force")
        returncode, stdout, stderr = run_command(command)
    elif kind == "metadata-extraction":
        command = [sys.executable, str(SCRIPT_DIR / "extract_metadata.py"), str(source), "--pretty"]
        returncode, stdout, stderr = run_command(command)
        if returncode == 0:
            atomic_write_text(output, stdout)
    elif kind == "bibliography-library":
        command = [
            sys.executable,
            str(SCRIPT_DIR / "convert_bibliography.py"),
            str(source),
            "--to",
            "researchos-json",
            "--out",
            str(output),
        ]
        if allow_overwrite:
            command.append("--force")
        returncode, stdout, stderr = run_command(command)
    else:
        return {
            "status": "failed",
            "error": "unsupported file type",
            "command": None,
        }
    record = {
        "status": "success" if returncode == 0 else "failed",
        "command": command,
        "stdout": stdout[-2000:] if stdout else "",
        "stderr": stderr[-4000:] if stderr else "",
    }
    if returncode != 0:
        record["error"] = f"processor exited {returncode}"
    return record


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_checkpoint(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "literature-batch":
        raise ValueError("existing checkpoint is not a literature-batch artifact")
    return payload


def make_checkpoint(source_root: Path, output_root: Path, checkpoint: Path, previous: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "literature-batch",
        "source_root": str(source_root.resolve()),
        "output_root": str(output_root.resolve()),
        "checkpoint": str(checkpoint.resolve()),
        "items": previous.get("items", []) if previous else [],
        "summary": {},
        "warnings": [],
        "provenance": {
            "created_by": "literature-reader/scripts/batch_literature.py",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "command": " ".join(["batch_literature.py", *sys.argv[1:]]),
            "seed": None,
            "sources": [{"kind": "file", "locator": str(source_root.resolve()), "note": "corpus root; per-item checksums are stored in items"}],
            "warnings": [],
        },
    }


def update_summary(state: dict[str, Any]) -> None:
    counts = {status: 0 for status in ("success", "failed", "pending", "unchanged", "removed", "skipped-large")}
    for item in state["items"]:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    state["summary"] = {"total": len(state["items"]), **counts}
    state["provenance"]["created_at"] = datetime.now(timezone.utc).isoformat()
    state["provenance"]["warnings"] = state["warnings"]


def validate_args(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    source_root, output_root = Path(args.source), Path(args.out_dir)
    checkpoint = Path(args.checkpoint) if args.checkpoint else output_root / "batch-state.json"
    if not source_root.is_dir():
        raise ValueError(f"source corpus directory not found: {source_root}")
    if not output_root.is_dir():
        raise ValueError(f"output directory not found: {output_root}")
    if output_root.resolve() == source_root.resolve() or output_root.resolve().is_relative_to(source_root.resolve()):
        raise ValueError("--out-dir must be outside the source corpus tree")
    if checkpoint.resolve().is_relative_to(source_root.resolve()):
        raise ValueError("checkpoint must be outside the source corpus tree")
    if checkpoint.parent.resolve() != output_root.resolve() and not checkpoint.parent.is_dir():
        raise ValueError("checkpoint parent directory must already exist")
    if checkpoint.exists() and not args.force:
        raise ValueError("checkpoint exists; use --force to resume/update it")
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be at least 1")
    if args.max_file_mib <= 0:
        raise ValueError("--max-file-mib must be positive")
    return source_root.resolve(), output_root.resolve(), checkpoint.resolve()


def run_batch(args: argparse.Namespace, source_root: Path, output_root: Path, checkpoint: Path) -> dict[str, Any]:
    previous = load_checkpoint(checkpoint) if checkpoint.exists() else None
    if previous and (
        Path(previous.get("source_root", "")).resolve() != source_root
        or Path(previous.get("output_root", "")).resolve() != output_root
    ):
        raise ValueError("checkpoint source/output roots do not match this invocation")
    state = make_checkpoint(source_root, output_root, checkpoint, previous)
    includes = args.include or list(DEFAULT_PATTERNS)
    files, discovery_warnings = discover(source_root, includes, args.exclude)
    state["warnings"] = discovery_warnings
    previous_by_path = {item["relative_path"]: item for item in state["items"]}
    current_paths = {path.relative_to(source_root).as_posix() for path in files}
    items = []
    processable = []
    max_bytes = int(args.max_file_mib * 1024 * 1024)

    for path in files:
        relative = path.relative_to(source_root).as_posix()
        kind = classify(path)
        file_size = path.stat().st_size
        fingerprint = sha256(path) if file_size <= max_bytes else None
        output = output_root / stable_name(relative, kind)
        old = previous_by_path.get(relative)
        base = {
            "relative_path": relative,
            "sha256": fingerprint,
            "size": file_size,
            "kind": kind,
            "output": str(output),
        }
        if file_size > max_bytes:
            item = {**base, "status": "skipped-large", "error": f"file exceeds {args.max_file_mib:g} MiB"}
        elif old and old.get("sha256") == fingerprint and old.get("status") in {"success", "unchanged"} and output.is_file():
            item = {**base, "status": "unchanged"}
        elif old and old.get("sha256") == fingerprint and old.get("status") == "failed" and not args.retry_failed:
            item = {
                **base,
                "status": "failed",
                "error": f"previous failure: {old.get('error', 'unknown error')}; use --retry-failed",
            }
        else:
            item = {**base, "status": "pending"}
            processable.append((path, item))
        items.append(item)

    for relative, old in previous_by_path.items():
        if relative not in current_paths:
            items.append({**old, "status": "removed", "error": "source file no longer present; derived output retained"})
    items.sort(key=lambda item: item["relative_path"].casefold())
    state["items"] = items
    update_summary(state)
    atomic_write_json(checkpoint, state)

    budget = args.limit if args.limit is not None else len(processable)
    processed = 0
    for path, pending in processable:
        if processed >= budget:
            continue
        result = process_file(
            path,
            pending["relative_path"],
            pending["kind"],
            Path(pending["output"]),
            args.pdf_ocr,
            args.force,
        )
        pending.update(result)
        processed += 1
        update_summary(state)
        atomic_write_json(checkpoint, state)
    update_summary(state)
    atomic_write_json(checkpoint, state)
    return state


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source_root, output_root, checkpoint = validate_args(args)
        state = run_batch(args, source_root, output_root, checkpoint)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"checkpoint": str(checkpoint), "summary": state["summary"]}, ensure_ascii=False))
    return 1 if state["summary"].get("failed", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
