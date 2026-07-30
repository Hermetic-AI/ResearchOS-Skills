# ResearchOS-Skills 开发路线图

本路线图将项目按开源产品标准持续完善。优先级定义：P0 为发布与可靠性基础，P1 为核心科研能力，P2 为扩展能力。完成项必须同时满足实现、测试、文档和可追溯性要求。

## 开源原则

- 默认采用 Apache-2.0 许可证；第三方代码、数据、配色和素材必须保留来源与兼容许可证。
- SKILL.md 只保留核心工作流，详细规则进入 `references/`，确定性操作进入 `scripts/`。
- 不虚构论文、引用、实验结果或统计结论；所有结论保留来源和证据锚点。
- 不覆盖用户原始数据；生成物写入新文件，并记录命令、参数、版本和随机种子。
- 不默认执行未信任的科研代码；复现任务优先使用隔离环境。
- 每项新能力同时提供正常、边界和失败测试，并确保 Windows/Linux 可运行。

## Phase 1：工程底座与发布门禁（P0）

- [x] 添加 Apache-2.0 `LICENSE`。
- [x] 添加 `CONTRIBUTING.md`、行为准则、安全策略和问题/PR 模板。
- [x] 添加 `.gitignore`、`.gitattributes`，隔离缓存、构建产物、数据和模型文件。
- [x] 为全部 skill 添加 `agents/openai.yaml`。
- [x] 建立 skill 结构校验：目录名、frontmatter、资源链接、行数和元数据。
- [x] 建立 Python 语法、CLI `--help`、确定性输出和代表性 smoke tests。
- [x] 在 GitHub Actions 中覆盖 Python 3.11–3.13 与 Windows/Linux。
- [x] 统一 CLI 的退出码、stderr、`--help`、`--version`、`--out` 与覆盖保护。
- [x] 清理或忽略 `__pycache__`、LaTeX 中间文件和用户 workspace 产物。
- [x] 建立第三方依赖与素材来源清单，完成许可证兼容性审计。

## Phase 2：跨 skill 数据协议（P0）

- [x] 定义版本化 JSON Schema：`paper-note`、`literature-matrix`、`research-gap`。
- [x] 定义 `design-brief`、`analysis-plan`、`cleaning-manifest`。
- [x] 定义 `stat-results`、`figure-manifest`、`reproduction-card`。
- [x] 定义统一 provenance 字段：来源、文件、命令、版本、时间、seed、警告。
- [x] 为 schema 提供最小测试样例和验证脚本。
- [x] 让相邻 skill 优先读写标准协议，保留 Markdown 人类可读输出。

## Phase 3：增强现有 skills（P1）

### literature-reader

- [x] PDF/OCR、双栏文本、表格、图注和补充材料提取工作流。
- [x] DOI/arXiv/PMID 核验、撤稿/勘误提示、文献去重和版本合并。
- [x] Zotero/BibTeX/RIS/EndNote XML 导入导出。
- [x] 每条核心结论携带页码、章节和原文证据锚点。
- [x] 大规模文献集分批、断点恢复和增量更新。
- [x] 与知识图谱使用统一 paper-note schema。

### experiment-designer

- [x] 预注册与统计分析计划模板。
- [x] 多终点、停止规则、序贯和适应性设计。
- [x] 等效性、非劣效性、集群随机和脱落率膨胀。
- [x] 重复测量、生存分析、纵向设计样本量。
- [x] DOE 别名结构、设计效率和可估计效应报告。
- [x] 功效计算与权威统计库数值交叉验证。

### data-analysis-assistant

- [x] 回归、GLM、ANCOVA、重复测量和混合效应模型。
- [x] Cox/竞争风险、时间序列和面板数据。
- [x] Bootstrap、置换、稳健统计和贝叶斯分析。
- [x] 残差、共线性、影响点和过度离散诊断。
- [x] 多重插补、敏感性分析、等效性和非劣效检验。
- [x] 完善所有检验的效应量与置信区间。
- [x] 支持 XLSX、TSV、Parquet、JSON 和数据字典。
- [x] 输出标准化 `cleaning-manifest.json`，并禁止覆盖原始数据或静默覆盖派生产物。
- [x] 输出标准化 `stat-results.json`，包含 provenance、稳定结果 ID、覆盖保护和 schema 校验。

### scientific-plot

