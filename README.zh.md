# ResearchOS-Skills（科研技能集）

🌐 [English](README.md) · **中文**

---

<div align="center">

<img src="assets/architecture.png" alt="ResearchOS-Skills 架构图" width="800"/>

**面向 AI 编程代理的 29 个独立科研技能**

*覆盖完整科研生命周期：文献 → 设计 → 分析 → 写作 → 复现 → 答辩*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-29-green.svg)](skills/)
[![Tests](https://img.shields.io/badge/Tests-21%20通过-brightgreen.svg)](skills/md2latex/tests/)

</div>

---

## 📄 产出展示

<div align="center">

### AI Agent Memory: A Survey of Mechanisms, Trade-offs, and Open Problems

**8 页 IEEE 格式综述** — 分类体系、机制族、评估审计、7 个研究空白

[![Memory Survey 封面](assets/papers/memory_survey_p1.png)](workspace/ai-agent-memory-survey/paper/paper.pdf)

[📄 阅读 PDF](workspace/ai-agent-memory-survey/paper/paper.pdf) · [📝 源 Markdown](workspace/ai-agent-memory-survey/paper/paper.md)

*由 `literature-reader` + `scientific-plot` + `md2latex` 生成*

</div>

---

## 安装

### 一键安装（所有 AI 代理）

```bash
npx skills add Hermetic-AI/ResearchOS-Skills
```

支持：**Claude Code** · **OpenCode** · **Codex** · **Gemini CLI** · **Cursor**

### 安装单个技能

```bash
npx skills add Hermetic-AI/ResearchOS-Skills --skill "literature-reader"
```

### 安装后

重启代理。技能以斜杠命令形式出现：

| 命令 | 说明 |
|------|------|
| `/researchos` | 主编排器 — 路由到正确的子技能 |
| `/literature-reader` | 读/提取/审计论文，PDF/OCR，DOI 校验 |
| `/data-analysis-assistant` | 数据分析，回归，生存分析，时间序列 |
| `/paper-writing-assistant` | 论文写作/检查，引用，DOCX/LaTeX 格式 |
| `/reproduction-assistant` | 复现论文代码，结果对比 |
| `/scientific-plot` | 投稿级图表，统计图 |
| `/md2latex` | Markdown→LaTeX，含定理、交叉引用、编译校验 |
| `/experiment-designer` | 实验设计，DOE，功效分析，预注册 |
| `/knowledge-graph-builder` | 从笔记构建概念图谱 |
| ... | （共 29 个） |

---

## 核心技能

| 技能 | 方向 | 说明 |
|------|------|------|
| `literature-reader` | 文献 | PDF/OCR 提取，DOI/arXiv/PMID 审计，Zotero/BibTeX/RIS/EndNote 互换，证据锚定笔记 |
| `knowledge-graph-builder` | 知识 | 从 Markdown + paper-note JSON 构建类型化概念图谱，声明级证据，谱系追踪，GraphML/GEXF/RDF 导出 |
| `experiment-designer` | 设计 | 随机化/因子/DOE 设计，功效分析，预注册/SAP，随机化，适应性监控 |
| `data-analysis-assistant` | 分析 | 数据画像/清洗，回归/GLM/ANCOVA，Cox/生存分析，SARIMAX，面板效应，MICE/敏感性/等效性 |
| `paper-writing-assistant` | 写作 | 图表分析段落，引用审计（GB/T 7714/IEEE/APA/ACM），DOCX/LaTeX 格式检查，DOCX 域语义 |
| `reproduction-assistant` | 复现 | 仓库探测，依赖解析，分布级结果对比，失败诊断，隔离执行 |
| `scientific-plot` | 可视化 | 投稿级图表（6 模板，期刊主题，显著性星标），Excalidraw/SVG，Mermaid/Graphviz/PlantUML |
| `md2latex` | 转换 | Markdown→LaTeX：脚注、定理、定义列表、交叉引用、图片属性、CSL→BibTeX、长表、编译校验 |

---

## 扩展技能

### 分析与证据

| 技能 | 说明 |
|------|------|
| `scholarly-search-manager` | 检索计划，DOI/题名去重，RIS/BibTeX/CSV 导出 |
| `systematic-review-meta-analysis` | PICOS/PRISMA，效应量计算，固定/随机效应元分析，I²/τ² 异质性 |
| `causal-inference-assistant` | DAG 审计，倾向评分匹配/加权，双重差分，断点回归，E-value 敏感性 |
| `survey-and-psychometrics` | EFA（主成分 + 方差最大旋转），Cronbach's α，题总相关，Rasch 1PL 拟合 |
| `qualitative-research-assistant` | 编码本，Krippendorff's α，饱和度曲线追踪，审计轨迹 |

### 诚信与管理

| 技能 | 说明 |
|------|------|
| `research-project-orchestrator` | 项目初始化，产物路由，决策溯源追踪 |
| `research-integrity-and-ethics` | 伦理准备，披露计划，政策覆盖审计 |
| `research-data-management` | DMP，FAIR，匿名化筛查，发布就绪度 |
| `research-proposal-and-grant` | 提案 charter，Specific Aims 审计，预算假设审计 |
| `research-software-quality` | 发布审计（LICENSE/README/CITATION.cff），基准执行 |

### 交流与答辩

| 技能 | 说明 |
|------|------|
| `academic-presentation-poster` | Beamer/reveal.js 幻灯片布局，WCAG 对比度检查，渲染预览清单 |
| `thesis-defense-assistant` | 模拟问答生成，计时审计，贡献-证据覆盖 |
| `peer-review-and-rebuttal` | 场馆特定审稿模板，CONSORT/STROBE/PRISMA 合规评分 |
| `protocol-authoring` | 报告规范映射，合规清单，注册摘要生成 |
| `patent-prior-art-search` | 专利家族解析，时间线计算，现有技术排序，Mermaid 树状图 |

### 领域专用

| 技能 | 说明 |
|------|------|
| `machine-learning-research` | ML 实验计划：划分，泄漏控制，基线，指标，消融 |
| `biomedical-research` | 研究计划：人群，终点，标本，安全，注册，治理 |
| `materials-research` | 实验计划：配方，工艺，表征，校准，溯源 |
| `chemistry-research` | 实验计划：试剂，条件，分析证据，危害/废弃物决策 |
| `social-science-research` | 研究计划：理论，抽样，测量，伦理，反身性，报告 |

---

## 项目结构

```
├── skills/               ← 29 个独立技能（每个可独立运行）
│   ├── literature-reader/
│   │   ├── SKILL.md            # 路由 + 工作流
│   │   ├── agents/openai.yaml  # 客户端可发现性
│   │   ├── scripts/            # 零依赖 Python CLI（stdlib）
│   │   └── references/         # 按需加载的领域知识
│   └── ... (另外 28 个)
├── tests/                ← 项目级测试套件（pytest）
├── schemas/              ← 版本化跨技能 JSON 协议
├── tools/                ← 技能校验器、产物校验器、安装器
├── assets/               ← 架构图、论文截图
└── docs/                 ← 开发路线图（88/88 已完成）
```

**零跨技能依赖。** 复制任意一个 skill 目录即可独立运行。

---

## 约定

- **每个技能独立。** 无跨技能导入；复制一个即可运行。
- **零依赖（stdlib）优先。** 第三方依赖用一行 `pip install` 声明。
- **CLI 约定：** `--help`、`--version`（匹配 `pyproject.toml`），诊断信息输出到 stderr，`--force` 覆盖输出，永不覆盖源数据。
- **用户报告：** 默认中文；产物内容跟随产物语言。

---

## 开发

```bash
python -m pip install -e ".[dev]"
python tools/validate_skills.py
python -m pytest
```

可选科学计算栈：

```bash
python -m pip install -e ".[analysis]"   # NumPy + SciPy
python -m pip install -e ".[plot]"       # Matplotlib + NumPy + SciPy
python -m pip install -e ".[pdf]"        # pdfplumber
python -m pip install -e ".[validation]" # SciPy + Statsmodels
python -m pip install -e ".[models]"     # pandas + Statsmodels
```

扫描版 PDF OCR 额外需要本地安装的 `pdftoppm`（Poppler）和 `tesseract`；均不打包，OCR 产物始终标注。

跨技能 JSON 协议：`schemas/researchos-artifacts.schema.json`。校验：

```bash
python tools/validate_artifact.py result.json --type stat-results
```

---

## 路线图

实现清单与完成标准见 [`docs/DEVELOPMENT_ROADMAP.md`](docs/DEVELOPMENT_ROADMAP.md)。88 项全部完成。

---

## 许可证与治理

- 许可证：[Apache-2.0](LICENSE)
- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全策略：[SECURITY.md](SECURITY.md)
- 社区准则：[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 第三方归属：[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

请勿提交凭证、私有科研数据、参与者信息、模型检查点、抓取的文章或生成的工作区产物。
