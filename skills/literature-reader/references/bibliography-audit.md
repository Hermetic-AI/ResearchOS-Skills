# 标识符核验、撤稿预警与版本合并

## 目录

- [安全默认值](#安全默认值)
- [离线审计](#离线审计)
- [在线核验](#在线核验)
- [撤稿与更正信号](#撤稿与更正信号)
- [去重与版本族](#去重与版本族)
- [结论边界](#结论边界)

## 安全默认值

`audit_bibliography.py` 默认不联网，只规范化 DOI/arXiv/PMID、检查语法、识别重复项和版本族。它从 `extract_metadata.py` 的 JSON 或 JSON 条目数组读取，不删除任何记录，不自动把预印本替换成期刊版，也不把“未命中”写成“真实有效”。

```bash
python3 scripts/extract_metadata.py references.txt --pretty > metadata.json
python3 scripts/audit_bibliography.py metadata.json --out bibliography.audit.json
python tools/validate_artifact.py bibliography.audit.json --type bibliography-audit
```

## 离线审计

离线结果包括：

- 标识符的规范值与语法状态；
- 同 DOI、同 PMID、同 arXiv 基础编号的强匹配；
- 标题、第一作者和年份共同支持的概率匹配；
- arXiv 版本号与“预印本—正式发表版”候选关系；
- 每个聚类的建议 canonical 条目和合并证据。

canonical 只用于优先汇总元数据：DOI 版优先，其次 PMID、arXiv，高版本 arXiv 优先于低版本。必须人工保留版本历史、发布日期、标题变化和引用语境。

可下载 Crossref 发布的 Retraction Watch CSV 后离线核验：

```bash
python3 scripts/audit_bibliography.py metadata.json \
  --retraction-index retraction-watch.csv \
  --out bibliography.audit.json
```

该数据由 Crossref 以 CC0 提供并在工作日更新。发表成果使用数据时按 Crossref/Retraction Watch 的说明引用来源；仓库不捆绑数据库快照。

## 在线核验

在线模式是显式选择，并要求联系邮箱：

```bash
python3 scripts/audit_bibliography.py metadata.json \
  --online --email researcher@example.org \
  --out bibliography.audit.json
```

- DOI：查询 `https://api.crossref.org/works/{doi}`，通过 `mailto` 和 User-Agent 标识客户端。
- arXiv：批量调用 `https://export.arxiv.org/api/query?id_list=...`，解析 Atom；同一次运行只发一个批量请求。
- PMID：批量调用 NCBI ESummary，发送 `tool` 与 `email`。遵守 NCBI E-utilities 使用政策；本功能不复制摘要。NCBI 免责声明与版权说明见 <https://www.ncbi.nlm.nih.gov/home/about/policies/>。

邮箱只用于请求标识，写入 provenance 命令时会替换成 `<redacted>`。API 超时、限流、服务错误或解析失败写入 warnings，不伪装成“未找到”。批量挖掘应改用各机构提供的 bulk/OAI-PMH/FTP 通道。

## 撤稿与更正信号

Crossref `update-to` 和 Retraction Watch CSV 可能给出 retraction、withdrawal、expression of concern、correction 或 reinstatement；PubMed 的 publication type 也可能标记 Retracted Publication。

- `critical`：撤稿或撤回，停止把该记录当作未受影响证据，回到通知原文核查范围和日期。
- `warning`：关注声明，不等于撤稿，但必须在综述与引用决策中披露。
- `notice`：更正、恢复等记录，需比较更新前后内容。

不同来源可重复报告同一事件；不要把重复条数解释为多次撤稿。数据库记录是预警入口，最终结论应回看出版商通知和论文页面。

## 去重与版本族

- `probable-duplicate`：强标识符相同，或标题高度相似且第一作者、年份相容。
- `version-family`：同一 arXiv 基础编号，或标题支持预印本与正式发表版关系。
- `evidence` 保存逐对匹配理由与相似度；不得只保留一个黑盒分数。
- 合并时以标识符并集、作者全表、版本日期和来源记录为准。不要把正式版新增实验或修改结论反向写入旧预印本。
- 标题短、作者缺失、会议扩展版或译文容易误判；聚类动作固定为 `review-and-merge-metadata; do-not-delete-automatically`。

## 结论边界

标识符语法正确不代表已注册；API 命中不代表论文可信；撤稿库未命中不代表未撤稿；标题近似不证明同一作品。报告应写“在本次查询的来源和时间下未发现信号”，并保留查询时间、输入 checksum、服务 warnings 和人工复核状态。
