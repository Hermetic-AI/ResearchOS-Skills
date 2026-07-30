#!/usr/bin/env python3
"""
docx_inspect.py — 零依赖提取 .docx 的真实排版属性，供论文格式检查比对。

只用 Python 标准库（zipfile + xml.etree），不需要 python-docx / pandoc。
用法:
    python3 docx_inspect.py path/to/thesis.docx [--json]

输出（默认人类可读，加 --json 输出结构化 JSON）：
  - 默认正文字体 / 字号 / 行距（docDefaults 解析）
  - 每个 section 的页边距、纸张、页码
  - 各级标题样式（字体/字号/加粗/对齐/大纲级别）
  - 正文段落抽样（字体/字号/行距/对齐/首行缩进）出现频次统计
  - 图表题注（caption）段落抽样
  - 最终有效样式（effective_styles）：沿 basedOn 链合并父样式属性

字号换算：Word 内部 w:sz 单位是「半磅」，值/2 = 磅(pt)。
常见中文字号对照：初号42 小初36 一号26 小一24 二号22 小二18 三号16 小三15
四号14 小四12 五号10.5 小五9 六号7.5。EMU/twips：页边距 w:pgMar 单位是 twip(1/1440 英寸)。
"""
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

# 题注模式：图/表/附图/附表/Fig./Figure/Table 后必须紧跟编号（1、1.1、1-1），
# 才算题注——避免把"图注意力机制""表示…"这类正文误判成题注。
CAPTION_RE = re.compile(r"^\s*(图|表|附图|附表|Fig\.?|Figure|Table|Tab\.?)\s?\d+([.\-]\d+)*",
                        re.IGNORECASE)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# 磅 -> 中文字号名（近似）
PT_TO_CN = {
    42: "初号", 36: "小初", 26: "一号", 24: "小一", 22: "二号", 18: "小二",
    16: "三号", 15: "小三", 14: "四号", 12: "小四", 10.5: "五号", 9: "小五",
    7.5: "六号", 6.5: "小六",
}


