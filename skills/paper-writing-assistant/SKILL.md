---
name: paper-writing-assistant
description: Assist thesis and paper writing by drafting evidence-aware figure or table analysis paragraphs, auditing in-text citations against reference lists and GB/T 7714/IEEE/APA/ACM or institution rules, and checking Word or statically verifiable LaTeX formatting against a confirmed requirement checklist. Use for drafting figure/table analysis paragraphs from images, auditing in-text citations, reference formatting, thesis formatting compliance, typesetting checks, citation audits, or thesis formatting. Not for Markdown-to-LaTeX conversion (md2latex), figure generation (scientific-plot), statistical analysis, literature reading, or experiment design.
---

# Paper Writing Assistant

Designed for master's and doctoral students. The three functions below are independent of each other — when the user mentions one, enter that one; do not force all three to run together.

**Global conventions**
- **Generated content follows the language of the paper**: text that will be inserted into the paper (figure/table analysis paragraphs, suggested revised wording) uses the language of the paper body — Chinese papers get Chinese, English papers get English.
- **Reports are always in Chinese**: all reports, explanations, and checklists shown to the user are in Chinese.
- **Default is report + modification suggestions only; do not edit the manuscript unilaterally**: after finding issues, list "location / current state / which rule is violated / suggested fix (including directly replaceable wording)"; whether to apply the change is the user's call. Only act when the user says, e.g., "fix the first three for me."
- **Two input formats**: a LaTeX source tree (`.tex/.bib/.cls/.sty`) and a Word `.docx`. Determine which one it is before choosing the path.
- **Prefer consuming standard artifacts**: if the project already contains a `paper-note`, `stat-results`, `figure-manifest`, or `reproduction-card`, read `references/artifact-contracts.md` first and validate it, to avoid hand-copying numbers and losing evidence provenance.

First determine which function the user wants, then jump to the corresponding section.

---

## Function 1: Draft Body Analysis Paragraphs from Figures/Tables

**Goal**: given an image of a figure or table from the user, generate an "As shown in Fig. X, …" analysis paragraph that can be dropped directly into the paper body — not describing pixels, but serving the argument.

**Steps**
1. **Get the image**: the user provides a file path to the figure/table image or pastes it directly; use vision capabilities to read the graph (trends, inflection points, data points, comparisons, significant differences, axis meanings).
2. **Fill in context** (this is the key to paragraph quality — do not skip):
   - Auto-extract background from the paper: if the user provided the paper file, locate the body section that references this figure (near `\ref{}` / `Fig. X` / `Figure X`), understand what the paper is arguing, how terminology is used, and what the previous paragraph's conclusion was.
   - Ask the user for a one-sentence intent: ask "What conclusion do you want this figure to support?" — a single sentence is enough; do not demand a long input.
3. **Write the paragraph**:
   - Open with a canonical reference form (Chinese "as shown in Fig. X" / English "As shown in Fig. X"), consistent with the paper's existing style.
   - First state objective readings (key values, trends, comparisons), then land on the argument (what conclusion this set of data supports, why), echoing the context.
   - Terms, variable names, and units must be unified with the rest of the paper. Language matches the paper body language.
   - Avoid empty but correct filler like "there are three rising curves in the figure"; every sentence must carry analytical value.
4. **Deliver the paragraph**, and briefly explain "I wrote this based on X and Y in the figure and the intent you stated; please double-check the numbers" (model-read figure values may have deviations; remind the user to verify).

---

## Function 2: Citation Convention Audit

**Goal**: audit all four dimensions — ① in-text citations ↔ reference list one-to-one correspondence; ② each reference's format compliance; ③ field completeness; ④ style consistency.

**Prerequisite: determine the style**. Three paths, follow based on the user's situation:

