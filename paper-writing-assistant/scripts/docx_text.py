#!/usr/bin/env python3
"""
docx_text.py — 零依赖抽取 .docx 全文，定位参考文献表，提取正文引用标记（供功能二引用检查）。

只用 Python 标准库。用法:
    python3 docx_text.py thesis.docx                 # 概览：段数/参考文献条数/引用编号核对
    python3 docx_text.py thesis.docx --refs           # 只输出参考文献表（带序号）
    python3 docx_text.py thesis.docx --cites          # 只输出正文引用编号核对
    python3 docx_text.py thesis.docx --dump out.txt   # 全文文字存到 out.txt
    python3 docx_text.py thesis.docx --json           # 结构化 JSON

关键设计（针对功能二实测踩坑）：
  1. 正文 [n] 引用会混入张量维度等噪声（如 [4096]）。本脚本在拿到参考文献条数 R 后，
     把 1..R 视为有效引用编号，> R 的标记单列为"疑似噪声/悬空引用"，不污染对应核对。
  2. EndNote/域引用：域的显示文本有时能抽到（本脚本尽力抽），有时是纯域代码抽不到——
     若正文几乎抽不到 [n] 但文献表有很多条，脚本会明确提示"疑似域引用，需转纯文本后再核"。
  3. 同时抓上标(superscript) run 里的数字，作为引用标记的补充来源。
"""
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

REF_HEAD_RE = re.compile(r"^\s*参\s*考\s*文\s*献\s*$")
STOP_HEAD_RE = re.compile(r"^\s*(致\s*谢|攻读|在读期间|读期间|附录|作者简介|个人简历|个人简介)")
# 引用标记：[1] [1-3] [1,2] [1，2] [1-3,5]，允许中英文逗号
CITE_RE = re.compile(r"\[(\d[\d,，\-\s]*)\]")


def q(el, path):
    return el.find(path.replace("w:", W))


def paragraphs(root):
    """返回 [(text, is_any_run_superscript), ...]，同时收集上标 run 里的文本。"""
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
    """把 '1-3,5' 展开成 [1,2,3,5]"""
    nums = set()
    for part in re.split(r"[,，]", inner):
        part = part.strip()
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b - a < 500:  # 防御异常大区间
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

    # ---- 定位参考文献表 ----
    ref_idx = None
    for i, t in enumerate(texts):
        if REF_HEAD_RE.match(t.strip()) and len(t.strip()) <= 8:
            ref_idx = i  # 取最后一个匹配（正文可能提到"参考文献"字样）
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

    # ---- 正文引用标记（排除参考文献表自身区域）----
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

    # 域引用启发式：文献表很多但正文几乎抽不到编号
    field_suspected = R >= 10 and len(valid) < max(3, R * 0.2)

    return {
        "file": path, "paragraphs": len(texts), "ref_count": R,
        "ref_index": ref_idx, "references": refs,
        "cited_valid": valid, "cited_noise": noise, "uncited": uncited,
        "superscript_paras": sup_hits, "field_citation_suspected": field_suspected,
        "full_text": full,
    }


def overview(r):
    L = [f"# 引用抽取概览：{r['file']}",
         f"- 总段数: {r['paragraphs']}",
         f"- 参考文献表: {'第%d段起' % r['ref_index'] if r['ref_index'] is not None else '未定位到'}，共 {r['ref_count']} 条",
         f"- 正文有效引用编号(1..{r['ref_count']}): 命中 {len(r['cited_valid'])} 个",
         f"- 疑似噪声/悬空引用(编号 > {r['ref_count']}): {r['cited_noise'] or '无'}",
         f"- 文献表中从未被引用(孤立条目): {r['uncited'] or '无'}",
         f"- 含上标数字的段落数: {r['superscript_paras']}"]
    if r["field_citation_suspected"]:
        L.append("\n⚠️ 疑似 EndNote/域引用：正文抽到的引用编号远少于文献条数。"
                 "维度①（正文↔文献表一一对应）不可靠，请在 Word 中"
                 "「更新域→全选→Ctrl+Shift+F9 转为纯文本副本」后重新运行本脚本。")
    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    flags = sys.argv[2:]
    r = analyze(path)

    if "--dump" in flags:
        out = flags[flags.index("--dump") + 1]
        open(out, "w", encoding="utf-8").write(r["full_text"])
        print(f"全文已写入 {out}（{len(r['full_text'])} 字）")
        return
    if "--json" in flags:
        r2 = {k: v for k, v in r.items() if k != "full_text"}
        print(json.dumps(r2, ensure_ascii=False, indent=2))
        return
    if "--refs" in flags:
        for i, ref in enumerate(r["references"], 1):
            print(f"[{i}] {ref}")
        return
    if "--cites" in flags:
        print("正文有效引用编号:", r["cited_valid"])
        print("疑似噪声/悬空:", r["cited_noise"])
        print("孤立(未被引用)条目:", r["uncited"])
        return
    print(overview(r))


if __name__ == "__main__":
    main()
