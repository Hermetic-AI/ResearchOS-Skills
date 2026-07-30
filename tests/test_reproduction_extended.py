"""Extended tests for reproduction-assistant: isolation script generation,
git evidence LFS/submodule/tag alignment, and dataset download manifest.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run(script, *args, cwd=ROOT):
    return subprocess.run(
        [sys.executable, str(ROOT / script), *map(str, args)],
        cwd=cwd,
        env=ENV,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=True,
    )


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        cwd=repo,
        env=ENV,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=True,
    )


def make_repo(tmp_path, with_tag=None):
    """Create a minimal git repo, optionally with a tag."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t.io")
    git(repo, "config", "user.name", "t")
    (repo / "README.md").write_text("# repo\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "init")
    if with_tag:
        git(repo, "tag", with_tag)
    return repo


# --- 1. isolation_plan --generate-script produces a valid shell script ---
def test_isolation_plan_generate_script_venv(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_dir = tmp_path / "run-001"
    out_json = tmp_path / "plan.json"
    script = tmp_path / "run.sh"
    result = run(
        "skills/reproduction-assistant/scripts/isolation_plan.py",
        repo, "--run-dir", run_dir, "--command", "python train.py",
        "--out", out_json, "--generate-script", script,
    )
    plan = json.loads(result.stdout)
    assert script.is_file(), "script should be written"
    content = script.read_text(encoding="utf-8")
    assert "python train.py" in content
    assert "run-dir must not equal or be under repo" in content or "run-dir must not equal repo" in content
    assert "HOME=" in content
    assert plan["generated_script"] == str(script.resolve())
    assert plan["backend"] == "venv"


def test_isolation_plan_generate_script_docker(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_dir = tmp_path / "run-001"
    script = tmp_path / "run.sh"
    result = run(
        "skills/reproduction-assistant/scripts/isolation_plan.py",
        repo, "--run-dir", run_dir, "--command", "python train.py",
        "--generate-script", script, "--backend", "docker",
    )
    plan = json.loads(result.stdout)
    content = script.read_text(encoding="utf-8")
    assert "docker run" in content
    assert "--network none" in content
    assert plan["backend"] == "docker"


# --- 2. git_evidence --tag reports tag alignment correctly ---
def test_git_evidence_tag_aligned(tmp_path):
    repo = make_repo(tmp_path, with_tag="v1.0.0")
    result = run(
        "skills/reproduction-assistant/scripts/git_evidence.py",
        repo, "--tag", "v1.0.0",
    )
    payload = json.loads(result.stdout)
    assert payload["tag"] == "v1.0.0"
    assert payload["tag_aligned"] is True
    assert payload["tag_commit"] == payload["head"]


def test_git_evidence_tag_mismatch(tmp_path):
    repo = make_repo(tmp_path, with_tag="v1.0.0")
    # add another commit so HEAD moves past the tag
    (repo / "extra.md").write_text("x\n", encoding="utf-8")
    git(repo, "add", "extra.md")
    git(repo, "commit", "-q", "-m", "extra")
    result = run(
        "skills/reproduction-assistant/scripts/git_evidence.py",
        repo, "--tag", "v1.0.0",
    )
    payload = json.loads(result.stdout)
    assert payload["tag_aligned"] is False
    assert payload["tag_commit"] != payload["head"]
    assert any("not aligned" in w for w in payload["warnings"])


# --- 3. dataset_download_manifest --verify detects checksum mismatch ---
def test_dataset_detect_manifest_verify_mismatch(tmp_path):
    spec = tmp_path / "spec.json"
    data = tmp_path / "data.bin"
    data.write_bytes(b"hello")
    good = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    bad = "0" * 64
    spec.write_text(json.dumps([{
        "url": "https://example.org/data.bin",
        "expected_checksum": bad,
        "license": "MIT",
        "version": "1.0",
        "path": str(data),
    }]), encoding="utf-8")
    result = run(
        "skills/reproduction-assistant/scripts/dataset_download_manifest.py",
        spec, "--verify",
    )
    payload = json.loads(result.stdout)
    assert payload["verify"]["all_ok"] is False
    results = payload["verify"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == "mismatch"
    assert results[0]["actual"] == good


def test_dataset_detect_manifest_verify_ok(tmp_path):
    spec = tmp_path / "spec.json"
    data = tmp_path / "data.bin"
    data.write_bytes(b"hello")
    good = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    spec.write_text(json.dumps([{
        "url": "https://example.org/data.bin",
        "expected_checksum": good,
        "license": "MIT",
        "version": "1.0",
        "path": str(data),
    }]), encoding="utf-8")
    result = run(
        "skills/reproduction-assistant/scripts/dataset_download_manifest.py",
        spec, "--verify",
    )
    payload = json.loads(result.stdout)
    assert payload["verify"]["all_ok"] is True
    assert payload["verify"]["results"][0]["status"] == "ok"


# --- 4. dataset_download_manifest --export produces a script with download + verify ---
def test_dataset_detect_manifest_export(tmp_path):
    spec = tmp_path / "spec.json"
    checksum = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    spec.write_text(json.dumps([{
        "url": "https://example.org/data.bin",
        "expected_checksum": checksum,
        "license": "MIT",
        "version": "1.0",
        "path": "data.bin",
    }]), encoding="utf-8")
    export = tmp_path / "download.sh"
    result = run(
        "skills/reproduction-assistant/scripts/dataset_download_manifest.py",
        spec, "--export", export,
    )
    payload = json.loads(result.stdout)
    content = export.read_text(encoding="utf-8")
    assert content.startswith("#!/usr/bin/env sh")
    assert "https://example.org/data.bin" in content
    assert checksum in content
    assert "sha256sum" in content or "checksum" in content.lower()
    assert payload["exported_script"] == str(export.resolve())


# --- 5. Protected output (no overwrite without --force) ---
def test_isolation_plan_protected_output(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_dir = tmp_path / "run"
    out = tmp_path / "plan.json"
    out.write_text("{}", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "skills/reproduction-assistant/scripts/isolation_plan.py"),
         repo, "--run-dir", run_dir, "--command", "echo hi", "--out", out],
        cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert proc.returncode != 0
    assert "output exists" in proc.stderr


def test_dataset_manifest_protected_export(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps([]), encoding="utf-8")
    export = tmp_path / "download.sh"
    export.write_text("# placeholder\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "skills/reproduction-assistant/scripts/dataset_download_manifest.py"),
         spec, "--export", export],
        cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert proc.returncode != 0
    assert "export exists" in proc.stderr


# --- 6. Backward compat: existing flags produce unchanged output ---
def test_isolation_plan_backward_compat(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_dir = tmp_path / "run"
    result = run(
        "skills/reproduction-assistant/scripts/isolation_plan.py",
        repo, "--run-dir", run_dir, "--command", "python train.py",
    )
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0.0"
    assert payload["artifact_type"] == "isolation-plan"
    assert payload["command"] == "python train.py"
    assert payload["network"] == "none"
    assert "generated_script" not in payload
    assert "suggested_docker_command" in payload


def test_git_evidence_backward_compat(tmp_path):
    repo = make_repo(tmp_path)
    result = run(
        "skills/reproduction-assistant/scripts/git_evidence.py", repo,
    )
    payload = json.loads(result.stdout)
    assert "repository" in payload
    assert "head" in payload
    assert "exact_tag" in payload
    assert "origin" in payload
    assert "submodules" in payload
    assert "lfs_files" in payload
    assert "warnings" in payload
    # new keys must not appear without flags
    assert "tag" not in payload
    assert "submodule_details" not in payload
    assert "lfs_fetch_check" not in payload


def test_dataset_manifest_default_mode(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps([{
        "url": "https://example.org/a.csv",
        "license": "MIT", "version": "1.0",
    }]), encoding="utf-8")
    result = run(
        "skills/reproduction-assistant/scripts/dataset_download_manifest.py", spec,
    )
    payload = json.loads(result.stdout)
    assert payload["artifact_type"] == "dataset-download-manifest"
    assert payload["datasets"][0]["url"] == "https://example.org/a.csv"
    assert "verify" not in payload
    assert "exported_script" not in payload
