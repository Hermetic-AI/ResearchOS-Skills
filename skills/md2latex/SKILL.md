---
name: md2latex
description: Convert research Markdown into clean LaTeX with headings, lists, GFM booktabs tables, figure floats, listings, math, links, Pandoc-style citation keys, raw LaTeX, article/ctexart/IEEEtran templates, custom template markers, CJK detection, and image-extension rewriting. Use for converting md to latex, converting markdown to tex, IEEEtran formatting, converting to ctex, producing compilable tex, converting Markdown to LaTeX, or preparing a Markdown draft for a venue template. Not for writing or polishing manuscript prose and citation style (paper-writing-assistant), generating figures (scientific-plot), or promising PDF compilation when no LaTeX toolchain is available.
---

# md2latex (Markdown → LaTeX)

Converts a Markdown draft into clean, compilable LaTeX. Zero-dependency (Python stdlib only). Reports to the user in English by default; generated .tex follows the source document's language.

**Global conventions**
- **Convert, don't compile**: this skill produces `.tex`. If a LaTeX distribution exists locally (`xelatex`/`latexmk`), you may offer to compile; otherwise state the required compiler and stop. CJK documents need **XeLaTeX** (or `--template ctexart`); never tell the user to compile Chinese docs with pdfLaTeX.
- **Never fabricate content**: conversion is structural. If a Markdown construct has no LaTeX mapping (e.g. HTML blocks other than `<img>`), pass it through verbatim and warn — do not "interpret" it.
- **Paths are the user's problem, say so**: `\includegraphics` keeps the relative paths from the .md; the .tex must be compiled from a directory where those paths resolve. Mention this whenever the output goes to a different directory.

## Workflow

1. **Convert**:
   `python3 scripts/md2latex.py paper.md -o paper.tex [--template article|ctexart|IEEEtran]`
   The script prints a JSON report (template, detected CJK, features used) — relay the CJK/compiler note to the user. Add `--compile` only when validation is explicitly requested: it disables shell escape and reports `passed`/`failed`/`unavailable`; conversion alone never implies PDF validation.
2. **Pick the template by target venue** (details in `references/templates.md`):
   - English draft / arXiv → `article` (default)
   - Chinese draft → `ctexart`
   - IEEE conference → `IEEEtran` (adds `cite` package, conference option)
   - User provides their venue's `.tex` template → `--template-file venue.tex` (must contain `% ----- begin md -----` / `% ----- end md -----` markers, convention borrowed from zijunwa/md2tex)
   - Output will be `\input` into another document → `--fragment`
3. **Figures**: LaTeX cannot embed `.svg`. The converter automatically uses a same-named sibling PDF, otherwise PNG, when one exists; it emits this rewrite in its JSON `warnings`. It also recognises the common ``figures/svg/*.svg`` + ``figures/pdf/*.pdf`` parallel-directory layout — when an SVG lives under an ``svg/`` folder, the converter checks the sibling ``pdf/`` (and ``png/``) folder for a same-stem fallback even if none sits next to the SVG. If no fallback exists anywhere, it keeps the SVG and reports that pdfLaTeX will reject it. Use `--figure-ext pdf|png` when you need to select the extension explicitly (the parallel-directory lookup applies here too). Float positions: `--figure-pos/--table-pos` (default `H`; journals often want `htbp`).
4. **Citations**: `[@key]` / `[@a; @b]` become `\cite{...}`. Supply `--bibliography refs.bib [--bib-style plain]` to insert explicit BibTeX commands in a built-in full document; it does not parse or validate the `.bib`. Numeric `[N]` references are left as literal text — if the draft uses them, tell the user to either keep the plain-text References section or migrate to BibTeX keys.
5. **Verify**: re-read the generated `.tex` for unconverted artifacts (stray `**`, `~~`, `![`, `` placeholders) before handing over. Full syntax coverage and known limits — **read `references/syntax-mapping.md` when a construct converts oddly or the user asks what is supported`.
6. **Compile-check (new)**: run `python3 scripts/latex_compile_check.py paper.tex` to scan for common compilation breakers before handing off. It detects `xeCJK`+pdfLaTeX conflicts, CJK characters without package support, missing `graphicx`, SVG figures (and locates PDF/PNG fallbacks), missing image files, undefined refs, and cite-without-bibliography. Add `--fix --force` to auto-fix what it can (add missing packages, rewrite SVG → PDF fallback). Add `--compiler pdflatex|xelatex` to check against a specific compiler. This check also works on **LLM-generated `.tex`** that was not produced by md2latex.
7. **Multi-file project (audit first)**: run `python3 scripts/markdown_project_audit.py project_dir --pretty` to inventory Markdown files and local resource links. It is read-only and proposes explicit per-file conversions; it does not rewrite paths or batch-convert/overwrite files.

## File index

- `scripts/md2latex.py` — the converter. Block parser (headings, nested lists, GFM tables, fenced code, `$$` math, blockquotes, figures with Pandoc-style `{width=…}` attributes, raw-LaTeX passthrough, fenced-div theorem/proof/algorithm environments, definition lists, footnotes `[^id]`) + inline parser (emphasis, code, math, links, citations, strikethrough, cross-references `[@sec:/-@fig:/-@tab:/-@eq:]` under `--cross-ref`, unicode symbol mapping with opt-in `--unicode-domain math|chem|text`). `--long-table` uses page-breaking `longtable`; `--strict` refuses output with warnings.
- `scripts/md2latex_e2e_test.py` — end-to-end test harness for the conversion pipeline. ``--self-test`` runs built-in smoke conversions (heading, list, table, math, figure, footnote, theorem, definition list, cross-ref) and asserts the generated ``.tex`` contains the expected LaTeX constructs (no LaTeX install required). ``--fixtures <dir>`` reads ``<stem>.md`` / ``<stem>.expected.tex`` pairs, runs the converter, and diffs output against expected; with ``--compile`` it also attempts LaTeX compilation when a toolchain is available and reports ``passed``/``failed``/``unavailable``. Zero-dependency, deterministic JSON report.
- `scripts/csl_to_bibtex.py` — convert a CSL-JSON or CSL-YAML library (Zotero/Pandoc shape) into a ``.bib`` file. Structural type/field mapping for the common subset; unknown CSL types map to ``@misc`` with a warning. Zero-dependency (a small hand-written CSL-YAML subset parser; no PyYAML).
- `scripts/markdown_project_audit.py` — read-only multi-file Markdown inventory: local link/resource existence and explicit conversion plan. ``--rewrite-plan`` proposes cross-file path rewrites for image/include links; ``--out-dir`` sets the output ``.tex`` directory used to compute those rewrites. No conversion or file rewrite is performed.
- `scripts/latex_compile_check.py` — pre-compilation checker for `.tex` files. Scans for `xeCJK`+pdfLaTeX conflicts, CJK characters without package support, missing `graphicx`, SVG figures (locates PDF/PNG fallbacks), missing image files, undefined refs, cite-without-bibliography. `--fix --force` auto-fixes (adds packages, rewrites SVG → PDF fallback). `--compiler pdflatex|xelatex` checks against a specific compiler. `--json` emits a structured report. Works on both md2latex output and LLM-generated `.tex`. Zero-dependency.
- `references/syntax-mapping.md` — full Markdown→LaTeX mapping table, design debt to the three reference projects (zijunwa/md2tex, VMIJUNV/md-to-latex, fastpen/markdown2latex), and known limitations.
- `references/templates.md` — built-in template details, custom template-file markers, per-venue checklist (arXiv/IEEE/Chinese/Overleaf), compiler guidance.
