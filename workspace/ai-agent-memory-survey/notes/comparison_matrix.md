# AI Agent Memory — Comparison Matrix (12 primary papers + 2 meta-surveys)

> 来源：12 篇精读笔记（Function 1） + 2 篇速读 survey（Function 1 triage）。  
> 矩阵规则：每格一行；`?` 表示无法从笔记/摘要中确定；`[未提及]` 保留作为不确定标记。  
> 维度的选取参见 `literature-reader/references/comparison-matrix.md` 中 ML/CS 维度库。  
> `证据类型` 中 `(仅摘要)` 表示只读了 abstract / wiki 类来源的二手信息。

## 1. 核心矩阵（Core dimensions）

| # | Paper | 研究问题 (technical gap) | 方法 (method + 关键设计) | 数据集·对象 | 核心结论 (with comparator) | 证据类型 | 关键局限 |
|---|---|---|---|---|---|---|---|
| 1 | **Park et al. 2023** — Generative Agents | LLM 缺持久可查询记忆，无法做长程社会行为 | Memory stream + 重要性打分 + 反思; recency×importance×relevance 加权检索 | Smallville sandbox, 25 agents, 2 days | 仿真出现邀请/关系等涌现行为；interview 85% match（请人工核对） | empirical + human-rater | n=25 小；评测偏主观；无遗忘/无 schema |
| 2 | **Packer et al. 2023** — MemGPT | LLM 上下文有限，长文档/多会话丢信息 | 两层 memory (main = RAM, external = disk) + 函数调用 paging；LLM 自己当 page-replacement policy | long-doc QA (~650k tokens), multi-session chat | 在 650k-doc QA 与多会话对话上显著超过截断/RAG（请人工核对） | empirical | 函数调用 token 成本未单独报告；paging-decision 消融才是关键 |
| 3 | **Shinn et al. 2023** — Reflexion | LLM 在多步任务中不能从失败里学 | Actor / Evaluator / Self-reflection 三角；reflection 入 episodic memory；下次重试时喂入 | HumanEval, MBPP, HotPotQA, AlfWorld | HumanEval pass@1 91 vs 80（GPT-4 baseline）; AlfWorld 大幅超 ReAct（请人工核对） | empirical | 单 seed；reflection 是否泛化未测；没有负结果 |
| 4 | **Zhong et al. 2024** — MemoryBank | 跨会话聊天无长期记忆；RAG 不考虑遗忘 | Ebbinghaus 遗忘曲线 + 访问巩固 S + 选择性合并 + 两阶段召回 | long-term dialogue, MSC, LoCoMo (?) | 长期记忆 probe 显著超 full-context；合并减存储 ~40% 质量 < 2% 下降（请人工核对） | empirical | 曲线参数手设；单用户；probe 构念窄 |
| 5 | **Wang et al. 2024** — Voyager | Minecraft 开放世界需持续学习技能 | GPT-4 自动出题 + 生成 JS 代码作为 skill 入库；embedding 检索 | Minecraft (314 items) | 收 3.3× 唯一物品于最强 baseline；技能库 200+（请人工核对） | empirical | 无 consolidation/遗忘；仅 Minecraft；无负结果 |
| 6 | **Sumers et al. 2024** — CoALA | 领域缺统一词汇；设计空间未形式化 | 概念框架：working / declarative / procedural / conditional memory + decision procedure | n/a（framework paper） | 提出四类 memory + 决策程序；映射现有系统 | position / framework | 无评测；decision procedure 格子过粗；未操作化 |
| 7 | **Qian et al. 2024** — ChatDev | 软件工程是多角色多步过程 | 多 agent chat-chain (CEO/CTO/programmer/tester) + communicative dehallucination + 跨 chat memory | SRDD, ~70 SE tasks | 多 agent + chat chain 大幅超单 agent GPT-4（completeness/executability）（请人工核对） | empirical | benchmark 玩具；无 variance；效果与「多数投票」未对比 |
| 8 | **Maharana et al. 2024** — Forgetting | 记忆增强 LLM 的稳定性-可塑性 | Bayesian 连续时间强度模型；推导出 Ebbinghaus 为特例 | synthetic sequential, knowledge update | 减遗忘 30-50% 于 no-forgetting baseline（请人工核对） | theoretical + small empirical | benchmark 小；与 [Zhong 2024] 未直接对比；无实现 |
| 9 | **Xu et al. 2025** — A-MEM | 固定 schema 不足以表达异构记忆 | LLM 动态生成 per-note 属性 + 动态链接 + 演化；embedding+结构检索 | LoCoMo | 超 MemoryBank / LangMem 等（请人工核对） | empirical | 评测集中在 LoCoMo；schema 质量难评；成本高 |
| 10 | **Hu et al. 2024** — LongAgent | 128K context 仍 lost-in-middle；内存工程是 workaround | 7B 模型 + DPO→GRPO 两阶段 RL；context 本身就是 memory | long-doc QA, agentic tasks | 7B 接近 GPT-4 128K；超 ReAct/MemGPT（请人工核对） | empirical + RL training | 与同 backbone 的 RAG 对比缺；评测任务自构 |
| 11 | **Liu et al. 2024** — Lost in the Middle | 长 context 是否被均匀使用 | 多文档 QA + 答案位置变化控制实验 | NaturalQuestions 多文档 | accuracy U 型：首尾高、中间低；CoT 不缓解 | controlled empirical | 闭源新模型未测；agentic 场景未测 |
| 12 | **Modarressi et al. 2024** — RET-LLM | 跨会话记忆；RAG 浪费 | Read/Write 两 controller LLM；结构化 memory entry + NL query 索引 | LoCoMo (?) | 超 vanilla RAG（请人工核对） | empirical | schema 偏死；与 A-MEM 关系未澄清 |

