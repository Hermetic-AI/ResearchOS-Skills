---
name: literature-reader
description: Extract and read papers; handle PDF/OCR, tables, captions, supplements, and large-corpus checkpointed processing; verify DOI/arXiv/PMID, retractions, duplicates, and versions; exchange Zotero/CSL JSON, BibTeX, RIS, EndNote XML, and ResearchOS libraries; create evidence-anchored notes, comparisons, and gap analyses. Use for reading papers, PDF/OCR extraction, batch incremental literature processing, identifier/retraction checks, deduplicating papers, Zotero/BibTeX/RIS/EndNote conversion, comparing papers, finding research gaps, extracting, auditing, batch processing, or converting papers. Not for manuscript prose/layout checking, cross-note graphs, visual PDF editing, or experiments.
---

# Literature Reader

For graduate researchers. Three independent functions — enter whichever the user asks for; never force all three in one run.

**Global conventions**
- **User-facing reports default to Chinese** (reports, lists, and explanations are always in Chinese).
- **Content written into artifacts follows the artifact's language**: notes on English papers go in English if the user's library is English; Chinese thesis libraries get Chinese notes. When unsure, follow the user's existing notes.
- **Never fabricate**: if a field cannot be determined from the text, write `[未提及]` / `[not stated]` and say so, instead of guessing. Numbers quoted from figures/tables must be flagged "please verify manually" when read from images.
- **Metadata is machine-extractable; analysis is not.** Use `scripts/extract_metadata.py` for DOI/title/author-year extraction; do the reading and judgment yourself.
- **Interchange artifacts**: when the result feeds another ResearchOS skill, read `references/artifact-contracts.md` and emit schema-validated JSON beside the human-readable Markdown.

Pick the function first, then jump to its section.

**Depth routing**: before reading anything, decide the reading depth — triage (quick scan/screening), deep read, or critical review (only for papers the thesis depends on). When the user gives a batch of papers without notes, or asks for coarse screening / "is this worth reading", start with triage. For per-depth procedures, checklists, and common criticism points (baseline fairness, statistical vs practical significance, leakage, reproducibility red flags), **read `references/reading-workflows.md`** — only the section for the chosen depth.

---

## Function 1: Single-paper structured reading note

**Goal**: turn one paper into a structured reading note the user can file into their library — covering research question, method, contributions, experimental setup, limitations, and reusable resources.

**Steps**
1. **Get the paper text**. Inputs, cheapest first: pasted abstract/text → PDF-exported text file → raw PDF. For a raw, scanned, double-column, table-heavy, or supplement-bearing PDF, **read `references/pdf-extraction.md` in full**, run `scripts/extract_pdf.py`, validate its `pdf-extraction` JSON, and retain page/method anchors. Read only abstract + intro + conclusion + figure captions first; go deeper only for deep reading. Never treat OCR or inferred table cells as verified source text.
2. **Extract metadata mechanically**. If the user pastes a reference entry or PDF front page text, run
   `python3 scripts/extract_metadata.py <textfile>` to pull DOI / arXiv / PMID / title / authors / year into JSON. When identifiers, retraction status, duplicates, or preprint-to-publication versions matter, **read `references/bibliography-audit.md` in full** and run `scripts/audit_bibliography.py`; online checks require explicit `--online --email`. Fill the note header from the audited output; mark `[to be confirmed]` for unresolved fields.
3. **Read actively**. Skim in this order: abstract → figures/tables + captions → conclusion → method → related work. Take position on *what is actually new* vs *repackaged* — do not parrot the authors' own claims of novelty.
4. **Fill the note** following `references/note-template.md` — **read it when you reach this step**; it contains the full template plus per-field filling rules. For every core conclusion, **read `references/evidence-anchoring.md` in full**, add a stable claim-level page/section/quote/method anchor to the companion `paper-note` JSON, and run `scripts/audit_claim_evidence.py` against `pdf-extraction` when available. Do not read these note-specific references for Functions 2/3.
5. **Deliver**: the filled note, schema-valid `paper-note` JSON and `evidence-audit` JSON when files are available, plus a 3–5 sentence Chinese oral quick overview. Disclose any unmatched quote or unverified OCR; never downgrade an audit failure to a prose footnote.

---

## Function 2: Multi-paper comparison matrix

**Goal**: a comparison matrix over a paper set — the deliverable is the *matrix*, not N per-paper summaries. The matrix should let the user see at a glance which papers cluster by method, where results conflict, and which paper to engage deeply.

**Steps**
1. **Collect the paper set**. Pasted reference list → run `python3 scripts/extract_metadata.py <textfile>` once to split entries and extract citation keys (it handles `[1]`, `1.`, and `(Author, Year)` numbering). For Zotero/CSL JSON, BibTeX, RIS, EndNote XML, or ResearchOS library files, **read `references/bibliography-interchange.md` in full** and normalize with `scripts/convert_bibliography.py` before comparison. Or use existing notes from Function 1.
2. **Choose comparison dimensions WITH the user** before reading anything in depth. Default dimensions: Research question / Method / Dataset·subjects / Core conclusion / Evidence type / Limitations / Relevance to the current topic. For the per-discipline dimension library (ML/biomedical/social sciences/engineering/humanities), note-field-to-matrix alignment rules, and conflict-handling rules, **read `references/comparison-matrix.md`** now.
3. **Fill cells tersely** — one line per cell, `?` when unknown (never guess). Papers whose source is only an abstract get `(abstract only)` marked in the evidence column.
4. **Read the matrix, not just write it**: after the table, add a short Chinese "cross-paper observations" block — which papers agree/conflict, which is the load-bearing citation for each claim, which can be cited in passing. This synthesis is the actual value.
5. **Cap effort**: ≤ 12 papers per run by default; for more, ask the user to triage first (title+abstract only, matrix with sparser cells). For large candidate sets, score papers on relevance/novelty/quality/reproducibility (1–5 each, your judgment) into a JSON file and rank them mechanically:
   `python3 scripts/triage_score.py <scores.json> --weights '{"relevance":0.4,"novelty":0.2,"quality":0.2,"reproducibility":0.2}' --format markdown`
   Use the ranking to decide which papers get matrix cells. For a directory-scale corpus, **read `references/batch-processing.md` in full** and use `scripts/batch_literature.py` for isolated outputs, content-hash checkpoints, limited batches, failure retry, and incremental updates before triage; do not build one giant matrix.

