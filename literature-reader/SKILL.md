---
name: literature-reader
description: Structured literature reading and management for graduate researchers. Three functions: (1) single-paper structured extraction — research question, method, contributions, experimental setup, limitations, reusable resources — producing a structured reading note; (2) multi-paper comparison producing a comparison matrix (NOT N independent per-paper summaries); (3) research-gap identification across a paper set, with gap-type classification and feasibility verdicts. Use when the user says "读论文/精读论文/帮我读这篇论文", "总结这篇论文的核心内容", "对比这几篇文献/做个文献对比表", "帮我找研究空白/创新点从哪来", "extract a reading note from this paper", "compare these papers", "find research gaps". NOT for writing analysis paragraphs into a manuscript or checking citation/format compliance — use paper-writing-assistant instead. NOT for extracting PDF page images or running experiments — that is out of scope.
---

# Literature Reader (文献阅读与管理)

For graduate researchers. Three independent functions — enter whichever the user asks for; never force all three in one run.

**Global conventions**
- **User-facing reports default to Chinese** (报告、清单、解释一律中文).
- **Content written into artifacts follows the artifact's language**: notes on English papers go in English if the user's library is English; Chinese thesis libraries get Chinese notes. When unsure, follow the user's existing notes.
- **Never fabricate**: if a field cannot be determined from the text, write `[未提及]` / `[not stated]` and say so, instead of guessing. Numbers quoted from figures/tables must be flagged "请人工核对" when read from images.
- **Metadata is machine-extractable; analysis is not.** Use `scripts/extract_metadata.py` for DOI/title/author-year extraction; do the reading and judgment yourself.

Pick the function first, then jump to its section.

**Depth routing**: before reading anything, decide the reading depth — triage (速读筛选), deep read (精读), or critical review (批判性阅读, only for papers the thesis depends on). When the user gives a batch of papers without notes, or asks for 粗筛/值不值得读, start with triage. For per-depth procedures, checklists, and common criticism points (baseline fairness, statistical vs practical significance, leakage, reproducibility red flags), **read `references/reading-workflows.md`** — only the section for the chosen depth.

---

## Function 1: Single-paper structured reading note

**Goal**: turn one paper into a structured reading note the user can file into their library — covering research question, method, contributions, experimental setup, limitations, and reusable resources.

**Steps**
1. **Get the paper text**. Inputs, cheapest first: pasted abstract/text → PDF-exported text file → raw PDF (read only abstract + intro + conclusion + figure captions first; go deeper only if the user asks for 精读).
2. **Extract metadata mechanically**. If the user pastes a reference entry or PDF front page text, run
   `python3 scripts/extract_metadata.py <textfile>` to pull DOI / title / authors / year into JSON. Fill the note header from its output; mark `[待确认]` for fields the script could not resolve.
3. **Read actively**. Skim in this order: abstract → figures/tables + captions → conclusion → method → related work. Take position on *what is actually new* vs *repackaged* — do not parrot the authors' own claims of novelty.
4. **Fill the note** following `references/note-template.md` — **read it when you reach this step**; it contains the full template plus per-field filling rules (what counts as a real contribution, how to write the "reusable resources" section, length caps). Do not read it for Functions 2/3.
5. **Deliver**: the filled note (as a `.md` file if the user gave a directory, otherwise inline), plus a 3–5 sentence Chinese oral summary (口头速览) for quick triage.

---

## Function 2: Multi-paper comparison matrix

**Goal**: a comparison matrix over a paper set — the deliverable is the *matrix*, not N per-paper summaries. The matrix should let the user see at a glance which papers cluster by method, where results conflict, and which paper to engage deeply.

**Steps**
1. **Collect the paper set**. Pasted reference list → run `python3 scripts/extract_metadata.py <textfile>` once to split entries and extract citation keys (it handles `[1]`, `1.`, and `(Author, Year)` numbering). Or existing notes from Function 1.
2. **Choose comparison dimensions WITH the user** before reading anything in depth. Default dimensions: 研究问题 / 方法 / 数据集·对象 / 核心结论 / 证据类型 / 局限性 / 与本课题的相关度. For the per-discipline dimension library (ML/生医/社科/工程/人文), note-field-to-matrix alignment rules, and conflict-handling rules, **read `references/comparison-matrix.md`** now.
3. **Fill cells tersely** — one line per cell, `?` when unknown (never guess). Papers whose source is only an abstract get `(仅摘要)` marked in the evidence column.
4. **Read the matrix, not just write it**: after the table, add a short Chinese "横向观察" block — which papers agree/conflict, which is the load-bearing citation for each claim, which can be cited in passing. This synthesis is the actual value.
5. **Cap effort**: ≤ 12 papers per run by default; for more, ask the user to triage first (title+abstract only, matrix with sparser cells). For large candidate sets, score papers on relevance/novelty/quality/reproducibility (1–5 each, your judgment) into a JSON file and rank them mechanically:
   `python3 scripts/triage_score.py <scores.json> --weights '{"relevance":0.4,"novelty":0.2,"quality":0.2,"reproducibility":0.2}' --format markdown`
   Use the ranking to decide which papers get matrix cells.

---

## Function 3: Research-gap identification

**Goal**: from a compared paper set (ideally a Function-2 matrix), identify candidate research gaps, classify them, and give a feasibility verdict — not a vague "未来工作" list.

**Steps**
1. **Input**: an existing comparison matrix (Function 2 output or user's own), or ≥ 4 papers on one topic. If the user has fewer, say so — gap identification on 1–2 papers is speculation; offer Function 1/2 instead.
2. **Read `references/gap-analysis.md` in full now** (this is its function). Follow its workflow: dimension scan → gap candidate enumeration → gap-type classification (方法/数据/人群/情境迁移/理论/评估/负结果 七类) with per-type evidence requirements → feasibility verdict (数据可得性 / 方法成熟度 / 工作量 vs 学位要求 / 撞车风险). Use its sentence templates for the gap statements.
3. **Deliver a Chinese report**: each candidate gap gets — 空白描述（一句话）/ 依据（矩阵里哪些行指向它）/ 空白类型 / 可行性裁决（可做·谨慎·不建议 + 理由）/ 与现有文献的区分点. Rank by 可行性 × 价值.
4. **Be candid**: if the set shows the area is crowded with no clear opening, say that instead of manufacturing a weak gap.

---

## File index

- `references/note-template.md` — structured reading-note template + per-field filling rules (read during Function 1, step 4).
- `references/reading-workflows.md` — triage / deep-read / critical-review procedures with checklists and criticism points (read the section matching the chosen depth; critical-review section for papers the thesis builds on).
- `references/comparison-matrix.md` — per-discipline dimension library, note-to-matrix alignment, conflict-handling rules (read in Function 2, step 2).
- `references/gap-analysis.md` — gap-identification workflow, gap-type classification + evidence requirements + statement templates, feasibility verdict rubric (read in full in Function 3).
- `scripts/extract_metadata.py` — zero-dependency extractor: splits pasted reference lists (`[1]` / `1.` / `(Author, Year)` numbering) and pulls DOI / title / authors / year from reference text or PDF-exported text; outputs JSON (default), BibTeX (`--format bibtex`), or RIS (`--format ris`), and parses `.bib` back to JSON (`--from-bibtex`).
- `scripts/triage_score.py` — zero-dependency weighted ranker: takes per-paper dimension scores (relevance/novelty/quality/reproducibility, 1–5) as JSON, outputs ranked JSON or markdown with keep/skim-later/drop verdicts; `--seed` for deterministic tie-breaking.
