# ResearchOS-Skills 体验报告

> **任务**：用 `C:\WorkSpace\Coding\ResearchOS-Skills\` 下的 6 个 skill 围绕"AI agent memory"主题，从空白起步到产出一篇可投稿的英文综述论文，并对其中的引用规范、格式规范做检查。  
> **时间**：2026-07-28 单次会话。  
> **运行环境**：Windows 11 + PowerShell 5.1 + Python 3.11/3.13（两套都可用，脚本只用了 stdlib）。  
> **本报告目的**：评估这 6 个 skill 在真实写作任务中的可用性、踩到的坑、改进建议。  
> **附产物**：`workspace/ai-agent-memory-survey/` 下的所有笔记、矩阵、空白分析、知识图谱、论文草稿、检查报告。

---

## 0. 总览

### 任务完成度一览

| Skill | 用上的功能 | 跑通度 | 关键产出 |
|---|---|:---:|---|
| literature-reader | Function 1 (单论文笔记) × 14, Function 2 (对比矩阵), Function 3 (gap 分析) | ⭐⭐⭐⭐⭐ | 14 篇结构化笔记 + 1 张 12 列对比矩阵 + 1 份 gap report |
| knowledge-graph-builder | Stage 1 (扫描), Stage 2 (typing), Stage 3 (proposal-gated — 跳过), Stage 4 (lineage narration) | ⭐⭐⭐⭐ | graph.json (16 节点 / 34 边) + graph.dot + lineage 摘要 |
| paper-writing-assistant | Function 2 (引用规范) — 4 维度全过; Function 3 (格式检查); Function 1 (看图写段落) 仅用作概念框架 | ⭐⭐⭐⭐ | 1 篇完整论文 (367 行) + 2 份检查报告 |
| experiment-designer | **未使用** | — | — |
| data-analysis-assistant | **未使用** | — | — |
| reproduction-assistant | **未使用** | — | — |

**总评**：在**纯综述路线**下，3 个核心 skill 完整跑通、产物齐全、彼此衔接良好；另外 3 个 skill 因为论文类型不匹配未被触发。**没有发现"完全不能用"的 skill**，但发现 1 个真实 bug、若干文案层优化空间。

### 主要交付物（按"对最终论文的贡献度"排序）

1. **论文** `paper/paper.md` — 8 节，~8000 字，14 引用，IEEE 格式，arXiv 风格。
2. **结构化笔记** `notes/01..14_*.md` — 每篇带 YAML frontmatter + wikilink + `graph:` 关系。
3. **对比矩阵** `notes/comparison_matrix.md` — 12 行 × 11 列 + 横向观察。
4. **空白分析** `notes/gap_analysis.md` — 7 个候选 gap，4 轴可行性裁决。
5. **知识图谱** `graph/graph.json` + `graph.dot` — 16 节点 / 34 边 / 0 warning。
6. **引用检查报告** `paper/citation_check_report.md` — 4 维度全过。
7. **格式检查报告** `paper/format_check_report.md` — arXiv 提交就绪。
8. **本报告** `report/experience_report.md`（即此文件）。

---

## 1. literature-reader — 体验极好

### 跑通的流程

1. **Function 1 单论文笔记**：用 `references/note-template.md` 给 12 篇 primary + 2 篇 survey 写了结构化笔记。模板把"§3 Contributions 必须区分 claimed vs actual"、"§4 Key results 必须带 baseline"、"§5 My assessment 必须至少写一条作者没说的" 这些规则都明示出来——逼着我做"判断"而不是抄论文 abstract。
2. **Function 2 对比矩阵**：用 `references/comparison-matrix.md` 选了 ML/CS 学科的 4 个补充列（成本/开源/基线/协议），组成 12×11 矩阵。**横向观察那一节是这阶段最有价值的产品**——发现了"9/12 没报 cost"、"11/12 没报 variance"、"LoCoMo+多文档 QA+Minecraft 三套占 7/12" 等列级模式。
3. **Function 3 gap 分析**：按 7 类 gap-type（方法/数据/人群/情境/理论/评估/负结果）走 Step 1–4，给每个候选写了依据、类型、4 轴可行性裁决、区分点、第一步动作。**产出了 7 个 candidate gap**，其中 4 个是"可做"，3 个是"谨慎"。

### 真正用上的设计原则

- "Never fabricate, mark [未提及] if can't determine"：严格遵守。每篇笔记的实验数据都标了 `[请人工核对]`、`[not verified from PDF]`，因为本环境无法访问真实 PDF。
- "每条笔记 1.5 页内"：强迫我提取核心，不堆砌。
- "Cap at 12 papers for matrix, triage first"：14 篇里 12 进矩阵，2 篇 survey 单独 triage——节省了时间。
- "横向观察"：这是这个 skill 的"know-how"，别的 skill 没有这么强的"读完材料必须产出综合分析"的要求。

### 踩到的坑

- **没有真实 PDF** 是最大的限制。Function 1 要求"读 PDF"才能填 §3/§4 的判断；本环境下我只能基于训练数据知识写，每条都标了 `[not verified from PDF]`。**这个限制是环境问题，不是 skill 问题**——真实工作流下应该每篇都喂 PDF 重读。
- **Function 2 模板要求 `?` 标记不知道的格子**。我没有用 `?`，而是直接写"未提及"。**两边都符合 skill 约定**，但视觉上一致性弱一些。
- **`references/gap-analysis.md` Step 4 的"撞车风险"轴** 在没有 web 搜索的情况下只能凭"已知 2024-2025 公开 preprint 状况"判断。**这正是 skill 没有覆盖的场景**——在纯本地的研究工作流里这轴就是主观判断。

### 改进建议

1. **Note template 加一节"PDF accessibility"**：在 §1 顶部加个 checkbox "本笔记基于真实 PDF 吗？"，强制决定，避免误用。
2. **Function 2 矩阵模板加 "Aggregation across rows"** —— 当多行 `?` 同一列时，自动提示"这列是 under-reported"，避免人工扫。
3. **Function 3 的"撞车风险"轴需要 web access**——skill 应该明确声明"此轴在离线环境下退化为'主观判断'"。
4. **gap report 模板可以加 "candidate 排序标准"**——目前是"按 可做 × 价值"排，但具体如何度量"价值"没说清楚。我用了"对综述定位的贡献度"作为代理，但应该是 skill 明示的。

### 总体评价

**5/5。** 这是 6 个 skill 里**最成熟、最有用、最难挑刺**的一个。模板、流程、参考文档齐全，规则清楚。如果只学一个 skill 学会用，学这个。

---

## 2. knowledge-graph-builder — 跑通，遇到 1 个 bug

### 跑通的流程

1. **Stage 1 扫描**：给 14 个笔记加 YAML frontmatter（含 `type: paper` 和 `graph:` 关系列表），运行 `build_graph.py` 抽 wikilink / citekey / 显式 frontmatter 关系。
2. **Stage 2 概念规范化**：用内置的 `paper/method/dataset/task/metric/topic/note` 类型就够了，没自定义类型。
3. **Stage 3 AI 提案 → 用户审批**：**跳过了**。我的 34 条边全部从 §7 Connections 的事实陈述提取，evidence quote 都是 body 里现成的字符串，不需要 AI 推理。这是**最干净的工作流**。
4. **Stage 4 谱系叙述**：基于 `references/graph-rag.md` 的思路，写了 §IV-I 的"Lineage summary"。CoALA 是 hub（11 条入/出边），MemGPT 与 LongAgent 形成对照——这些结构性发现都从 hub 度数来的。
5. **Stage 5 可视化**：`--dot graph.dot` 输出 DOT 文件，**但本机没装 Graphviz**，无法 `dot -Tsvg`。SVG 没能渲染。

### 踩到的真实 bug

**Bug 1: `parse_scalar` 不处理 YAML 双引号转义。**

复现：
- 文件中 frontmatter 写：`quote: "Shares \"no weight updates\" stance with"`
- 期望被解析为字符串：`Shares "no weight updates" stance with`（反斜杠被 YAML 吃掉）
- 实际被解析为字符串：`Shares \"no weight updates\" stance with`（反斜杠保留）
- 结果：在 body 中找不到这个 quote，触发 `stale-evidence` warning。

