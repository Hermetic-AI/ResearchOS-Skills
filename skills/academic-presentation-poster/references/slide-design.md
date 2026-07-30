# Slide Design — Layout, Typography, and Contrast

Rules of thumb for a legible, evidence-traceable slide deck. These are heuristics
for the scaffold stage; final visual quality is confirmed by rendering and human
review.

## Aspect ratio

| Ratio | Use when |
|---|---|
| `16:9` | default for modern projectors and conference displays |
| `4:3` | legacy projectors, some institutional setups |
| `16:10` | laptop-native screens, some poster-adjacent talks |
| `1:1` | single-slide social / poster-thumbnail exports |

State the ratio up front; mixing ratios in one deck forces rescaling and breaks
font-size budgets. `slide_layouter.py` validates the ratio and selects the
matching Beamer `aspectratio` / reveal.js viewport.

## Typography hierarchy

A deck needs at least three visually distinct text roles. Keep the hierarchy
strictly decreasing so the eye can parse structure at a glance:

| Role | Beamer default (pt) | Minimum for a large room |
|---|---|---|
| Frame title | 30 | 24 |
| Subtitle / subtitle | 24 | 20 |
| Body text | 18 | 18 (hard floor) |
| Footnote / reference | 12 | 10 |

- **One typeface family**; use weight (bold/regular) and size for emphasis, not a
  second font.
- **One accent color** for emphasis; never rely on color alone to convey a claim
  (pair with position, weight, or a marker).
- `slide_layouter.py` flags any role below the body floor and any non-decreasing
  step in the title > subtitle > body chain.

## Contrast (WCAG 2.1)

Compute contrast against the *rendered* background, not the brand swatch on white.

| Level | Ratio | Applies to |
|---|---|---|
| AA (normal text) | `>= 4.5` | body, captions, references |
| AA (large text) | `>= 3.0` | titles >= 18 pt bold |
| AAA (normal text) | `>= 7.0` | recommended for dense rooms / dim projectors |

- `slide_layouter.py --min-contrast` defaults to AA (4.5); pass `7.0` for AAA.
- Theme palettes differ from the storyboard's declared colors — re-check contrast
  on the *rendered* background, because a color pair that passes on white can fail
  on a dark slide master.
- Never encode a result by color alone; add a shape, hatch, or direct label so
  the point survives grayscale projection and color-vision-deficiency viewers.

## Evidence traceability

Every quantitative claim on a slide should resolve to a source the audience can
inspect:

- Link figures to their `figure-manifest` or data artifact; never restate a
  statistic without naming its source.
- Keep a `claim_evidence_ledger` entry per slide claim; `audit_storyboard.py`
  enforces that each claim has text and a source/artifact.
- Reserve the bottom margin or a final references slide for the full locator
  (file, page, DOI) so the claim is reproducible after the talk.

## Render-preview checklist

Before delivery, confirm:

1. Aspect ratio matches the venue's display.
2. Smallest body text is legible from the back of the room.
3. All color pairs meet the intended WCAG level on the rendered background.
4. Every image is embedded at the target DPI (300 for print, 150 for screen).
5. Reading order / tab order matches the declared accessibility plan.
6. Alt text is present for every non-decorative visual.
7. The deck compiles and the first and last slides render as intended.
