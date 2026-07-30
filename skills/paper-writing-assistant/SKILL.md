---
name: paper-writing-assistant
description: Assist thesis and paper writing by drafting evidence-aware figure or table analysis paragraphs, auditing in-text citations against reference lists and GB/T 7714/IEEE/APA/ACM or institution rules, and checking Word or statically verifiable LaTeX formatting against a confirmed requirement checklist. Use for 看图写论文段落, 图表分析, 检查论文引用, 参考文献格式, 学校论文格式, 排版核对, citation audit, or thesis formatting. Not for Markdown-to-LaTeX conversion (md2latex), figure generation (scientific-plot), statistical analysis, literature reading, or experiment design.
---

# 论文写作辅助（Paper Writing Assistant）

面向在读硕士/博士。三个功能相互独立，用户提到哪个就进哪个，不要强行三个一起跑。

**全局约定**
- **生成内容跟随论文语言**：会进入论文的文字（图表分析段、建议改法原文）用论文正文的语言——中文论文写中文，英文论文写英文。
- **检查报告一律中文**：所有报告、说明、清单给用户看的部分用中文。
- **默认只报告+给修改建议，不擅自改稿**：查出问题后列"位置 / 现状 / 违反哪条 / 建议改法（含可直接替换的原文）"，是否落笔由用户说了算。用户说"帮我改前三条"再动手。
- **输入格式两类**：LaTeX 源码树（`.tex/.bib/.cls/.sty`）与 Word `.docx`。先判断是哪种再选路径。
- **优先消费标准产物**：若项目中已有 `paper-note`、`stat-results`、`figure-manifest` 或 `reproduction-card`，先读 `references/artifact-contracts.md` 并校验，避免手抄数值和丢失证据来源。

先判断用户要哪个功能，再跳到对应小节。

---

## 功能一：看图写正文分析段落

**目标**：用户给一张图或表的图片，生成能直接放进论文正文的"如图 X 所示，……"分析段落——不是描述像素，而是服务论点。

**步骤**
1. **拿到图片**：用户提供图/表的图片文件路径或直接贴图，用视觉能力读图（趋势、拐点、数据点、对比、显著差异、坐标轴含义）。
2. **补上下文**（这是段落好坏的关键，别跳）：
   - 自动从论文里抽背景：如果用户给了论文文件，定位引用这张图的那一节正文（`\ref{}`/`图X`/`Figure X` 附近），了解论文在论证什么、术语怎么用、上一段结论是什么。
   - 让用户补一句意图：问"这张图你想用它说明什么结论？"——一句话即可，不要求大段输入。
3. **写段落**：
   - 开头用规范引用式（中文"如图 X 所示"/英文"As shown in Fig. X"），跟论文既有写法一致。
   - 先客观读数（关键数值、趋势、对比），再落到论点（这组数据支持了什么结论、为什么），与上下文呼应。
   - 术语、变量名、单位与全文统一。语言跟论文正文语言。
   - 避免"图中有三条上升曲线"这种正确但无用的空话；每句都要有分析价值。
4. **给出段落**，并简短说明"我依据图里的 X、Y 和你说的意图这样写的，数值请你核对一遍"（模型读图数值可能有偏差，提醒复核）。

---

## 功能二：引用规范检查

**目标**：四个维度全查——① 正文引用 ↔ 参考文献表一一对应；② 每条文献格式合规；③ 字段完整；④ 风格一致。

**前置：定风格**。三条路，按用户情况走：

- **(a) 用户直接选内置**：GB/T 7714、IEEE、APA、ACM 四套，规则读 `references/citation-styles.md`。若用户没说也没给要求文档，问一句选哪套。
- **(b) 用户给了「学校/期刊要求文档」，要按它查**（如华东理工 §9、某期刊投稿须知）：按功能三的读法读要求文件（`.doc`→`textutil`（Windows 无 textutil，建议在 Word 里另存为 .docx 后再读），`.docx`→`docx_text.py`，`.pdf`→Read/`pdftotext`），把其中的参考文献格式**解析成一份「校方风格规格」**（字段顺序、分隔标点、是否带类型码 `[J]`、作者缩写规则、卷期页写法、给了哪些文献类型的模板），发给用户确认。**这份校方规格优先于内置风格作为检查基准。**
- **(c) 校方要求 ⇆ 国标 差异比对（关键增值，必做）**：把 (b) 的校方规格和最接近的内置风格（多为 GB/T 7714）逐项对比，**主动提示三类风险**：
  1. **冲突**：论文实际写法符合国标却不符校方示例，或反之（如华理 §9 示例无 `[J]` 类型码、用中文标点，而论文按 GB/T 7714 带 `[J]`、用半角）——明确指出"按校方 vs 按国标结论相反"，不要单方面下判。
  2. **过时**：要求文档年份早于 GB/T 7714 现行版（2015），或与论文近年文献的通行写法明显脱节 → 提示"该要求可能已被新版研究生手册取代"。
  3. **不全**：校方只给了部分文献类型模板（如只有期刊）→ 缺的类型建议用国标补全。
  最后**请用户拍板以哪套为准**（校方规格 / 国标 / 校方为主国标补全），再进入四维检查。规则细节仍读 `references/citation-styles.md` 作对照底本。

