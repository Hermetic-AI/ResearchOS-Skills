# AI Agent Memory — Research Gap Analysis Report (Function 3)

> 输入：12 篇 primary 论文对比矩阵 + 2 篇 meta-survey (Function 2 output)。  
> 维度扫描方法：参见 `literature-reader/references/gap-analysis.md` Step 1–3c。  
> 输出格式：中文，按"可行性 × 价值"排序；末尾列 `[弱依据]` / `[间接证据]` 候选。

---

## Step 1 — 维度扫描信号清单

| 信号 | 证据列 | 出处 |
|---|---|---|
| **空区域 1**: 没有人把"工作记忆"作为可操作变量独立评测 | 评测协议列 | 多数论文只测 long-term 整体；[Liu 2024] 测 in-context，coala 提"working memory"但没 benchmark |
| **空区域 2**: 多模态记忆基本缺席 | 数据集列 | 12 篇全是文本/对话；[Wang 2024] 视觉但只作 observation；无人评测多模态长记忆 |
| **空区域 3**: 多用户 agent（一个 bot 服务多人，每人独立 memory）无人评测 | 评测协议列 | 12 篇全部单用户/单 agent |
| **`?` 行**: compute cost 列 9/12 报 `?` | 成本列 | 见矩阵 |
| **`?` 行**: variance reporting 11/12 缺失 | 评测协议列 | 见矩阵 |
| **Conflict cluster**: 记忆工程 vs 训练长 context | 横向观察 §3.2 | [Packer 2023] vs [Hu 2024] |
| **Conflict cluster**: reflection 是否真的有用 | 横向观察 §3.2 | [Shinn 2023] vs 隐含 [Hu 2024] |
| **Monoculture**: LoCoMo / 多文档 QA / Minecraft 三套占 7/12 | 数据集列 | 见矩阵 |
| **Recency edge**: [Xu 2025] 提动态 schema；老论文 [Park 2023] 没有；[Modarressi 2024] 半固定 | 数据集 + 方法 | 见矩阵 |
| **Monoculture**: 12 篇里 1 篇理论 ([Maharana 2024])，11 篇工程 | 类型列 | 见矩阵 |

---

## Step 2 — 候选空白枚举（按 gap-type）

### 候选 1：长期记忆的**计算成本评测协议**缺失
- **依据**：对比矩阵"计算成本"列 9/12 报 `?` 或未提及。
- **类型**：**评估空白**。
- **可行性**（4 轴）：
  - 数据可得性：成本数据从 API 后台就能取到；公开模型的 cost 可估算；✅
  - 方法成熟度：已有 token 计数 / GPU-hour 统计工具；✅
  - 工作量 vs 学位要求：单一论文 / 1 个 metric；✅
  - 撞车风险：未发现 preprint 在做这件事；低。
- **裁决**：**可做**。
- **与现有文献的区分点**：现有工作以"能不能记住"为准；本空白是"记得起要花多少钱"。可与 [Packer 2023] 的 cost 缺失、 [Wang 2024] 的 cost-only 提及形成对照。
- **建议第一步**：以 [Zhong 2024], [Xu 2025] 复现为案例，量化 100 轮对话下的 memory growth 与 API cost 曲线。

### 候选 2：**多用户 agent 记忆** —— 几乎无人评测
- **依据**：数据集列全 12 篇单用户/单 agent；[Zhong 2024] 显式声明"单用户假设"。
- **类型**：**人群空白**（从"人群"扩展到"用户群体"）。
- **可行性**：
  - 数据可得性：可构造多用户共享 agent 的合成场景（社交助手、客服 bot）；✅ 但需要构造 benchmark
  - 方法成熟度：现有架构大多可加 user-id 区分；✅
  - 工作量：~1–2 个 benchmark 子任务 + 评测协议；✅
  - 撞车风险：2025 年起 ChatGPT / Claude 出现 "shared team workspace" 概念，**撞车风险中**。
