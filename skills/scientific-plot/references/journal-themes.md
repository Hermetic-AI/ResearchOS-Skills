# Journal Themes — Full Parameter Tables

All themes are matplotlib rcParams dictionaries in `scripts/plot_chart.py` (`THEMES` + `PALETTES`). mm → inch: divide by 25.4. Single column 89 mm = 3.50 in; double column 183 mm = 7.20 in (set via `--column`).

## nature

| Parameter | Value |
|---|---|
| body font | 7 pt sans-serif (Arial/Helvetica family) |
| title | 8 pt, bold panel letters |
| axes.linewidth | 0.6 |
| lines.linewidth / markersize | 1.0 / 3 |
| ticks | outward, width 0.6 |
| grid | off |
| legend | frameless |
| spines | top/right hidden |
| palette | muted colorblind-safe (Okabe-Ito) |

## science

| Parameter | Value |
|---|---|
| body font | 7 pt (labels 7–9 pt allowed) |
| title | 8 pt |
| axes.linewidth | 0.7 |
| ticks | outward, no grid |
| spines | top/right hidden |
| palette | slightly brighter than nature |

## ieee

| Parameter | Value |
|---|---|
| body font | 8 pt Times/serif family |
| palette | grayscale only (0.15/0.45/0.7 gray levels) |
| series distinction | line styles (solid/dashed/dotted/dashdot) + marker shapes; bars get hatches (`//`, `\\`, `xx`) |
| grid | light y-grid allowed |
| purpose | survives black-and-white printing and photocopying; never rely on color alone |

## prism

| Parameter | Value |
|---|---|
| fonts/lines | matplotlib defaults, 8 pt base |
| palette | GraphPad-Prism-like bright default cycle |
| purpose | internal slides, lab meetings, demos — **not for submission** |

## Shared export settings (all themes)

- `pdf.fonttype=42`, `ps.fonttype=42` (TrueType embedded, editable in Illustrator)
- `svg.fonttype="none"` (text stays as text in SVG)
- PNG fallback always 300 DPI
- Figure size: `--column single` → 3.50 in wide, `--column double` → 7.20 in wide; height auto per template (golden-ish ratio)

## Pre-submission checklist

1. Figure width matches the journal's column at 100% scale — never rescale text below 7 pt.
2. Open the PDF and zoom to 400%: lines crisp (vector), no rasterized axes.
3. Fonts embedded: `pdffonts fig.pdf` shows `emb yes` for every font.
4. Colorblind check: nature/science palettes are Okabe-Ito; if custom colors were used, verify with a simulator.
5. Grayscale check for IEEE: print preview in B/W — series must be distinguishable by dash/hatch.
6. Star brackets: caption states test name, exact threshold convention, and multiple-comparison correction (see `significance.md`).
7. Panel letters (A, B, C) match the caption; axis labels carry units.
8. Keep the exact CLI + seed in the lab notebook / figure log for regeneration.