- **(a) User directly picks a built-in style**: the four built-in sets are GB/T 7714, IEEE, APA, ACM; rules are in `references/citation-styles.md`. If the user says nothing and provides no requirement document, ask which one to pick.
- **(b) User provides a "school/journal requirement document" and wants auditing against it** (e.g., East China University of Technology §9, a journal's submission guidelines): read the requirement file using the Function 3 reading method (`.doc` → `textutil` (Windows has no textutil; recommended to Save As .docx in Word first, then read), `.docx` → `docx_text.py`, `.pdf` → Read/`pdftotext`), and parse its reference format **into a "school-style specification"** (field order, separating punctuation, whether it carries type codes like `[J]`, author abbreviation rules, volume/issue/page notation, which reference type templates are provided) and send it to the user for confirmation. **This school specification takes priority over the built-in styles as the audit baseline.**
- **(c) School requirement ↔ national standard differential comparison (key value-add, mandatory)**: compare (b)'s school specification against the closest built-in style (usually GB/T 7714) item by item, and **proactively flag three categories of risk**:
  1. **Conflict**: the paper's actual formatting conforms to the national standard but not the school example, or vice versa (e.g., ECUT §9 examples have no `[J]` type code and use Chinese punctuation, while the paper follows GB/T 7714 with `[J]` and half-width punctuation) — clearly state "conclusion under school rules vs. under national standard is opposite," do not unilaterally judge.
  2. **Outdated**: the requirement document's year predates the current GB/T 7714 edition (2015), or is clearly out of step with common recent practice for the paper's references → flag "this requirement may have been superseded by a newer graduate handbook."
  3. **Incomplete**: the school only provides templates for some reference types (e.g., only journal articles) → for missing types, suggest using the national standard to fill the gap.
  Finally, **ask the user to decide which set to take as authoritative** (school specification / national standard / school-led with national standard filling gaps), then proceed to the four-dimensional audit. Rule details still reference `references/citation-styles.md` as the reference base.

**Steps**
1. **Confirm the style** (see above).
2. **Extract two lists**:
   - LaTeX: the set of all keys from `\cite{key}` / `\parencite{}` etc. in the body; reference sources — all entries in the `.bib` file, or `\bibitem{key}` entries in `thebibliography`.
   - Word: run `python3 scripts/docx_text.py <paper.docx>`. It locates the reference list (`--refs` outputs the full numbered list), extracts in-text citation numbers and **auto-filters noise** (isolates `[4096]`-like tensor-dimension numbers and numbers exceeding the reference count as "suspected noise/dangling," so they don't pollute correspondence checking); `--cites` directly gives the "cited / dangling / orphaned" three groups; `--json` gives structured data.
   - Markdown: run `python3 scripts/md_text.py <paper.md>` — the Markdown symmetric counterpart of `docx_text.py`, same interface (`--refs/--cites/--dump/--json`); before extraction, strips frontmatter and code blocks; the in-text citation vs. References list difference-set check proceeds the same way.
3. **Dimension ① one-to-one correspondence** (mostly computed directly by `docx_text.py`; verify the conclusion):
   - Cited in the body but not in the reference list (number > reference count) → missing source / dangling citation (after excluding noise).
   - In the reference list but never cited in the body (the script's "orphaned entries") → orphaned entries.
   - Numbered style: check whether numbering is consecutive and consistent with appearance order.
   - **EndNote/field reference special case**: if the script reports "⚠️ suspected field references" (far fewer numbers extracted from the body than reference entries), it means the citations are Word field codes that plain text extraction cannot reach. In this case, **do not conclude "large number of missing/orphaned"**; instead, ask the user to "update fields in Word → select all → `Ctrl+Shift+F9` to convert to a plain-text copy" and re-run the script; dimensions ②③④ can still proceed normally based on the reference list.
4. **Dimension ② format compliance**: check each entry item by item against the chosen style's field order, punctuation, italics, author-name abbreviation rules, volume/issue/page notation, type identifier codes (GB/T 7714's `[J]/[M]`), etc., and point out deviations.
5. **Dimension ③ field completeness**: whether each entry is missing key fields such as author/year/pages/DOI/publisher (per that style's required-field rules).
6. **Dimension ④ style consistency**: whether the paper mixes styles — inconsistent author abbreviations, inconsistent full/half-width punctuation, journal names switching between abbreviated and full, inconsistent in-text citation forms, inconsistent reference-list sorting rules (see the self-check checklist at the end of the rule card for details).
7. **Produce the report**: grouped by dimension, each issue gets "location (which entry / where in the body) + current state + which rule is violated + suggested fix (give the directly replaceable correct entry text, in the language of the reference)." At the end, ask whether the user wants the fixes applied on their behalf.

> Note: the fields in the `.bib` themselves may be correct, but the final appearance is what the `.bst`/style renders; if the paper uses `\bibliographystyle`, note that "the final presentation is determined by that bst," and simultaneously check the completeness and conventionality of the `.bib` source fields.

---

## Function 3: Paper Format Audit (against user requirements)

**Goal**: the user manually provides formatting requirements; parse them into a structured checklist, **confirm with the user first**, then compare each item against the paper's actual typesetting and report deviations.

**Steps**
1. **Collect requirements**: the user pastes natural-language requirements (e.g., "body in SimSun 12pt, 1.5× line spacing, margins top/bottom 2.5cm left/right 3cm, level-1 headings in Heiti 18pt centered, figure/table captions in 10.5pt"), or points to a requirement file — choose the reading method by extension:
   - `.docx`: run `python3 scripts/docx_text.py <requirement.docx> --dump req.txt` to extract full text, or read directly.
   - **`.doc` (legacy binary OLE2; the script cannot read it)**: use macOS built-in `textutil -convert txt -stdout <requirement.doc>` to extract text (if no textutil, fall back to `antiword`/`catdoc`; on Windows, recommended to Save As .docx in Word first, then read).
   - `.pdf`: prefer the Read tool to read directly; text-only PDF can also use `pdftotext <requirement.pdf> -` (if poppler is installed).
   - `.txt/.md`: read directly.
2. **Parse into a checklist and confirm** (key gate — do not skip): break the natural language into structured verifiable items, e.g.:
   ```
   | # | Item        | Requirement        | Scope   |
   |---|-------------|--------------------|---------|
   | 1 | Body font   | SimSun             | Body    |
   | 2 | Body size   | 12pt               | Body    |
   | 3 | Line spacing| 1.5×               | Body    |
   | 4 | Margins     | top/bottom 2.5cm, left/right 3cm | Whole doc |
   | 5 | Level-1 heading | Heiti 18pt centered | Headings |
   | 6 | Figure/table caption | 10.5pt       | Caption |
   ```
   Send this checklist to the user and let them confirm / add / correct before proceeding. Proactively ask about ambiguous items ("Does 'main heading' mean level-1 heading or the paper title?").
3. **Extract the paper's actual typesetting**:
   - **Word `.docx` (full audit)**: run
     `python3 scripts/docx_inspect.py <paper.docx>`
     to get default font/size/line spacing, section margins and paper size per section, heading styles at each level, body paragraph samples, figure/table caption samples. Add `--json` for structured data. The script is zero-dependency (Python standard library); no packages to install.
   - **LaTeX (only statically verifiable source items)**: read the main `.tex`, the preamble, files pulled in by `\input/\include`, and accompanying `.cls/.sty`. Per `references/latex-format-checkable.md`, judge each requirement as "source-verifiable" or "requires compilation to verify." **For items requiring compilation, honestly state that static determination is impossible; do not fabricate conclusions.**
4. **Compare item by item and produce the report**: for each checklist item, give a verdict —
   - ✅ Compliant (provide evidence: docx measured value / LaTeX command verbatim + filename)
   - ❌ Non-compliant (current state vs. requirement + suggested fix: for Word, say which style/setting to change; for LaTeX, give the command to change)
   - ⚠️ Cannot be statically determined (LaTeX rendering-only items: explain that the PDF must be compiled and measured)
5. At the end, ask whether the user wants the fixes applied on their behalf per the suggestions.

---

## File Index
- `scripts/bibtex_audit.py` — offline BibTeX/BibLaTeX field completeness and DOI syntax audit; authenticity or retraction verification must explicitly invoke the `literature-reader`'s online audit.
- `scripts/online_verification.py` — online DOI / journal metadata verification: queries each DOI via the Crossref API (``api.crossref.org/works/{doi}``) and compares against local records for title/journal/year/pages/author. Supports ``--doi`` (single, repeatable) or ``--bibtex <file.bib>`` (batch); ``--timeout`` / ``--retries`` control HTTP behavior; reports ``unavailable`` instead of crashing when the network is unreachable; outputs a JSON report containing ``schema_version``/``artifact_type``/``tool_version``/``warnings`` and explicitly states "does not replace human verification." Zero-dependency (urllib.request).
- `scripts/consistency_audit.py` — heuristic consistency screen for Markdown/LaTeX abbreviations, figure/table references, and LaTeX label/ref; `--symbols` enables LaTeX symbol-table consistency analysis (command definition vs. usage, equation label/ref, multi-notation symbol detection); does not replace post-render or DOCX semantic review.
- `scripts/claim_audit.py` — heuristic Markdown/LaTeX screen for strong causal or evidential wording without a nearby numeric citation; `--paper-note` preserves claim-level page/section evidence anchors in its report, but never claims automatic semantic verification.
- `scripts/docx_citation_audit.py` — zero-dependency DOCX screen for visible author-year citation candidates and Zotero/Mendeley/Word field-marker evidence; with ``--fields`` it also parses Word ``CITATION`` field instructions (raw ``instrText``/``instr``) and the rendered RESULT text between field markers.  Parsing is heuristic — it does not perform live Word resolution or verify bibliography semantics.
- `scripts/docx_structure_audit.py` — read-only DOCX evidence inventory for declared style inheritance, theme part, section count, and header/footer parts/references; final effective formatting still requires rendered verification.
- `scripts/evidence_matrix_audit.py` — validates IDs and traceability fields in a manually curated claim-evidence-citation JSON matrix; it does not establish semantic entailment or bibliographic truth.
- `scripts/structure_audit.py` — zero-dependency Markdown/LaTeX outline screen: core-section presence, order, and duplicate headings; reports only and never edits the manuscript.
- `scripts/docx_inspect.py` — zero-dependency extraction of real .docx typesetting (Chinese/English fonts listed separately / font size / line spacing / margins / heading styles / captions including bold), and computes final effective styles along the ``basedOn`` chain (``effective_styles``) and document default properties (``docDefaults`` parsing).
- `scripts/docx_text.py` — zero-dependency extraction of full .docx text, locates the reference list (`--refs`), extracts in-text citation numbers and filters noise / detects EndNote field references (`--cites`).
- `scripts/md_text.py` — Markdown symmetric counterpart of `docx_text.py`: extracts plain text from .md (stripping frontmatter/code blocks), locates the reference list (`--refs`), extracts in-text citation numbers and filters noise (`--cites`), same interface.
- `references/citation-styles.md` — GB/T 7714 · IEEE · APA · ACM four-set citation rule card + cross-style consistency self-check.
- `references/latex-format-checkable.md` — LaTeX format check: mapping table of source-statically-verifiable items vs. items requiring compilation to verify.
- `references/artifact-contracts.md` — input boundaries and conflict handling for literature, statistics, figure, and reproduction artifacts. Read when writing across skills.
