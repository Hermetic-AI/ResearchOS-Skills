#!/usr/bin/env python3
"""
docx_inspect.py — Zero-dependency extractor of real formatting properties from .docx files, for paper format checking.

Uses only the Python standard library (zipfile + xml.etree), no python-docx / pandoc required.
Usage:
    python3 docx_inspect.py path/to/thesis.docx [--json]

Output (default human-readable; add --json for structured JSON):
  - Default body font / size / line spacing (docDefaults parsing)
  - Page margins, paper size, page numbers per section
  - Heading styles (font/size/bold/alignment/outline level)
  - Body paragraph sampling (font/size/line spacing/alignment/first-line indent) frequency counts
  - Figure/table caption paragraph sampling
  - Effective styles (effective_styles): merge parent style properties along the basedOn chain

Point size conversion: Word's internal w:sz unit is "half-points"; value/2 = points (pt).
EMU/twips: page margin w:pgMar unit is twips (1/1440 inch).
"""
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

# Caption pattern: a Chinese or English figure/table keyword must be immediately
# followed by a number (1, 1.1, 1-1) to count as a caption — avoids misclassifying
# body text that merely starts with a figure/table keyword as a caption.
CAPTION_RE = re.compile(r"^\s*(图|表|附图|附表|Fig\.?|Figure|Table|Tab\.?)\s?\d+([.\-]\d+)*",
                        re.IGNORECASE)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# pt -> Chinese type-size name (approximate)
PT_TO_CN = {
    42: "Primary", 36: "Small Primary", 26: "1st size", 24: "Small 1st",
    22: "2nd size", 18: "Small 2nd", 16: "3rd size", 15: "Small 3rd",
    14: "4th size", 12: "Small 4th", 10.5: "5th size", 9: "Small 5th",
    7.5: "6th size", 6.5: "Small 6th",
}


def cn_size(pt):
    if pt is None:
        return None
    name = PT_TO_CN.get(pt)
    return f"{pt}pt" + (f" ({name})" if name else "")


def half_to_pt(v):
    try:
        return int(v) / 2
    except (TypeError, ValueError):
        return None


def twip_to_cm(v):
    try:
        return round(int(v) / 1440 * 2.54, 2)
    except (TypeError, ValueError):
        return None


def q(el, path):
    return el.find(path.replace("w:", W))


def qa(el, path):
    return el.findall(path.replace("w:", W))


def attr(el, name):
    if el is None:
        return None
    return el.get(W + name)


def read_xml(z, name):
    try:
        return ET.fromstring(z.read(name))
    except KeyError:
        return None


def rpr_font(rpr):
    """Extract font name (East Asian / Western), size in pt, bold, italic from rPr."""
    if rpr is None:
        return {}
    out = {}
    rfonts = q(rpr, "w:rFonts")
    if rfonts is not None:
        out["font_ascii"] = attr(rfonts, "ascii")
        out["font_eastasia"] = attr(rfonts, "eastAsia")
    sz = q(rpr, "w:sz")
    if sz is not None:
        out["size_pt"] = half_to_pt(attr(sz, "val"))
    szcs = q(rpr, "w:szCs")
    if szcs is not None and "size_pt" not in out:
        out["size_pt"] = half_to_pt(attr(szcs, "val"))
    b = q(rpr, "w:b")
    if b is not None:
        out["bold"] = attr(b, "val") not in ("0", "false")
    i = q(rpr, "w:i")
    if i is not None:
        out["italic"] = attr(i, "val") not in ("0", "false")
    return out


def ppr_para(ppr):
    """Extract line spacing, alignment, first-line indent, outline level, style reference from pPr."""
    if ppr is None:
        return {}
    out = {}
    spacing = q(ppr, "w:spacing")
    if spacing is not None:
        line = attr(spacing, "line")
        rule = attr(spacing, "lineRule")
        if line is not None:
            if rule in ("auto", None):
                # 240 = single spacing
                out["line_spacing"] = f"{round(int(line) / 240, 2)}x"
            else:  # atLeast / exact, unit twips
                out["line_spacing"] = f"{round(int(line) / 20, 1)}pt({rule})"
    jc = q(ppr, "w:jc")
    if jc is not None:
        out["align"] = attr(jc, "val")
    ind = q(ppr, "w:ind")
    if ind is not None:
        fl = attr(ind, "firstLine") or attr(ind, "firstLineChars")
        if fl is not None:
            out["first_line_indent"] = fl
    outline = q(ppr, "w:outlineLvl")
    if outline is not None:
        out["outline_level"] = attr(outline, "val")
    pstyle = q(ppr, "w:pStyle")
    if pstyle is not None:
        out["style"] = attr(pstyle, "val")
    return out