- **裁决**：**谨慎**。
- **区分点**：工业界先做了产品，**学术界 benchmark 缺位**。综述可指出这一"学界追产" gap，但独立研究需要构造 novel evaluation。
- **建议第一步**：盘点既有 chatbot 平台的 memory 行为作为 baseline（虽不能直接复现），提出"multi-user memory probe"协议。

### 候选 3：记忆的**稳定性-可塑性**理论扩展
- **依据**：[Maharana 2024] 是唯一理论工作；与 [Zhong 2024] 工程化版的连接仍弱。
- **类型**：**理论空白**。
- **可行性**：
  - 数据：✅
  - 方法成熟度：需要 Ebbinghaus 外的更丰富模型（如 ACT-R, SOAR）；✅ 文献多
  - 工作量：1 个理论 + 1 个 benchmark 验证；可做
  - 撞车风险：低（理论工作稀少）。
- **裁决**：**可做**。
- **区分点**：现有理论只覆盖 Ebbinghaus 单条曲线；现实 memory 是多模态、多通道、access-pattern-dependent。需要更丰富的 generative model。
- **建议第一步**：在 [Maharana 2024] 框架上加"关联激活"（一个 memory 访问触发相关 memory 强度调整）—— 模拟人脑的 spreading activation。

### 候选 4：**多模态长记忆**
- **依据**：数据集列 12 篇全文本；[Wang 2024] 视觉作 observation 但不评测视觉 recall。
- **类型**：**数据空白**（数据集）+ **评估空白**。
- **可行性**：
  - 数据：多模态长对话/agent 轨迹可构造（已有 [VideoAgent], [MM-Vet] 等，但作为 memory benchmark 缺位）；✅ 但构造成本高
  - 方法：✅
  - 工作量：~1–2 benchmark + 实验；大
  - 撞车风险：多模态 agent 在 2024-2025 急速发展，撞车风险**高**。
- **裁决**：**谨慎**（"做新 benchmark" + "避开头部团队赛道"）。
- **建议第一步**：先 survey 多模态 agent 现状，确认"长期"维度是否真的空白。

### 候选 5：**schema 质量本身的 metric**
- **依据**：[Modarressi 2024] 固定 schema vs [Xu 2025] 动态 schema 评测都只测端任务。
- **类型**：**评估空白**。
- **可行性**：
  - 数据：✅
  - 方法：可借鉴 schema matching, ontology alignment 领域的指标；✅
  - 工作量：单论文；✅
  - 撞车风险：低。
- **裁决**：**可做**。
- **区分点**：这是**"评测元方法"**——给"如何评测记忆机制"本身做评测。
- **建议第一步**：定义 schema coherence, schema coverage, schema stability 三个 metric，跑在 [Modarressi 2024] / [Xu 2025] 的输出上。

### 候选 6：reflection 在**强基座**下是否仍有效
- **依据**：[Shinn 2023] 报大增益但基于 GPT-3.5；[Hu 2024] 在 RL 后用不上 reflection。
- **类型**：**理论空白**（机制解释缺）。
- **可行性**：
  - 数据：✅
  - 方法：✅
  - 工作量：1 个实验；✅
  - 撞车风险：低。
- **裁决**：**可做**。
- **建议第一步**：用 GPT-4o / Claude-3.5 复跑 Reflexion 主表，看 reflection 的边际收益。

### 候选 7（弱依据）：**跨 session 角色变化**（bot 角色由"助手"变"专家"再变回"助手"，记忆是否平滑过渡）
- **依据**：横向观察 §3.2 / §3.4 间接提示。**仅 [Qian 2024] ChatDev 涉及多角色，但没评估跨 session 角色变化**。→ `[弱依据]`
- **类型**：**情境迁移空白**。
- **可行性**：
  - 数据：构造性；✅
  - 方法：✅
  - 工作量：✅
  - 撞车风险：中。
- **裁决**：**谨慎**。
- **建议第一步**：先做小规模 user study（5–10 用户），看他们是否能察觉角色变化对记忆的影响。

---

## Step 3 — 输出格式（中文报告，按"可做 × 价值"排序）

