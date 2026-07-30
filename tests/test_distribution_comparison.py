import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "skills/reproduction-assistant/scripts/compare_results.py"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def run(*args, cwd=ROOT):
    return subprocess.run(
        [sys.executable, str(ROOT / SCRIPT), *map(str, args)],
        cwd=cwd,
        env=ENV,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=True,
    )


def json_pair(paper_value, repro_runs, paper_std=None, paper_n=None, seed=42,
              bootstrap_ci=0.95, uncertainty=True, abs_tol=None, tol=0.01):
    paper = {"model": "m", "dataset": "d", "metric": "acc",
             "value": paper_value, "source": "paper"}
    if paper_std is not None:
        paper["std"] = paper_std
    if paper_n is not None:
        paper["n"] = paper_n
    repro = {"model": "m", "dataset": "d", "metric": "acc",
             "value": repro_runs, "source": "runs"}
    paper_path = ROOT / "_tp_paper.json"
    repro_path = ROOT / "_tp_repro.json"
    paper_path.write_text(json.dumps([paper]), encoding="utf-8")
    repro_path.write_text(json.dumps([repro]), encoding="utf-8")
    try:
        args = ["--paper", str(paper_path), "--repro", str(repro_path),
                "--format", "json", "--seed", str(seed),
                "--bootstrap-ci", str(bootstrap_ci)]
        if uncertainty:
            args.append("--uncertainty")
        if abs_tol is not None:
            args += ["--abs-tolerance", str(abs_tol)]
        else:
            args += ["--tolerance", str(tol)]
        out = run(*args).stdout
    finally:
        paper_path.unlink(missing_ok=True)
        repro_path.unlink(missing_ok=True)
    return json.loads(out)["rows"][0]


# 1. Bootstrap CI is deterministic with same seed, differs with different seed
def test_bootstrap_ci_deterministic_and_seed_sensitive():
    runs = [0.85, 0.91, 0.88, 0.93, 0.87, 0.92, 0.89, 0.94, 0.86, 0.90]
    a = json_pair(0.90, runs, seed=42)
    b = json_pair(0.90, runs, seed=42)
    c = json_pair(0.90, runs, seed=99)
    assert a["repro_runs"]["ci_low"] == b["repro_runs"]["ci_low"]
    assert a["repro_runs"]["ci_high"] == b["repro_runs"]["ci_high"]
    assert (c["repro_runs"]["ci_low"], c["repro_runs"]["ci_high"]) != \
           (a["repro_runs"]["ci_low"], a["repro_runs"]["ci_high"])


# 2. Bootstrap CI narrows with more runs
def test_bootstrap_ci_narrows_with_more_runs():
    narrow = [0.896, 0.897, 0.895, 0.896, 0.897, 0.895, 0.896, 0.897]
    wide = [0.85, 0.95, 0.87, 0.93, 0.88, 0.92, 0.86, 0.94]
    narrow_row = json_pair(0.90, narrow, seed=7)
    wide_row = json_pair(0.90, wide, seed=7)
    narrow_width = narrow_row["repro_runs"]["ci_high"] - narrow_row["repro_runs"]["ci_low"]
    wide_width = wide_row["repro_runs"]["ci_high"] - wide_row["repro_runs"]["ci_low"]
    assert narrow_width < wide_width, (narrow_width, wide_width)


# 3. Welch t-test: clearly different -> low p; similar -> high p
def test_welch_ttest_known_cases():
    runs_near = [0.896, 0.897, 0.895, 0.896, 0.897]     # mean ~0.8962
    runs_far = [0.70, 0.71, 0.69, 0.72, 0.68]            # mean 0.70
    near = json_pair(0.896, runs_near, paper_std=0.003, paper_n=5, seed=1)
    far = json_pair(0.896, runs_far, paper_std=0.003, paper_n=5, seed=1)
    assert near["repro_runs"]["p_value"] > 0.1
    assert far["repro_runs"]["p_value"] < 0.001
    assert near["repro_runs"]["uncertainty_verdict"] == "consistent"
    assert far["repro_runs"]["uncertainty_verdict"] == "inconsistent"


