# Claim 级证据锚点

## 目录

- [最小合同](#最小合同)
- [建立锚点](#建立锚点)
- [PDF 提取匹配](#pdf-提取匹配)
- [OCR 与视觉证据](#ocr-与视觉证据)
- [审计与交付](#审计与交付)

## 最小合同

`paper-note` 中每条核心 claim 必须有稳定 ID 和至少一个 evidence anchor。核心 claim 包括研究问题界定、关键方法、主要发现、实际贡献、重要局限和研究者解释；背景性常识无需为了凑数机械加引文。

```json
{
  "id": "finding-primary",
  "claim_type": "finding",
  "text": "The method improves the primary endpoint.",
  "support_level": "direct",
  "evidence": [{
    "source": "paper.pdf",
    "page": 7,
    "section": "Results",
    "quote": "The primary endpoint increased ...",
    "extraction_method": "native-text",
    "verification": "exact-match"
  }]
}
```

- `claim_type`：`research-question`、`method`、`finding`、`contribution`、`limitation`、`interpretation`。
- `support_level`：`direct` 表示原文直接支持；`partial` 表示只支持一部分；`context-only` 表示原文仅提供背景，不能当作结论证据。
- `page` 使用 PDF 物理页序号；若印刷页码不同，在 `section` 或人类笔记中同时写明。
- `quote` 是定位用短摘录，默认不超过 25 个词；500 字符 schema 上限只是安全护栏，不是版权许可。
- `extraction_method`：`native-text`、`ocr`、`human-transcription` 或 `visual`。
- `verification`：`exact-match`、`human-verified` 或 `unverified`。

## 建立锚点

1. 先写原子 claim：一句只表达一个可核查主张，不把方法、结果和因果解释塞在一起。
2. 找最接近原始证据的位置。结果优先结果表/正文，方法优先方法章节，局限优先作者限制段；不要只引用摘要转述。
3. 复制最短且能唯一定位的原文，记录 PDF 页和章节。引用表格或图时，同时记录编号，在人类笔记中注明“视觉核对”。
4. 明确支持强度。证据只显示相关性时，不得把 claim 写成因果；作者自称“novel”只支持“作者声称创新”，不自动支持“实际创新”。
5. 多个来源共同支持时分别建 anchor；一条模糊长引文不能代替多条精确证据。

## PDF 提取匹配

有 `pdf-extraction` 时运行：

```bash
python3 scripts/audit_claim_evidence.py note.json \
  --extraction paper.extraction.json \
  --out note.evidence-audit.json
```

审计器按物理页查找规范化后的短摘录，核对该页的 `native-text`/`ocr` 方法，并报告页码缺失、来源不一致、方法不一致和原文未命中。它只证明摘录在提取文本中出现，不证明 claim 的推理正确；支持强度仍需研究者判断。

只有章节、没有整数 PDF 页码的锚点可以保留，但不能自动逐页匹配。重新排版的出版社 HTML、accepted manuscript 和正式 PDF 页码可能不同，必须在 `source` 中区分版本。

## OCR 与视觉证据

OCR 摘录在回看页面图像前使用 `verification: unverified`。主要结论、数值、公式、表格单元格和图中读数必须人工核对后改为 `human-verified`。使用 `--strict-ocr` 可让直接 claim 仅由未核 OCR 支持时审计失败。

`visual` 用于图形趋势、示意图或无法可靠转写的公式；短摘录写图/表编号和可见标签，真正判断写在 claim 中。不得把肉眼估算数值伪装成精确表格数据。

## 审计与交付

先验证两个 artifact，再交付 Markdown：

```bash
python tools/validate_artifact.py note.json --type paper-note
python tools/validate_artifact.py note.evidence-audit.json --type evidence-audit
```

`status: fail` 表示结构或页内匹配错误；`warning` 表示仍需人工动作；`pass` 只表示当前机器检查通过。保留 note、PDF extraction、evidence audit 三者的 checksum。任何改写核心 claim、替换论文版本或重新 OCR 后都要重跑审计。