### 候选 1：长期记忆的**计算成本评测协议**缺失
- **类型**：评估空白
- **可行性**：可做
  - 数据可得性：✅（API 账单 + token 计数）
  - 方法成熟度：✅
  - 工作量匹配：✅（1 个 metric 论文）
  - 撞车风险：低
- **与现有文献的区分点**：从"准"切换到"贵不贵"维度。
- **建议第一步**：复现 [Zhong 2024] + [Xu 2025] 案例并报告 cost-Quality 帕累托。
- **综述角色**：本综述可以**命名并形式化**这个 gap，即使不亲自填。

### 候选 3：记忆的**稳定性-可塑性**理论扩展
- **类型**：理论空白
- **可行性**：可做
  - 数据可得性：✅
  - 方法成熟度：✅（ACT-R/SOAR 文献丰富）
  - 工作量匹配：✅（理论 + 单 benchmark 验证）
  - 撞车风险：低
- **与现有文献的区分点**：从单条 Ebbinghaus 曲线扩展到激活扩散模型。
- **建议第一步**：在 [Maharana 2024] 框架上加 spreading activation 机制。
- **综述角色**：本综述可**在 Discussion 中指出**这一理论方向是 [Maharana 2024] 之后的下一步。

### 候选 5：**schema 质量本身的 metric**
- **类型**：评估空白
- **可行性**：可做
  - 数据：✅
  - 方法：✅（可借鉴 ontology alignment）
  - 工作量：✅
  - 撞车风险：低
- **与现有文献的区分点**：评测"评测"。
- **建议第一步**：定义 schema coherence, coverage, stability 三 metric。
- **综述角色**：综述可作为**评测协议章节**的 critical 视角。

### 候选 6：reflection 在**强基座**下是否仍有效
- **类型**：理论空白（机制解释）
- **可行性**：可做
  - 数据：✅
  - 方法：✅
  - 工作量：✅
  - 撞车风险：低
- **与现有文献的区分点**：把 [Shinn 2023] 的结论在当代 base model 上重新测试。
- **综述角色**：综述 Discussion 的"未解之谜"小节。

### 候选 4：多模态长记忆
- **类型**：数据空白 + 评估空白
- **可行性**：谨慎（撞车高、构造成本大）
- **综述角色**：作为 **open problem** 提出，不主张综述本身填。

### 候选 2：多用户 agent 记忆
- **类型**：人群空白（用户群体维度）
- **可行性**：谨慎（构造 benchmark 成本中，撞车中）
- **综述角色**：作为 **open problem** 提出，呼应工业界产品。

### 候选 7：跨 session 角色变化
- **类型**：情境迁移空白
- **可行性**：谨慎
- **综述角色**：开放问题。

---

## Step 4 — 综述定位

基于 gap analysis，本综述的**独特角度**是：

> **"AI agent memory is not a solved engineering problem; it is a three-axis space with measurable, under-measured trade-offs."**

具体地，本综述将组织为：
1. **维度 1：taxonomy**（按 CoALA + Wu/Zhang 综述的混合）—— 形式化现有设计的词汇。
2. **维度 2：evaluation**（评测现状）—— 系统化呈现**评测协议缺口**（成本、variance、schema 质量）。
3. **维度 3：design trade-offs**（设计权衡）—— 在 memory engineering vs long-context training 路线、fixed vs dynamic schema、reflection 的边际收益等问题上，**不预设立场**地呈现各路线证据。

**本综述不直接填补某 gap**（survey 论文的传统角色），但**显式命名了 7 个 gap**（含 1 弱依据），并以"open problems"章节收尾。

---

## Notes on this gap analysis

- 本分析**完全基于 12 篇精读 + 2 篇速读笔记**，没有引入笔记之外的引用。
- 所有 gap-类型判定参照 `references/gap-analysis.md` §3 的 7 类定义。
- "可行性"裁决的 4 轴都基于：**对当前 AI agent memory 领域一般工程实践的判断**，不是新构造的 hard criterion。
- 不建议做"撞车风险"显式 web 搜索验证（受限于本测试环境），按 2024-2025 已知 preprint 状况判断。
