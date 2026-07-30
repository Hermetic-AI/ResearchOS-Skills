import json
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "literature-reader" / "scripts" / "batch_literature.py"
ENVIRONMENT = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=60,
        check=False,
    )


def validate_batch(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_artifact.py"), str(path), "--type", "literature-batch"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENVIRONMENT,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_batch_limit_resume_incremental_update_and_removed_marker(tmp_path: Path):
    source, output = tmp_path / "corpus", tmp_path / "derived"
    source.mkdir()
    output.mkdir()
    bib = source / "paper.bib"
    bib.write_text(
        "@article{Smith2024,\n title={Open Batch Processing},\n author={Smith, Jane},\n year={2024},\n doi={10.1000/batch}\n}\n",
        encoding="utf-8",
    )
    references = source / "references.txt"
    references.write_text(
        "[1] Lee, A. Incremental Literature Processing. Journal of Tests, 2025. 10.1000/incremental\n",
        encoding="utf-8",
    )
    checkpoint = output / "batch-state.json"

    first = run_cli(source, "--out-dir", output, "--limit", "1")
    assert first.returncode == 0, first.stderr
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert state["summary"]["success"] == 1
    assert state["summary"]["pending"] == 1
    validate_batch(checkpoint)

    protected = run_cli(source, "--out-dir", output)
    assert protected.returncode == 2
    assert "--force" in protected.stderr

    resumed = run_cli(source, "--out-dir", output, "--force")
    assert resumed.returncode == 0, resumed.stderr
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert state["summary"]["success"] == 1
    assert state["summary"]["unchanged"] == 1
    assert state["summary"]["pending"] == 0
    outputs = {item["relative_path"]: Path(item["output"]) for item in state["items"]}
    assert all(path.is_file() for path in outputs.values())

    unchanged = run_cli(source, "--out-dir", output, "--force")
    assert unchanged.returncode == 0, unchanged.stderr
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert state["summary"]["unchanged"] == 2

    references.write_text(
        references.read_text(encoding="utf-8") + "[2] Chen, B. A New Record for Incremental Update. Tests, 2026.\n",
        encoding="utf-8",
    )
    changed = run_cli(source, "--out-dir", output, "--force")
    assert changed.returncode == 0, changed.stderr
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    by_path = {item["relative_path"]: item for item in state["items"]}
    assert by_path["references.txt"]["status"] == "success"
    assert by_path["paper.bib"]["status"] == "unchanged"

    retained = outputs["paper.bib"]
    bib.unlink()
    removed = run_cli(source, "--out-dir", output, "--force")
    assert removed.returncode == 0, removed.stderr
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert next(item for item in state["items"] if item["relative_path"] == "paper.bib")["status"] == "removed"
    assert retained.is_file()
    validate_batch(checkpoint)


def test_failed_item_is_checkpointed_and_changed_source_retries(tmp_path: Path):
    source, output = tmp_path / "corpus", tmp_path / "derived"
    source.mkdir()
    output.mkdir()
    xml = source / "library.xml"
    xml.write_text("<xml><records><record>", encoding="utf-8")
    checkpoint = output / "batch-state.json"

    failed = run_cli(source, "--out-dir", output)
    assert failed.returncode == 1
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert state["summary"]["failed"] == 1
    assert state["items"][0]["stderr"]

    unchanged_failure = run_cli(source, "--out-dir", output, "--force")
    assert unchanged_failure.returncode == 1
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert "previous failure" in state["items"][0]["error"]

    xml.write_text(
        "<?xml version=\"1.0\"?><xml><records><record><ref-type name=\"Journal Article\">17</ref-type>"
        "<titles><title>Recovered Record</title></titles><dates><year>2025</year></dates>"
        "</record></records></xml>",
        encoding="utf-8",
    )
    recovered = run_cli(source, "--out-dir", output, "--force")
    assert recovered.returncode == 0, recovered.stderr
    state = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert state["items"][0]["status"] == "success"


def test_output_directory_must_be_outside_source_tree(tmp_path: Path):
    source = tmp_path / "corpus"
    output = source / "derived"
    source.mkdir()
    output.mkdir()
    result = run_cli(source, "--out-dir", output)
    assert result.returncode == 2
    assert "outside" in result.stderr


def test_fresh_batch_does_not_overwrite_preexisting_derived_output(tmp_path: Path):
    source, output = tmp_path / "corpus", tmp_path / "derived"
    source.mkdir()
    output.mkdir()
    item = source / "references.txt"
    item.write_text("[1] Author, A. A valid reference record for testing. Journal, 2025.\n", encoding="utf-8")
    spec = importlib.util.spec_from_file_location("researchos_batch_literature", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    derived = output / module.stable_name("references.txt", "metadata-extraction")
    sentinel = "existing derived artifact\n"
    derived.write_text(sentinel, encoding="utf-8")

    result = run_cli(source, "--out-dir", output)
    assert result.returncode == 1
    assert derived.read_text(encoding="utf-8") == sentinel
    state = json.loads((output / "batch-state.json").read_text(encoding="utf-8"))
    assert "already exists" in state["items"][0]["error"]


def test_large_file_is_checkpointed_without_hashing_or_processing(tmp_path: Path):
    source, output = tmp_path / "corpus", tmp_path / "derived"
    source.mkdir()
    output.mkdir()
    item = source / "large.txt"
    item.write_text("x" * 2048, encoding="utf-8")
    result = run_cli(source, "--out-dir", output, "--max-file-mib", "0.001")
    assert result.returncode == 0, result.stderr
    state = json.loads((output / "batch-state.json").read_text(encoding="utf-8"))
    assert state["items"][0]["status"] == "skipped-large"
    assert state["items"][0]["sha256"] is None
    validate_batch(output / "batch-state.json")