# ---------------------------------------------------------------------------
# Effective-style computation
# ---------------------------------------------------------------------------

def _rpr_to_dict(rpr):
    """Convert a <w:rPr> element into a flat property dict (lower-level keys)."""
    if rpr is None:
        return {}
    out = {}
    rfonts = q(rpr, "w:rFonts")
    if rfonts is not None:
        for key in ("ascii", "eastAsia", "hAnsi", "cs"):
            val = attr(rfonts, key)
            if val is not None:
                out[f"font_{key.lower()}"] = val
    sz = q(rpr, "w:sz")
    if sz is not None:
        out["size_pt"] = half_to_pt(attr(sz, "val"))
    szcs = q(rpr, "w:szCs")
    if szcs is not None and "size_pt" not in out:
        out["size_pt"] = half_to_pt(attr(szcs, "val"))
    b = q(rpr, "w:b")
    if b is not None:
        out["bold"] = attr(b, "val") not in ("0", "false")
    i = q(rpr, "w:i")
    if i is not None:
        out["italic"] = attr(i, "val") not in ("0", "false")
    u = q(rpr, "w:u")
    if u is not None:
        val = attr(u, "val")
        out["underline"] = val not in ("0", "false", "none") if val is not None else True
    color = q(rpr, "w:color")
    if color is not None:
        out["color"] = attr(color, "val")
    return out


def _ppr_to_dict(ppr):
    """Convert a <w:pPr> element into a flat property dict (paragraph level)."""
    if ppr is None:
        return {}
    out = {}
    spacing = q(ppr, "w:spacing")
    if spacing is not None:
        line = attr(spacing, "line")
        rule = attr(spacing, "lineRule")
        if line is not None:
            if rule in ("auto", None):
                out["line_spacing"] = round(int(line) / 240, 2)
                out["line_spacing_rule"] = rule or "auto"
            else:
                out["line_spacing"] = round(int(line) / 20, 1)
                out["line_spacing_rule"] = rule
        before = attr(spacing, "before")
        if before is not None:
            out["space_before_twips"] = int(before)
        after = attr(spacing, "after")
        if after is not None:
            out["space_after_twips"] = int(after)
    jc = q(ppr, "w:jc")
    if jc is not None:
        out["align"] = attr(jc, "val")
    ind = q(ppr, "w:ind")
    if ind is not None:
        for key in ("left", "right", "firstLine", "firstLineChars", "hanging"):
            val = attr(ind, key)
            if val is not None:
                out[f"indent_{key}"] = val
    outline = q(ppr, "w:outlineLvl")
    if outline is not None:
        out["outline_level"] = attr(outline, "val")
    return out


def _collect_styles(styles_root):
    """Return {styleId: (basedOn|None, rPr|pPr element, name)} for every style."""
    collected: dict[str, dict] = {}
    if styles_root is None:
        return collected
    for st in qa(styles_root, "w:style"):
        sid = attr(st, "styleId")
        if not sid:
            continue
        name_el = q(st, "w:name")
        sname = attr(name_el, "val") or sid
        based_on = q(st, "w:basedOn")
        collected[sid] = {
            "name": sname,
            "based_on": attr(based_on, "val"),
            "rPr": q(st, "w:rPr"),
            "pPr": q(st, "w:pPr"),
        }
    return collected


def _effective_styles(styles_root):
    """Compute the effective (inherited) run + paragraph properties per style.

    Walks each style's ``basedOn`` chain to its root, merging parent properties
    first and letting the child override.  Cycles are broken after the first
    repeated style.  Document defaults (``docDefaults``) are returned separately
    and are *not* folded into every style — callers can layer them on top.
    """
    collected = _collect_styles(styles_root)
    cache: dict[str, dict] = {}

    def compute(sid, visiting):
        if sid in cache:
            return cache[sid]
        if sid in visiting or sid not in collected:
            return {"run_properties": {}, "paragraph_properties": {}}
        visiting = visiting | {sid}
        info = collected[sid]
        parent = info.get("based_on")
        if parent:
            parent_eff = compute(parent, visiting)
            run_props = dict(parent_eff["run_properties"])
            para_props = dict(parent_eff["paragraph_properties"])
        else:
            run_props, para_props = {}, {}
        run_props.update(_rpr_to_dict(info.get("rPr")))
        para_props.update(_ppr_to_dict(info.get("pPr")))
        eff = {"run_properties": run_props, "paragraph_properties": para_props}
        cache[sid] = eff
        return eff

    out: dict[str, dict] = {}
    for sid in collected:
        eff = compute(sid, frozenset())
        out[sid] = {
            "name": collected[sid]["name"],
            "based_on": collected[sid].get("based_on"),
            "run_properties": eff["run_properties"],
            "paragraph_properties": eff["paragraph_properties"],
        }
    return out