---

## Function 3: Research-gap identification

**Goal**: from a compared paper set (ideally a Function-2 matrix), identify candidate research gaps, classify them, and give a feasibility verdict — not a vague "future work" list.

**Steps**
1. **Input**: an existing comparison matrix (Function 2 output or user's own), or ≥ 4 papers on one topic. If the user has fewer, say so — gap identification on 1–2 papers is speculation; offer Function 1/2 instead.
2. **Read `references/gap-analysis.md` in full now** (this is its function). Follow its workflow: dimension scan → gap candidate enumeration → gap-type classification (Method / Data / Population / Context transfer / Theory / Evaluation / Negative results — seven types) with per-type evidence requirements → feasibility verdict (Data availability / Method maturity / Workload vs degree requirements / Risk of being scooped). Use its sentence templates for the gap statements.
3. **Deliver a Chinese report**: each candidate gap gets — Gap description (one sentence) / Evidence (which rows in the matrix point to it) / Gap type / Feasibility verdict (doable / cautious / not recommended + reason) / Differentiation from existing literature. Rank by Feasibility × value.
4. **Be candid**: if the set shows the area is crowded with no clear opening, say that instead of manufacturing a weak gap.

---

## File index

- `references/note-template.md` — structured reading-note template + per-field filling rules (read during Function 1, step 4).
- `references/reading-workflows.md` — triage / deep-read / critical-review procedures with checklists and criticism points (read the section matching the chosen depth; critical-review section for papers the thesis builds on).
- `references/comparison-matrix.md` — per-discipline dimension library, note-to-matrix alignment, conflict-handling rules (read in Function 2, step 2).
- `references/gap-analysis.md` — gap-identification workflow, gap-type classification + evidence requirements + statement templates, feasibility verdict rubric (read in full in Function 3).
- `references/artifact-contracts.md` — versioned `paper-note`, `literature-matrix`, and `research-gap` JSON handoff rules. Read only for reusable/cross-skill output.
- `references/pdf-extraction.md` — native PDF, two-column, table, caption, OCR, supplement, and evidence-anchor workflow. Read in full for raw or complex PDFs.
- `references/bibliography-audit.md` — DOI/arXiv/PMID syntax and optional API verification, Crossref/Retraction Watch and PubMed integrity signals, conservative deduplication, and version-family merge rules. Read in full when identity or publication status matters.
- `references/bibliography-interchange.md` — Zotero/CSL JSON, BibTeX, RIS, EndNote XML, and ResearchOS conversion workflow, field mappings, provenance, security, and loss boundaries. Read in full before library migration.
- `references/evidence-anchoring.md` — claim-level IDs, page/section/short-quote anchors, support strength, native/OCR/visual verification states, and evidence-audit workflow. Read in full for Function 1 deliverables.
- `references/batch-processing.md` — source/output isolation, discovery rules, stable names, content hashes, per-file checkpointing, `--limit`, resume, retry, removed items, and completion checks. Read in full for directory-scale corpora.
- `scripts/extract_pdf.py` — optional-`pdfplumber` extractor for page-anchored text, tables, captions, supplement mentions, and explicitly labeled local OCR fallback; outputs schema-validated JSON and optional Markdown.
- `scripts/audit_bibliography.py` — offline-by-default bibliography auditor; emits schema-validated `bibliography-audit` JSON, accepts an optional local Retraction Watch CSV, and accesses Crossref/arXiv/PubMed only with explicit online mode and a redacted contact email.
- `scripts/convert_bibliography.py` — zero-dependency, provenance-producing converter across ResearchOS JSON, CSL JSON/Zotero data, BibTeX, RIS, and a safe common-field subset of EndNote XML; outputs a schema-validated companion manifest.
- `scripts/audit_claim_evidence.py` — zero-dependency structural and page-level quote auditor for `paper-note` + optional `pdf-extraction`; always emits an `evidence-audit` report and returns nonzero on failed evidence checks.
- `scripts/batch_literature.py` — resumable, incremental corpus processor for PDFs, reference text, and bibliography formats; writes a schema-validated `literature-batch` checkpoint after every item and never deletes source or stale derived artifacts.
- `scripts/extract_metadata.py` — zero-dependency extractor: splits pasted reference lists (`[1]` / `1.` / `(Author, Year)` numbering) and pulls DOI / arXiv base+version / PMID / title / authors / year from reference text or PDF-exported text; outputs JSON (default), BibTeX (`--format bibtex`), or RIS (`--format ris`), and parses `.bib` back to JSON (`--from-bibtex`). Latin-script names only; Chinese author names resolve to null + warning.
- `scripts/triage_score.py` — zero-dependency weighted ranker: takes per-paper dimension scores (relevance/novelty/quality/reproducibility, 1–5) as JSON, outputs ranked JSON or markdown with keep/skim-later/drop verdicts; `--seed` for deterministic tie-breaking.
