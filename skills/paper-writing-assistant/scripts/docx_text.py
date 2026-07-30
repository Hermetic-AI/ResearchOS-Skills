#!/usr/bin/env python3
"""
docx_text.py — Zero-dependency extractor of full .docx text, locates the reference list, and extracts in-text citation markers (for citation checking).

Uses only the Python standard library. Usage:
    python3 docx_text.py thesis.docx                 # overview: paragraph count / reference count / citation number check
    python3 docx_text.py thesis.docx --refs           # output only the reference list (with numbering)
    python3 docx_text.py thesis.docx --cites          # output only the in-text citation number check
    python3 docx_text.py thesis.docx --dump out.txt [--force] # save full text to out.txt; no overwrite by default
    python3 docx_text.py thesis.docx --json           # structured JSON

Key design (lessons from real-world citation checking):
  1. In-text [n] citations can be mixed with noise such as tensor dimensions (e.g. [4096]).
     After obtaining the reference count R, numbers 1..R are treated as valid citation
     numbers; markers > R are listed separately as "suspected noise / dangling citations"
     so they don't pollute the correspondence check.
  2. EndNote/field citations: the display text of fields is sometimes extractable (this
     script tries its best), but sometimes only the field code is present and nothing is
     extractable — if almost no [n] markers are found in the text but the reference list
     has many entries, the script explicitly warns "suspected field citations; convert to
     plain text and re-run".
  3. Superscript runs containing digits are also captured as a supplementary source of
     citation markers.
"""
import sys
import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

REF_HEAD_RE = re.compile(r"^\s*参\s*考\s*文\s*献\s*$")
STOP_HEAD_RE = re.compile(r"^\s*(致\s*谢|攻读|在读期间|读期间|附录|作者简介|个人简历|个人简介)")
# Citation markers: [1] [1-3] [1,2] [1，2] [1-3,5], allowing both English and Chinese commas
CITE_RE = re.compile(r"\[(\d[\d,，\-\s]*)\]")


def q(el, path):
    return el.find(path.replace("w:", W))


def paragraphs(root):
    """Return [(text, superscript_run_text), ...], also collecting text from superscript runs."""
    out = []
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t"))
        sup_text = ""
        for r in p.iter(W + "r"):
            rpr = q(r, "w:rPr")
            va = q(rpr, "w:vertAlign") if rpr is not None else None
            if va is not None and va.get(W + "val") == "superscript":
                sup_text += "".join(t.text or "" for t in r.iter(W + "t"))
        out.append((text, sup_text))
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
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    paras = paragraphs(root)
    texts = [t for t, _ in paras]
    full = "\n".join(texts)

    # ---- Locate the reference list ----
    ref_idx = None
    for i, t in enumerate(texts):
        if REF_HEAD_RE.match(t.strip()) and len(t.strip()) <= 8:
            ref_idx = i  # take the last match (body text may mention "参考文献")
    refs = []
    if ref_idx is not None:
        for t in texts[ref_idx + 1:]:
            s = t.strip()
            if not s:
                continue
            if STOP_HEAD_RE.match(s):
                break
            refs.append(s)
    R = len(refs)

    # ---- In-text citation markers (excluding the reference list region itself) ----
    body_end = ref_idx if ref_idx is not None else len(texts)
    cited = set()
    sup_hits = 0
    for t, sup in paras[:body_end]:
        for m in CITE_RE.finditer(t):
            cited |= expand_nums(m.group(1))
        if re.search(r"\d", sup):
            sup_hits += 1
    valid = sorted(n for n in cited if 1 <= n <= R) if R else sorted(cited)
    noise = sorted(n for n in cited if R and n > R)
    uncited = [n for n in range(1, R + 1) if n not in cited] if R else []

    # Field citation heuristic: many references but almost no numbers extracted from body
    field_suspected = R >= 10 and len(valid) < max(3, R * 0.2)

    return {
        "file": path, "paragraphs": len(texts), "ref_count": R,
        "ref_index": ref_idx, "references": refs,
        "cited_valid": valid, "cited_noise": noise, "uncited": uncited,
        "superscript_paras": sup_hits, "field_citation_suspected": field_suspected,
        "full_text": full,
    }


def overview(r):
    L = [f"# Citation extraction overview: {r['file']}",
         f"- Total paragraphs: {r['paragraphs']}",
         f"- Reference list: {'starting at paragraph %d' % r['ref_index'] if r['ref_index'] is not None else 'not located'}, {r['ref_count']} entries total",
         f"- Valid in-text citation numbers (1..{r['ref_count']}): {len(r['cited_valid'])} found",
         f"- Suspected noise / dangling citations (number > {r['ref_count']}): {r['cited_noise'] or 'none'}",
         f"- Never-cited entries in reference list (orphans): {r['uncited'] or 'none'}",
         f"- Paragraphs containing superscript digits: {r['superscript_paras']}"]
    if r["field_citation_suspected"]:
        L.append("\n⚠️ Suspected EndNote/field citations: far fewer citation numbers "
                 "extracted from the body than reference entries. Dimension 1 "
                 "(body↔reference one-to-one correspondence) is unreliable; in Word, "
                 "please \"update fields → select all → Ctrl+Shift+F9 to convert to a "
                 "plain-text copy\" and re-run this script.")
    return "\n".join(L)


def main():
    # Windows GBK console would crash printing ⚠️ etc.; force UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if "--version" in sys.argv[1:]:
        print("docx_text.py 0.1.0")
        return 0
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print(__doc__.strip())
        return 0
    if len(sys.argv) < 2:
        print("error: provide an input .docx; use --help for usage", file=sys.stderr)
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
            sys.exit("error: --dump cannot overwrite the input .docx")
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
