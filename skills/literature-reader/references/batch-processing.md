# Batching, Recovery, and Incremental Updates for Large Literature Sets

## Table of Contents

- [Directory Isolation](#directory-isolation)
- [First Run and Batching](#first-run-and-batching)
- [Recovery and Incremental Updates](#recovery-and-incremental-updates)
- [Status and Failure Handling](#status-and-failure-handling)
- [Delivery Checks](#delivery-checks)

## Directory Isolation

The raw corpus directory is read-only; the derived-output directory must live outside the corpus tree. Create two clearly defined directories first, e.g. `corpus/` and `derived/`; the tools refuse to write output back into `corpus/`, do not delete source files, and do not automatically delete old outputs whose source has disappeared.

By default, `.pdf`, `.txt`, `.bib`, `.ris`, `.xml`, and `.json` are discovered. Markdown is only processed with an explicit `--include '*.md'`, because ordinary research notes are not necessarily reference lists. Hidden files, symlinks that escape the root directory, and files matching exclusion rules are skipped.

## First Run and Batching

```bash
python3 scripts/batch_literature.py corpus \
  --out-dir derived \
  --limit 100
```

`--limit` processes only the specified number of pending/changed files, atomically updating `derived/batch-state.json` after each file completes. Default processors:

- PDF → `pdf-extraction`; OCR defaults to `never` and is enabled only with an explicit `--pdf-ocr auto|always`.
- `.txt` → reference metadata extraction JSON.
- BibTeX/RIS/EndNote XML/JSON → normalized `bibliography-library` and conversion manifest.

Use repeatable `--include`/`--exclude` to narrow the scope, e.g. `--include 'topic-a/*.pdf' --exclude '**/archive/*'`. The default per-file ceiling is 50 MiB; `--max-file-mib` adjusts it. Oversized files are recorded as `skipped-large`, without reading the full-text hash or processing.

## Recovery and Incremental Updates

When a checkpoint already exists, an explicit `--force` is required, signaling permission to update the state and any derived outputs whose content has changed:

```bash
python3 scripts/batch_literature.py corpus --out-dir derived --limit 100 --force
```

Each relative path stores its SHA-256, size, processing type, stable output name, and status. Projects with an identical hash and whose output still exists become `unchanged`; newly added or content-changed projects are re-processed; projects whose source has been deleted become `removed`, but old outputs are retained for manual archiving. Do not use timestamps as the basis for incrementality.

The stable name is composed of the normalized stem and a hash of the relative path, so identically named files do not collide. Content changes still write back to the same derived path, making downstream references convenient; only a recovery run with `--force` can overwrite it.

## Status and Failure Handling

- `success`: processed successfully this run.
- `unchanged`: identical hash and output exists; not re-run.
- `pending`: constrained by `--limit`; left for the next batch.
- `failed`: sub-processor exited non-zero; the checkpoint retains truncated stdout/stderr.
- `skipped-large`: exceeded the file size ceiling.
- `removed`: source file disappeared; derived output not deleted.

Failed items with the same hash are not re-run by default; add `--retry-failed --force` after confirming that dependencies or configuration have been fixed. Source content changes automatically trigger re-processing. Any `failed` item causes the batch to return non-zero; pending, removed, or skipped-large alone do not masquerade as full completion — check the summary.

When creating a new checkpoint, if the stable target file already exists, the tool fails by default instead of overwriting. After inspecting the source, re-run with `--force` to permit replacement. If the checkpoint's source/output root differs from the new command, recovery is refused to prevent cross-contamination between libraries.

## Delivery Checks

```bash
python tools/validate_artifact.py derived/batch-state.json --type literature-batch
```

Pre-delivery requirements: `pending == 0` and `failed == 0`; explain each `skipped-large` and `removed` item individually; spot-check at least one output from each processor type; for PDFs, retain OCR warnings; for bibliography libraries, re-run the bibliography audit. The checkpoint is a run ledger, not a final review, and does not prove that every paper has been read in depth.