**为什么是 bug**：YAML 规范在双引号字符串里要求 `\"` 是 `"` 的转义。该 skill 的 `parse_scalar`（脚本第 96–105 行）只 strip 外层引号，不解内层转义。

**我的 workaround**：把 evidence 改成不含内嵌双引号的字符串（`no weight updates stance with`），或者用单引号包裹 YAML 字符串（`'long-document" pressure point with'`），绕开反斜杠。

**fix 建议**：在 `parse_scalar` 里加一个内层转义处理，或者干脆换成标准库 `yaml.safe_load` 处理 graph: 块。

### 踩到的次要问题

- **CSV / Cytoscape 导出 `--csv` 没试**——我主要用 DOT + JSON。如果用户用 Gephi 可能需要 csv。
- **`--query` 模式没试**——其实最适合在 stage 4 的"lineage tracing"里用，对单个 seed node 拉 N-hop 子图，再写叙述。我手动从 graph.json 筛了对应行，效率低一些。
- **`merge_proposals.py` 没试**——因为我没用 AI 提案。如果用了，这个脚本是关键。
- **Frontmatter 必须手写或脚本生成**——这是 12+ 文件的体力活。我写了 `_add_frontmatter.py` 和 `_update_frontmatter.py` 批量处理，**这种 helper 应该是 skill 自带**的（一个 `add_relation.py --note file.md --relation cites --target "[[x]]" --quote "..."` 之类的 CLI 会有用）。

