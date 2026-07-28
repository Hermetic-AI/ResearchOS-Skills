#!/usr/bin/env python3
"""Extract bibliographic metadata from pasted reference text or PDF-exported text.

Purpose
    Given a plain-text file containing either a reference list (bibliography
    section) or arbitrary PDF-exported text, split it into individual reference
    entries and extract structured metadata (DOI, title, authors, year) from
    each entry using regular expressions only.

Dependencies
    None. Python 3.8+ standard library only (re, json, sys, argparse).

CLI usage
    python3 extract_metadata.py <input.txt> [--pretty] [--mode auto|list|text]
                                            [--format json|bibtex|ris]
    python3 extract_metadata.py <input.bib> --from-bibtex [--pretty]

    <input>       UTF-8 text file: a pasted reference list, PDF-exported text,
                  or (with --from-bibtex) a BibTeX file.
    --pretty      Pretty-print JSON output (2-space indent).
    --mode        Entry splitting mode:
                  auto - detect numbering style (default)
                  list - force reference-list splitting ([1] / 1. / (Author, Year))
                  text - treat the whole file as one blob (single-paper PDF text)
    --format      Output format: json (default), bibtex, or ris.
                  bibtex/ris render each extracted entry as one record;
                  unresolved fields are omitted, never fabricated.
    --from-bibtex Parse the input as BibTeX entries and emit the same JSON
                  structure as normal extraction (round-trip path).

Output format (JSON to stdout, default)
    {
      "mode": "list" | "text" | "bibtex",
      "numbering": "bracket" | "dot" | "author-year" | "none",
      "entry_count": <int>,
      "entries": [
        {
          "index": <int>,              # 0-based order in the list
          "label": "[1]" | "1." | "(Smith, 2020)" | null,
          "raw": "<original entry text, whitespace-normalized>",
          "doi": "10.xxxx/yyyy" | null,
          "arxiv_id": "2103.12345" | null,
          "year": <int> | null,        # 1900-2099
          "title": "<best-effort title>" | null,
          "authors": ["<name>", ...],  # best-effort; empty list if none found
          "citation_key": "Smith 2020" # short key for matrix/notes; null if unknown
        }, ...
      ],
      "warnings": ["<human-readable parsing caveat>", ...]
    }

    BibTeX output: one @article entry per input entry, key derived from
    citation_key ("Smith2020"), fields limited to author/title/year/doi/eprint
    (arXiv). RIS output: TY JOUR records with AU/TI/T1, PY, DO fields.
    Entries with neither title nor authors are skipped with a warning.

Notes
    - Extraction is heuristic. Fields that cannot be resolved are null and a
      warning is emitted; downstream consumers must not treat nulls as absent.
    - Fully deterministic: no randomness, no network, no clock dependence.
"""

import argparse
import json
import re
import sys

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>]+)", re.IGNORECASE)
ARXIV_RE = re.compile(r"\b(?:arXiv:)?(\d{4}\.\d{4,5})(?:v\d+)?\b")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
BRACKET_LABEL_RE = re.compile(r"^\s*\[(\d{1,4})\]\s*")
DOT_LABEL_RE = re.compile(r"^\s*(\d{1,3})\.\s+")
AUTHOR_YEAR_LABEL_RE = re.compile(
    r"^\s*\(\s*([A-Z][A-Za-z'`-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'`-]+)*"
    r"(?:\s+et\s+al\.?)?)\s*,\s*((?:19|20)\d{2}[a-z]?)\s*\)\s*"
)
# A name like "Smith, J." / "J. Smith" / "van der Berg, Alice"
NAME_RE = re.compile(
    r"(?:[A-Z][A-Za-z'`-]+,\s*)?(?:[A-Z]\.\s*)*[A-Z][A-Za-z'`-]+"
    r"|(?:[A-Z]\.\s*)+[A-Z][A-Za-z'`-]+"
)
QUOTED_TITLE_RE = re.compile(r'["\u201c\u201d]([^"\u201c\u201d]{10,300})["\u201c\u201d]')


def normalize_ws(text):
    return re.sub(r"\s+", " ", text).strip()


def detect_numbering(lines):
    """Guess the numbering style of a reference list from its lines."""
    bracket = sum(1 for ln in lines if BRACKET_LABEL_RE.match(ln))
    dot = sum(1 for ln in lines if DOT_LABEL_RE.match(ln))
    if bracket >= 2 and bracket >= dot:
        return "bracket"
    if dot >= 2:
        return "dot"
    return "none"


