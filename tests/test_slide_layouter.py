"""Tests for academic-presentation-poster/scripts/slide_layouter.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "academic-presentation-poster" / "scripts" / "slide_layouter.py"
INIT = ROOT / "skills" / "academic-presentation-poster" / "scripts" / "init_storyboard.py"

# A realistic storyboard with two sections, slides, and declared color pairs.
STORYBOARD = {
    "schema_version": "1.0.0",
    "artifact_type": "presentation-storyboard",
    "title": "Memory in AI Agents",
    "format": "slides",
    "audience": "Specialists",
    "core_takeaway": "Structured memory improves long-horizon agent reliability.",
    "sections": [
        {
            "title": "Motivation",
            "slides": [
                {"title": "The forgetting problem",
                 "bullets": ["Agents lose context past a fixed window.",
                          "Failures compound over long tasks."]},
            ],
        },
        {
            "title": "Method",
            "slides": [
                {"title": "Memory stream",
                 "bullets": ["Append-only event log", "Retrieval via recency + relevance"]},
                {"title": "Reflexion loop", "points": ["Reflect, store, retrieve"]},
            ],
        },
    ],
    "visual_inventory": ["fig1_memory_stream.svg"],
    "claim_evidence_ledger": [
        {"claim": "context loss is the dominant failure mode", "source": "sec-evaluation"},
    ],
    "accessibility_plan": {
        "reading_order": ["title", "takeaway", "sections"],
        "contrast_review": ["body on background"],
        "alt_text": ["fig1_memory_stream.svg"],
        "color_pairs": [
            {"foreground": "#000000", "background": "#FFFFFF", "context": "body"},
            {"foreground": "#CCCCCC", "background": "#111111", "context": "body"},
        ],
    },
    "unresolved": [],
    "warnings": [],
}


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def make_storyboard(tmp_path: Path, data: dict | None = None) -> Path:
    path = tmp_path / "storyboard.json"
    path.write_text(json.dumps(data or STORYBOARD, ensure_ascii=False), encoding="utf-8")
    return path


def test_version_flag():
    result = run("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_beamer_deck_contains_sections_and_slides(tmp_path: Path):
    src = make_storyboard(tmp_path)
    out = tmp_path / "deck.tex"
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    assert result.returncode == 0, result.stderr
    tex = out.read_text(encoding="utf-8")
    assert "\\documentclass[aspectratio=169]{beamer}" in tex
    assert "Memory in AI Agents" in tex
    assert "\\section{Motivation}" in tex
    assert "\\section{Method}" in tex
    assert "\\begin{itemize}" in tex
    # The takeaway slide is emitted.
    assert "Structured memory improves" in tex


def test_reveal_deck_emits_html_slides(tmp_path: Path):
    src = make_storyboard(tmp_path)
    out = tmp_path / "deck.html"
    result = run("--storyboard", src, "--engine", "reveal", "--aspect", "4:3", "--out", out)
    assert result.returncode == 0, result.stderr
    html = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "<div class='reveal'>" in html
    assert "The forgetting problem" in html
    # reveal.js points key is honored.
    assert "Reflexion loop" in html


def test_report_carries_schema_metadata(tmp_path: Path):
    src = make_storyboard(tmp_path)
    out = tmp_path / "deck.tex"
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    report = json.loads(result.stdout)
    assert report["schema_version"] == "1.0.0"
    assert report["artifact_type"] == "presentation-deck-layout"
    assert report["tool_version"] == "0.1.0"
    assert "warnings" in report and isinstance(report["warnings"], list)
    assert "checklist" in report and report["checklist"]
    assert report["ready_for_human_review"] is True


def test_contrast_check_flags_failing_pair(tmp_path: Path):
    data = dict(STORYBOARD)
    data["accessibility_plan"] = {
        "color_pairs": [
            {"foreground": "#111111", "background": "#222222", "context": "body"},
        ],
    }
    src = make_storyboard(tmp_path, data)
    out = tmp_path / "deck.tex"
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    report = json.loads(result.stdout)
    assert report["ready_for_human_review"] is False
    assert any(f["check"] == "contrast" for f in report["contrast_findings"])


def test_aaa_contrast_floor_is_stricter(tmp_path: Path):
    data = dict(STORYBOARD)
    # 4.5:1 pair — passes AA but fails AAA.
    data["accessibility_plan"] = {
        "color_pairs": [
            {"foreground": "#767676", "background": "#FFFFFF", "context": "body"},
        ],
    }
    src = make_storyboard(tmp_path, data)
    out = tmp_path / "deck.tex"
    aa = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9",
             "--min-contrast", "4.5", "--out", out)
    aaa = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9",
              "--min-contrast", "7.0", "--out", out, "--force")
    assert json.loads(aa.stdout)["ready_for_human_review"] is True
    assert json.loads(aaa.stdout)["ready_for_human_review"] is False


def test_font_hierarchy_findings(tmp_path: Path):
    src = make_storyboard(tmp_path)
    out = tmp_path / "deck.tex"
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9",
                 "--title-pt", "20", "--subtitle-pt", "22", "--body-pt", "18", "--out", out)
    report = json.loads(result.stdout)
    # title (20) <= subtitle (22) violates the decreasing hierarchy.
    assert any("title" in f.get("roles", []) for f in report["font_findings"])
    assert report["ready_for_human_review"] is False


def test_invalid_aspect_ratio_rejected(tmp_path: Path):
    src = make_storyboard(tmp_path)
    out = tmp_path / "deck.tex"
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "5:0", "--out", out)
    assert result.returncode != 0
    assert "aspect" in result.stderr.lower()


def test_malformed_color_reported_not_crashed(tmp_path: Path):
    data = dict(STORYBOARD)
    data["accessibility_plan"] = {
        "color_pairs": [{"foreground": "not-a-color", "background": "#FFFFFF"}],
    }
    src = make_storyboard(tmp_path, data)
    out = tmp_path / "deck.tex"
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert any("bad color" in f.get("issue", "") for f in report["contrast_findings"])


def test_output_protected_then_forced(tmp_path: Path):
    src = make_storyboard(tmp_path)
    out = tmp_path / "deck.tex"
    out.write_text("keep-me", encoding="utf-8")
    protected = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    assert protected.returncode != 0
    assert out.read_text(encoding="utf-8") == "keep-me"
    forced = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", out, "--force")
    assert forced.returncode == 0
    assert out.read_text(encoding="utf-8") != "keep-me"


def test_out_must_differ_from_storyboard(tmp_path: Path):
    src = make_storyboard(tmp_path)
    result = run("--storyboard", src, "--engine", "beamer", "--aspect", "16:9", "--out", src)
    assert result.returncode != 0


def test_rejects_non_storyboard_input(tmp_path: Path):
    bad = tmp_path / "not-a-storyboard.json"
    bad.write_text(json.dumps({"artifact_type": "something-else"}), encoding="utf-8")
    out = tmp_path / "deck.tex"
    result = run("--storyboard", bad, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    assert result.returncode != 0
    assert "presentation-storyboard" in result.stderr


def test_init_then_layout_round_trip(tmp_path: Path):
    sb = tmp_path / "sb.json"
    init_result = subprocess.run(
        [sys.executable, str(INIT), "--out", sb, "--title", "Talk", "--format", "slides",
         "--audience", "General"],
        capture_output=True, text=True, encoding="utf-8", check=False)
    assert init_result.returncode == 0, init_result.stderr
    out = tmp_path / "deck.tex"
    result = run("--storyboard", sb, "--engine", "beamer", "--aspect", "16:9", "--out", out)
    assert result.returncode == 0, result.stderr
    assert "\\documentclass" in out.read_text(encoding="utf-8")
