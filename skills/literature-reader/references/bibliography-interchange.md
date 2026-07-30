# Zotero, BibTeX, RIS, and EndNote XML Interchange

## Table of Contents

- [Format selection](#format-selection)
- [Conversion workflow](#conversion-workflow)
- [Fields and loss boundaries](#fields-and-loss-boundaries)
- [Security and validation](#security-and-validation)

## Format selection

`convert_bibliography.py` supports:

| Format | Argument | Typical use |
|---|---|---|
| ResearchOS JSON | `researchos-json` | Lossless normalized intermediate layer, schema validation, subsequent auditing |
| CSL JSON | `csl-json` | Zotero import/export and the citeproc ecosystem |
| BibTeX | `bibtex` | LaTeX projects and general interchange |
| RIS | `ris` | Broadly compatible interchange between Zotero, EndNote, and databases |
| EndNote XML | `endnote-xml` | Unicode text record exchange between EndNote libraries |

Zotero's official documentation lists CSL JSON, BibTeX, RIS, and EndNote XML as importable formats; when exporting for Zotero, prefer CSL JSON, BibTeX, or RIS. EndNote XML is EndNote's proprietary interchange format. This script implements only a subset of common text fields and does not claim to reproduce its rich text, attachments, or all private fields. References: <https://www.zotero.org/support/kb/importing_standardized_formats>, <https://docs.endnote.com/docs/endnote/2025/v1/windows/en/content/15independentbibs_export/exporting_to_endnote_xml.htm>.

## Conversion workflow

Every conversion must write both the target file and a provenance manifest:

```bash
python3 scripts/convert_bibliography.py zotero.json \
  --to bibtex --out library.bib

python3 scripts/convert_bibliography.py library.ris \
  --to researchos-json --out library.normalized.json
```

When `--from` is not specified, the source is auto-detected by content and extension. When the source is ambiguous or the extension is wrong, specify `--from csl-json|bibtex|ris|endnote-xml|researchos-json` explicitly. The default manifest is `<out>.manifest.json`; use `--manifest-out` to change the path. Existing target or manifest files are refused overwrite by default; only `--force` can replace them. Input files must never be used as output.

ResearchOS JSON and the conversion manifest are validated separately:

```bash
python tools/validate_artifact.py library.normalized.json --type bibliography-library
python tools/validate_artifact.py library.bib.manifest.json --type bibliography-conversion
```

After conversion, run `audit_bibliography.py` to handle identifier online verification, retraction signals, duplicate records, and version families; format conversion itself does not replace auditing.

## Fields and loss boundaries

The normalized layer preserves: type, title, authors, year, journal/booktitle, volume/issue/pages, DOI, PMID, arXiv, URL, abstract, keywords, and citation key. The Zotero API's `{key, data}` wrapper, CSL author objects, and Zotero creator/tag structures are all readable.

- Non-standard fields in BibTeX/RIS/EndNote XML vary by software and translator; spot-check after conversion.
- Attachments, PDFs, notes, annotations, collections, related items, sync status, and internal database keys are not guaranteed across formats.
- EndNote XML rich text, superscripts/subscripts, images, and proprietary styling are outside this script's fidelity scope.
- LaTeX macros and case protection are preserved as input text; no TeX-compilation-level semantic rewriting is performed.
- Abstracts may be subject to author or publisher copyright. Only convert records the user has lawfully provided; do not batch-scrape or redistribute abstracts from external databases.
- Citation key conflicts are resolved with a stable suffix; do not replace old keys in an existing LaTeX project without a diff.

Spot-check at least one ordinary journal paper, one multi-author record, one non-English record, one record with DOI/PMID/arXiv, and one non-journal type. For large libraries, take a small sample round-trip first, confirm the target software's actual import result, then process the full library.

## Security and validation

Input is limited to 50 MiB. EndNote XML rejects `DOCTYPE` and `ENTITY` to avoid processing entity declarations on untrusted XML. `--strict` fails when a record lacks both a title and an academic identifier; the default keeps the record and writes a warning.

Output checksum, record count, source/target format, and command are saved in the manifest. After importing into the target software, compare record counts and spot-check author order, year, page numbers, Unicode, identifiers, and document type. Equal record counts do not imply lossless fields; any automatic migration should retain a backup of the original library.
