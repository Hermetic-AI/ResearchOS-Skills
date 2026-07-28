# Format Check Report (paper-writing-assistant Function 3)

**Paper:** AI Agent Memory: A Survey of Mechanisms, Trade-offs, and Open Problems
**File:** `paper/paper.md`
**Target format:** arXiv preprint / generic CS conference (e.g., NeurIPS, ICLR survey track)
**Date:** 2026-07-28

---

## Format specification (parsed from target)

Since the user did not paste a separate format spec, I assumed the standard arXiv / CS-conference format requirements. Items checked:

| # | Item | Required | Result |
|---|---|---|---|
| 1 | Title in title case, not all-caps | yes | ✅ |
| 2 | Author block with affiliation, email | yes | ⚠️ placeholder; user to add |
| 3 | Abstract 100–300 words | yes | ✅ ~270 words |
| 4 | Sections numbered with Roman numerals (I., II., …) | optional | ✅ |
| 5 | Subsection labels A., B., … | optional | ✅ |
| 6 | Figures with captions | yes if used | ⚠️ referenced Figure 1 but not embedded (graph.dot only) |
| 7 | Tables with captions | yes if used | ✅ Table I |
| 8 | References in IEEE/ACM format | yes | ✅ (see citation_check_report.md) |
| 9 | No emoji | yes | ✅ none |
| 10 | No "all-caps" headers | yes | ✅ |
| 11 | Consistent citation style | yes | ✅ IEEE [N] throughout |
| 12 | Inline math, equation environment | optional | n/a (no equations) |
| 13 | Markdown source well-formed | yes | ✅ |

---

## Issues to address before submission

1. **Author block.** The paper has no author block. For a real submission, add:
   ```
   Author Name¹, Co-Author Name²
   ¹Affiliation, email
   ²Affiliation, email
   ```
   This is a manual edit the user must do.
2. **Figure 1.** §IV-I mentions "Figure 1 (in the supplementary material `graph.dot`)" but the graph was not rendered to PNG/SVG (no Graphviz on this machine). Two options:
   - Install Graphviz (`dot -Tsvg graph.dot -o figure1.svg`) and embed.
   - Replace the figure reference with a prose description of the graph (e.g., "see `graph.dot` in supplementary").

---

## Items that are *static-checkable* but deferred

- **LaTeX-specific format checks** (per `references/latex-format-checkable.md`): not applicable — the source is markdown, not LaTeX.
- **Word document checks** (per `scripts/docx_inspect.py`): not applicable — no .docx.

---

## Verdict

**Markdown source is submission-ready for arXiv** pending:
- Author block addition (manual)
- Figure 1 rendering (requires Graphviz install, or replace figure ref with prose)

The body text, sections, citations, and references all conform to standard arXiv/conference survey format. The 14-entry reference list is in IEEE format and the body uses `[N]` citations consistently.