def split_entries(text, mode):
    """Split text into (label, body) reference entries.

    Supports three numbering patterns:
      bracket    [1] ...
      dot        1. ...
      author-year (Smith, 2020) ...  -- or bare APA-style "Smith, J. (2020)."
    Falls back to blank-line / line-based splitting when unnumbered.
    """
    if mode == "text":
        return [("none", None, text)]

    # Unwrap hard-wrapped lines: a new entry starts at a numbered label or
    # an (Author, Year) opener; other lines continue the previous entry.
    raw_lines = [ln for ln in text.replace("\r\n", "\n").split("\n")]
    numbering = detect_numbering(raw_lines)
    entries = []
    cur_label, cur_lines = None, []
    saw_author_year = False

    def flush():
        if cur_lines:
            entries.append((cur_label, " ".join(cur_lines)))

    for ln in raw_lines:
        stripped = ln.strip()
        if not stripped:
            continue
        label = None
        m = None
        if numbering == "bracket":
            m = BRACKET_LABEL_RE.match(ln)
            label = m and m.group(0).strip()
        elif numbering == "dot":
            m = DOT_LABEL_RE.match(ln)
            label = m and m.group(0).strip()
        if m is None:
            m = AUTHOR_YEAR_LABEL_RE.match(ln)
            label = m and ("(" + m.group(1) + ", " + m.group(2) + ")")
            if m:
                saw_author_year = True
        if m is not None:
            flush()
            cur_label = label
            cur_lines = [ln[m.end():].strip()]
            continue
        # APA-style bare author-year: line starts with names then (Year).
        if numbering == "none" and re.match(
            r"^[A-Z][A-Za-z'`-]+,.*\((?:19|20)\d{2}[a-z]?\)\.", stripped
        ):
            flush()
            cur_label = None
            cur_lines = [stripped]
            continue
        cur_lines.append(stripped)
    flush()

    if entries:
        if numbering == "none" and saw_author_year:
            numbering = "author-year"
        return [(numbering, label, body) for label, body in entries]
    # Last resort: split on blank-line-separated paragraphs.
    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    return [(numbering, None, normalize_ws(b)) for b in blocks]


def extract_doi(text):
    m = DOI_RE.search(text)
    if not m:
        return None
    # Strip trailing punctuation commonly glued on by PDF export.
    return m.group(1).rstrip(".,;)")


def extract_arxiv(text):
    m = ARXIV_RE.search(text)
    return m.group(1) if m else None


def extract_year(text):
    # Remove arXiv ids and DOIs first so their digits are not read as years.
    cleaned = ARXIV_RE.sub(" ", DOI_RE.sub(" ", text))
    years = [int(y) for y in YEAR_RE.findall(cleaned) if 1900 <= int(y) <= 2099]
    return min(years) if years else None


def extract_title(text, doi):
    """Best-effort title.

    Heuristics, in order:
      1. Text inside double quotes / curly quotes.
      2. First sentence-like segment (in reference order the title precedes the
         venue) that does not look like an author list or an "In <venue>" lead-in.
    """
    m = QUOTED_TITLE_RE.search(text)
    if m:
        return m.group(1).strip()
    cleaned = text
    if doi:
        cleaned = cleaned.replace(doi, " ")
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    cleaned = ARXIV_RE.sub(" ", cleaned)
    # Split into rough segments on '. ' and ';'.
    segments = re.split(r"(?<=[.!?])\s+|;\s*", cleaned)
    for seg in segments:
        seg = seg.strip(" .\"'")
        words = seg.split()
        if len(words) < 4 or len(seg) > 300:
            continue
        # Skip segments that look like an author list: every comma-part is a
        # name token (surname / initials / "et al").
        parts = [p.strip() for p in seg.split(",") if p.strip()]
        name_like = all(
            re.fullmatch(r"(?:[A-Z]\.\s*)*[A-Z][A-Za-z'`-]*\.?|[A-Z]\.?", re.sub(r"^(?:and|&)\s+", "", p, flags=re.IGNORECASE))
            or p.lower().startswith("et al")
            for p in parts
        )
        if parts and name_like and (seg.count(",") >= 1 or "et al" in seg.lower()):
            continue
        if re.match(r"^(In|Proc\.?|Proceedings)\b", seg):
            continue
        # Trim a trailing venue/pages tail glued to the title by commas.
        seg = re.split(
            r",\s*(?=Journal\b|Proc\.|Proceedings\b|Advances\b|IEEE\b|ACM\b|"
            r"Nature\b|Science\b|doi|[^,]*\b\d{3,})",
            seg,
            maxsplit=1,
        )[0].strip(" ,")
        if len(seg.split()) < 2:
            continue
        return seg
    return None


