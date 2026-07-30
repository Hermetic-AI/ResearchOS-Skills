# Release Readiness — Artifacts, Versioning, and Benchmarks

A research-software release is believable only when its claims are backed by
visible artifacts and a reproducible build/test/benchmark trail.
`release_audit.py` inventories the files a release normally requires and runs an
optional benchmark probe; it does not execute the project's own test suite or
publish a release.

## Required release artifacts

| Artifact | Why it matters | Common names |
|---|---|---|
| **License** | without one, no one may reuse the code | `LICENSE`, `LICENSE.txt`, `COPYING` |
| **README** | install, usage, and scope entry point | `README.md`, `README.rst` |
| **Version** | releases are identified by a unique version | `VERSION`, `pyproject.toml`, `__init__.py` |
| **Changelog** | users need to know what changed | `CHANGELOG.md`, `HISTORY.md`, `NEWS.md` |
| **Citation** | Academic software must be citable | `CITATION.cff`, `CITATION.bib` |
| **Tests** | a release should have a runnable test entry point | `pytest.ini`, `tox.ini`, `tests/` |

`release_audit.py` reports each category present/absent with the path found.
A release is `ready_for_human_review` only when license, README, and tests are
present and a version resolves. Passing the audit is necessary, not sufficient —
the content still needs human verification.

## Version resolution order

`release_audit.py --release-version` takes precedence, then the scanner checks,
in order:

1. A `VERSION` file at the repository root.
2. The `version =` line in `pyproject.toml`.
3. The `__version__ =` line in `src/__init__.py` or `__init__.py`.

If none resolve, the audit reports `release_version: null` and the release is
not ready. Pin the version explicitly (`--release-version 1.2.0`) when the
project uses a scheme the scanner does not know.

## Benchmarking a release baseline

A release that claims performance should cite a measured baseline.
`release_audit.py --benchmark <command>` runs the command in the repository root
and records:

- `wall_time_seconds`: end-to-end wall time.
- `peak_memory_kb`: peak resident memory, when the platform exposes it
  (`resource` on Unix, `/proc/self/status` VmHWM on Linux). On platforms that
  do not expose it, the field is `null` with a `memory_note`.
- `returncode`, `timed_out`, `error`: execution outcome.

Without `--benchmark`, the script runs a tiny built-in CPU probe so the report
always contains a timing data point; replace it with a real benchmark
(`python -m pytest tests/ -q`, a representative workload) for meaningful numbers.

## Release audit workflow

1. Author a quality plan with `init_quality_plan.py` and collect repository
   evidence with `collect_repository_evidence.py`.
2. Screen declared evidence with `release_readiness.py`.
3. Run `release_audit.py repo_dir --out release-audit.json` to confirm the
   on-disk artifacts and capture a benchmark baseline.
4. Resolve every `missing_required` item and benchmark `error`/`timed_out`.
5. Tag, archive (DOI), and update the changelog only after the audit is clean.

## Determinism and provenance

- Record the exact benchmark command, environment, and seed in the release notes.
- A release artifact should be built from a fixed commit; record the commit hash.
- Archive the release with a DOI (Zenodo, figshare) so the version is citable.
