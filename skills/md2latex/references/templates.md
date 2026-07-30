# Templates & Compilation Guide

## Built-in templates (`--template`)

| Name | `\documentclass` | Adds | Use for |
|---|---|---|---|
| `article` (default) | `\documentclass[11pt]{article}` | — | English drafts, arXiv preprints |
| `ctexart` | `\documentclass[11pt]{ctexart}` | — | Chinese drafts (compile with XeLaTeX) |
| `IEEEtran` | `\documentclass[conference]{IEEEtran}` | `cite` package | IEEE conferences |

All templates include (only when used): `amsmath, amssymb, graphicx, booktabs, float,
hyperref, listings, xcolor, ulem[normalem]` — the converter tracks which features the
document actually uses and omits the rest. When CJK characters are detected with a
non-CJK template, `xeCJK` is appended automatically and a stderr note reminds you to
compile with XeLaTeX.

## Custom template files (`--template-file venue.tex`)

For a real venue template (conference-provided `.tex`), insert two marker lines where
the converted body should go (convention from zijunwa/md2tex):

```latex
\documentclass{llncs}
% ... venue preamble, \author, \title, \maketitle ...
\begin{document}

% ----- begin md -----
% anything between the markers is replaced
% ----- end md -----

\bibliographystyle{splncs04}
\bibliography{refs}
\end{document}
```

Everything outside the markers is preserved verbatim. Missing markers = hard error.

## `--fragment`

Emits only the converted body — for `\input{body}` inside an existing project
(e.g. replacing one chapter of a thesis). No preamble, no template logic.

## Per-venue checklist

- **arXiv**: `--template article`, upload the `.tex` + figure files; arXiv compiles with
  (xe)latex automatically. Include `references.bib` if `[@key]` citations were used.
- **IEEE conference**: `--template IEEEtran --figure-pos htbp --table-pos htbp`,
  migrate numeric `[N]` citations to `[@key]` + `IEEEtran.bst`, export figures as PDF
  (`--figure-ext pdf`).
- **中文论文/报告**: `--template ctexart`, compile `xelatex main.tex` twice (refs/toc).
  pdfLaTeX will fail on CJK — always say this.
- **Overleaf**: upload `.tex`; if CJK, Menu → Compiler → **XeLaTeX**.
- **Figures**: LaTeX cannot embed SVG. Export PDF (vector, preferred) or 300-DPI PNG
  first — scientific-plot's `plot_chart.py` already emits `.pdf` alongside `.svg`, and
  `references/diagram-formats.md` there documents browser-based SVG→PDF export.
  The converter also recognises the ``figures/svg/*.svg`` + ``figures/pdf/*.pdf``
  parallel-directory layout: when an SVG sits under an ``svg/`` folder with no
  same-stem PDF/PNG beside it, the converter checks the sibling ``pdf/`` / ``png/``
  folder before giving up.

## Compilation quick reference

```bash
xelatex paper.tex && xelatex paper.tex      # CJK / xeCJK docs, run twice for refs
pdflatex paper.tex                          # plain English article template
latexmk -xelatex paper.tex                  # automated multi-pass, if available
```

No LaTeX distribution on the machine? State that conversion succeeded but compilation
was not verified, and point to Overleaf as the zero-install option.