# 4. Uncertainty verdict: inside CI -> consistent; far outside -> inconsistent
def test_uncertainty_verdict_scalar_paper():
    runs = [0.896, 0.897, 0.895, 0.896, 0.897, 0.895, 0.896, 0.897]
    inside = json_pair(0.896, runs, seed=3)
    assert inside["repro_runs"]["uncertainty_verdict"] == "consistent"
    # Far outside CI with paper std+n so a t-test can fire -> inconsistent
    outside = json_pair(0.95, runs, paper_std=0.002, paper_n=5, seed=3)
    assert outside["repro_runs"]["uncertainty_verdict"] == "inconsistent"


# 5. Backward compat: without new flags, output unchanged
def test_backward_compat_no_new_flags():
    paper_path = ROOT / "_tp_paper.json"
    repro_path = ROOT / "_tp_repro.json"
    paper_path.write_text(json.dumps(
        [{"model": "m", "dataset": "d", "metric": "acc", "value": 0.9,
          "source": "paper"}]), encoding="utf-8")
    repro_path.write_text(json.dumps(
        [{"model": "m", "dataset": "d", "metric": "acc",
          "value": [0.895, 0.897, 0.893], "source": "runs"}]), encoding="utf-8")
    try:
        out = run("--paper", paper_path, "--repro", repro_path, "--format", "json").stdout
    finally:
        paper_path.unlink(missing_ok=True)
        repro_path.unlink(missing_ok=True)
    row = json.loads(out)["rows"][0]
    assert "ci_low" not in row["repro_runs"]
    assert "t_statistic" not in row["repro_runs"]
    assert "uncertainty_verdict" not in row["repro_runs"]
    assert row["verdict"] == "match"


# 6. Edge cases
def test_edge_cases():
    # Single run -> no CI, no uncertainty verdict
    single = json_pair(0.90, [0.895], seed=42)
    assert "ci_low" not in single["repro_runs"]
    assert "uncertainty_verdict" not in single["repro_runs"]

    # Empty runs -> repro value None -> missing_repro
    paper_path = ROOT / "_tp_paper.json"
    repro_path = ROOT / "_tp_repro.json"
    paper_path.write_text(json.dumps(
        [{"model": "m", "dataset": "d", "metric": "acc", "value": 0.9,
          "source": "paper"}]), encoding="utf-8")
    repro_path.write_text(json.dumps(
        [{"model": "m", "dataset": "d", "metric": "acc",
          "value": [], "source": "runs"}]), encoding="utf-8")
    try:
        out = run("--paper", paper_path, "--repro", repro_path, "--format", "json",
                  "--seed", "42", "--bootstrap-ci", "0.95", "--uncertainty").stdout
    finally:
        paper_path.unlink(missing_ok=True)
        repro_path.unlink(missing_ok=True)
    row = json.loads(out)["rows"][0]
    assert row["verdict"] == "missing_repro"
    assert row["repro_runs"] is None

    # Paper with std+n vs repro multi-run -> Welch t-test populates df, t, p
    welch = json_pair(0.896, [0.895, 0.897, 0.894, 0.898, 0.896],
                      paper_std=0.002, paper_n=6, seed=11)
    assert "t_statistic" in welch["repro_runs"]
    assert "df" in welch["repro_runs"]
    assert "p_value" in welch["repro_runs"]
    assert welch["repro_runs"]["df"] > 0


# 7. --seed required when --bootstrap-ci given
def test_seed_required_with_bootstrap_ci():
    paper_path = ROOT / "_tp_paper.json"
    repro_path = ROOT / "_tp_repro.json"
    paper_path.write_text(json.dumps(
        [{"model": "m", "dataset": "d", "metric": "acc", "value": 0.9}]),
        encoding="utf-8")
    repro_path.write_text(json.dumps(
        [{"model": "m", "dataset": "d", "metric": "acc", "value": [0.89, 0.91]}]),
        encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / SCRIPT), "--paper", str(paper_path),
             "--repro", str(repro_path), "--bootstrap-ci", "0.95"],
            cwd=ROOT, env=ENV, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
    finally:
        paper_path.unlink(missing_ok=True)
        repro_path.unlink(missing_ok=True)
    assert proc.returncode != 0
    assert "--seed" in (proc.stderr + proc.stdout)
