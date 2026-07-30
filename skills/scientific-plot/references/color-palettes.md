# Color Palettes for Publication Figures (论文配色指南)

Discrete palettes live in `scripts/palettes.json` (227 schemes, converted from the MIT-licensed
[lcpmgh/colors](https://github.com/lcpmgh/colors) collection — ggsci, grDevices, RColorBrewer, and
~180 schemes curated from top-journal figure articles). Use them via
`plot_chart.py --palette NAME`; run `--list-palettes` to browse. `--palette` overrides the theme's
default series colors but keeps the theme's typography/spines — the two choices are orthogonal.

## How to choose (decision order)

1. **How many categories?** Pick a palette with at least that many colors; extras are ignored.
   For 2–4 groups, a small curated scheme beats a 10-color one (less visual noise).
2. **Print / colorblind safety**: default choice is `Okabe-Ito` (the `nature` theme already uses it,
   minus black). Avoid red–green pairings (`Set1`, `Paired`) for lines that must be distinguished
   in grayscale — use the `ieee` theme for print-safe output instead.
3. **Journal match** (cosmetic, never required):
   - Nature-family: `npg` (Nature Publishing Group palette from ggsci)
   - Science/AAAS: `aaas`
   - Medical: `nejm`, `lancet`, `jama`, `bmj`, `frontiers`
   - CS / general: `d3` (= matplotlib default), `observable`, `Classic Tableau`, `ggplot2`
4. **Still unsure**: stay with the theme default. The defaults are chosen to be safe.

## Recommended workhorses

| Name | n | Colors (first) | Use for |
|---|---|---|---|
| `Okabe-Ito` | 9 | `#E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00` (first entry is `#000000`) | colorblind-safe default, any chart |
| `npg` | 10 | `#E64B35 #4DBBD5 #00A087 #3C5488 #F39B7F` | Nature-style multi-group bars/violins |
| `aaas` | 10 | `#3B4992 #EE0000 #008B45 #631879` | Science-style figures |
| `nejm` | 8 | `#BC3C29 #0072B5 #E18727 #20854E` | medical papers |
| `lancet` | 9 | `#00468B #ED0000 #42B540 #0099B4` | medical papers |
| `jama` | 7 | `#374E55 #DF8F44 #00A1D5 #B24745` | medical papers |
| `Set1` | 9 | `#E41A1C #377EB8 #4DAF4A #984EA3` | high-contrast categories (not colorblind-safe) |
| `Classic Tableau` | 10 | `#1F77B4 #FF7F0E #2CA02C #D62728` (= matplotlib default) | dashboards/slides |

## zhihu-* curated schemes

The 177 `zhihu-<id>` entries are 2–6 color combinations extracted from Nature/Science figure
breakdowns (sources in `docs/colors/articles/`). They are **nameless by design** — browse them with
`--list-palettes | grep zhihu` or pick by category count. Solid starting points:

- 2 colors: `zhihu-2` (`#ACD6EC #F5A889`, soft blue/orange)
- 3 colors: `zhihu-16` (`#009E73 #B02226 #F0A12C`), `zhihu-19` (`#377EB9 #4DAE48 #974F9F`)
- 4+ colors: filter `--list-palettes` output by the `n` column

## Continuous data (heatmaps)

`--palette` is for **discrete series only**. For heatmaps use `--cmap` (default `RdBu_r`, diverging,
centered at `--center 0`). Good choices: `RdBu_r` (diverging around 0), `viridis` (sequential,
colorblind-safe), `cividis` (sequential, print-safe). Do not use `jet` — it distorts magnitude
perception and is rejected by many journals.

## Schematics (Tier 2 excalidraw)

For box-and-arrow diagrams, take node fill colors from the same palette family for visual
consistency with the data figures — e.g. pastel tints of `npg`:
`#FDEBE9 #E5F4F7 #E3F3EE #E8EBF4` (light backgrounds) with `#1e1e1e` strokes.