**步骤**
1. **确认风格**（见上）。
2. **抽取两份清单**：
   - LaTeX：正文里所有 `\cite{key}`/`\parencite{}` 等的 key 集合；参考文献来源——`.bib` 文件的所有条目，或 `thebibliography` 里的 `\bibitem{key}`。
   - Word：跑 `python3 scripts/docx_text.py <论文.docx>`。它会定位参考文献表（`--refs` 输出带序号全表）、抽取正文引用编号并**自动过滤噪声**（把 `[4096]` 这类张量维度、超出文献条数的编号单列为"疑似噪声/悬空"，不污染对应核对），`--cites` 直接给出「已引用/悬空/孤立」三组，`--json` 给结构化数据。
   - Markdown：跑 `python3 scripts/md_text.py <论文.md>`——`docx_text.py` 的 Markdown 对称版，接口一致（`--refs/--cites/--dump/--json`），抽取前先剥离 frontmatter 与代码块，正文引用 vs References 列表的差集核对同法进行。
3. **维度①一一对应**（多数由 `docx_text.py` 直接算出，核对结论即可）：
   - 正文引用了但文献表里没有（编号 > 文献条数）→ 缺失来源/悬空引用（先排除噪声）。
   - 文献表里有但正文从没引用（脚本的"孤立条目"）→ 孤立条目。
   - 编号制：检查编号是否连续、是否与出现顺序一致。
   - **EndNote/域引用特判**：若脚本报"⚠️ 疑似域引用"（正文抽到的编号远少于文献条数），说明引用是 Word 域代码、纯文本抽不到。此时**不要下"大量缺失/孤立"的结论**，而是让用户在 Word 里「更新域 → 全选 → `Ctrl+Shift+F9` 转为纯文本副本」后重跑脚本；②③④三维仍可照常基于文献表进行。
4. **维度②格式合规**：逐条对照所选风格的字段顺序、标点、斜体、作者名缩写规则、卷期页写法、类型标识码（GB/T 7714 的 `[J]/[M]`）等，指出偏差。
5. **维度③字段完整**：每条是否缺作者/年份/页码/DOI/出版者等关键字段（按该风格的必填要求）。
6. **维度④风格一致**：全文是否混用风格——作者缩写不一致、标点忽全忽半、期刊名忽缩写忽全称、正文引用形式不统一、参考文献表排序规则不统一（详见规则卡末尾自查清单）。
7. **出报告**：按维度分组，每个问题给"位置（第几条/正文哪处）+ 现状 + 违反哪条规则 + 建议改法（给出可直接替换的正确条目原文，语言跟文献）"。最后问是否需要代改。

> 注意：`.bib` 里的字段本身可能正确但 `.bst`/风格渲染出来才是最终样子；如果论文用 `\bibliographystyle`，说明"最终呈现由该 bst 决定"，并同时检查 `.bib` 源字段的完整性与规范性。

---

## 功能三：论文格式检查（按用户要求）

**目标**：用户手动给出格式要求，解析成结构化检查清单，**先给用户确认**，再逐项比对论文实际排版并报告偏差。

**步骤**
1. **收要求**：用户粘贴自然语言要求（如"正文小四宋体，行距 1.5 倍，页边距上下 2.5cm 左右 3cm，一级标题黑体三号居中，图表题注五号"），或指一份要求文件——按后缀选读法：
   - `.docx`：跑 `python3 scripts/docx_text.py <要求.docx> --dump req.txt` 抽全文，或直接读。
   - **`.doc`（旧二进制 OLE2，脚本读不了）**：用 macOS 自带 `textutil -convert txt -stdout <要求.doc>` 抽文本（无 textutil 时退 `antiword`/`catdoc`；Windows 下建议在 Word 里另存为 .docx 后再读）。
   - `.pdf`：优先用 Read 工具直接读；纯文本 PDF 也可 `pdftotext <要求.pdf> -`（若装了 poppler）。
   - `.txt/.md`：直接读。
2. **解析成清单并确认**（关键门禁，别跳）：把自然语言拆成结构化可核项，例如：
   ```
   | # | 项目       | 要求           | 适用范围 |
   |---|-----------|----------------|---------|
   | 1 | 正文字体   | 宋体            | 正文     |
   | 2 | 正文字号   | 小四(12pt)      | 正文     |
   | 3 | 行距       | 1.5 倍          | 正文     |
   | 4 | 页边距     | 上下2.5 左右3cm | 全文     |
   | 5 | 一级标题   | 黑体三号居中     | 标题     |
   | 6 | 图表题注   | 五号            | caption  |
   ```
   把这张清单发给用户，让 TA 确认/补充/修正后再往下。措辞含糊的项主动追问（"'大标题'指一级还是论文题目？"）。