def _doc_defaults(styles_root):
    """Parse <w:docDefaults> into default run + paragraph properties."""
    if styles_root is None:
        return {}, {}
    dd = q(styles_root, "w:docDefaults")
    if dd is None:
        return {}, {}
    rprd = q(dd, "w:rPrDefault/w:rPr")
    pprd = q(dd, "w:pPrDefault/w:pPr")
    return _rpr_to_dict(rprd), _ppr_to_dict(pprd)


def inspect(path):
    result = {"file": path, "defaults": {}, "sections": [],
              "heading_styles": {}, "body_sample": {}, "captions": []}
    with zipfile.ZipFile(path) as z:
        styles = read_xml(z, "word/styles.xml")
        if "word/document.xml" not in set(z.namelist()):
            raise ValueError("DOCX has no word/document.xml")
        document = read_xml(z, "word/document.xml")

        # ---- Default font/size/line spacing ----
        if styles is not None:
            dd = q(styles, "w:docDefaults")
            if dd is not None:
                rprd = q(dd, "w:rPrDefault/w:rPr")
                result["defaults"].update(rpr_font(rprd))
                pprd = q(dd, "w:pPrDefault/w:pPr")
                result["defaults"].update(ppr_para(pprd))

            # ---- Heading styles ----
            for st in qa(styles, "w:style"):
                sid = attr(st, "styleId") or ""
                name_el = q(st, "w:name")
                sname = attr(name_el, "val") or sid
                low = (sid + " " + (sname or "")).lower()
                if "heading" in low or "标题" in (sname or "") or "title" in low:
                    info = {}
                    info.update(rpr_font(q(st, "w:rPr")))
                    info.update(ppr_para(q(st, "w:pPr")))
                    result["heading_styles"][sname] = info

            # ---- Effective styles (merged along basedOn chain) ----
            default_run, default_para = _doc_defaults(styles)
            result["default_run_properties"] = default_run
            result["default_paragraph_properties"] = default_para
            result["effective_styles"] = _effective_styles(styles)

        # ---- Section page setup ----
        if document is not None:
            for sect in qa(document, ".//w:sectPr"):
                s = {}
                pg = q(sect, "w:pgSz")
                if pg is not None:
                    s["page_w_cm"] = twip_to_cm(attr(pg, "w"))
                    s["page_h_cm"] = twip_to_cm(attr(pg, "h"))
                mar = q(sect, "w:pgMar")
                if mar is not None:
                    s["margin_cm"] = {
                        "top": twip_to_cm(attr(mar, "top")),
                        "bottom": twip_to_cm(attr(mar, "bottom")),
                        "left": twip_to_cm(attr(mar, "left")),
                        "right": twip_to_cm(attr(mar, "right")),
                    }
                result["sections"].append(s)

            # ---- Body paragraph sampling + captions ----
            body_combo = Counter()
            for p in qa(document, ".//w:p"):
                ppr = q(p, "w:pPr")
                pinfo = ppr_para(ppr)
                # Use the first run's font in the paragraph as representative
                run = q(p, "w:r")
                rinfo = rpr_font(q(run, "w:rPr")) if run is not None else {}
                text = "".join(t.text or "" for t in qa(p, ".//w:t"))
                style = (pinfo.get("style") or "").lower()

                # Caption detection: style name contains "caption" (or its Chinese equivalent), or text starts with
                # a figure/table keyword + number; and the whole paragraph is short (captions are
                # usually brief), to avoid misclassifying long body paragraphs that start with a
                # figure/table keyword as captions.
                is_caption = (("caption" in style or "题注" in (pinfo.get("style") or ""))
                              or (CAPTION_RE.match(text) and len(text.strip()) <= 60))
                if is_caption and text.strip():
                    result["captions"].append({
                        "text": text.strip()[:80],
                        # Report Chinese and Western fonts separately, to avoid Western font
                        # overriding Chinese detection in mixed-language paragraphs
                        "font_cn": rinfo.get("font_eastasia"),
                        "font_en": rinfo.get("font_ascii"),
                        "size": rinfo.get("size_pt"),
                        "bold": rinfo.get("bold"),
                        "align": pinfo.get("align"),
                    })
                    continue

                if not text.strip() or pinfo.get("outline_level") is not None:
                    continue
                key = (
                    rinfo.get("font_eastasia") or "default",   # Chinese (East Asian) font
                    rinfo.get("font_ascii") or "default",       # Western font
                    rinfo.get("size_pt"),
                    pinfo.get("line_spacing"),
                    pinfo.get("align"),
                    pinfo.get("first_line_indent"),
                )
                body_combo[key] += 1

            result["body_sample"] = [
                {"font_cn": k[0], "font_en": k[1], "size_pt": k[2], "line_spacing": k[3],
                 "align": k[4], "first_line_indent": k[5], "paragraphs": n}
                for k, n in body_combo.most_common(6)
            ]
    return result