- [x] 正式投稿图按稳定结果 ID 消费 `stat-results.json`，优先使用校正后 p 值并避免重复统计计算。
- [x] 自动输出含数据、统计来源、命令和 seed 的 `figure-manifest.json`，并保护已有输出。
- [x] 增加折线、配对点、雨云、森林、漏斗、ROC/PR、校准图（漏斗图仅提供描述性参考边界，不进行发表偏倚检验）。
- [x] 增加火山、Manhattan、PCA/UMAP、富集气泡、Sankey 和网络图（火山、Manhattan、PCA、富集气泡、Sankey、网络图已完成；前两者仅绘制输入值，PCA 仅做居中 SVD；UMAP 需显式 `umap-learn`、种子与预处理记录）。
- [x] 生存图增加置信带、删失标记和 number-at-risk 表。
- [x] 增强多面板布局、共享图例和坐标对齐（`--share-x/--share-y` 仅应应用于单位与尺度兼容的面板）。
- [x] 自动检查色盲、灰度和文本对比度。
- [x] 支持 TIFF/EPS 投稿输出。

### paper-writing-assistant

- [x] 大纲、摘要、引言、方法、结果和讨论的结构审查。
- [x] 术语、缩写、符号、交叉引用和图表编号一致性（Markdown/LaTeX 缩写、图表引用和 label/ref 启发式审计已实现；`--symbols` 符号表一致性——命令定义/使用、方程 label/ref、记号变体——已实现；DOCX 域语义解析（`--fields` 作者-年份指令解析）已实现；渲染后核验需 Word/PDF 工具链）。
- [x] 声称—证据—引用三元组审计和过度因果措辞检查（Markdown/LaTeX 过度措辞启发式筛查 + 人工三元组矩阵 ID/证据/引用定位字段审计已实现；语义蕴含与引用真实性需人工/`literature-reader` 核验——已标注为人工审核项）。
- [x] BibTeX/BibLaTeX 与 Word 作者—年份引用解析（BibTeX/BibLaTeX 字段审计与 DOCX 可见作者—年份候选/字段线索审计已实现；Word 作者—年份域语义解析——`docx_citation_audit.py --fields` 解析 CITATION 指令键与 `\l`/`\p`/`\t` 开关——已实现）。
- [x] DOI、年份、期刊名和页码真实性核验（离线字段完整性与 DOI 语法审计已实现；`online_verification.py` 通过 Crossref API 在线核验 DOI 元数据——标题/年份/期刊/页码/作者比对——已实现，需网络访问）。
- [x] 深入解析 DOCX 样式继承、主题、页眉页脚和分节（只读声明式样式继承链、主题部件、页眉页脚部件/引用和节数量审计已实现；`docx_inspect.py` 最终有效样式计算——`basedOn` 链继承合并 + `docDefaults` 默认属性——已实现；渲染布局需 Word/PDF 工具链）。
- [x] 编译后 PDF 版式核验与学术语言润色（`md2latex_e2e_test.py --compile` 在 LaTeX 工具链可用时验证编译；`--strict` 模式拒绝有警告的输出；学术语言润色需人工/编辑——已标注为人工审核项）。

### reproduction-assistant

- [x] 默认隔离运行未信任代码，约束网络、凭据和宿主目录（`isolation_plan.py --generate-script` 生成 venv/Docker 隔离脚本，默认无网络、只读仓库挂载、`HOME` 重定向到临时目录防泄露——已实现）。
- [x] Git LFS、submodule、release/tag 和论文 commit 对齐（`git_evidence.py --lfs-fetch-check` LFS 文件完整性、`--submodule-check` 子模块 SHA/初始化状态、`--tag <tag>` release 标签对齐——已实现）。
- [x] 数据集许可证、checksum、版本和下载清单（本地数据 checksum、许可证/条款来源与版本来源 inventory 及远端数据声明清单的离线审计已实现；`dataset_download_manifest.py` 下载清单生成 + `--verify` SHA-256 校验 + `--export` 可执行下载脚本——已实现）。
- [x] 记录硬件、驱动、CUDA、环境变量、seed、配置覆盖和 git diff（GPU/CUDA 取决于本地 `nvidia-smi` 可用性；环境变量默认只记录哈希）。
- [x] 支持 Docker/Make/Shell/Nix/Poetry/uv 及 R/Julia/MATLAB 项目的只读结构探测、运行线索提取和原生环境证据报告；不会自动执行原生包管理器或项目命令。
- [x] 支持多次运行、分布比较、绝对/相对容差和指标方向（多次运行均值/标准差、相对/绝对容差和方向性变化标签已实现；分布级统计比较——bootstrap CI、Welch t-test、不确定性 verdict（consistent/inconsistent/uncertain）——已实现）。
- [x] 输出 schema 校验的 `reproduction-card`，强制记录 commit、环境和证据缺失警告。
- [x] 输出可归档 reproduction package 与复现等级（显式 ZIP 归档会排除常见缓存和敏感文件名，但仍要求人工审查许可与秘密）。

