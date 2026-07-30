#!/usr/bin/env python3
"""Extract evidence-anchored text, tables, and captions from research PDFs.

Native PDF extraction uses the optional ``pdfplumber`` dependency. OCR is an
explicit fallback through local ``pdftoppm`` and ``tesseract`` executables; the
script never uploads a document or silently labels OCR text as native text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.1.0"
CAPTION_RE = re.compile(
    r"^\s*(?P<label>(?:fig(?:ure)?|table|图|表)\s*[A-Za-z]?\d+[A-Za-z]?)"
    r"\s*[.:：．-]?\s*(?P<text>.+)$",
    re.IGNORECASE,
)
SUPPLEMENT_RE = re.compile(
    r"\b(?:supplement(?:ary|al)?|appendix|supporting information)\b|补充(?:材料|信息)|附录",
    re.IGNORECASE,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract page-anchored research-PDF text, tables, captions, and OCR provenance."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("pdf", help="input PDF")
    parser.add_argument("--out", help="write structured JSON here (default: stdout only)")
    parser.add_argument("--markdown-out", help="also write a page-anchored Markdown rendering")
    parser.add_argument("--force", action="store_true", help="replace existing output files")
    parser.add_argument(
        "--pages",
        help="1-based pages/ranges, for example 1-3,7 (default: all pages)",
    )
    parser.add_argument(
        "--layout",
        choices=["auto", "single", "two-column"],
        default="auto",
        help="reading-order strategy (default: auto)",
    )
    parser.add_argument(
        "--ocr",
        choices=["never", "auto", "always"],
        default="auto",
        help="local OCR policy (default: auto for sparse pages)",
    )
    parser.add_argument("--ocr-lang", default="eng", help="Tesseract language code(s)")
    parser.add_argument("--ocr-dpi", type=int, default=300)
    parser.add_argument(
        "--min-native-chars",
        type=int,
        default=80,
        help="OCR an auto-mode page below this native-text threshold",
    )
    parser.add_argument(
        "--no-tables",
        action="store_true",
        help="skip pdfplumber table extraction",
    )
    return parser


def parse_page_spec(spec: str | None, page_count: int) -> list[int]:
    if page_count < 1:
        return []
    if not spec:
        return list(range(1, page_count + 1))
    selected: set[int] = set()
    for token in spec.split(","):
        token = token.strip()
        if not token:
            raise ValueError("empty page token")
        if "-" in token:
            parts = token.split("-", 1)
            if not all(part.isdigit() for part in parts):
                raise ValueError(f"invalid page range: {token}")
            start, end = map(int, parts)
            if start > end:
                raise ValueError(f"descending page range: {token}")
            selected.update(range(start, end + 1))
        elif token.isdigit():
            selected.add(int(token))
        else:
            raise ValueError(f"invalid page: {token}")
    invalid = sorted(page for page in selected if page < 1 or page > page_count)
    if invalid:
        raise ValueError(f"page outside 1-{page_count}: {invalid[0]}")
    return sorted(selected)


def _line_text(words: list[dict[str, Any]], tolerance: float = 3.0) -> str:
    lines: list[list[dict[str, Any]]] = []
    for word in sorted(words, key=lambda item: (float(item["top"]), float(item["x0"]))):
        if not lines or abs(float(word["top"]) - float(lines[-1][0]["top"])) > tolerance:
            lines.append([word])
        else:
            lines[-1].append(word)
    return "\n".join(
        " ".join(str(word["text"]) for word in sorted(line, key=lambda item: float(item["x0"])))
        for line in lines
    )


def detect_two_columns(words: list[dict[str, Any]], width: float, height: float) -> bool:
    if len(words) < 20 or width <= 0 or height <= 0:
        return False
    narrow = [word for word in words if float(word["x1"]) - float(word["x0"]) < width * 0.45]
    left = [word for word in narrow if (float(word["x0"]) + float(word["x1"])) / 2 < width * 0.44]
    right = [word for word in narrow if (float(word["x0"]) + float(word["x1"])) / 2 > width * 0.56]
    if len(left) < 10 or len(right) < 10:
        return False
    left_span = (min(float(w["top"]) for w in left), max(float(w["bottom"]) for w in left))
    right_span = (min(float(w["top"]) for w in right), max(float(w["bottom"]) for w in right))
    overlap = max(0.0, min(left_span[1], right_span[1]) - max(left_span[0], right_span[0]))
    return overlap >= height * 0.25


def words_to_text(
    words: list[dict[str, Any]], width: float, height: float, layout: str
) -> tuple[str, str]:
    two_columns = layout == "two-column" or (
        layout == "auto" and detect_two_columns(words, width, height)
    )
    if not two_columns:
        return _line_text(words), "single"

    left = [word for word in words if float(word["x0"]) < width / 2]
    right = [word for word in words if float(word["x0"]) >= width / 2]
    parts = [part for part in (_line_text(left), _line_text(right)) if part.strip()]
    return "\n\n".join(parts), "two-column"


def normalize_table(table: list[list[Any]] | None) -> list[list[str | None]]:
    return [
        [None if cell is None else " ".join(str(cell).split()) for cell in row]
        for row in (table or [])
    ]


def extract_captions(text: str, page_number: int) -> list[dict[str, Any]]:
    captions = []
    for line in text.splitlines():
        match = CAPTION_RE.match(line)
        if match:
            label = match.group("label").strip()
            captions.append(
                {
                    "page": page_number,
                    "label": label,
                    "kind": "table" if label.lower().startswith(("table", "表")) else "figure",
                    "text": match.group("text").strip(),
                }
            )
    return captions


def extract_supplement_mentions(text: str, page_number: int) -> list[dict[str, Any]]:
    mentions = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if SUPPLEMENT_RE.search(line):
            mentions.append(
                {"page": page_number, "line": line_number, "text": line.strip()[:500]}
            )
    return mentions


def ocr_page(pdf: Path, page_number: int, lang: str, dpi: int) -> str:
    pdftoppm = shutil.which("pdftoppm")
    tesseract = shutil.which("tesseract")
    missing = [name for name, path in (("pdftoppm", pdftoppm), ("tesseract", tesseract)) if not path]
    if missing:
        raise RuntimeError("OCR backend unavailable: " + ", ".join(missing))
    with tempfile.TemporaryDirectory(prefix="researchos-ocr-") as temporary:
        prefix = str(Path(temporary) / "page")
        rendered = subprocess.run(
            [pdftoppm, "-f", str(page_number), "-l", str(page_number), "-singlefile", "-png", "-r", str(dpi), str(pdf), prefix],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
        if rendered.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {rendered.stderr.strip()}")
        image = prefix + ".png"
        recognized = subprocess.run(
            [tesseract, image, "stdout", "-l", lang],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
        if recognized.returncode != 0:
            raise RuntimeError(f"tesseract failed: {recognized.stderr.strip()}")
        return recognized.stdout.strip()


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# PDF extraction",
        "",
        f"- Source: `{result['input']['locator']}`",
        f"- SHA-256: `{result['input']['checksum']}`",
        f"- Pages: {', '.join(map(str, result['selected_pages']))}",
        "",
    ]
    for page in result["pages"]:
        lines.extend(
            [
                f"## Page {page['page_number']}",
                "",
                f"Extraction: `{page['extraction_method']}`; layout: `{page['layout']}`",
                "",
                page["text"] or "[no text extracted]",
                "",
            ]
        )
    if result["captions"]:
        lines.extend(["## Captions", ""])
        lines.extend(
            f"- p.{item['page']} **{item['label']}**: {item['text']}"
            for item in result["captions"]
        )
        lines.append("")
    return "\n".join(lines)


def extract(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import pdfplumber
    except ImportError as error:
        raise RuntimeError(
            'PDF extraction requires the optional dependency: pip install -e ".[pdf]"'
        ) from error

    source = Path(args.pdf)
    warnings: list[str] = []
    pages: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    captions: list[dict[str, Any]] = []
    supplement_mentions: list[dict[str, Any]] = []

    with pdfplumber.open(source) as document:
        selected = parse_page_spec(args.pages, len(document.pages))
        for page_number in selected:
            page = document.pages[page_number - 1]
            words = page.extract_words(use_text_flow=False, keep_blank_chars=False) or []
            native_text, detected_layout = words_to_text(
                words, float(page.width), float(page.height), args.layout
            )
            text = native_text.strip()
            method = "native-text"
            needs_ocr = args.ocr == "always" or (
                args.ocr == "auto" and len(re.sub(r"\s+", "", text)) < args.min_native_chars
            )
            if needs_ocr:
                try:
                    text = ocr_page(source, page_number, args.ocr_lang, args.ocr_dpi)
                    method = "ocr"
                    detected_layout = "ocr-reading-order"
                except RuntimeError as error:
                    if args.ocr == "always":
                        raise
                    warnings.append(f"page {page_number}: {error}; retained native extraction")
            pages.append(
                {
                    "page_number": page_number,
                    "extraction_method": method,
                    "layout": detected_layout,
                    "character_count": len(text),
                    "text": text,
                }
            )
            captions.extend(extract_captions(text, page_number))
            supplement_mentions.extend(extract_supplement_mentions(text, page_number))
            if not args.no_tables:
                for table_index, table in enumerate(page.extract_tables() or [], start=1):
                    normalized = normalize_table(table)
                    if normalized:
                        tables.append(
                            {"page": page_number, "table_index": table_index, "rows": normalized}
                        )

        return {
            "artifact_type": "pdf-extraction",
            "schema_version": "1.0.0",
            "input": {
                "kind": "file",
                "locator": str(source.resolve()),
                "checksum": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest(),
            },
            "page_count": len(document.pages),
            "selected_pages": selected,
            "pages": pages,
            "tables": tables,
            "captions": captions,
            "supplementary_mentions": supplement_mentions,
            "warnings": warnings,
            "provenance": {
                "created_by": "literature-reader/scripts/extract_pdf.py",
                "tool_version": VERSION,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "command": " ".join(
                    ["extract_pdf.py", *sys.argv[1:]]
                    if sys.argv[1:]
                    else ["extract_pdf.py", str(source)]
                ),
                "seed": None,
                "sources": [
                    {
                        "kind": "file",
                        "locator": str(source.resolve()),
                        "checksum": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest(),
                    }
                ],
                "warnings": warnings,
            },
        }


def validate_paths(args: argparse.Namespace) -> None:
    source = Path(args.pdf)
    if not source.is_file():
        raise ValueError(f"input PDF not found: {source}")
    if source.suffix.lower() != ".pdf":
        raise ValueError("input must use the .pdf extension")
    outputs = [Path(path) for path in (args.out, args.markdown_out) if path]
    if len({path.resolve() for path in outputs}) != len(outputs):
        raise ValueError("--out and --markdown-out must be different files")
    if any(path.resolve() == source.resolve() for path in outputs):
        raise ValueError("output must not replace the input PDF")
    existing = [path for path in outputs if path.exists()]
    if existing and not args.force:
        raise ValueError(f"output exists: {existing[0]}; use --force to replace it")
    if args.ocr_dpi < 72 or args.ocr_dpi > 600:
        raise ValueError("--ocr-dpi must be between 72 and 600")
    if args.min_native_chars < 0:
        raise ValueError("--min-native-chars must be nonnegative")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validate_paths(args)
        result = extract(args)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(payload, end="")
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"written: {args.out}", file=sys.stderr)
    if args.markdown_out:
        Path(args.markdown_out).write_text(render_markdown(result), encoding="utf-8")
        print(f"written: {args.markdown_out}", file=sys.stderr)
    for warning in result["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
