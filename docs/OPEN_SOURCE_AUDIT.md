# Open-source provenance audit

Audit date: 2026-07-29. This inventory covers source or data visibly derived from, modeled on, or interoperating with third-party projects. Re-run the audit whenever a copied asset, template, dataset, palette, or substantial code fragment is added.

## Status: phase audit, not release approval

This is a completed inventory for the materials reviewed on the audit date, but **not** the final release provenance approval. Before the first public release, re-audit every dependency extra, script added after this date (including statistical/MICE and palette-audit helpers), documentation asset, example data file, and generated distribution artifact. Confirm that notices remain complete and that ignored research material was not force-added.

Run `python tools/release_preflight.py . --pretty` before a release to inventory baseline repository readiness. Its `needs-human-release-review` status is intentionally never release approval.

## Distribution findings

| Component | Upstream | Upstream license | Relationship | Release action |
|---|---|---|---|---|
| `scientific-plot/scripts/palettes.json` | [lcpmgh/colors](https://github.com/lcpmgh/colors) | MIT, copyright 2025 Liang Chen | Palette data converted from upstream CSV | Keep attribution and MIT license copy; exclude archived web articles and screenshots |
| `md2latex` template-marker idea | [zijunwa/md2tex](https://github.com/zijunwa/md2tex) | MIT | Behavior/interface idea; local implementation is independent | Attribute the inspiration; no upstream code is bundled |
| `md2latex` mapping ideas | [VMIJUNV/md-to-latex](https://github.com/VMIJUNV/md-to-latex) | No repository license found | Behavior ideas only | Do not copy or redistribute upstream code; describe it as a public reference, not open source |
| `md2latex` CJK and option ideas | [fastpen Markdown to LaTeX](https://marketplace.visualstudio.com/items?itemName=fastpen.markdown2latex) | Source/license not verified | Behavior ideas only | Do not copy extension code or assets; keep only independent behavior descriptions |
| `.excalidraw.md` interoperability | [Obsidian Excalidraw plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin) | AGPL-3.0 | Output-format interoperability; no plugin code bundled | Do not vendor plugin code; state that output targets an external compatible format |
| Native PDF extraction | [pdfplumber](https://github.com/jsvine/pdfplumber) | MIT | Optional runtime dependency; no source code bundled | Declare under the `pdf` extra and retain upstream dependency license |
| PDF page rendering for OCR | [Poppler](https://poppler.freedesktop.org/) `pdftoppm` | GPL-2.0-or-later | Optional external executable invoked locally; not distributed | Do not vendor binaries; document separate installation and license |
| OCR recognition | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) | Apache-2.0 | Optional external executable invoked locally; not distributed | Do not vendor binaries or language models without a separate provenance review |
| Retraction and scholarly metadata | [Crossref Retraction Watch](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/) | CC0 metadata | Optional user-supplied CSV or explicit REST query; no snapshot bundled | Record query provenance; cite Retraction Watch for published use; never redistribute copyrighted abstracts |
| arXiv metadata | [arXiv API](https://info.arxiv.org/help/api/user-manual.html) | Service terms apply | Explicit, batched online identifier verification; responses not bundled | Follow API terms, cache responsibly, and avoid bulk harvesting through the interactive API |
| PubMed metadata | [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/) | Record-specific terms; abstracts may be copyrighted | Explicit, batched online PMID verification; responses not bundled | Send tool/email, follow rate rules, show NCBI disclaimer, and do not redistribute protected abstracts |
| Adaptive/sequential design guidance | [FDA adaptive design guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/adaptive-design-clinical-trials-drugs-and-biologics-guidance-industry), [EMA multiplicity guidance](https://www.ema.europa.eu/en/multiplicity-issues-clinical-trials-scientific-guideline), [ACE statement](https://doi.org/10.1136/bmj.m115), and [DeMets–Lan](https://doi.org/10.1002/sim.4780131308) | Public government guidance and cited scholarly publications | Method and reporting references; no source code, article text, or proprietary tables bundled | Cite the sources, implement independently, and require design-specific validation rather than claiming regulatory approval |
| Longitudinal/survival sample-size methods | [Schoenfeld 1983](https://doi.org/10.2307/2531021), [Schoenfeld 1981](https://doi.org/10.1093/biomet/68.1.316), and [Hedeker et al. 1999](https://doi.org/10.3102/10769986024001070) | Cited scholarly publications | Formula/method references; no paper text, code, or proprietary tables bundled | Keep the implementation independent, cite the method, and label normal-approximation/model limitations |
| Power reference validation | [Statsmodels](https://www.statsmodels.org/stable/) and [SciPy](https://docs.scipy.org/doc/scipy/) | BSD-3-Clause | Optional runtime dependencies used only for numerical comparison; no source code bundled | Declare in `validation` extra, record versions/tolerances, and retain upstream licenses in installed distributions |
| Formula-based statistical models | [Statsmodels](https://www.statsmodels.org/stable/) and [pandas](https://pandas.pydata.org/) | BSD-3-Clause | Optional runtime dependencies for OLS/GLM/GEE/MixedLM and CSV data frames; no source code bundled | Declare in `models` extra, restrict formula evaluation, record versions through the environment, and retain upstream licenses |

## Code-independence check for md2latex

The local `md2latex/scripts/md2latex.py` was compared line-by-line after whitespace normalization with the two retrievable Python implementations on 2026-07-29:

- Against `zijunwa/md2tex` — similarity ratio 0.0266; longest exact block was two ordinary import lines.
- Against `VMIJUNV/md-to-latex` — similarity ratio 0.0126; longest exact block was one line.

This is evidence that the current implementation does not contain substantial verbatim copying from those two repositories. It does not authorize future copying; contributors must repeat provenance review for later ports or rewrites.

## Dependencies

Development dependencies `jsonschema`, `PyYAML`, and `pytest` report MIT licenses. Optional numerical/plotting/PDF/model/validation dependencies are installed by users and are not vendored: NumPy, SciPy, Statsmodels, and pandas use BSD-family licenses; Matplotlib uses the PSF-compatible Matplotlib license; pdfplumber uses MIT. Dependency licenses apply to those packages and their transitive dependencies and are not replaced by this repository's Apache-2.0 license.

## Excluded local source material

The following material may exist locally for research but is intentionally excluded by `.gitignore`:

- saved `.mhtml` pages;
- copied web articles and article Markdown;
- scraped screenshots and the `docs/{pageTitle}/` directory;
- generated `workspace/` artifacts, LaTeX intermediates, checkpoints, and caches.

“Publicly available” does not mean “licensed for redistribution.” Do not force-add excluded material into a release.
