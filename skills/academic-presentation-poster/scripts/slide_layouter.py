#!/usr/bin/env python3
"""Generate a slide deck scaffold from a storyboard and run render checks.

Reads a ``presentation-storyboard`` artifact and emits a deck structure: a LaTeX
Beamer file or a reveal.js HTML file, chosen by ``--engine``. Alongside the deck
it runs a render-preview checklist that validates the declared aspect ratio, a
font-size hierarchy, and WCAG contrast ratios for color pairs the storyboard
declares. The script writes the deck to ``--out`` and prints a JSON layout
report to stdout.

This is a scaffold generator and a pre-flight checker. It does not render a
PDF/HTML, does not verify that embedded images or fonts exist, and does not
certify accessibility or visual quality.

Dependencies: none (Python 3.8+ standard library only).

CLI usage:
    python slide_layouter.py --storyboard storyboard.json \\
        --engine beamer --aspect 16:9 --out deck.tex

    python slide_layouter.py --storyboard storyboard.json \\
        --engine reveal --aspect 16:9 --out deck.html --min-contrast 4.5

    # Override the font hierarchy or contrast floor:
    python slide_layouter.py --storyboard storyboard.json --engine beamer \\
        --aspect 4:3 --out deck.tex --title-pt 30 --body-pt 18 --min-contrast 7.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"

# Beamer ``aspectratio`` keys for the supported deck ratios.
BEAMER_ASPECT = {
    "16:9": "169",
    "4:3": "43",
    "16:10": "1610",
    "3:2": "32",
    "1:1": "11",
}

# Default typography hierarchy (points), strictly decreasing by role.
DEFAULT_FONT_PT = {
    "title": 30,
    "subtitle": 24,
    "body": 18,
    "footnote": 12,
}

# WCAG 2.1 contrast floors: AA normal text 4.5, AAA normal text 7.0.
AA_CONTRAST = 4.5
AAA_CONTRAST = 7.0


def parse_color(value):
    """Return ``(r, g, b)`` floats in [0, 1] from ``#RRGGBB`` or ``#RGB``.

    Raises ``ValueError`` on malformed input so callers can report a finding
    instead of silently producing nonsense contrast numbers.
    """
    if not isinstance(value, str):
        raise ValueError("color must be a string")
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in text):
        raise ValueError(f"bad color '{value}', expected #RRGGBB")
    r, g, b = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
    return r / 255.0, g / 255.0, b / 255.0


def _channel_luminance(c):
    """Per-sRGB channel contribution to WCAG relative luminance."""
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(color):
    """WCAG relative luminance for an ``#RRGGBB`` color string."""
    r, g, b = parse_color(color)
    return 0.2126 * _channel_luminance(r) + 0.7152 * _channel_luminance(g) + 0.0722 * _channel_luminance(b)


def contrast_ratio(fg, bg):
    """WCAG contrast ratio between two ``#RRGGBB`` color strings (>= 1.0)."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_aspect(ratio):
    """Validate an aspect ratio like ``16:9``; return ``(w, h)`` ints or raise."""
    if not isinstance(ratio, str) or ":" not in ratio:
        raise ValueError(f"bad aspect '{ratio}', expected W:H")
    w, _, h = ratio.partition(":")
    w, h = int(w), int(h)
    if w <= 0 or h <= 0:
        raise ValueError(f"aspect components must be positive in '{ratio}'")
    return w, h


def check_fonts(font_pt, min_body_pt):
    """Validate a font-size hierarchy dict; return a list of findings.

    Rules: every role must meet the body floor, and sizes must strictly
    decrease title > subtitle > body so the visual hierarchy is legible.
    """
    findings = []
    for role, size in font_pt.items():
        if not isinstance(size, (int, float)) or size <= 0:
            findings.append({"check": "font", "role": role, "issue": "size must be a positive number"})
        elif role != "footnote" and size < min_body_pt:
            findings.append({"check": "font", "role": role, "size": size,
                             "issue": f"below minimum {min_body_pt} pt"})
    hierarchy = ["title", "subtitle", "body"]
    present = [r for r in hierarchy if r in font_pt]
    for a, b in zip(present[:-1], present[1:]):
        if font_pt[a] <= font_pt[b]:
            findings.append({"check": "font", "roles": [a, b],
                             "issue": f"{a} ({font_pt[a]} pt) must exceed {b} ({font_pt[b]} pt)"})
    return findings


def check_contrasts(color_pairs, floor):
    """Check each declared color pair against a contrast floor.

    ``color_pairs`` entries: ``{"foreground": "#..", "background": "#..",
    "context": "body"}``. Returns a list of findings; malformed colors are
    reported rather than silently skipped.
    """
    findings = []
    for idx, pair in enumerate(color_pairs or [], 1):
        fg = pair.get("foreground")
        bg = pair.get("background")
        if not fg or not bg:
            findings.append({"check": "contrast", "pair": idx,
                             "issue": "pair needs foreground and background"})
            continue
        try:
            ratio = contrast_ratio(fg, bg)
        except ValueError as exc:
            findings.append({"check": "contrast", "pair": idx, "issue": str(exc)})
            continue
        if ratio < floor:
            findings.append({"check": "contrast", "pair": idx,
                             "foreground": fg, "background": bg,
                             "ratio": round(ratio, 2), "floor": floor,
                             "issue": f"contrast {ratio:.2f} below floor {floor}"})
    return findings


def _escape_latex(text):
    """Minimal LaTeX escaping for ``& % $ # _ { }`` in user-provided strings."""
    if not isinstance(text, str):
        return str(text)
    special = {"\\": "\\textbackslash{}", "&": "\\&", "%": "\\%", "$": "\\$",
               "#": "\\#", "_": "\\_", "{": "\\{", "}": "\\}",
               "~": "\\textasciitilde{}", "^": "\\textasciicircum{}"}
    out = []
    for ch in text:
        out.append(special.get(ch, ch))
    return "".join(out)