def extract_authors(text, label):
    """Best-effort author extraction from the leading part of an entry.

    Note: entry bodies from split_entries no longer contain their label, so
    the label is only used as a fallback name source for (Author, Year) lists.
    """
    if label and label.startswith("("):
        raw = label.strip("()")
        raw = re.sub(r",?\s*(?:19|20)\d{2}[a-z]?\s*$", "", raw)
        raw = re.sub(r"\s+et\s+al\.?$", "", raw)
        parts = re.split(r"\s+(?:and|&)\s+", raw)
        return [p.strip() for p in parts if p.strip()]
    # Consecutive "Surname, I." pairs from the head of the entry.
    zone = text[:250]
    authors = []
    pos = 0
    pair_re = re.compile(r"([A-Z][A-Za-z'`-]+),\s*((?:[A-Z]\.\s*)+)")
    while True:
        m = pair_re.match(zone, pos)
        if not m:
            break
        authors.append(m.group(1) + ", " + m.group(2).strip())
        pos = m.end()
        sep = re.match(r"[\s,;]*(?:(?:and|&)\s+)?", zone[pos:])
        if not sep:
            break
        pos += sep.end()
    if authors:
        return authors[:20]
    # Fallback: "First Last, First Last" style (common in PDF front pages).
    head = zone.split("\n")[0] if "\n" in zone else zone
    head = re.split(r"\s{2,}|\bAbstract\b|(?:19|20)\d{2}", head)[0]
    names = [
        c.strip()
        for c in re.split(r",|\band\b", head)
        if re.fullmatch(r"[A-Z][a-z'`-]+\s+[A-Z][A-Za-z'`-]+", c.strip())
    ]
    return names[:20]


def citation_key(authors, year):
    if not authors:
        return None
    first = authors[0].split(",")[0].split()[-1]
    suffix = " et al." if len(authors) > 1 else ""
    return first + suffix + (" " + str(year) if year else "")


def bibtex_key(entry):
    base = re.sub(r"[^A-Za-z0-9]", "", entry["citation_key"] or "")
    return base or "entry%d" % entry["index"]


def to_bibtex_author(name):
    """Render an extracted author name as BibTeX ('Last, First' kept as-is)."""
    if "," in name:
        return name
    parts = name.split()
    if len(parts) >= 2:
        return parts[-1] + ", " + " ".join(parts[:-1])
    return name


def entry_to_bibtex(entry):
    lines = ["@" + ("article" if not entry["arxiv_id"] else "misc") +
             "{" + bibtex_key(entry) + ","]
    if entry["authors"]:
        lines.append("  author = {" + " and ".join(to_bibtex_author(a) for a in entry["authors"]) + "},")
    if entry["title"]:
        lines.append("  title = {" + entry["title"] + "},")
    if entry["year"]:
        lines.append("  year = {" + str(entry["year"]) + "},")
    if entry["doi"]:
        lines.append("  doi = {" + entry["doi"] + "},")
    if entry["arxiv_id"]:
        lines.append("  eprint = {" + entry["arxiv_id"] + "},")
        lines.append("  archivePrefix = {arXiv},")
    lines.append("}")
    return "\n".join(lines)


def entry_to_ris(entry):
    lines = ["TY  - JOUR"]
    for a in entry["authors"]:
        lines.append("AU  - " + to_bibtex_author(a))
    if entry["title"]:
        lines.append("TI  - " + entry["title"])
        lines.append("T1  - " + entry["title"])
    if entry["year"]:
        lines.append("PY  - " + str(entry["year"]))
    if entry["doi"]:
        lines.append("DO  - " + entry["doi"])
    if entry["arxiv_id"]:
        lines.append("UR  - https://arxiv.org/abs/" + entry["arxiv_id"])
    lines.append("ER  -")
    return "\n".join(lines)


BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\}", re.DOTALL)
BIB_FIELD_RE = re.compile(r"(\w+)\s*=\s*[\{\"](.*?)[\}\"]\s*,?\s*(?:\n|$)", re.DOTALL)