def cn_size(pt):
    if pt is None:
        return None
    name = PT_TO_CN.get(pt)
    return f"{pt}pt" + (f"（{name}）" if name else "")


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
    """从 rPr 提取字体名（东亚/西文）、字号pt、加粗、斜体"""
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
    """从 pPr 提取行距、对齐、首行缩进、大纲级别、样式引用"""
    if ppr is None:
        return {}
    out = {}
    spacing = q(ppr, "w:spacing")
    if spacing is not None:
        line = attr(spacing, "line")
        rule = attr(spacing, "lineRule")
        if line is not None:
            if rule in ("auto", None):
                # 240 = 单倍行距
                out["line_spacing"] = f"{round(int(line) / 240, 2)}倍"
            else:  # atLeast / exact，单位 twip
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

        # ---- 默认字体/字号/行距 ----
        if styles is not None:
            dd = q(styles, "w:docDefaults")
            if dd is not None:
                rprd = q(dd, "w:rPrDefault/w:rPr")
                result["defaults"].update(rpr_font(rprd))
                pprd = q(dd, "w:pPrDefault/w:pPr")
                result["defaults"].update(ppr_para(pprd))

            # ---- 标题样式 ----
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

            # ---- 最终有效样式（沿 basedOn 链合并）----
            default_run, default_para = _doc_defaults(styles)
            result["default_run_properties"] = default_run
            result["default_paragraph_properties"] = default_para
            result["effective_styles"] = _effective_styles(styles)

        # ---- section 页面设置 ----
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

            # ---- 正文段落抽样 + 题注 ----
            body_combo = Counter()
            for p in qa(document, ".//w:p"):
                ppr = q(p, "w:pPr")
                pinfo = ppr_para(ppr)
                # 段内首个 run 的字体作代表
                run = q(p, "w:r")
                rinfo = rpr_font(q(run, "w:rPr")) if run is not None else {}
                text = "".join(t.text or "" for t in qa(p, ".//w:t"))
                style = (pinfo.get("style") or "").lower()

                # 题注判定：样式名标了 caption/题注，或文本以"图/表/Fig/Table+编号"开头；
                # 且整段较短（题注通常不长），避免把以"图"开头的长正文段误判。
                is_caption = (("caption" in style or "题注" in (pinfo.get("style") or ""))
                              or (CAPTION_RE.match(text) and len(text.strip()) <= 60))
                if is_caption and text.strip():
                    result["captions"].append({
                        "text": text.strip()[:80],
                        # 中英文字体分开报，避免中英混排时用西文字体覆盖中文判定
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
                    rinfo.get("font_eastasia") or "默认",   # 中文(东亚)字体
                    rinfo.get("font_ascii") or "默认",       # 西文字体
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
    L.append(f"# 文档实际排版：{r['file']}\n")
    d = r["defaults"]
    L.append("## 默认正文")
    L.append(f"- 西文字体: {d.get('font_ascii', '—')}  东亚字体: {d.get('font_eastasia', '—')}")
    L.append(f"- 默认字号: {cn_size(d.get('size_pt')) or '—'}")
    L.append(f"- 默认行距: {d.get('line_spacing', '—')}\n")

    drp = r.get("default_run_properties") or {}
    dpp = r.get("default_paragraph_properties") or {}
    if drp or dpp:
        L.append("## 文档默认属性（docDefaults 解析）")
        if drp:
            L.append(f"- 默认字体(西文): {drp.get('font_ascii', '—')}  "
                     f"默认字体(东亚): {drp.get('font_eastasia', '—')}  "
                     f"默认字号: {cn_size(drp.get('size_pt')) or '—'}")
        if dpp:
            ls = dpp.get("line_spacing")
            L.append(f"- 默认行距: {ls if ls is not None else '—'}  "
                     f"默认对齐: {dpp.get('align', '—')}")
        L.append("")

    L.append("## 页面 / 页边距")
    for i, s in enumerate(r["sections"], 1):
        m = s.get("margin_cm", {})
        L.append(f"- 节{i}: 纸张 {s.get('page_w_cm')}×{s.get('page_h_cm')} cm; "
                 f"边距 上{m.get('top')} 下{m.get('bottom')} 左{m.get('left')} 右{m.get('right')} cm")
    L.append("")

    L.append("## 标题样式")
    for name, h in r["heading_styles"].items():
        L.append(f"- {name}: 字号{cn_size(h.get('size_pt')) or '—'}, "
                 f"东亚字体{h.get('font_eastasia', '—')}, 加粗{h.get('bold', '—')}, "
                 f"对齐{h.get('align', '—')}, 大纲级别{h.get('outline_level', '—')}")
    L.append("")

    eff = r.get("effective_styles") or {}
    if eff:
        L.append("## 最终有效样式（沿 basedOn 链合并）")
        for sid, info in eff.items():
            rp = info.get("run_properties", {})
            pp = info.get("paragraph_properties", {})
            L.append(f"- {sid} ({info.get('name', '')})"
                     f"{' ← ' + info['based_on'] if info.get('based_on') else ''}: "
                     f"字号{cn_size(rp.get('size_pt')) or '—'}, "
                     f"东亚字体{rp.get('font_eastasia', '—')}, "
                     f"加粗{rp.get('bold', '—')}, 行距{pp.get('line_spacing', '—')}")
        L.append("")

    L.append("## 正文段落抽样（按段数排序）")
    for b in r["body_sample"]:
        L.append(f"- {b['paragraphs']}段: 中文字体{b['font_cn']}, 西文字体{b['font_en']}, "
                 f"字号{cn_size(b['size_pt']) or '—'}, 行距{b['line_spacing'] or '—'}, "
                 f"对齐{b['align'] or '默认'}, 首行缩进{b['first_line_indent'] or '无'}")
    L.append("")

    if r["captions"]:
        L.append("## 图表题注抽样")
        for c in r["captions"][:10]:
            L.append(f"- 「{c['text']}」字号{cn_size(c['size']) or '—'}, "
                     f"中文字体{c['font_cn'] or '—'}, 西文字体{c['font_en'] or '—'}, "
                     f"加粗{c['bold'] if c['bold'] is not None else '—'}, 对齐{c['align'] or '默认'}")
    return "\n".join(L)


def main():
    # Windows GBK 控制台打印 ⚠️ 等字符会崩，强制 UTF-8
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
