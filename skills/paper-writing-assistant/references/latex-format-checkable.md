# LaTeX Format Check: Verifiable Statically vs. Requiring Compilation

This feature checks only the items that **can be determined from the source code** of a LaTeX paper. The table below pins down which command/package each type of requirement maps to,
and which requirements cannot be judged from the source at all and must be measured after compiling to PDF. **Do not pretend to give conclusions for "requires compilation" items.**

## ✅ Verifiable Statically from Source (find evidence in .tex / preamble)

| Requirement Category | What to Check | Notes |
|---|---|---|
| Base font size (10/11/12pt) | `\documentclass[12pt]{...}` option | The base body font size is in the class option |
| Paper size | `\documentclass[a4paper]` or `geometry`'s `a4paper` | |
| Page margins | `\usepackage[top=..,bottom=..,left=..,right=..]{geometry}` or `\geometry{}` | Verifiable if explicit values are present |
| Line spacing | `\usepackage{setspace}` + `\onehalfspacing`/`\doublespacing`/`\setstretch{1.5}`; or `\linespread{1.5}`; or `\renewcommand{\baselinestretch}{1.5}` | |
| Chinese font | `ctex`/`xeCJK`'s `\setCJKmainfont{SimSun}`, `\setCJKmainfont[..]{}`; `\documentclass[fontset=..]` | SimSun/Hei etc. are set through these |
| Western font | `\setmainfont{}`, `\usepackage{times/newtxtext/...}` | |
| Section heading levels and numbering | `\section/\subsection`, `\titleformat`(titlesec), `secnumdepth` | Heading size/bold/centering defined via titlesec is verifiable |
| Page number format/position | `fancyhdr` config, `\pagenumbering{}`, `\thepage` | |
| Figure/table captions | `caption` package options, `\caption{}`, `\captionsetup{}` | Caption size/label name verifiable |
| Bibliography style | `\bibliographystyle{gbt7714-numerical/IEEEtran/...}`, `biblatex`'s `style=` | Linked with feature two |
| TOC/abstract/keywords structure | `\tableofcontents`, `abstract` environment, `\keywords{}` | Existence verifiable |

## ⚠️ Requires Compiling to PDF to Verify (source cannot give a conclusion — state honestly, do not guess)

- The **actual rendered** body font size/line spacing (final value after multiple packages, local commands, and class defaults are layered).
- The **actual** text area size per page, whether the page overflows its boundaries (overfull/underfull box).
- The **true position** of headings, figures, and tables on the page, whether they cross pages, which page floats land on.
- Total page count, each chapter's starting page, whether TOC page numbers align.
- Whether Chinese fonts are actually embedded, missing glyphs / fallback font issues.
- Widows/orphans, hyphenation.

> In the report, uniformly write for these items: **"This item requires measuring after compiling to PDF; the source cannot determine it statically. If verification is needed, please provide the compiled PDF or run a local `xelatex` compilation and report the measured values."**

## Checking Method Tips
- First read the main `.tex` and the preamble files pulled in by `\input/\include`, as well as any custom `.cls/.sty` (if bundled with the paper).
- The class of `\documentclass` (e.g. a university template `xxthesis.cls`) often encapsulates a large amount of formatting; if a requirement is met, look for the definition in the `.cls`. If not found, classify it as "determined by the template class; consult the template documentation or verify by compiling."
- When capturing evidence, provide **file name + original command text** so the student can locate and modify it.