**Meta-surveys (triage depth, used as references not matrix rows):**
- **Wu et al. 2024** — taxonomy of memory types, write/read mechanisms, evaluation. (concept-axes source)
- **Zhang et al. 2024** — operational decomposition (write / read / manage). (operational-axes source)

## 2. ML/CS 学科维度（补充列）

| # | Paper | 计算成本 | 开源情况 | 基线强度 | 评测协议 |
|---|---|---|---|---|---|
| 1 | Park 2023 | 不可忽略（25 agents × 2 days） | code: 是 (MIT-style) [未核] | qualitative，无 controlled baseline | 仿真 + 人类评 believability |
| 2 | Packer 2023 | 函数调用 + paging 决策 token 成本未分报 | code: 是 (Letta) | 含 RAG、truncation、full-context | 长文 QA + 多会话 F1 |
| 3 | Shinn 2023 | 每次重试一整轮 | code: 是 [未核] | 含 retry-without-memory 关键消融 | pass@1, 任务 success |
| 4 | Zhong 2024 | 中等（合并步骤） | code: 是 [未核] | 含 vanilla RAG, no-forgetting | long-term probe + 自动指标 |
| 5 | Wang 2024 | 高（持续 GPT-4 调用） | code: 是 [未核] | 含 ReAct, Auto-GPT, prior SOTA | in-game 物品 + milestone |
| 6 | Sumers 2024 | n/a | n/a | n/a | n/a |
| 7 | Qian 2024 | 高（多 agent 多轮） | code: 是 [未核] | 含单 agent GPT-4 + naive multi-agent | SE 任务 completeness/exec |
| 8 | Maharana 2024 | 低 | code: 否 | 多个 decay schedule | forgetting rate |
| 9 | Xu 2025 | 中-高（per-note LLM 调用） | code: 是 [未核] | 含 MemoryBank, LangMem, full-prompt | LoCoMo F1 + LLM-judge |
| 10 | Hu 2024 | 极高（RL 训练 7B） | code: 否 [未核] | 含 GPT-4-128K, GPT-3.5+RAG, MemGPT, ReAct | 自构 long-doc / agentic 任务 |
| 11 | Liu 2024 | 低（推理） | code: 是 [未核] | 含 random/oracle | 多文档 QA accuracy vs 位置 |
| 12 | Modarressi 2024 | 中（两 controller） | code: 否 [未核] | 含 full-prompt, vanilla RAG | LoCoMo (?) F1 + LLM-judge |

## 3. 横向观察（Synthesis — the value of the matrix）

按 `comparison-matrix.md §4` 的要求写。