def _slide_items(slide):
    """Pull bullet strings from a slide entry, tolerating several shapes."""
    bullets = slide.get("bullets") or slide.get("points") or slide.get("body") or []
    if isinstance(bullets, str):
        bullets = [bullets]
    return [b for b in bullets if isinstance(b, str) and b.strip()]


def generate_beamer(storyboard, ratio, font_pt):
    """Build a LaTeX Beamer scaffold from the storyboard."""
    check_aspect(ratio)  # validated earlier, kept here for standalone use
    aspect = BEAMER_ASPECT.get(ratio, "169")
    title = _escape_latex(storyboard.get("title") or "Untitled presentation")
    audience = _escape_latex(storyboard.get("audience") or "")
    takeaway = _escape_latex(storyboard.get("core_takeaway") or "")
    lines = [
        f"\\documentclass[aspectratio={aspect}]{{beamer}}",
        "\\usepackage[utf8]{inputenc}",
        "\\usepackage[T1]{fontenc}",
        f"\\title{{{title}}}",
        f"\\author{{{audience}}}" if audience else "\\author{}",
        "\\date{\\today}",
        "",
        "\\begin{document}",
        "",
        "\\begin{frame}",
        "\\titlepage",
        "\\end{frame}",
        "",
    ]
    if takeaway:
        lines += ["\\begin{frame}{Core takeaway}", takeaway, "\\end{frame}", ""]
    for section in storyboard.get("sections") or []:
        sect_title = _escape_latex(section.get("title") or "Section")
        lines += [f"\\section{{{sect_title}}}", ""]
        for slide in section.get("slides") or []:
            slide_title = _escape_latex(slide.get("title") or sect_title)
            lines += [f"\\begin{{frame}}{{{slide_title}}}", "\\begin{itemize}"]
            for bullet in _slide_items(slide):
                lines += [f"  \\item {_escape_latex(bullet)}"]
            if not _slide_items(slide):
                lines += ["  \\item "]
            lines += ["\\end{itemize}", "\\end{frame}", ""]
    if not any(section.get("slides") for section in storyboard.get("sections") or []):
        lines += ["% TODO: add slides to your sections", ""]
    lines += ["\\end{document}", ""]
    return "\n".join(lines)


def generate_reveal(storyboard, ratio, font_pt):
    """Build a reveal.js HTML scaffold from the storyboard."""
    check_aspect(ratio)
    title = (storyboard.get("title") or "Untitled presentation")
    takeaway = storyboard.get("core_takeaway") or ""
    slides = []
    if takeaway:
        slides.append(
            "    <section data-transition='slide'>\n"
            "      <h2>Core takeaway</h2>\n"
            f"      <p>{takeaway}</p>\n"
            "    </section>")
    for section in storyboard.get("sections") or []:
        sect_title = section.get("title") or "Section"
        for slide in section.get("slides") or []:
            slide_title = slide.get("title") or sect_title
            items = "".join(f"<li>{b}</li>" for b in _slide_items(slide)) or "<li></li>"
            slides.append(
                "    <section data-transition='slide'>\n"
                f"      <h2>{slide_title}</h2>\n"
                f"      <ul>{items}</ul>\n"
                "    </section>")
    slides_html = "\n".join(slides) or "    <!-- TODO: add slides to your sections -->"
    return "\n".join([
        "<!DOCTYPE html>", "<html lang='en'>", "<head>",
        "  <meta charset='utf-8'>",
        f"  <title>{title}</title>",
        "  <link rel='stylesheet' href='dist/reveal.css'>",
        "  <link rel='stylesheet' href='dist/theme/black.css' id='theme'>",
        "</head>", "<body>",
        "  <div class='reveal'>",
        "    <div class='slides'>",
        "      <section data-transition='slide'>",
        f"        <h1>{title}</h1>",
        f"        <p>{storyboard.get('audience') or ''}</p>",
        "      </section>",
        slides_html,
        "    </div>",
        "  </div>",
        "  <script src='dist/reveal.js'></script>",
        "  <script>Reveal.initialize({hash: true, slideNumber: true});</script>",
        "</html>", "",
    ])


