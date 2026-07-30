# PDF, OCR, and Complex Layout Extraction

## Table of Contents

- [Capability Boundaries](#capability-boundaries)
- [Layered Extraction Flow](#layered-extraction-flow)
- [Two-Column Layouts, Tables, and Captions](#two-column-layouts-tables-and-captions)
- [OCR and Quality Gates](#ocr-and-quality-gates)
- [Supplementary Materials](#supplementary-materials)
- [Evidence Anchors](#evidence-anchors)

## Capability Boundaries

Treat the PDF as a container; do not equate "successfully opening a file" with "correctly reading out the paper." Native text, OCR text, table inference, and human visual judgment must be tagged separately. Scripts do not access the network, bypass encryption, infer missing content, or guarantee that complex formulas, cross-page tables, or reading order are one hundred percent correct.

Install optional dependencies:

```bash
python -m pip install -e ".[pdf]"
"
```

OCR additionally requires a local installation of Poppler's `pdftoppm` and Tesseract, plus the corresponding language packs; these executables are not distributed with the repository.

## Layered Extraction Flow

1. Perform native text extraction first, preserving the page number, method, and character count for each page:

   ```bash
   python3 scripts/extract_pdf.py paper.pdf --out paper.extraction.json --markdown-out paper.extraction.md
   ```

2. For long papers, limit the page range first, e.g. `--pages 1-3,12-14`. Prioritize the abstract, introduction, results, methods, discussion, conclusion, and figure/table pages; do not waste OCR time on full-volume processing by default.
3. Default to `--layout auto`. Use `--layout two-column` when a two-column layout is known; when reading order errors are found, verify manually against page screenshots — do not continue summarizing on top of incorrect text.
4. Validate the JSON first:

   ```bash
   python tools/validate_artifact.py paper.extraction.json --type pdf-extraction
   ```

5. Then feed the page-numbered text into the reading notes; do not discard `extraction_method`, `warnings`, or the source checksum.

## Two-Column Layouts, Tables, and Captions

- Two-column re-flow is heuristic. Check the end of the abstract, spanning headings, headers/footers, formulas, and the seams between the left and right columns.
- `tables` are layout-recognition results, not author-published data files. Merged cells, cross-page tables, footnotes, and superscripts often require manual review.
- `captions` only capture text lines starting with Figure/Fig./Table numbering (including Chinese figure/table labels). A missing caption does not mean the paper lacks figures.
- Quantitative conclusions drawn from images, captions, or OCR must be tagged "please verify manually" unless they have already been visually compared against the original page.

## OCR and Quality Gates

- `--ocr auto` attempts OCR only on pages where native text is fewer than `--min-native-chars`.
- `--ocr always` requires the OCR backend to be fully available and returns non-zero on failure; `auto` retains the native result and writes a warning when the backend is missing.
- Use `--ocr-lang eng+chi_sim` to specify installed multilingual models. A missing language model should be treated as a failure; do not switch to an incorrect language and continue.
- Spot-check at least: the title page, one body page, one two-column page, one table page, and one formula-dense page. Check for missing characters, hyphenation artifacts, column order, and page-number correspondence.
- When scan quality is too low, handwritten annotations obscure content, or formulas are dense, stop automatic summarization and request a clearer original or human transcription.

## Supplementary Materials

`supplementary_mentions` only records mentions of supplement/appendix/supplementary materials in the main text; it does not indicate that attachments have been obtained. Run the same script on each supplementary PDF as an independent input, and record the filenames, checksums, and correspondence between the main text and attachments in the reading notes. Web attachments must be provided by the user or a legitimate data source; do not guess attachment URLs or bypass access controls.

## Evidence Anchors

Every core claim must retain at minimum: the source file checksum, PDF page number, section (if confirmable), a short evidence excerpt, and the extraction method. Page numbers use the PDF's physical page index; if the printed page number differs, write both as "PDF p.7 / printed p.123". OCR citations must be explicitly tagged, and the original page must be revisited before formal citation.