def human(r):
    L = []
    L.append(f"# Document actual formatting: {r['file']}\n")
    d = r["defaults"]
    L.append("## Default body text")
    L.append(f"- Western font: {d.get('font_ascii', '—')}  East Asian font: {d.get('font_eastasia', '—')}")
    L.append(f"- Default size: {cn_size(d.get('size_pt')) or '—'}")
    L.append(f"- Default line spacing: {d.get('line_spacing', '—')}\n")

    drp = r.get("default_run_properties") or {}
    dpp = r.get("default_paragraph_properties") or {}
    if drp or dpp:
        L.append("## Document default properties (docDefaults parsing)")
        if drp:
            L.append(f"- Default font (Western): {drp.get('font_ascii', '—')}  "
                     f"Default font (East Asian): {drp.get('font_eastasia', '—')}  "
                     f"Default size: {cn_size(drp.get('size_pt')) or '—'}")
        if dpp:
            ls = dpp.get("line_spacing")
            L.append(f"- Default line spacing: {ls if ls is not None else '—'}  "
                     f"Default alignment: {dpp.get('align', '—')}")
        L.append("")

    L.append("## Page / Margins")
    for i, s in enumerate(r["sections"], 1):
        m = s.get("margin_cm", {})
        L.append(f"- Section {i}: paper {s.get('page_w_cm')}×{s.get('page_h_cm')} cm; "
                 f"margins top {m.get('top')} bottom {m.get('bottom')} left {m.get('left')} right {m.get('right')} cm")
    L.append("")

    L.append("## Heading styles")
    for name, h in r["heading_styles"].items():
        L.append(f"- {name}: size {cn_size(h.get('size_pt')) or '—'}, "
                 f"East Asian font {h.get('font_eastasia', '—')}, bold {h.get('bold', '—')}, "
                 f"alignment {h.get('align', '—')}, outline level {h.get('outline_level', '—')}")
    L.append("")

    eff = r.get("effective_styles") or {}
    if eff:
        L.append("## Effective styles (merged along basedOn chain)")
        for sid, info in eff.items():
            rp = info.get("run_properties", {})
            pp = info.get("paragraph_properties", {})
            L.append(f"- {sid} ({info.get('name', '')})"
                     f"{' <- ' + info['based_on'] if info.get('based_on') else ''}: "
                     f"size {cn_size(rp.get('size_pt')) or '—'}, "
                     f"East Asian font {rp.get('font_eastasia', '—')}, "
                     f"bold {rp.get('bold', '—')}, line spacing {pp.get('line_spacing', '—')}")
        L.append("")

    L.append("## Body paragraph sampling (sorted by paragraph count)")
    for b in r["body_sample"]:
        L.append(f"- {b['paragraphs']} paragraphs: CN font {b['font_cn']}, EN font {b['font_en']}, "
                 f"size {cn_size(b['size_pt']) or '—'}, line spacing {b['line_spacing'] or '—'}, "
                 f"alignment {b['align'] or 'default'}, first-line indent {b['first_line_indent'] or 'none'}")
    L.append("")

    if r["captions"]:
        L.append("## Figure/table caption sampling")
        for c in r["captions"][:10]:
            L.append(f"- \"{c['text']}\" size {cn_size(c['size']) or '—'}, "
                     f"CN font {c['font_cn'] or '—'}, EN font {c['font_en'] or '—'}, "
                     f"bold {c['bold'] if c['bold'] is not None else '—'}, alignment {c['align'] or 'default'}")
    return "\n".join(L)


def main():
    # Windows GBK console would crash printing ⚠️ etc.; force UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if "--version" in sys.argv[1:]:
        print("docx_inspect.py 0.1.0")
        return 0
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print(__doc__.strip())
        return 0
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("error: provide an input .docx file; use --help for usage", file=sys.stderr)
        return 2
    r = inspect(args[0])
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(human(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
