import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "peer-review-and-rebuttal" / "scripts" / "review_simulator.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_template_journal_and_conference(tmp_path):
    out_j = tmp_path / "journal.json"
    result = run("--mode", "template", "--venue", "journal", "--out", str(out_j))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out_j.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "review-template"
    assert artifact["venue"] == "journal"
    ids = [s["id"] for s in artifact["template"]["sections"]]
    assert "summary" in ids and "recommendation" in ids
    assert any("does not contain actual reviewer comments" in w for w in artifact["warnings"])

    out_c = tmp_path / "conf.json"
    result = run("--mode", "template", "--venue", "conference", "--out", str(out_c))
    assert result.returncode == 0, result.stderr
    conf = json.loads(out_c.read_text(encoding="utf-8"))
    conf_ids = [s["id"] for s in conf["template"]["sections"]]
    assert "technical_correctness" in conf_ids


def test_checklist_consort_scoring(tmp_path):
    manuscript = tmp_path / "manuscript.md"
    manuscript.write_text(
        "This randomised trial reports the trial design, eligibility criteria, "
        "interventions, primary outcome, sample size calculation, randomisation, "
        "blinding, statistical methods, participant flow, recruitment dates, "
        "baseline characteristics, numbers analysed, results with odds ratio, "
        "harms, limitations, trial registration, and funding.",
        encoding="utf-8",
    )
    out = tmp_path / "checklist.json"
    result = run("--mode", "checklist", "--guideline", "consort",
                 "--manuscript", str(manuscript), "--sections", "title,methods",
                 "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "reporting-guideline-checklist"
    assert artifact["guideline"] == "CONSORT (RCTs)"
    assert 0.0 <= artifact["compliance_score"] <= 1.0
    assert artifact["items_present"] > 0
    assert artifact["items_present"] <= artifact["items_applicable"]
    assert any(f["status"] == "present" for f in artifact["findings"])
    assert any("keyword presence only" in w for w in artifact["warnings"])


def test_checklist_strobe_and_prisma(tmp_path):
    strobe_text = ("cohort study design setting eligibility criteria exposure "
                   "outcome data source bias sample size variables statistical methods "
                   "participants results sensitivity interpretation funding")
    manuscript = tmp_path / "strobe.md"
    manuscript.write_text(strobe_text, encoding="utf-8")
    out = tmp_path / "strobe.json"
    result = run("--mode", "checklist", "--guideline", "strobe",
                 "--manuscript", str(manuscript), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["guideline"] == "STROBE (observational)"
    assert artifact["compliance_score"] > 0.5

    prisma_text = ("systematic review background registered population database search "
                   "strategy screening risk of bias data extraction effect size "
                   "meta-analysis heterogeneity i2 publication bias funding")
    manuscript2 = tmp_path / "prisma.md"
    manuscript2.write_text(prisma_text, encoding="utf-8")
    out2 = tmp_path / "prisma.json"
    result = run("--mode", "checklist", "--guideline", "prisma",
                 "--manuscript", str(manuscript2), "--out", str(out2))
    assert result.returncode == 0, result.stderr
    prisma = json.loads(out2.read_text(encoding="utf-8"))
    assert prisma["guideline"] == "PRISMA (systematic reviews)"


def test_full_mode_combines_template_and_checklist(tmp_path):
    manuscript = tmp_path / "manuscript.md"
    manuscript.write_text(
        "randomised trial trial design eligibility interventions outcome sample size "
        "randomisation blinding statistical methods flow recruitment baseline analysed "
        "odds ratio harms limitations registration funding",
        encoding="utf-8",
    )
    out = tmp_path / "full.json"
    result = run("--mode", "full", "--venue", "journal", "--guideline", "consort",
                 "--manuscript", str(manuscript), "--sections", "methods", "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "review-with-checklist"
    assert "review_template" in artifact
    assert "compliance_score" in artifact
    assert artifact["venue"] == "journal"


def test_empty_manuscript_scores_zero(tmp_path):
    manuscript = tmp_path / "empty.md"
    manuscript.write_text("lorem ipsum dolor sit amet", encoding="utf-8")
    out = tmp_path / "checklist.json"
    result = run("--mode", "checklist", "--guideline", "consort",
                 "--manuscript", str(manuscript), "--out", str(out))
    assert result.returncode == 0, result.stderr
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["compliance_score"] == 0.0
    assert artifact["items_present"] == 0


def test_output_protected(tmp_path):
    out = tmp_path / "template.json"
    args = ["--mode", "template", "--venue", "preprint", "--out", str(out)]
    assert run(*args).returncode == 0
    second = run(*args)
    assert second.returncode == 1 and "--force" in second.stderr


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
