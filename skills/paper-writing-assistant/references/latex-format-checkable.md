# LaTeX 格式检查：可静态核实 vs 需编译才能验

功能三对 LaTeX 论文**只查源码能确定的项**。下表定死每类要求落到哪个命令/宏包，
以及哪些要求源码里根本判断不了、必须编译成 PDF 再量。**不要对"需编译"项假装给出结论。**

## ✅ 源码可静态核实（在 .tex / 导言区里找证据）

| 要求类别 | 查什么命令/宏包 | 说明 |
|---|---|---|
| 基础字号(10/11/12pt) | `\documentclass[12pt]{...}` 选项 | 正文基准字号在类选项里 |
| 纸张 | `\documentclass[a4paper]` 或 `geometry` 的 `a4paper` | |
| 页边距 | `\usepackage[top=..,bottom=..,left=..,right=..]{geometry}` 或 `\geometry{}` | 有明确数值即可核 |
| 行距 | `\usepackage{setspace}` + `\onehalfspacing`/`\doublespacing`/`\setstretch{1.5}`；或 `\linespread{1.5}`；或 `\renewcommand{\baselinestretch}{1.5}` | |
| 中文字体 | `ctex`/`xeCJK` 的 `\setCJKmainfont{SimSun}`、`\setCJKmainfont[..]{}`；`\documentclass[fontset=..]` | 宋体/黑体等靠这些设定 |
| 西文字体 | `\setmainfont{}`、`\usepackage{times/newtxtext/...}` | |
| 标题层级与编号 | `\section/\subsection`、`\titleformat`(titlesec)、`secnumdepth` | 标题字号/加粗/居中若用 titlesec 定义即可核 |
| 页码格式/位置 | `fancyhdr` 配置、`\pagenumbering{}`、`\thepage` | |
| 图表题注 | `caption` 宏包选项、`\caption{}`、`\captionsetup{}` | 题注字号/标签名可核 |
| 参考文献风格 | `\bibliographystyle{gbt7714-numerical/IEEEtran/...}`、`biblatex` 的 `style=` | 与功能二联动 |
| 目录/摘要/关键词结构 | `\tableofcontents`、`abstract` 环境、`\keywords{}` | 存在性可核 |

## ⚠️ 需编译成 PDF 才能验（源码给不出结论——如实告知，别猜）

- 正文**实际渲染**的字号/行距（被多个宏包、局部命令、类默认叠加后的最终值）。
- 每页**实际**版心尺寸、页面是否溢出边界（overfull/underfull box）。
- 标题、图表在页面上的**真实位置**、是否跨页、图表浮动到哪一页。
- 总页数、每章起始页、目录页码是否对齐。
- 中文字体是否真的嵌入、缺字/回退字体问题。
- 孤行寡行（widow/orphan）、断字。

> 报告里对这些项统一写：**"该项需编译 PDF 后测量，源码无法静态判定；若需核实请提供编译后的 PDF 或在本地 `xelatex` 编译后告知实测值。"**

## 检查方法提示
- 先读主 `.tex` 和被 `\input/\include` 的导言区文件、以及自定义 `.cls/.sty`（若随论文附带）。
- `\documentclass` 的类（如学校模板 `xxthesis.cls`）常已封装大量格式，命中要求要去 `.cls` 里找定义，找不到则归入"由模板类决定，需查模板文档或编译核实"。
- 抓证据要给出**文件名+命令原文**，方便学生定位修改。