def build_checklist(storyboard, font_findings, contrast_findings, ratio, engine):
    """Assemble a render-preview checklist (items to verify before final render)."""
    items = [
        {"id": "aspect", "category": "layout",
         "detail": f"Confirm {ratio} aspect ratio in the {engine} template"},
        {"id": "fonts", "category": "typography",
         "detail": "Verify title/subtitle/body sizes render legibly at room scale"},
        {"id": "contrast", "category": "accessibility",
         "detail": "Re-check contrast on the actual rendered background (theme palettes differ)"},
        {"id": "images", "category": "assets",
         "detail": "Embed or link every visual_inventory entry at target DPI"},
        {"id": "claims", "category": "evidence",
         "detail": "Confirm every claim in claim_evidence_ledger resolves to a source or artifact"},
        {"id": "reading-order", "category": "accessibility",
         "detail": "Validate tab/reading order matches accessibility_plan.reading_order"},
        {"id": "alt-text", "category": "accessibility",
         "detail": "Add alt text for every visual per accessibility_plan.alt_text"},
        {"id": "compile", "category": "render",
         "detail": f"Compile/run the {engine} deck and inspect the first and last slide"},
    ]
    if font_findings:
        items.append({"id": "font-findings", "category": "typography",
                      "detail": f"Resolve {len(font_findings)} font-size finding(s)"})
    if contrast_findings:
        items.append({"id": "contrast-findings", "category": "accessibility",
                      "detail": f"Resolve {len(contrast_findings)} contrast finding(s)"})
    for item in items:
        item["status"] = "pending"
    return items


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--storyboard", required=True, help="path to a presentation-storyboard JSON file")
    p.add_argument("--engine", choices=("beamer", "reveal"), default="beamer",
                   help="deck backend: beamer (LaTeX) or reveal (HTML)")
    p.add_argument("--aspect", default="16:9", help="aspect ratio W:H (default 16:9)")
    p.add_argument("--out", required=True, help="output deck file (Beamer .tex or reveal .html)")
    p.add_argument("--title-pt", type=float, default=DEFAULT_FONT_PT["title"])
    p.add_argument("--subtitle-pt", type=float, default=DEFAULT_FONT_PT["subtitle"])
    p.add_argument("--body-pt", type=float, default=DEFAULT_FONT_PT["body"])
    p.add_argument("--footnote-pt", type=float, default=DEFAULT_FONT_PT["footnote"])
    p.add_argument("--min-contrast", type=float, default=AA_CONTRAST,
                   help=f"WCAG contrast floor (default {AA_CONTRAST}, use {AAA_CONTRAST} for AAA)")
    p.add_argument("--force", action="store_true", help="replace an existing --out file")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    a = p.parse_args(argv)

    try:
        src = Path(a.storyboard).resolve(strict=True)
        out = Path(a.out).resolve()
        if out == src:
            raise ValueError("--out must differ from --storyboard")
        if out.exists() and not a.force:
            raise ValueError("output exists; use --force only for a revised deck")

        storyboard = json.loads(src.read_text(encoding="utf-8-sig"))
        if storyboard.get("artifact_type") != "presentation-storyboard":
            raise ValueError("--storyboard must be a presentation-storyboard artifact")

        check_aspect(a.aspect)
        font_pt = {"title": a.title_pt, "subtitle": a.subtitle_pt,
                   "body": a.body_pt, "footnote": a.footnote_pt}
        font_findings = check_fonts(font_pt, min_body_pt=a.body_pt)
        declared = (storyboard.get("accessibility_plan") or {}).get("color_pairs")
        contrast_findings = check_contrasts(declared, a.min_contrast)

        if a.engine == "beamer":
            deck = generate_beamer(storyboard, a.aspect, font_pt)
        else:
            deck = generate_reveal(storyboard, a.aspect, font_pt)

        checklist = build_checklist(storyboard, font_findings, contrast_findings,
                                    a.aspect, a.engine)

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(deck, encoding="utf-8")

        report = {
            "schema_version": "1.0.0",
            "artifact_type": "presentation-deck-layout",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": VERSION,
            "storyboard": str(src),
            "output": str(out),
            "engine": a.engine,
            "aspect": a.aspect,
            "font_pt": font_pt,
            "min_contrast": a.min_contrast,
            "font_findings": font_findings,
            "contrast_findings": contrast_findings,
            "checklist": checklist,
            "ready_for_human_review": not font_findings and not contrast_findings,
            "warnings": [
                "Scaffold generator only: it does not render PDF/HTML, verify embedded "
                "assets/fonts, or certify accessibility. Compile and visually inspect "
                "the deck before delivery.",
            ],
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles: force UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