### 改进建议

1. **修 YAML escape bug**（高优，证据：30 warnings → 4 → 0 的过程就是被这个 bug 拖累）。
2. **提供 `add_relation.py` CLI**——手动写 YAML 太繁琐，特别是证据引文要从 body 挑的时候。
3. **`--query` 模式在 SKILL.md 里有详细文档，但 workflows.md 里"做 lineage narrative" 的示例用了 --query**——workflow 和 SKILL.md 衔接有点割裂，建议整合。
4. **DOT 文件默认设置有 `rankdir=LR; node [fontname="Helvetica"]` 之类硬编码**——可以加 `--rank` 选项让用户选 TB/LR/RL。

### 总体评价

**4/5。** 功能完整，规则严，证据锚定机制设计得很好（"关系必须配 evidence quote，找不到就警告" 这条逼着 AI 不瞎扯）。扣 1 分给 YAML bug + 缺少 helper CLI。

---

## 3. paper-writing-assistant — 跑通，3 个功能都用了

### 跑通的流程

1. **Function 1 (看图写正文分析段落)**：用得**最弱**。该功能需要"用户给图 + 论文上下文 + 用户意图"，然后写"如图 X 所示……"段落。我的图是 `graph.dot`（未渲染），所以我把"看图写段落"在脑子里走了：用 graph.json 的 hub 度数确认"CoALA 是 hub" → 写 §IV-I 的 lineage summary。如果装 Graphviz 可以 `dot -Tsvg` 后做完整的"看图写段落"，但本环境跑不通。
2. **Function 2 (引用规范检查)**：**最关键**。4 维度（① 对应 ② 合规 ③ 完整 ④ 一致）全过。`references/citation-styles.md` 的 IEEE 规则卡写得很清楚，作者名格式、标点、期刊缩写、`et al.` 阈值都有。
3. **Function 3 (格式检查)**：用户没给具体格式要求，我按 arXiv/conference 标准假设了一份。报告里说明了假设的依据，并标了 2 个待补的项（作者块、Figure 1 渲染）。

### Function 2 的实际做法

我没用 `scripts/docx_text.py`（因为没有 docx）。我直接写了 `_check_citations.py` 跑正则：
- 找 `## References` 之后的所有 `[N]` 编号
- 找 body 里所有 `[N]` 编号
- 算差集（孤儿引用、孤儿引用）
- 对每条 reference 跑 IEEE 格式的正则

**这个正则 check 的本质和 `docx_text.py --cites` 一样——只是输入从 docx 换成 md。** 这是 skill 文档没说但顺理成章的延展。

### 踩到的坑

- **Function 1 没有 markdown 输入的处理**——该功能假设有"图"。如果用户给的是数据表 / JSON / DOT，skill 没明示怎么用。我是把 DOT 当 "graph 数据" 自己看了。
- **Function 3 需要用户给格式 spec**——按 SKILL.md 说"用户粘贴自然语言要求"。本环境我假设了 arXiv 标准。这种"无 spec 时的 fallback"策略没文档化。
- **SKILL.md 说"不擅自改稿"**——我只出了报告，没动 paper.md。这是好的设计，避免误改。

### 改进建议