### knowledge-graph-builder

- [x] 稳定实体 ID、自动消歧、别名聚类和合并评分（确定性 identity key、保守别名合并建议及高阈值 token 相似度候选评分已实现；`graph_entity_merge.py` 交互式/自动实体合并应用——合并节点、重写边、记录 provenance——已实现）。
- [x] 增量更新、图版本迁移、冲突/否定关系和时间有效性（节点/边 diff 与时间字段、谱系倒置、冲突关系的只读审计已实现；`graph_version_migrate.py` schema 版本迁移与 `graph_conflict_resolve.py` 已审批冲突消解已实现）。
- [x] 证据锚点增加页码、DOI 和可信等级（审计工具只报告缺失字段，不验证页面、DOI 或可信等级真伪）。
- [x] 支持 GraphML、GEXF、RDF/Turtle、JSON-LD。
- [x] schema 验证、图差异、社区发现和中心性分析。
- [x] 与 literature-reader 统一 note schema。

### md2latex

- [x] 统一“仅转换”和“可选编译验证”的能力边界。
- [x] 脚注、定义列表、定理、算法、长表和合并单元格（`[^id]` 脚注、PHP Markdown Extra 定义列表、`::: ` fenced-div 定理/证明/算法环境、`--long-table` 分页长表、单元格内 `\multicolumn`/`multirow` 透传已实现）。
- [x] 交叉引用、图片属性、BibTeX/BibLaTeX 和 CSL 迁移（显式 `.bib` 的 BibTeX 命令插入已实现；`--cross-ref` 标题/图/表 `\label` + `[@sec:/-@fig:/-@tab:/-@eq:]`→`\ref`、图片 `{width=… height=…}` 属性、`csl_to_bibtex.py` CSL-JSON/YAML→BibTeX 转换已实现）。
- [x] 多文件 Markdown 项目和资源路径重写（只读项目清单、局部资源存在性检查和逐文件转换计划已实现；`--rewrite-plan` 跨文件路径重写方案与 `--out-dir` 输出目录计算已实现；`--apply-rewrites` 直接改写源 `.md` 文件路径 + `.md.bak` 备份——已实现）。
- [x] 完善 Unicode/特殊字符映射并增加 `--strict`（`--strict`、常见数学符号、智能引号、破折号、省略号和不可见字符提示已完成；`--unicode-domain math|chem|text` 领域专用 Unicode 补充映射——希腊/逻辑/集合、反应箭头、货币符号——已实现）。
- [x] 建立 Markdown → TeX → PDF 端到端测试（`md2latex_e2e_test.py --self-test` 内置烟雾测试无需 LaTeX；`--fixtures` 夹具对比 + `--compile` 有条件调用 LaTeX 工具链——已实现）。

## Phase 4：新增核心 skills（P1）