3. **提取论文实际排版**：
   - **Word `.docx`（全查）**：运行
     `python3 scripts/docx_inspect.py <论文.docx>`
     得到默认字体/字号/行距、每节页边距与纸张、各级标题样式、正文段落抽样、图表题注抽样。加 `--json` 可拿结构化数据。脚本零依赖（Python 标准库），无需装包。
   - **LaTeX（只查源码可静态核实项）**：读主 `.tex`、导言区、`\input/\include` 的文件、随附的 `.cls/.sty`。按 `references/latex-format-checkable.md` 判断每条要求是"源码可核"还是"需编译才能验"。**对需编译项如实告知无法静态判定，不要编造结论。**
4. **逐项比对出报告**：对清单每一项给判定——
   - ✅ 符合（给证据：docx 实测值 / LaTeX 命令原文+文件名）
   - ❌ 不符合（现状 vs 要求 + 建议改法：Word 说改哪个样式/设置，LaTeX 给要改的命令）
   - ⚠️ 无法静态判定（仅 LaTeX 渲染类项：说明需编译 PDF 后测量）
5. 最后问是否需要按建议代改。

---

## 文件索引
- `scripts/bibtex_audit.py` — BibTeX/BibLaTeX 离线字段完整性与 DOI 语法审计；真实性或撤稿核验须明确调用 `literature-reader` 的在线审计。
- `scripts/online_verification.py` — 在线 DOI / 期刊元数据核验：通过 Crossref API (``api.crossref.org/works/{doi}``) 查询每个 DOI 并与本地记录比对 title/journal/year/pages/author。支持 ``--doi`` (单个, 可重复) 或 ``--bibtex <file.bib>`` (批量)；``--timeout`` / ``--retries`` 控制 HTTP 行为；网络不可达时报告 ``unavailable`` 而非崩溃；输出含 ``schema_version``/``artifact_type``/``tool_version``/``warnings`` 的 JSON 报告并显式声明"不替代人工核验"。零依赖 (urllib.request)。
- `scripts/consistency_audit.py` — Markdown/LaTeX 的缩略词、图表引用及 LaTeX label/ref 启发式一致性筛查；`--symbols` 启用 LaTeX 符号表一致性分析（命令定义 vs 使用、方程 label/ref、符号多记法检测）；不替代渲染后或 DOCX 的语义审校。
- `scripts/claim_audit.py` — heuristic Markdown/LaTeX screen for strong causal or evidential wording without a nearby numeric citation; `--paper-note` preserves claim-level page/section evidence anchors in its report, but never claims automatic semantic verification.
- `scripts/docx_citation_audit.py` — zero-dependency DOCX screen for visible author-year citation candidates and Zotero/Mendeley/Word field-marker evidence; with ``--fields`` it also parses Word ``CITATION`` field instructions (raw ``instrText``/``instr``) and the rendered RESULT text between field markers.  Parsing is heuristic — it does not perform live Word resolution or verify bibliography semantics.
- `scripts/docx_structure_audit.py` — read-only DOCX evidence inventory for declared style inheritance, theme part, section count, and header/footer parts/references; final effective formatting still requires rendered verification.
- `scripts/evidence_matrix_audit.py` — validates IDs and traceability fields in a manually curated claim-evidence-citation JSON matrix; it does not establish semantic entailment or bibliographic truth.
- `scripts/structure_audit.py` — zero-dependency Markdown/LaTeX outline screen: core-section presence, order, and duplicate headings; reports only and never edits the manuscript.
- `scripts/docx_inspect.py` — 零依赖提取 .docx 真实排版（中英文字体分列/字号/行距/页边距/标题样式/题注含加粗），并沿 ``basedOn`` 链计算最终有效样式（``effective_styles``）与文档默认属性（``docDefaults`` 解析）。
- `scripts/docx_text.py` — 零依赖抽 .docx 全文、定位参考文献表(`--refs`)、提取正文引用编号并过滤噪声/检测 EndNote 域引用(`--cites`)。
- `scripts/md_text.py` — `docx_text.py` 的 Markdown 对称版：抽 .md 纯文本（去 frontmatter/代码块）、定位参考文献表(`--refs`)、提取正文引用编号并过滤噪声(`--cites`)，接口一致。
- `references/citation-styles.md` — GB/T 7714 · IEEE · APA · ACM 四套引用规则卡 + 跨风格一致性自查。
- `references/latex-format-checkable.md` — LaTeX 格式检查：源码可静态核实项 vs 需编译才能验项的映射表。
- `references/artifact-contracts.md` — 文献、统计、图和复现产物的输入边界与冲突处理。跨 skill 写作时读取。