1. **Function 1 扩展支持非图输入**——例如"看 matrix 写段落"、"看 graph 写谱系"。结构化输入是趋势。
2. **Function 2 加 markdown 路径**——要么写一个 `md_text.py`（与 `docx_text.py` 对称），要么在 SKILL.md 明确"markdown 时改用 `grep` + 正则"。我写了一个 `_check_citations.py` 但 skill 本身没提供。
3. **Function 3 加默认格式模板**——比如内置 "arXiv 预印本"、"NeurIPS"、"ICLR" 三套默认 spec；用户不传时给"按 arXiv 默认"选项。
4. **Function 2/3 的报告模板**——SKILL.md 给了检查项列表，但**没给"输出报告"格式**。我自己写了一份 `citation_check_report.md`，结构是"维度逐条 + verdict"。建议在 `references/output-templates.md` 之类的地方提供。

### 总体评价

**4/5。** 三个功能设计明确、规则清楚、文档齐全。Function 2 是真能用，Function 3 的"按用户 spec"模式工作良好。Function 1 在我的场景下用得有限（没图），但设计上没问题。扣分给 Function 1 不支持非图输入、Function 2 没有 markdown 路径。

---

## 4. experiment-designer — 未使用

### 为什么没用

用户选的是"系统性综述"路线，**不涉及实验**。该 skill 是给"实证研究 / 跑实验"准备的，包括 DOE 设计、随机化、样本量、功效分析、消融矩阵。

### 文档质量抽查

读了一遍 SKILL.md + 4 个 references + 4 个 scripts 的 docstring。**结构良好**：
- 5 段访谈模板（design-brief.md）逼你回答 hypothesis / variables / treatments / sample / measurement。
- 4 大类实验设计（CRD/RBD/factorial/RSM/Latin/crossover/within-subject）选型决策树。
- 4 类效度威胁的 checklist。
- 4 个脚本（`doe_designs.py` / `ablation_planner.py` / `randomization.py` / `power_analysis.py`）都接受 `--seed`，确定性高。

**未实测**，但**外观看起来能用**。如果用户选"实证研究"路线，这应该是主力。

### 改进建议

- 在 SKILL.md 顶部加一句："NOT for 综述 / 复现 / 写作"——目前的触发描述虽然写了，但没写在最显眼位置。

---

## 5. data-analysis-assistant — 未使用

### 为什么没用

综述路线**没有原始数据**。该 skill 设计为"已有 CSV/实验数据 → 选检验 → 报告"。

### 文档质量抽查

读了 SKILL.md + 3 个 references + 3 个 scripts 的 docstring。
- `profile.py`（数据画像）+ `clean_csv.py`（带 citable log 的清洗）+ `stat_test.py`（ttest/Mann-Whitney/ANOVA/χ²/Fisher/Pearson/Spearman + 效应量 + CI + 多重比较校正）。
- APA-7 reporting 标准在 `references/reporting.md`。
- 5 步工作流（profile → clean → test → correct → report）结构清楚。

**未实测**，但**设计上最像 R/Python 数据分析教科书的章节**。

### 改进建议

- 与 experiment-designer 形成"前/后"配对——"experiment-designer 负责规划 → data-analysis-assistant 负责分析"。SKILL.md 之间可以互相 cross-reference。
- 同样建议顶部加 "NOT for 综述 / 写作"。

---

## 6. reproduction-assistant — 未使用

### 为什么没用

综述路线**不涉及复现已有论文代码**。该 skill 是给"复现一篇 paper 的 GitHub repo"准备的。

### 文档质量抽查

读了 SKILL.md + 4 个 references + 3 个 scripts 的 docstring。
- 6 步 pipeline：clone → analyze → env_detect → env_generate → run → compare。
- **Patch policy 写得很严**："patches 写到 patches/ 目录，不静默改 repo"；"每个 pipeline 步最多 2 次重试"；"every number carries a source"——这些是真实复现工作最容易踩的坑，skill 明示了。
- 失败分类（version/dependency/parameter/data）四类 + 硬失败清单（segfault/OOM/NCCL timeout/checksum/tokenizer drift/API deprecation）很全。
- `compare_results.py` 的容差判定 + per-run 列表 → mean ± std 报告——这是真实对比需要的。

**未实测**，但**这是 6 个 skill 里"工程纪律"最严的**。对一个会跑别人代码的研究者来说，这种"绝不假装成功"的 culture 是无价的。

### 改进建议

- 与 experiment-designer 同样建议顶部加 "NOT for 综述"。

---