- [x] `scholarly-search-manager`：检索式、数据库检索、DOI 核验、去重、引用追踪和文献库交换（本地检索计划、DOI/题名去重和 JSON→RIS 本地交换已实现；`search_manager.py` PubMed/Crossref/Semantic Scholar 检索式格式化 + DOI/题名去重 + RIS/BibTeX/CSV 导出——已实现）。
- [x] `systematic-review-meta-analysis`：PICOS、PRISMA、筛选、RoB、效应量、异质性、偏倚与 GRADE（PICOS/PRISMA 草案协议、人工筛选决策台账和人工 RoB 台账完整性审计已实现；`meta_analysis.py` SMD/Hedges' g/RR/OR 效应量 + 固定/随机效应逆方差元分析 + Cochran's Q/I²/τ²——已实现）。
- [x] `research-project-orchestrator`：项目初始化、任务路由、中间产物、状态和全链路 provenance（初始化、状态更新、基础路由、产物 checksum/更新 provenance 及只读工件链验已实现；`trace_decision_provenance.py` 全链路决策/输入 provenance 追踪——已实现）。
- [x] `research-integrity-and-ethics`：伦理、隐私、作者贡献、AI 披露、科研诚信和报告规范（readiness checklist、作者/利益冲突/AI/可用性披露记录及规则字段映射覆盖审计已实现；机构/期刊规则解释与审核流程需提供规则文档后由脚本映射——框架已实现）。
- [x] `causal-inference-assistant`：DAG、匹配/加权、IV、DID、RDD、合成控制和敏感性分析（估计量/假设 charter、方法路由、DAG 结构/角色审计与 E-value 已实现；`causal_estimate.py` 倾向评分匹配/加权（Newton-Raphson 逻辑回归）+ DiD + 断点回归 + E-value——已实现）。
- [x] `qualitative-research-assistant`：访谈、编码本、主题分析、一致性、饱和度和审计轨迹（编码本、审计轨迹草案、编码决策台账校验、Cohen's κ 与新代码累积轨迹已实现；`saturation.py` Krippendorff's α + 饱和度曲线/阈值判断——已实现）。
- [x] `survey-and-psychometrics`：问卷、信效度、EFA/CFA、不变性、IRT/Rasch（构念/验证 charter、项目响应范围/缺失审计与 Cronbach α 已实现；`psychometrics.py` 主成分因子提取 + varimax 旋转 EFA + Cronbach's α/题总相关 + Rasch 1PL 拟合——已实现）。
- [x] `peer-review-and-rebuttal`：模拟审稿、意见分级、回复矩阵和修改一致性（审稿意见分级、回复矩阵草案、修订位置一致性审计及人工模拟审稿问题清单已实现；`review_simulator.py` 场馆特定审稿模板 + CONSORT/STROBE/PRISMA 合规评分——已实现）。
- [x] `research-proposal-and-grant`：科学问题、Specific Aims、创新性、路线、预算和风险（proposal charter、Specific Aims 完整性审计与预算假设字段/规则来源审计已实现；资助方规则解释与提交前检查需提供规则文档后由脚本映射——框架已实现）。
- [x] `research-data-management`：DMP、FAIR、元数据、匿名化、许可、发布和长期归档（数据分级、FAIR/DMP 治理草案、发布前 DMP 检查及数据集元数据字段审计已实现；`anonymize_check.py` 直接标识符 + 准标识符唯一性风险筛查——已实现）。

## Phase 5：扩展 skills（P2）

- [x] `academic-presentation-poster`（storyboard、证据/可访问性清单、storyboard 审计已实现；`slide_layouter.py` LaTeX Beamer/reveal.js 版式生成 + 宽高比/字体层级/WCAG 对比度检查 + 渲染预览清单——已实现）
- [x] `thesis-defense-assistant`（答辩 brief、贡献—证据台账与问题覆盖矩阵已实现；`defense_qa.py` 模拟答辩问答生成 + 计时审计 + 贡献-证据覆盖检查——已实现）
- [x] `protocol-authoring`（研究方案 charter、伦理/注册决策与偏离日志草案已实现；`protocol_mapper.py` CONSORT/SPIRIT/STROBE/PRISMA 规范映射 + 合规清单 + 注册摘要生成——已实现）
- [x] `research-software-quality`（软件质量证据与发布门槛计划、发布声明检查及只读仓库质量证据采集已实现；`release_audit.py` 发布就绪审计（LICENSE/README/版本/CITATION.cff）+ 基准执行 + 内存占用测量——已实现）
- [x] `patent-prior-art-search`（检索特征、查询日志、证据台账草案及特征—文献定位覆盖审计已实现；`patent_family.py` 专利家族解析 + 时间线 + 优先权候选排序 + Mermaid 树状图——已实现）
- [x] 生物医学、材料、化学、社会科学和 ML 领域扩展包（均提供可审计计划/证据契约基础；各领域的专用计算、规则映射与数据连接器继续按需求扩展）。

## 完成定义

一个清单项只有在以下条件全部满足时才能勾选：

1. 功能已写入 SKILL.md 或渐进加载资源。
2. 确定性操作已实现为脚本并通过代表性测试。
3. 新增资源有来源、许可证和使用边界。
4. 正常、边界、错误路径均有测试。
5. `agents/openai.yaml` 与实际能力一致。
6. README 的能力矩阵与路由关系已更新。
7. CI 在支持的平台和 Python 版本上通过。
