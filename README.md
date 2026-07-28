# ResearchOS-Skills

A collection of research-oriented agent skills (Anthropic `SKILL.md` format), distilled from the ResearchOS project. Each skill follows progressive disclosure: a short routing `SKILL.md`, on-demand domain knowledge in `references/`, and deterministic CLIs in `scripts/`.

## Skills

| Skill | 方向 | What it does |
|-------|------|--------------|
| `literature-reader` | 文献阅读与管理 | Structured reading notes from single papers, multi-paper comparison matrices, research-gap analysis. |
| `knowledge-graph-builder` | 知识图谱构建 | Build a domain concept graph from Markdown notes (controlled ontology, evidence-anchored relations), trace research threads, export Graphviz DOT. |
| `experiment-designer` | 实验设计辅助 | Experiment design guidance (CRD/RBD/factorial), control-group design, randomization/blocking, power & sample-size estimation. |
| `data-analysis-assistant` | 数据处理分析 | CSV data profiling & outlier detection, statistical-test selection with effect sizes, conclusion drafting. |
| `paper-writing-assistant` | 论文写作辅助 | 看图写正文分析段落、引用规范检查（GB/T 7714/IEEE/APA/ACM）、论文格式检查（Word/LaTeX）。 |
| `reproduction-assistant` | 代码与实验复现 | Paper-code reproduction pipeline discipline, dependency parsing, result comparison with tolerance, failure diagnosis taxonomy. |
| `scientific-plot` | 科研绘图 | Publication-grade statistical charts (6 templates, journal themes, significance stars), Excalidraw/SVG schematics, Mermaid/Graphviz/PlantUML diagram-as-code. |

## Conventions

- Frontmatter: `name` + `description` only; description carries trigger scenarios (EN + 中文口语短语) and "NOT for X" routing boundaries between sibling skills.
- `SKILL.md` ≤ ~150 lines: overview, when-to-use, workflow skeleton, file index. Load `references/*` files only when the workflow step calls for them.
- `scripts/*`: Python 3, zero-dependency (stdlib) preferred; third-party needs are declared with a one-line `pip install` in the skill. All CLIs emit JSON/Markdown; randomized scripts take a fixed seed.
- Reports to the user default to Chinese; artifact content follows the artifact's language.