def parse_bibtex(text):
    """Parse BibTeX entries back into the extraction JSON structure."""
    entries = []
    warnings = []
    for idx, m in enumerate(BIB_ENTRY_RE.finditer(text)):
        body = m.group(3)
        fields = {}
        for fm in BIB_FIELD_RE.finditer(body):
            fields[fm.group(1).lower()] = normalize_ws(fm.group(2))
        authors = [normalize_ws(a) for a in re.split(r"\s+and\s+", fields.get("author", "")) if a.strip()]
        year = None
        if fields.get("year"):
            ym = YEAR_RE.search(fields["year"])
            year = int(ym.group(1)) if ym else None
        eprint = fields.get("eprint")
        if not eprint and fields.get("archiveprefix", "").lower() == "arxiv" and fields.get("url"):
            am = ARXIV_RE.search(fields["url"])
            eprint = am.group(1) if am else None
        entry = {
            "index": idx,
            "label": m.group(2).strip(),
            "raw": normalize_ws(m.group(0)),
            "doi": fields.get("doi"),
            "arxiv_id": eprint,
            "year": year,
            "title": fields.get("title"),
            "authors": authors,
            "citation_key": citation_key(authors, year),
        }
        if entry["title"] is None:
            warnings.append("bib entry %s: no title field" % entry["label"])
        entries.append(entry)
    if not entries:
        warnings.append("no BibTeX entries matched; check the input is a .bib file")
    return entries, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract DOI/title/authors/year from reference text (regex-only, zero dependencies)."
    )
    parser.add_argument("input", help="UTF-8 text file with a reference list, PDF-exported text, or .bib file")
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    parser.add_argument(
        "--mode",
        choices=["auto", "list", "text"],
        default="auto",
        help="entry splitting mode (default: auto)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "bibtex", "ris"],
        default="json",
        help="output format (default: json)",
    )
    parser.add_argument(
        "--from-bibtex",
        action="store_true",
        help="parse input as BibTeX and emit the extraction JSON",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(json.dumps({"error": "cannot read input: %s" % exc}), file=sys.stderr)
        return 2
    if not text.strip():
        print(json.dumps({"error": "input file is empty"}), file=sys.stderr)
        return 2

    if args.from_bibtex:
        entries, warnings = parse_bibtex(text)
        result = {
            "mode": "bibtex",
            "numbering": "none",
            "entry_count": len(entries),
            "entries": entries,
            "warnings": warnings,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    mode = args.mode
    warnings = []
    if mode == "auto":
        numbering = detect_numbering(text.splitlines())
        year_hits = len(YEAR_RE.findall(text))
        ay_hits = sum(1 for ln in text.splitlines() if AUTHOR_YEAR_LABEL_RE.match(ln))
        mode = "list" if (numbering != "none" or ay_hits >= 1 or year_hits >= 3) else "text"

    raw_entries = split_entries(text, mode)
    numbering = raw_entries[0][0] if raw_entries else "none"
    if mode == "list" and numbering == "none":
        warnings.append("no numbering pattern detected; fell back to paragraph splitting")

    entries = []
    for idx, (_, label, body) in enumerate(raw_entries):
        body = normalize_ws(body)
        if len(body) < 15:
            continue
        # Include the label in the scan text: for (Author, Year) lists the year
        # only appears in the label.
        full = (label + " " + body) if label else body
        doi = extract_doi(full)
        year = extract_year(full)
        authors = extract_authors(body, label)
        entry = {
            "index": idx,
            "label": label,
            "raw": body,
            "doi": doi,
            "arxiv_id": extract_arxiv(body),
            "year": year,
            "title": extract_title(body, doi),
            "authors": authors,
            "citation_key": citation_key(authors, year),
        }
        if entry["title"] is None:
            warnings.append("entry %d: title not resolved" % idx)
        if not authors:
            warnings.append("entry %d: authors not resolved" % idx)
        entries.append(entry)

    if args.format in ("bibtex", "ris"):
        render = entry_to_bibtex if args.format == "bibtex" else entry_to_ris
        rendered = []
        for entry in entries:
            if not entry["title"] and not entry["authors"]:
                warnings.append("entry %d skipped in %s output: no title or authors" % (entry["index"], args.format))
                continue
            rendered.append(render(entry))
        sys.stderr.write("".join("warning: %s\n" % w for w in warnings))
        print("\n\n".join(rendered))
        return 0

    result = {
        "mode": mode,
        "numbering": numbering,
        "entry_count": len(entries),
        "entries": entries,
        "warnings": warnings,
    }
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
