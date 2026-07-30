#!/usr/bin/env python3
"""Inventory a multi-file Markdown project before explicit md2latex conversion.

Reports Markdown files and local Markdown/image links relative to the project
root. With ``--rewrite-plan`` it proposes cross-file path rewrites that make
image/include links valid from the perspective of each output ``.tex`` file
(by default placed alongside its source ``.md``). With ``--apply-rewrites`` it
actually rewrites those paths in the source ``.md`` files (creating a ``.md.bak``
backup of each modified file first). ``--dry-run`` shows what would change
without writing anything.

Usage: python3 markdown_project_audit.py project_dir [--pretty] [--rewrite-plan]
                            [--apply-rewrites] [--dry-run] [--out-dir DIR]
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path

VERSION = "0.1.0"
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "build", "dist"}


def linkable_text(text: str) -> str:
    """Mask code examples so placeholder links are not reported as resources."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "", text)


def propose_rewrite(source_md, target_tex, raw_link):
    """Given a link relative to ``source_md``, return the path that resolves
    the same target from ``target_tex``'s directory. Returns None when the
    link is not a rewritable local resource (URL, anchor-only, or outside)."""
    if raw_link.startswith(("#", "http://", "https://", "mailto:")):
        return None
    src = Path(source_md)
    tgt = Path(target_tex)
    anchor = ""
    path_part = raw_link
    if "#" in raw_link and not raw_link.startswith("#"):
        path_part, anchor = raw_link.split("#", 1)
        anchor = "#" + anchor
    if not path_part:
        return None
    try:
        target = (src.parent / path_part).resolve()
    except (OSError, ValueError):
        return None
    if not tgt.parent.is_dir():
        return None
    try:
        rewritten = Path(os_relpath(target, tgt.parent))
    except ValueError:
        return None
    return str(rewritten).replace("\\", "/") + anchor


def os_relpath(path, start):
    """os.path.relpath wrapper kept import-local for clarity."""
    import os.path
    return os.path.relpath(path, start)


def compute_target_tex(source_path, root, out_dir):
    """Return the absolute path of the ``.tex`` output for a source ``.md``,
    matching the layout used by the rewrite plan (flattened into out_dir)."""
    rel = Path(source_path).relative_to(root)
    if out_dir:
        return (Path(root) / Path(out_dir) / rel.with_suffix(".tex").name).resolve()
    return (Path(root) / rel.with_suffix(".tex")).resolve()


def rewrite_text(text, source_path, root, out_dir):
    """Return (rewritten_text, changes) where changes is a list of
    {"link": old, "rewrite": new}. Only links that exist, are local, and would
    break from the new output location are changed."""
    target_tex = compute_target_tex(source_path, root, out_dir)
    src = Path(source_path)
    tgt = Path(target_tex)
    changes = []

    def repl(m):
        raw = m.group(1)
        if raw.startswith(("#", "http://", "https://", "mailto:")):
            return m.group(0)
        rewritten = propose_rewrite(src, tgt, raw)
        if rewritten is not None and rewritten != raw:
            changes.append({"link": raw, "rewrite": rewritten})
            prefix = m.group(0)[:m.start(1) - m.start(0)]
            suffix = m.group(0)[m.end(1) - m.start(0):]
            return prefix + rewritten + suffix
        return m.group(0)

    new_text = LINK.sub(repl, text)
    return new_text, changes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--rewrite-plan", action="store_true",
                        help="propose cross-file path rewrites for image/include links")
    parser.add_argument("--apply-rewrites", action="store_true",
                        help="rewrite paths in the source .md files so they stay valid "
                             "from the output .tex location (requires --out-dir)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change without writing any file")
    parser.add_argument("--out-dir",
                        help="directory the converted .tex files will live in "
                             "(default: alongside each source .md). Relative to the project root.")
    parser.add_argument("--force", action="store_true",
                        help="replace existing .md.bak backup files")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)

    if args.apply_rewrites and not args.out_dir:
        print("error: --apply-rewrites requires --out-dir", file=sys.stderr)
        return 2

    try:
        root = Path(args.project).resolve()
        if not root.is_dir():
            raise ValueError("project must be a directory")
        markdown = sorted(path for path in root.rglob("*.md")
                          if not any(part in SKIP for part in path.relative_to(root).parts))
        files, missing, rewrites = [], [], []
        for path in markdown:
            rel = path.relative_to(root)
            links = []
            text = linkable_text(path.read_text(encoding="utf-8", errors="replace"))
            if args.out_dir:
                out_tex = Path(args.out_dir) / rel.with_suffix(".tex").name
            else:
                out_tex = rel.with_suffix(".tex")
            for raw in LINK.findall(text):
                if raw.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                destination = (path.parent / raw.split("#", 1)[0]).resolve()
                exists = destination.exists() and destination.is_relative_to(root)
                item = {"path": raw, "exists": exists}
                links.append(item)
                if not exists:
                    missing.append({"source": str(rel), **item})
                if args.rewrite_plan and exists:
                    rewritten = propose_rewrite(path, root / out_tex, raw.split("#", 1)[0])
                    if rewritten is not None and rewritten != raw.split("#", 1)[0]:
                        rewrites.append({"source": str(rel), "link": raw, "rewrite": rewritten})
            files.append({"path": str(rel), "local_links": links})

        # Apply or dry-run rewrites on the real file text (not the code-masked text).
        apply_mode = args.apply_rewrites and not args.dry_run
        files_modified = []
        backups_created = []
        if args.apply_rewrites:
            # Ensure the output directory exists so path rewrites are computable.
            target_dir = (root / Path(args.out_dir)).resolve()
            if apply_mode:
                target_dir.mkdir(parents=True, exist_ok=True)
            for path in markdown:
                rel = path.relative_to(root)
                text = path.read_text(encoding="utf-8")
                new_text, changes = rewrite_text(text, path, root, args.out_dir)
                if not changes:
                    continue
                if args.dry_run:
                    files_modified.append({"path": str(rel), "changes": changes})
                    continue
                backup = path.with_suffix(path.suffix + ".bak")
                if backup.exists() and not args.force:
                    raise ValueError(
                        f"backup exists: {backup}; use --force to replace it")
                backup.write_text(text, encoding="utf-8")
                path.write_text(new_text, encoding="utf-8")
                backups_created.append(str(backup.relative_to(root)))
                files_modified.append({"path": str(rel), "changes": changes})

        warnings = ["Audit only: conversion remains explicit per file.",
                    "Markdown include directives and cross-document reference semantics are not interpreted."]
        if args.apply_rewrites and args.dry_run:
            warnings.append("Dry-run: no files were modified; backups are only created when applying.")
        elif args.apply_rewrites:
            warnings.append("Backups (.md.bak) were created for each modified source file before rewriting.")
        elif args.rewrite_plan:
            warnings.append("Rewrite plan is advisory: paths are proposed, not applied. Review before editing sources.")

        report = {
            "schema_version": "1.0.0",
            "artifact_type": "markdown-project-audit",
            "tool_version": VERSION,
            "project": str(root),
            "markdown_files": files,
            "missing_or_outside_resources": missing,
            "conversion_plan": [{"input": entry["path"],
                                 "suggested_output": str(Path(entry["path"]).with_suffix(".tex"))}
                                for entry in files],
            "rewrite_plan": rewrites if args.rewrite_plan else [],
            "dry_run": args.dry_run or not args.apply_rewrites,
            "files_modified": files_modified,
            "backups_created": backups_created,
            "warnings": warnings,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
