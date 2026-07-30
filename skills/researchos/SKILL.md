---
name: researchos
description: Orchestrate 28 research skills (literature, design, data, figures, writing, reproduction, etc.). Routes user tasks to the right sub-skill. Use when starting a research project, picking a research tool, asking "what's next" in a research workflow, or chaining literature→design→data→figures→writing. Not for executing domain workflows directly — routes to sub-skills.
---

# ResearchOS (科研技能编排器)

ResearchOS is a suite of 28 independent, zero-dependency research skills. This is the **orchestrator** — it routes your task to the right sub-skill. Each sub-skill is invoked via its slash command (e.g., `/literature-reader`) and runs independently.

## How to use

1. Tell me your research task in natural language (Chinese or English).
2. I'll route you to the correct sub-skill based on the trigger table below.
3. Invoke the sub-skill with its slash command, or ask me to continue and I'll load it.

## Routing table

### Literature & Evidence

| User wants... | Slash command | Triggers |
|---|---|---|
| Read/extract/audit papers, PDF/OCR, DOI check, Zotero/BibTeX/RIS convert | `/literature-reader` | 读论文, PDF提取, 文献去重, Zotero转换, extract, audit papers |
| Build concept graphs from notes, trace research lineages | `/knowledge-graph-builder` | 知识图谱, 研究脉络, paper-note入图, trace lineage |
| Plan database searches, deduplicate citations, export RIS/BibTeX/CSV | `/scholarly-search-manager` | 检索式, DOI去重, 文献库交换, search strategy |
| Systematic review, meta-analysis, PICOS, PRISMA, effect sizes, I² | `/systematic-review-meta-analysis` | 系统综述, 元分析, PRISMA, 效应量, meta-analysis |

### Study Design & Data

| User wants... | Slash command | Triggers |
|---|---|---|
| Design experiments, DOE, randomization, power analysis, preregistration | `/experiment-designer` | 实验设计, 预注册, 样本量, 功效分析, DOE, power |
| Analyze data, regression, GLM, Cox, SARIMAX, panel, MICE, equivalence | `/data-analysis-assistant` | 数据分析, 回归, 生存分析, 时间序列, analyze data |
| Causal inference, DAG, propensity score, DiD, RDD, IV, E-value | `/causal-inference-assistant` | 因果推断, 倾向得分, 双重差分, DAG, causal |
| Qualitative coding, codebooks, Krippendorff's α, saturation | `/qualitative-research-assistant` | 编码本, 质性研究, 饱和度, qualitative |
| Survey design, EFA, CFA, IRT, Rasch, Cronbach's α | `/survey-and-psychometrics` | 问卷, 因子分析, 信度, 效度, psychometrics |

### Writing & Communication

| User wants... | Slash command | Triggers |
|---|---|---|
| Write/check papers, citation audit, DOCX/LaTeX format, DOI verify | `/paper-writing-assistant` | 论文写作, 引用检查, 格式检查, 排版, citation audit |
| Convert Markdown→LaTeX, footnotes, theorems, cross-refs, CSL→BibTeX | `/md2latex` | md转latex, markdown转tex, IEEEtran, 转ctex |
| Publication figures, statistical charts, journal themes, SVG/PDF export | `/scientific-plot` | 科研绘图, 统计图, 森林图, 生存曲线, figure |
| Presentations, posters, Beamer/reveal.js, WCAG contrast | `/academic-presentation-poster` | 演示, 海报, 幻灯片, presentation, poster |
| Thesis defense, mock Q&A, contribution-evidence audit | `/thesis-defense-assistant` | 答辩, 模拟问答, defense preparation |

### Reproduction & Integrity

| User wants... | Slash command | Triggers |
|---|---|---|
| Reproduce paper code, compare results, isolation planning | `/reproduction-assistant` | 复现论文, 结果对比, reproduce, reproduction |
| Peer review triage, response matrix, CONSORT/STROBE/PRISMA check | `/peer-review-and-rebuttal` | 审稿, 回复矩阵, rebuttal, review |
| Ethics checklist, authorship, AI disclosure, policy coverage | `/research-integrity-and-ethics` | 伦理, 作者贡献, AI披露, ethics, integrity |

### Management & Planning

| User wants... | Slash command | Triggers |
|---|---|---|
| Research proposal, Specific Aims, budget, milestones | `/research-proposal-and-grant` | 研究计划, 申请书, proposal, grant |
| Data management plan, FAIR, anonymization, release readiness | `/research-data-management` | DMP, FAIR, 数据管理, 匿名化 |
| Project orchestration, artifact routing, decision provenance | `/research-project-orchestrator` | 项目编排, 工作流, orchestrate |
| Software quality, release audit, benchmark, CITATION.cff | `/research-software-quality` | 软件质量, 发布审计, release audit |
| Research protocol, reporting guidelines, registry summary | `/protocol-authoring` | 研究方案, 规范映射, protocol |
| Patent prior-art search, family parsing, Mermaid tree | `/patent-prior-art-search` | 专利检索, 家族解析, prior art |

### Domain-Specific

| User wants... | Slash command | Triggers |
|---|---|---|
| ML experiment plan, baselines, ablations, model card | `/machine-learning-research` | ML实验, 消融, baseline, model card |
| Biomedical study plan, endpoints, specimens, safety | `/biomedical-research` | 生物医学, 临床试验, biomedical |
| Materials experiment, synthesis, characterization, provenance | `/materials-research` | 材料实验, 合成, materials |
| Chemistry experiment, reagents, analytical, hazard/waste | `/chemistry-research` | 化学实验, 试剂, chemistry |
| Social-science study, sampling, measurement, mixed-methods | `/social-science-research` | 社会科学, 问卷, social science |

## Workflow patterns

**Full pipeline** (literature → design → data → figures → writing):
```
/literature-reader → /experiment-designer → /data-analysis-assistant → /scientific-plot → /paper-writing-assistant
```

**Reproduction** (paper code → results):
```
/reproduction-assistant
```

**Knowledge synthesis** (notes → graph → gaps):
```
/literature-reader → /knowledge-graph-builder
```

## Installation

Each skill is self-contained. To install the full suite:

```bash
# Clone the repository
git clone <repo-url> researchos-skills

# Install all skills to user-level (.claude/skills/)
python researchos-skills/tools/install_skills.py

# Or install to project-level
python researchos-skills/tools/install_skills.py --scope project
```

After installation, all 28 skills appear as slash commands in Claude Code.
