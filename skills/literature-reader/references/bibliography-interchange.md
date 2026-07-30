# Zotero、BibTeX、RIS 与 EndNote XML 互换

## 目录

- [格式选择](#格式选择)
- [转换流程](#转换流程)
- [字段与损失边界](#字段与损失边界)
- [安全与验证](#安全与验证)

## 格式选择

`convert_bibliography.py` 支持：

| 格式 | 参数 | 典型用途 |
|---|---|---|
| ResearchOS JSON | `researchos-json` | 无损规范化中间层、schema 校验、后续审计 |
| CSL JSON | `csl-json` | Zotero 导入/导出及 citeproc 生态 |
| BibTeX | `bibtex` | LaTeX 工程和通用交换 |
| RIS | `ris` | Zotero、EndNote 与数据库之间的广泛兼容交换 |
| EndNote XML | `endnote-xml` | EndNote 库之间的 Unicode 文本记录交换 |

Zotero 官方文档列出 CSL JSON、BibTeX、RIS 和 EndNote XML 为可导入格式；为 Zotero 输出时优先 CSL JSON、BibTeX 或 RIS。EndNote XML 是 EndNote 的专有交换格式，本脚本只实现常见文字字段子集，不声称复制其富文本、附件或全部私有字段。参考：<https://www.zotero.org/support/kb/importing_standardized_formats>、<https://docs.endnote.com/docs/endnote/2025/v1/windows/en/content/15independentbibs_export/exporting_to_endnote_xml.htm>。

## 转换流程

每次转换必须写目标文件和 provenance manifest：

```bash
python3 scripts/convert_bibliography.py zotero.json \
  --to bibtex --out library.bib

python3 scripts/convert_bibliography.py library.ris \
  --to researchos-json --out library.normalized.json
```

未指定 `--from` 时按内容和扩展名自动识别。来源不明确或扩展名错误时显式指定 `--from csl-json|bibtex|ris|endnote-xml|researchos-json`。默认 manifest 是 `<out>.manifest.json`；用 `--manifest-out` 改路径。已有目标或 manifest 默认拒绝覆盖，只有 `--force` 可替换；输入永远不可作为输出。

ResearchOS JSON 和转换 manifest 分别验证：

```bash
python tools/validate_artifact.py library.normalized.json --type bibliography-library
python tools/validate_artifact.py library.bib.manifest.json --type bibliography-conversion
```

转换后再运行 `audit_bibliography.py`，处理标识符在线核验、撤稿信号、重复记录和版本族；格式转换本身不替代审计。

## 字段与损失边界

规范层保留：类型、题名、作者、年份、期刊/书名、卷期页、DOI、PMID、arXiv、URL、摘要、关键词和 citation key。Zotero API 的 `{key, data}` 包装、CSL 作者对象和 Zotero creator/tag 结构均可读取。

- BibTeX/RIS/EndNote XML 的非标准字段会因软件和 translator 不同而变化；转换后必须抽查。
- 附件、PDF、笔记、批注、collection、related item、同步状态和数据库内部 key 不做跨格式承诺。
- EndNote XML 富文本、上下标、图片和专有样式不在本脚本的保真范围。
- LaTeX 宏和大小写保护按输入文字保留，不做 TeX 编译级语义重写。
- 摘要可能受作者或出版商版权约束。只转换用户合法提供的记录，不从外部数据库批量抓取或再分发摘要。
- citation key 冲突通过稳定后缀消解；不要在已有 LaTeX 工程中未经 diff 就替换旧 key。

至少抽查一条普通期刊论文、一条多作者记录、一条非英文记录、一条带 DOI/PMID/arXiv 的记录和一种非期刊类型。大库先取小样往返，确认目标软件实际导入结果后再处理全库。

## 安全与验证

输入限制为 50 MiB。EndNote XML 拒绝 `DOCTYPE` 与 `ENTITY`，避免在不受信 XML 上处理实体声明。`--strict` 在记录同时缺少题名和学术标识符时失败；默认则保留记录并写 warning。

输出 checksum、记录数、源/目标格式和命令保存在 manifest。导入目标软件后比较记录数，并抽查作者顺序、年份、页码、Unicode、标识符和文献类型。记录数相同不代表字段无损；任何自动迁移都应保留原始库备份。
