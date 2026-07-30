---
name: academic-presentation-poster
description: Plan evidence-backed academic talks, slide decks, and posters with an auditable narrative, visual inventory, accessibility checks, and claim-to-source traceability. Use when users need a conference presentation, scientific poster, seminar storyboard, slide outline, poster critique, or presentation evidence audit.
---

# Academic Presentation and Poster

Create a narrative and layout plan before generating visual assets. Do not present preliminary, non-significant, simulated, or unverified results as confirmed findings. Every quantitative or factual claim needs an artifact, source, or explicit placeholder.

## Initialize a storyboard

```bash
python scripts/init_storyboard.py --out storyboard.json --title "Talk title" --format slides --audience "Specialists"
```

The artifact organizes messages, visual placeholders, claim sources, accessibility considerations, and unresolved decisions. It does not generate a final deck or poster.

## Audit storyboard readiness

```bash
python scripts/audit_storyboard.py --storyboard storyboard.json --out storyboard-audit.json
```

The audit requires a takeaway, claim source/artifact declarations, and accessibility-plan fields when visuals are listed. It does not render a final file or certify accessibility.

## Generate the final deck and render checks

```bash
python scripts/slide_layouter.py --storyboard storyboard.json \
    --engine beamer --aspect 16:9 --out deck.tex
```

Generates a LaTeX Beamer (or reveal.js HTML with `--engine reveal`) scaffold from the audited storyboard and runs a render-preview checklist: it validates the aspect ratio, the title > subtitle > body font hierarchy, and WCAG contrast ratios for color pairs declared in the storyboard's accessibility plan. The checklist is a pre-flight aid; it does not render PDF/HTML, verify embedded assets, or certify accessibility. Read `references/slide-design.md` when choosing aspect ratio, typography, or contrast targets.

`python scripts/audit_export_package.py --storyboard storyboard.json --export final.pdf` inventories declared final exports but never certifies rendered layout or accessibility.

## Workflow

1. Define a single audience-appropriate takeaway and the evidence required to support it.
2. Allocate one claim or question to each slide/panel; link every result figure to its `figure-manifest` or source.
3. Use `scientific-plot` for figures, then record exact artifact paths rather than recreating statistics in the presentation.
4. Check reading order, font size, contrast, color-independent encodings, captions, and alt-text plan before export.
5. Generate the deck with `slide_layouter.py` and work through its render-preview checklist.
6. Use `paper-writing-assistant` to audit citations and wording before delivery.

## Resources

- `scripts/init_storyboard.py` — protected storyboard scaffold for slides or posters.
- `scripts/slide_layouter.py` — Beamer/reveal scaffold generator with aspect, font, and contrast checks.