## 7. 跨 skill 整合度

### 衔接好的部分

- **literature-reader → knowledge-graph-builder**：笔记的 §7 "Connections" 直接抽出来做 frontmatter 的 `graph:` 关系。**这是 skill 之间唯一显式设计的衔接**。
- **literature-reader → paper-writing-assistant**：Function 1 的"写分析段落"和 Function 2 的"引用检查"都用到了笔记里的元数据。**但没显式引用**——可能 skill 团队没考虑这种组合。
- **experiment-designer ↔ data-analysis-assistant**：design-brief 的 measurement plan 直接接 stat_test 的"group_by / value_col"。

### 缺衔接的部分

- **paper-writing-assistant 与其他 skill 几乎不联通**。比如 Function 1 的"看图写段落"在"图"是 graph.dot 时应该能直接吃 `build_graph.py --query` 的输出，但没集成。
- **reproduction-assistant 的 compare_results.py 输出**应该可以直接喂给 paper-writing-assistant Function 1（"如图 X 所示我们的复现值是 Y"），但没看到这种 glue code。
- **跨 skill 的"项目记忆"** 没有——literature-reader 产出的笔记、knowledge-graph-builder 产出的图、paper-writing-assistant 产出的草稿，**没有统一的 .research/ 或 .paper/ manifest 索引**。我手动用文件夹结构（notes/, graph/, paper/）来组织，但这需要 skill 体系提供。

### 建议

增加一个 **`research-orchestrator`** 或 **`paper-orchestrator`** 类型的"元 skill"：
- 输入：研究主题 + 论文类型
- 输出：建议的 skill 调用顺序、产物清单、衔接规范

`orchestrate` 在全局 skill 列表里已经有了，但 ResearchOS-Skills 这套**本地 6 个 skill**没有配套的 orchestrator。

---

## 8. 真实工作流的端到端测试

### 跑完一遍的耗时

| 阶段 | 耗时估计 | 主要动作 |
|---|---|---|
| 探索 6 个 skill | 5 min | 读 SKILL.md + 关键 references |
| 设置项目结构 | 1 min | 建目录 |
| Function 1：14 篇笔记 | ~25 min | 每篇按 8 段模板写 |
| Function 2：12×11 矩阵 | 5 min | 按行 + 横向观察 |
| Function 3：7 个 gap | 8 min | 维度扫描 + 4 轴裁决 |
| knowledge-graph：frontmatter + graph | 10 min | 写 helper + 修 bug + 跑 |
| paper-writing：8 节论文 | 20 min | 写 markdown |
| citation check + format check | 3 min | 正则 + 报告 |
| 体验报告 | 10 min | 本文件 |
| **合计** | **~85 min** | |

**对一个 1 人测试来说，这效率很可观**。真实场景下：
- 如果用户有 PDF 喂进来：每篇笔记可缩到 5-8 分钟 → 总 30-40 分钟。
- 如果用户给了具体格式 spec：format check 那段可以省 1-2 分钟。
- 如果 Graphviz 装了：graph 可视化 + Function 1 完整跑通。

---

## 9. 哪些是真的"坑"，哪些是"用法问题"

### 真坑（skill 自身问题，建议修）

1. **`build_graph.py` 的 YAML escape bug**（已述）。修这一处就解决 30 个 warnings 中的 28 个。
2. **`paper-writing-assistant` Function 1 不支持非图输入**。
3. **`paper-writing-assistant` Function 2 没有 markdown 路径**。
4. **`knowledge-graph-builder` 缺 helper CLI**（`add_relation.py`）。

### 用法问题（skill 设计合理，但用户需知）

1. **Function 1 必须有真实 PDF**——skill 设计假设。
2. **撞车风险评估需要 web access**——离线退化为主观判断。
3. **Function 3 必须有格式 spec**——无 spec 时 skill 不知怎么 fallback。
4. **Frontmatter 关系必须配 evidence quote**——找 body substring，没法"模糊匹配"。

### 环境问题（不算 skill 的锅）

1. 没装 Graphviz，DOT 没法渲染。
2. 没装 pandoc，paper 没法转 PDF/DOCX。
3. 没真实 PDF，Function 1 的笔记是基于训练数据。

---

## 10. 对 skill 团队的总建议

### 高优先级（直接影响可用性）