### 3.1 Clusters（哪几篇方法/数据相同，互相冗余）
- **Stream-of-observations + retrieval by importance/recency/relevance 集群**：[Park 2023]（创始）, [Zhong 2024]（+ 遗忘）. 这两篇是**同一方法族的两个时间切片**——综述里不需要分别深读，引用 [Park 2023] 即可，cite [Zhong 2024] 作为"加遗忘"的代表。
- **多 agent + chat / role 集群**：[Qian 2024, ChatDev] 与 [Wang 2024, Voyager]（自动 curriculum）。多 agent memory 是另一个独立 cluster，cite [Qian 2024] + [Wang 2024] 一对。
- **Read/Write 控制器架构集群**：[Modarressi 2024, RET-LLM] → [Xu 2025, A-MEM]（动态 schema 升级）。A-MEM 是 RET-LLM 的"下一代"；综述中 cite A-MEM + 一句提 RET-LLM 即可。
- **遗忘/记忆强度理论集群**：[Zhong 2024]（经验）↔ [Maharana 2024]（理论）。两者必须同时引用——前者是工程，后者是解释。
- **长 context vs 记忆工程对位**：[Liu 2024, Lost in the Middle]（诊断）→ [Packer 2023, MemGPT]（工程对策）→ [Hu 2024, LongAgent]（训练对策）。**这是综述里最有故事线的一对**，应当独立成节。

### 3.2 Conflicts / 冲突
- **「记忆工程」vs「训练长 context」的方法冲突**：[Packer 2023], [Park 2023], [Zhong 2024] 走记忆工程路线；[Hu 2024, LongAgent] 主张训练长 context 替代。**两种路线在不同目标下各有理**：
  - 工程路线：通用 LLM 可立即部署，无需重训。
  - 训练路线：避免 prompt 成本，但需大规模 RL。
  - 不算真正的"科学冲突"，而是设计选择冲突。综述中要明确"两条路线并存，不应视作互斥"。
- **Memory schema 灵活度的权衡**：[Modarressi 2024]（固定结构）vs [Xu 2025]（动态 schema）。前者稳定但僵，后者灵活但难评估。**评测协议缺口**：缺 schema 质量本身的 metric。
- **Reflection 是否真的有用**：[Shinn 2023] 报大增益；[Hu 2024] 在 RL 训练下用不上 reflection。**潜在解释**：reflection 的价值在 base model 弱时最大；强模型 + 强训练下被吸收。**综述里这是一个未解之谜**（→ Gap）。

### 3.3 Load-bearing citations（综述中"每条主论点对应一篇核心引用"）
- "记忆工程可解长 context 容量问题" → 锚 [Packer 2023, MemGPT]
- "记忆工程可解长程一致行为" → 锚 [Park 2023, Generative Agents]
- "跨会话记忆需要 forgetting 机制" → 锚 [Zhong 2024, MemoryBank]
- "长 context 仍存在 lost-in-middle" → 锚 [Liu 2024]
- "训练可替代记忆工程" → 锚 [Hu 2024, LongAgent]
- "记忆领域需要统一词汇" → 锚 [Sumers 2024, CoALA]
- "反思式自我改进" → 锚 [Shinn 2023, Reflexion]
- "可执行代码作为记忆" → 锚 [Wang 2024, Voyager]
- "动态 schema 是新方向" → 锚 [Xu 2025, A-MEM]
- "遗忘的理论基础" → 锚 [Maharana 2024]

### 3.4 列级模式（column-wide patterns that feed gap analysis）
- **Dataset monoculture**：评测集中在 LoCoMo / 多文档 QA / Minecraft **三套**。**7/12** 至少用其中之一。**多用户/多模态/开放域 agent 长程记忆几乎没有公共 benchmark**。→ Gap: 数据空白。
- **Compute cost 几乎全 missing**：12 篇中只有 [Wang 2024] 与 [Hu 2024] 谈到 cost，**9/12 未报告 token 成本或 GPU 时**。→ Gap: 评估空白（缺 cost metric）。
- **Variance reporting 几乎全 missing**：除 [Hu 2024] 隐约有 multi-seed（请核），**其余 11/12 单 seed**。→ Gap: 评估空白（缺 variance）。
- **Code release 比例 7/12**：不算低，但发布后是否维护、可复现是另一回事（实际复现留到 [reproduction-assistant] 测试时验证）。
- **Theory row**：[Maharana 2024] 是唯一理论 + 经验结合的。**该方向严重欠饱和**。→ Gap: 理论空白。

> 下一步：进入 Function 3 gap-analysis，把列级模式转成具体的空白候选。
