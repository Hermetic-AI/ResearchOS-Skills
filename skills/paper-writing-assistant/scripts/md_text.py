#!/usr/bin/env python3
"""
md_text.py — 零依赖抽取 .md 纯文本，定位参考文献表，提取正文引用标记（功能二引用检查的 Markdown 对称版，
与 docx_text.py 接口一致）。

只用 Python 标准库。用法:
    python3 md_text.py thesis.md                 # 概览：行数/参考文献条数/引用编号核对
    python3 md_text.py thesis.md --refs           # 只输出参考文献表（带序号）
    python3 md_text.py thesis.md --cites          # 只输出正文引用编号核对
    python3 md_text.py thesis.md --dump out.txt [--force] # 纯文本存到 out.txt；默认不覆盖
    python3 md_text.py thesis.md --json           # 结构化 JSON

关键设计（与 docx_text.py 对齐）：
  1. 先剥离 YAML frontmatter 与围栏代码块（```/~~~），正文 [n] 引用不受代码块噪声污染。
  2. 正文 [n] 引用仍可能混入数组维度等噪声（如 [4096]）。拿到参考文献条数 R 后，
     1..R 视为有效引用编号，> R 的单列为"疑似噪声/悬空引用"。
  3. Markdown 的参考文献条目按行首编号识别（[1] / 1. / 1) 等），标题匹配
     "参考文献" / "References" / "Bibliography"。
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
# 引用标记：[1] [1-3] [1,2] [1，2] [1-3,5]，允许中英文逗号
CITE_RE = re.compile(r"\[(\d[\d,，\-\s]*)\]")
# 参考文献条目行首编号：[1] / [1]. / 1. / 1) / 1、（编号后可无空格，如 [1]张三.）
REF_ITEM_RE = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.)、])\s*\S")


def strip_markdown(text):
    """去 frontmatter 与围栏代码块，返回正文行列表（保留原行号信息不需要，
    引用核对只看集合）。"""
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
    with open(path, encoding="utf-8") as fh:
        texts = strip_markdown(fh.read())
    full = "\n".join(texts)

    # ---- 定位参考文献表（取最后一个匹配标题）----
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

    # ---- 正文引用标记（排除参考文献表自身区域）----
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
    L = [f"# 引用抽取概览：{r['file']}",
         f"- 总行数(去 frontmatter/代码块): {r['paragraphs']}",
         f"- 参考文献表: {'第%d行起' % r['ref_index'] if r['ref_index'] is not None else '未定位到'}，共 {r['ref_count']} 条",
         f"- 正文有效引用编号(1..{r['ref_count']}): 命中 {len(r['cited_valid'])} 个",
         f"- 疑似噪声/悬空引用(编号 > {r['ref_count']}): {r['cited_noise'] or '无'}",
         f"- 文献表中从未被引用(孤立条目): {r['uncited'] or '无'}"]
    if r["ref_index"] is None:
        L.append("\n⚠️ 未定位到参考文献表标题（参考文献/References/Bibliography），"
                 "维度①核对不可用；②③④可先人工指定文献表范围。")
    return "\n".join(L)


def main():
    # Windows GBK 控制台打印 ⚠️ 等字符会崩，强制 UTF-8
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
        print("错误：请提供输入 Markdown；使用 --help 查看用法", file=sys.stderr)
        return 2
    path = sys.argv[1]
    flags = sys.argv[2:]
    if not os.path.isfile(path):
        sys.exit(f"错误：文件不存在：{path}")
    r = analyze(path)

    if "--dump" in flags:
        i = flags.index("--dump")
        if i + 1 >= len(flags):
            sys.exit("错误：--dump 需要一个输出文件路径参数")
        out = flags[i + 1]
        if os.path.abspath(out) == os.path.abspath(path):
            sys.exit("错误：--dump 不能覆盖输入 Markdown")
        if os.path.exists(out) and "--force" not in flags:
            sys.exit(f"错误：输出已存在：{out}；如需覆盖请添加 --force")
        open(out, "w", encoding="utf-8").write(r["full_text"])
        print(f"全文已写入 {out}（{len(r['full_text'])} 字）")
        return 0
    if "--json" in flags:
        r2 = {k: v for k, v in r.items() if k != "full_text"}
        print(json.dumps(r2, ensure_ascii=False, indent=2))
        return 0
    if "--refs" in flags:
        # 条目可能自带 [N]/1. 前缀，strip 掉再统一编号，避免双重编号
        for i, ref in enumerate(r["references"], 1):
            ref = re.sub(r"^\s*(?:\[\d+\]|\d+[.)、])\s*", "", ref)
            print(f"[{i}] {ref}")
        return 0
    if "--cites" in flags:
        print("正文有效引用编号:", r["cited_valid"])
        print("疑似噪声/悬空:", r["cited_noise"])
        print("孤立(未被引用)条目:", r["uncited"])
        return 0
    print(overview(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
