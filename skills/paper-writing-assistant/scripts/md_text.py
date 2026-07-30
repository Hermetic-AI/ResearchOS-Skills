#!/usr/bin/env python3
"""
md_text.py — Zero-dependency extractor of plain text from .md files, locates the reference list, and extracts in-text citation markers (Markdown-symmetric version for citation checking, with the same interface as docx_text.py).

Uses only the Python standard library. Usage:
    python3 md_text.py thesis.md                 # overview: line count / reference count / citation number check
    python3 md_text.py thesis.md --refs           # output only the reference list (with numbering)
    python3 md_text.py thesis.md --cites          # output only the in-text citation number check
    python3 md_text.py thesis.md --dump out.txt [--force] # save plain text to out.txt; no overwrite by default
    python3 md_text.py thesis.md --json           # structured JSON

Key design (aligned with docx_text.py):
  1. Strip YAML frontmatter and fenced code blocks (```/~~~) first, so in-text [n]
     citations are not polluted by code-block noise.
  2. In-text [n] citations may still be mixed with array-dimension noise (e.g. [4096]).
     After obtaining the reference count R, 1..R are treated as valid citation numbers;
     numbers > R are listed separately as "suspected noise / dangling citations".
  3. Markdown reference entries are identified by leading numbering ([1] / 1. / 1) etc.);
  headings match the reference section heading (Chinese equivalent / "References" / "Bibliography").
"""
import sys
import os
import re
import json

REF_HEAD_RE = re.compile(
    r"^\s*#*\s*(参\s*考\s*文\s*献|references|bibliography)\s*#*\s*$",
    re.IGNORECASE)
STOP_HEAD_RE = re.compile(
    r"^\s*#*\s*(致\s*谢|攻读|在读期间|读期间|附录|作者简介|个人简历|个人简介|"
    r"acknowledg|appendix)", re.IGNORECASE)
# Citation markers: [1] [1-3] [1,2] [1，2] [1-3,5], allowing both English and Chinese commas
CITE_RE = re.compile(r"\[(\d[\d,，\-\s]*)\]")
# Reference entry leading numbering: [1] / [1]. / 1. / 1) / 1、 (number may be followed without space, e.g. [1]Zhang.)
REF_ITEM_RE = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.)、])\s*\S")


def strip_markdown(text):
    """Remove frontmatter and fenced code blocks, return body line list (original line
    number info not needed; citation checking only looks at the set)."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break
    out = []
    in_fence = False
    for line in lines:
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(line)
    return out


def expand_nums(inner):
    """Expand '1-3,5' into [1,2,3,5]."""
    nums = set()
    for part in re.split(r"[,，]", inner):
        part = part.strip()
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b - a < 500:  # guard against abnormally large ranges
                nums.update(range(a, b + 1))
        elif part.isdigit():
            nums.add(int(part))
    return nums


def analyze(path):
    with open(path, encoding="utf-8") as fh:
        texts = strip_markdown(fh.read())
    full = "\n".join(texts)

    # ---- Locate the reference list (take the last matching heading) ----
    ref_idx = None
    for i, t in enumerate(texts):
        if REF_HEAD_RE.match(t.strip()):
            ref_idx = i
    refs = []
    if ref_idx is not None:
        for t in texts[ref_idx + 1:]:
            s = t.strip()
            if not s:
                continue
            if STOP_HEAD_RE.match(s):
                break
            if REF_ITEM_RE.match(s):
                refs.append(s)
    R = len(refs)

    # ---- In-text citation markers (excluding the reference list region itself) ----
    body_end = ref_idx if ref_idx is not None else len(texts)
    cited = set()
    for t in texts[:body_end]:
        for m in CITE_RE.finditer(t):
            cited |= expand_nums(m.group(1))
    valid = sorted(n for n in cited if 1 <= n <= R) if R else sorted(cited)
    noise = sorted(n for n in cited if R and n > R)
    uncited = [n for n in range(1, R + 1) if n not in cited] if R else []

    return {
        "file": path, "paragraphs": len(texts), "ref_count": R,
        "ref_index": ref_idx, "references": refs,
        "cited_valid": valid, "cited_noise": noise, "uncited": uncited,
        "full_text": full,
    }


def overview(r):
    L = [f"# Citation extraction overview: {r['file']}",
         f"- Total lines (without frontmatter/code blocks): {r['paragraphs']}",
         f"- Reference list: {'starting at line %d' % r['ref_index'] if r['ref_index'] is not None else 'not located'}, {r['ref_count']} entries total",
         f"- Valid in-text citation numbers (1..{r['ref_count']}): {len(r['cited_valid'])} found",
         f"- Suspected noise / dangling citations (number > {r['ref_count']}): {r['cited_noise'] or 'none'}",
         f"- Never-cited entries in reference list (orphans): {r['uncited'] or 'none'}"]
    if r["ref_index"] is None:
        L.append("\n⚠️ Reference list heading not located; "
                 "dimension 1 checking unavailable; for dimensions 2/3/4, manually specify "
                 "the reference list range first.")
    return "\n".join(L)


def main():
    # Windows GBK console would crash printing ⚠️ etc.; force UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if "--version" in sys.argv[1:]:
        print("md_text.py 0.1.0")
        return 0
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print(__doc__.strip())
        return 0
    if len(sys.argv) < 2:
        print("error: provide an input Markdown file; use --help for usage", file=sys.stderr)
        return 2
    path = sys.argv[1]
    flags = sys.argv[2:]
    if not os.path.isfile(path):
        sys.exit(f"error: file not found: {path}")
    r = analyze(path)

    if "--dump" in flags:
        i = flags.index("--dump")
        if i + 1 >= len(flags):
            sys.exit("error: --dump requires an output file path argument")
        out = flags[i + 1]
        if os.path.abspath(out) == os.path.abspath(path):
            sys.exit("error: --dump cannot overwrite the input Markdown")
        if os.path.exists(out) and "--force" not in flags:
            sys.exit(f"error: output already exists: {out}; add --force to overwrite")
        open(out, "w", encoding="utf-8").write(r["full_text"])
        print(f"Full text written to {out} ({len(r['full_text'])} chars)")
        return 0
    if "--json" in flags:
        r2 = {k: v for k, v in r.items() if k != "full_text"}
        print(json.dumps(r2, ensure_ascii=False, indent=2))
        return 0
    if "--refs" in flags:
        # Entries may carry their own [N]/1. prefix; strip it before renumbering to avoid double numbering
        for i, ref in enumerate(r["references"], 1):
            ref = re.sub(r"^\s*(?:\[\d+\]|\d+[.)、])\s*", "", ref)
            print(f"[{i}] {ref}")
        return 0
    if "--cites" in flags:
        print("Valid in-text citation numbers:", r["cited_valid"])
        print("Suspected noise / dangling:", r["cited_noise"])
        print("Orphan (never cited) entries:", r["uncited"])
        return 0
    print(overview(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