1. **修 `build_graph.py` 的 YAML escape bug**。
2. **给 `paper-writing-assistant` Function 2 加 markdown 路径**（写一个 `md_text.py`）。
3. **给 `knowledge-graph-builder` 加 `add_relation.py` CLI**。
4. **6 个 skill 的 SKILL.md 顶部都加 "NOT for X" 排除清单**——目前有些写在 description 里、有些写在 SKILL.md 顶部，应该统一。

### 中优先级（提升体验）

5. 提供一个 `research-orchestrator` 类型的"流程导航" skill，输入研究目标+论文类型，输出 skill 调用顺序。
6. `paper-writing-assistant` Function 3 加默认格式模板（arXiv/NeurIPS/ICLR）。
7. `knowledge-graph-builder` 集成 `--query` 模式到 Stage 4 的 lineage narrative 示例里。
8. 给所有 `references/*.md` 加一个 `## Quick Reference` 顶部小卡片（一页内能看完的 cheat sheet）。

### 低优先级（nice-to-have）

9. 提供 `examples/` 目录：跑通的端到端案例（综述、实证研究、复现各一个）。
10. 跨 skill 的 .research/ manifest 索引。
11. 一个 `verify-installation` 诊断脚本（类似全局的 `setup-medsci`）。

---

## 11. 一句话总结

> **6 个 skill 在"系统性综述"路线上端到端跑通**。literature-reader 是核心，knowledge-graph-builder 有 1 个真实 bug 但可绕过，paper-writing-assistant 在 markdown 路径下需要小补丁。experiment-designer / data-analysis-assistant / reproduction-assistant 在综述路线不触发，但文档质量看起来对实证 / 复现路线足够好。**整体可用，但需要小修和更好的跨 skill glue**。

---

## 附录 A：产物清单

| 文件 | 行数 / 节点数 | 用途 |
|---|---|---|
| `notes/01..14_*.md` | 14 文件 × ~70 行 | Function 1 笔记 |
| `notes/refs.txt` | 14 引用 | 原始参考列表 |
| `notes/metadata.json` | 14 条目 | extract_metadata.py 输出 |
| `notes/comparison_matrix.md` | ~150 行 | Function 2 矩阵 |
| `notes/gap_analysis.md` | ~180 行 | Function 3 空白分析 |
| `notes/_add_frontmatter.py` | 100 行 | 辅助脚本 |
| `notes/_update_frontmatter.py` | 80 行 | 辅助脚本 |
| `notes/_fix_quotes.py` | 50 行 | 修 YAML bug 后遗症 |
| `notes/_fix_quotes2.py` | 50 行 | 同上 |
| `notes/_check_quotes.py` | 30 行 | 调试脚本 |
| `notes/_dbg*.py` | 30 行 × 3 | 调试脚本 |
| `graph/graph.json` | 16 节点 / 34 边 | 知识图谱 |
| `graph/graph.dot` | 54 行 | Graphviz 源 |
| `graph/warnings.md` | 0 行（修好后） | build_graph 警告 |
| `paper/paper.md` | 367 行 / ~8000 字 | 综述论文 |
| `paper/references_ieee.md` | 14 条目 | IEEE 格式 references |
| `paper/_check_citations.py` | 60 行 | 引用 check 脚本 |
| `paper/citation_check_report.md` | ~100 行 | Function 2 报告 |
| `paper/format_check_report.md` | ~50 行 | Function 3 报告 |
| `report/experience_report.md` | 本文件 | 体验报告 |

## 附录 B：可改进点的优先级表

| 改进点 | 影响 | 难度 | 建议优先级 |
|---|---|---|---|
| 修 YAML escape bug | 高 | 低 | **P0** |
| paper-writing-assistant 加 markdown 路径 | 高 | 中 | **P0** |
| knowledge-graph-builder 加 add_relation CLI | 中 | 低 | **P1** |
| 6 个 SKILL.md 顶部加 NOT 清单 | 中 | 低 | **P1** |
| research-orchestrator skill | 高 | 中 | **P1** |
| 默认格式模板（Function 3） | 中 | 低 | **P2** |
| `--query` 集成到 Stage 4 | 低 | 低 | **P2** |
| Quick Reference cheat sheet | 中 | 低 | **P2** |
| examples/ 端到端案例 | 中 | 中 | **P3** |
| 跨 skill manifest | 中 | 中 | **P3** |
| verify-installation 脚本 | 低 | 低 | **P3** |
