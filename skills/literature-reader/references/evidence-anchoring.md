# Claim-Level Evidence Anchors

## Table of Contents

- [Minimum Contract](#minimum-contract)
- [Establishing Anchors](#establishing-anchors)
- [PDF Extraction Matching](#pdf-extraction-matching)
- [OCR and Visual Evidence](#ocr-and-visual-evidence)
- [Audit and Delivery](#audit-and-delivery)

## Minimum Contract

Every core claim in a `paper-note` must have a stable ID and at least one evidence anchor. Core claims include research question definition, key methods, primary findings, practical contributions, important limitations, and author interpretations; background common knowledge does not need mechanical citations added just to pad the count.

```json
{
  "id": "finding-primary",
  "claim_type": "finding",
  "text": "The method improves the primary endpoint.",
  "support_level": "direct",
  "evidence": [{
    "source": "paper.pdf",
    "page": 7,
    "section": "Results",
    "quote": "The primary endpoint increased ...",
    "extraction_method": "native-text",
    "verification": "exact-match"
  }]
}
```

- `claim_type`: `research-question`, `method`, `finding`, `contribution`, `limitation`, `interpretation`.
- `support_level`: `direct` means the source directly supports the claim; `partial` means it supports only part of it; `context-only` means the source provides background only and cannot serve as evidence for the conclusion.
- `page` uses the PDF physical page index; if the printed page number differs, state this together in the `section` or in human notes.
- `quote` is a short locating excerpt, defaulting to no more than 25 words; the 500-character schema ceiling is a safety guardrail, not a copyright license.
- `extraction_method`: `native-text`, `ocr`, `human-transcription`, or `visual`.
- `verification`: `exact-match`, `human-verified`, or `unverified`.

## Establishing Anchors

1. Write atomic claims first: each sentence expresses only one verifiable assertion; do not pack methods, results, and causal explanations together.
2. Find the location closest to the original evidence. Prioritize result tables/main text for results, methods sections for methods, and author limitation paragraphs for limitations; do not cite only abstract paraphrases.
3. Copy the shortest source text that uniquely locates the claim, and record the PDF page and section. When citing a table or figure, record its number as well and note "visual verification" in the human notes.
4. Be explicit about support strength. When evidence shows only correlation, do not write the claim as causal; an author calling their work "novel" supports only "the author claims novelty," not automatically "actual novelty."
5. When multiple sources jointly support a claim, create a separate anchor for each; one vague, long citation cannot substitute for multiple precise pieces of evidence.

## PDF Extraction Matching

When a `pdf-extraction` is available, run:

```bash
python3 scripts/audit_claim_evidence.py note.json \
  --extraction paper.extraction.json \
  --out note.evidence-audit.json
```

The auditor looks up the normalized short excerpt by physical page, checks that page's `native-text`/`ocr` method, and reports missing page numbers, source inconsistencies, method mismatches, and source-text misses. It only proves that the excerpt appears in the extracted text; it does not prove that the claim's reasoning is correct; support strength still requires the researcher's judgment.

Anchors that have only a section with no integer PDF page number may be retained but cannot be automatically matched page by page. Page numbers may differ across publisher HTML, accepted manuscripts, and the final PDF; the version must be distinguished in `source`.

## OCR and Visual Evidence

OCR excerpts use `verification: unverified` until the page image is revisited. Primary conclusions, numerical values, formulas, table cell contents, and in-figure readings must be changed to `human-verified` after manual checking. Using `--strict-ocr` can make the audit fail when a direct claim is supported only by unverified OCR.

`visual` is used for graphical trends, schematics, or formulas that cannot be reliably transcribed; the short excerpt writes the figure/table number and visible labels, while the actual judgment is written in the claim. Do not disguise eyeball-estimated values as precise table data.

## Audit and Delivery

Validate both artifacts before delivering the Markdown:

```bash
python tools/validate_artifact.py note.json --type paper-note
python tools/validate_artifact.py note.evidence-audit.json --type evidence-audit
```

`status: fail` indicates structural or in-page matching errors; `warning` indicates that a human action is still required; `pass` only means the current machine check passed. Preserve the checksums of the note, the PDF extraction, and the evidence audit. Re-run the audit after any rewrite of a core claim, replacement of a paper version, or re-OCR.
