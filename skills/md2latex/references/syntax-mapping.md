# Markdown → LaTeX Syntax Mapping

Complete mapping implemented by `scripts/md2latex.py`, plus the limitations you should know
before trusting a conversion. The implementation is independent; behavior ideas were informed by
three publicly accessible tools. Two do not have verified redistribution licenses, so do not copy
their code or assets. See `docs/OPEN_SOURCE_AUDIT.md` in the collection repository for the audit.

| Public reference | Behavior independently implemented here |
|---|---|
| [zijunwa/md2tex](https://github.com/zijunwa/md2tex) | zero-dependency single-file script; custom template via `% ----- begin md -----` markers; `--figure-pos/--table-pos` float specifiers |
| [VMIJUNV/md-to-latex](https://github.com/VMIJUNV/md-to-latex) | booktabs tables (`\toprule/\midrule/\bottomrule`); raw-LaTeX passthrough (backtick-wrapped `\cmd`, `\bibliography` lines); figure float with auto `\label`; `\cite` support |
| [fastpen/markdown2latex](https://marketplace.visualstudio.com/items?itemName=fastpen.markdown2latex) | selectable document class; configurable math environment; CJK detection + XeLaTeX guidance; `--fragment` body-only output |

## Block level

| Markdown | LaTeX | Notes |
|---|---|---|
| `#` … `######` | `\section` … `\subparagraph` | H1→section, H2→subsection, … |
| paragraph | paragraph | blank-line separated |
| `- ` / `* ` / `+ ` lists | `itemize` | **nesting by indentation is supported** (unlike zijunwa/md2tex) |
| `1. ` lists | `enumerate` | nesting supported; marker style is lost (always `\item`) |
| `- [ ]` / `- [x]` | `item` + `$\square$` / `$\boxtimes$` | needs amssymb (auto-included) |
| GFM table | `table` + `tabularx` + booktabs | Cells wrap to `\linewidth`; `:--`/`--:`/`:-:` set l/r/c alignment. In `IEEEtran`, tables with 4+ columns or long rows automatically use `table*` and `\textwidth`. |
| `![alt](path "caption")` alone on a line | `figure[H]` + `\includegraphics[width=0.8\linewidth]` + `\caption` + `\label{fig:...}` | label slugified from alt/caption |
| `<img src="...">` | same figure float | alt= becomes caption fallback |
| ` ```lang ` fenced code | `lstlisting[language=lang]` | ` ```latex ` blocks pass through **verbatim** |
| `$$ … $$` | `\begin{equation}…\end{equation}` | `--math-env align|displaymath` changes it |
| `> quote` | `quote` environment | consecutive `>` lines merged |
| `---` / `***` | `\bigskip\hrule\bigskip` | |
| line starting with `\` | passed through raw | for `\newpage`, `\bibliography{...}`, etc. |
| YAML frontmatter | stripped | |

## Inline level

| Markdown | LaTeX |
|---|---|
| `**bold**` / `__bold__` | `\textbf{...}` |
| `*italic*` / `_italic_` | `\textit{...}` |
| `~~strike~~` | `\sout{...}` (ulem, loaded with `[normalem]`) |
| `` `code` `` | `\texttt{...}` |
| `` `\command{...}` `` | raw LaTeX passthrough (backslash-led code span) |
| `$E=mc^2$` | `$E=mc^2$` (untouched) |
| `[text](url)` | `\href{url}{text}` (`%`/`#` in url escaped) |
| `<https://...>` | `\url{...}` |
| `[@key]`, `[@a; @b]` | `\cite{key}`, `\cite{a,b}` |
| `& % $ # _ { } ~ ^ \` | escaped (`\&` … `\textbackslash{}`) |
| `× ≤ ≥ ± ≠ ≈ → ← ·` | `$\times$ $\leq$ …` (unicode map, pdflatex-safe) |

## Extended block constructs

These go beyond the three reference tools and are specific to this converter.

| Markdown | LaTeX | Notes |
|---|---|---|
| `![alt](url){width=50% height=3cm}` | `figure` + `\includegraphics[width=50%, height=5cm]{url}` | Pandoc-style attribute block; keys without `=` are flags. Without attributes the default `width=0.8\linewidth` applies. |
| `::: {.theorem #thm:x}` … `:::` | `\begin{theorem}\label{thm:x}…\end{theorem}` | Fenced div. Theorem-like names (`theorem`/`lemma`/`proof`/…) pull in `amsthm`. `#id` becomes `\label`. |
| `::: {.algorithm}` … `:::` | `\begin{algorithm}…\end{algorithm}` | Pulls in `algorithm` + `algpseudocode`. |
| `Term\n: definition` | `\begin{description}\item[Term] definition\end{description}` | PHP Markdown Extra definition list. |
| `[^1]` / `[^1]: text` | `\footnote{text}` | Footnote reference / definition. Definition lines are removed from the body. |

## Extended inline constructs

| Markdown | LaTeX | Notes |
|---|---|---|
| `[@sec:label]`, `[@fig:label]`, `[@tab:label]`, `[@eq:label]` | `\ref{sec:label}`, … | Only active with `--cross-ref`. Headings/figures/tables emit matching `\label`. |
| `--cross-ref` heading | `\section{Title}\label{sec:title}` | Auto-slugified label on every heading. |
| `--long-table` | `longtable` + `tabular` | Page-breaking tables instead of `table`+`tabularx`. |
| `\multicolumn{2}{c}{X}` in a cell | passed through unescaped | Explicit merge commands are honoured; pulls in `multirow`. |
| `--unicode-domain math` | `α`→`$\alpha$`, `∈`→`$\in$`, … | Opt-in Greek/logic/set supplement. |
| `--unicode-domain chem` | `⇌`→`$\rightleftharpoons$`, … | Opt-in reaction-arrow supplement. |

## Known limitations (be honest with the user)

1. **Not a full CommonMark parser** — it is a line-oriented block parser. Setext headings
   (`===`/`---` underline style) are not recognized; `---` under text becomes `\hrule`.
2. **No inline nesting inside stashed fragments**: emphasis inside `\sout{}`, links, or code
   spans is not processed (`\sout{**x**}` comes out literal).
3. **Numeric `[N]` citations stay literal** — migrate to `[@key]` + BibTeX for real venues.
4. **Table cells cannot contain `|`** (no escaped-pipe handling) and multi-row cells written
   directly via `\multirow` still require the `multirow` package (auto-included).
5. **HTML other than `<img>`** is passed through untouched and will likely not compile — warn.
6. **Image paths are not rebased**: they stay relative to the .md; compile from the right
   directory or move the .tex next to the .md.
7. **No compiling**: no LaTeX distribution is assumed. State the required compiler
   (XeLaTeX for CJK) instead of claiming the output "compiles".
8. **CSL→BibTeX** (`csl_to_bibtex.py`) covers the common CSL type/field subset only; exotic
   types map to `@misc` with a warning, and the bundled YAML parser handles the Zotero/Pandoc
   subset (no anchors/aliases/block scalars).
