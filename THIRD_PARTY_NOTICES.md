# Third-party notices

ResearchOS-Skills is licensed under Apache-2.0. Files derived from third-party projects remain subject to their original licenses and attribution requirements.

## lcpmgh/colors

`scientific-plot/scripts/palettes.json` was converted from the palette collection in [`lcpmgh/colors`](https://github.com/lcpmgh/colors). The upstream project is licensed under the MIT License:

> Copyright (c) 2025 Liang Chen

A copy of its license is retained at `docs/colors/LICENSE` when the upstream source-material directory is distributed.

Some palette names in that collection were curated from published web articles and journal figures. ResearchOS-Skills redistributes color-value data and attribution metadata, not copies of those articles or figures. Locally collected `.mhtml`, article backups, and scraped images are excluded through `.gitignore` and must not be included in releases without separate permission.

## Interoperability and design references

`md2latex` independently implements behaviors observed in several public Markdown-to-LaTeX tools. No upstream source code or assets are bundled. One reference is MIT-licensed; two have no verified redistribution license and must not be copied. `scientific-plot` can write `.excalidraw.md` compatible output but does not bundle the AGPL-3.0 Obsidian Excalidraw plugin. The evidence and restrictions are recorded in `docs/OPEN_SOURCE_AUDIT.md`.

`experiment-designer` optionally compares its documented normal approximations with SciPy and Statsmodels. `data-analysis-assistant` optionally uses pandas and Statsmodels for formula models. These BSD-family packages are installed separately through optional extras; none is vendored.

## Optional PDF tooling

`literature-reader` can use the MIT-licensed `pdfplumber` Python package for native PDF text and table extraction. Local OCR interoperability uses external Poppler `pdftoppm` (GPL-2.0-or-later) and Tesseract OCR (Apache-2.0). These packages and executables are installed separately by users and are not copied or distributed in this repository. Their own licenses continue to apply.

## External scholarly metadata

Optional bibliography verification queries Crossref, arXiv, and NCBI E-utilities only when a user supplies `--online`. The repository does not mirror their service responses. Crossref publishes the Retraction Watch dataset as CC0; users may separately supply a local CSV, which is not bundled. Crossref requests citation of Retraction Watch when its data is used in published work. PubMed records and especially abstracts may include publisher- or author-copyrighted material; NCBI usage policies and disclaimers continue to apply.

## Contributor responsibility

Contributors must document the origin, copyright holder, license, modifications, and redistribution constraints for every added dataset, template, image, font, palette collection, or copied code fragment. “Available online” is not a redistribution license.
