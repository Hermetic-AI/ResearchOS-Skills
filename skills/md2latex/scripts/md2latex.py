#!/usr/bin/env python3
"""Convert Markdown to LaTeX — publication-oriented, zero-dependency.

Purpose: turn a Markdown draft (headings, lists, tables, math, figures, code,
citations) into clean, compilable LaTeX. Independently implements behavior ideas
observed in three public tools (see references/syntax-mapping.md and the root
open-source provenance audit; no upstream source code is bundled):
  - template file with `% ----- begin md -----` markers (zijunwa/md2tex)
  - booktabs tables, raw-LaTeX passthrough, \\cite support (VMIJUNV/md-to-latex)
  - configurable document class / math environment, CJK handling
    (fastpen/markdown2latex VSCode extension)

Dependencies: none (Python 3.8+ stdlib only).

CLI:
  python3 md2latex.py paper.md -o paper.tex
  python3 md2latex.py paper.md --template ctexart          # Chinese draft
  python3 md2latex.py paper.md --template IEEEtran --figure-pos htbp
  python3 md2latex.py paper.md --fragment -o body.tex      # no preamble, for \\input
  python3 md2latex.py paper.md --template-file my.tex      # markers: % ----- begin md -----

Extra Markdown conventions beyond CommonMark/GFM:
  [@doe2024]              -> \\cite{doe2024};  [@a; @b] -> \\cite{a,b}
  `\\ref{fig:x}`          -> backtick-wrapped code starting with a backslash is
                             emitted as raw LaTeX (VMIJUNV convention)
  ```latex ... ```        -> fenced latex blocks pass through verbatim
  ![alt](path "caption")  -> figure float with caption + auto \\label{fig:...}
"""

import argparse
import shutil
import subprocess
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

MATH_ENVS = {"equation": ("equation", False), "align": ("align", True),
             "displaymath": ("displaymath", False)}
CJK_RE = re.compile(r"[　-鿿豈-﫿︰-﹏]")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TASK_RE = re.compile(r"^\[([ xX])\]\s+(.*)$")
DEF_RE = re.compile(r"^(\s*):\s+(.*)$")
FENCED_DIV_OPEN_RE = re.compile(r"^:::\s+(.*)$")
# Pandoc fenced div: "{.env #label key=val}" or bare "env". Capture the first
# ".env" class as the environment name and a "#foo" id as the label.
# The brace group tolerates a missing closing "}" (malformed single-line open).
FENCED_DIV_ENV_RE = re.compile(r"\{\s*\.(\w[\w:-]*)\s*(.*?)(?:\}|$)")
FENCED_DIV_BARE_RE = re.compile(r"^(\w[\w:-]*)\b(.*)$")
DIV_LABEL_RE = re.compile(r"#(\w[\w:-]*)")
THEOREM_LIKE = {"theorem", "lemma", "proposition", "corollary", "definition",
                "remark", "example", "proof", "assumption", "conjecture"}

# ---------------------------------------------------------------- templates

BUILTIN_TEMPLATES = {
    "article": {
        "class": "article",
        "options": "11pt",
        "extra_packages": [],
    },
    "ctexart": {
        "class": "ctexart",
        "options": "11pt",
        "extra_packages": [],
        "cjk": True,
    },
    "IEEEtran": {
        "class": "IEEEtran",
        "options": "conference",
        "extra_packages": ["cite"],
        "two_col": True,
    },
}

LISTINGS_CFG = r"""\lstset{basicstyle=\ttfamily\small, breaklines=true,
  frame=single, framesep=2mm, showstringspaces=false}"""


# ---------------------------------------------------------------- utilities

def fig_path(path, ext):
    path = path.strip().replace("\\", "/")
    if ext:
        path = os.path.splitext(path)[0] + "." + ext.lstrip(".")
    return path


def slugify(text, prefix):
    s = re.sub(r"[^\w一-鿿]+", "-", text.strip().lower()).strip("-")
    return f"{prefix}:{s}" if s else prefix


UNICODE_MAP = {  # common symbols pdflatex cannot render directly
    "×": r"$\times$", "≤": r"$\leq$", "≥": r"$\geq$", "±": r"$\pm$",
    "≠": r"$\neq$", "≈": r"$\approx$", "→": r"$\to$", "←": r"$\leftarrow$",
    "↔": r"$\leftrightarrow$", "✓": r"$\checkmark$", "✗": r"$\times$",
    "·": r"$\cdot$", "−": "--", " ": " ",
}

# Keep this readable supplemental map in UTF-8 source. The older compatibility
# entries above are retained for documents created on legacy Windows consoles.
# The map below extends the base set with quotation marks, dashes, the ellipsis,
# and a domain-oriented supplement (see DOMAINS below).
UNICODE_MAP.update({
    "×": r"$\times$", "≤": r"$\leq$", "≥": r"$\geq$", "±": r"$\pm$",
    "≠": r"$\neq$", "≈": r"$\approx$", "→": r"$\to$", "←": r"$\leftarrow$",
    "↔": r"$\leftrightarrow$", "✓": r"$\checkmark$", "✗": r"$\times$",
    "·": r"$\cdot$", "–": "--", "—": "---", "…": r"\ldots{}",
    "“": "``", "”": "''", "‘": "`", "’": "'", " ": "~",
    "§": r"\S ", "¶": r"\P ",
})

# Domain-oriented supplemental Unicode -> LaTeX. These are opt-in via
# ``--unicode-domain <name>`` so a math paper does not silently pull in
# chemistry arrows, and vice versa. Each entry overrides/augments UNICODE_MAP.
UNICODE_DOMAINS = {
    "math": {
        "α": r"$\alpha$", "β": r"$\beta$", "γ": r"$\gamma$", "δ": r"$\delta$",
        "ε": r"$\epsilon$", "θ": r"$\theta$", "λ": r"$\lambda$", "μ": r"$\mu$",
        "π": r"$\pi$", "σ": r"$\sigma$", "τ": r"$\tau$", "φ": r"$\phi$",
        "ω": r"$\omega$", "Γ": r"$\Gamma$", "Δ": r"$\Delta$", "Θ": r"$\Theta$",
        "Λ": r"$\Lambda$", "Σ": r"$\Sigma$", "Φ": r"$\Phi$", "Ω": r"$\Omega$",
        "∞": r"$\infty$", "∂": r"$\partial$", "∇": r"$\nabla$", "∈": r"$\in$",
        "∉": r"$\notin$", "⊂": r"$\subset$", "⊆": r"$\subseteq$", "∪": r"$\cup$",
        "∩": r"$\cap$", "∀": r"$\forall$", "∃": r"$\exists$", "∅": r"$\emptyset$",
        "∧": r"$\land$", "∨": r"$\lor$", "¬": r"$\lnot$", "⇒": r"$\Rightarrow$",
        "⇔": r"$\Leftrightarrow$", "∑": r"$\sum$", "∏": r"$\prod$", "∫": r"$\int$",
        "≈": r"$\approx$", "≡": r"$\equiv$", "∝": r"$\propto$",
    },
    "chem": {
        "→": r"$\rightarrow$", "←": r"$\leftarrow$", "⇌": r"$\rightleftharpoons$",
        "↑": r"$\uparrow$", "↓": r"$\downarrow$", "°": r"$^{\circ}$",
        "∆": r"$\Delta$",
    },
    "text": {
        "…": r"\ldots{}", "–": "--", "—": "---",
        "“": "``", "”": "''", "‘": "`", "’": "'",
        " ": "~", "™": r"\texttrademark{}", "©": r"\copyright{}",
        "®": r"\textregistered{}", "€": r"\euro{}", "£": r"\pounds{}",
    },
}


def unicode_warnings(source):
    """Flag invisible/control and emoji-like characters left outside supported mappings."""
    warnings = []
    for ch in sorted(set(source)):
        code = ord(ch)
        if ch in UNICODE_MAP or ch in "\n\r\t":
            continue
        if 0x4E00 <= code <= 0x9FFF:  # CJK is handled through XeLaTeX/ctex.
            continue
        if code in (0x200B, 0x00AD) or code >= 0x1F000:
            warnings.append("unmapped Unicode character U+%04X requires manual review" % code)
    return warnings


def esc_text(s, unicode_map=None):
    """Escape LaTeX special characters in ordinary text. ``unicode_map``
    selects the active Unicode supplement (base + any opted-in domains)."""
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    mapping = unicode_map if unicode_map is not None else UNICODE_MAP
    for a, b in mapping.items():
        s = s.replace(a, b)
    return s


def esc_code(s):
    return esc_text(s)


# ---------------------------------------------------------------- attributes

def _parse_attrs(braces):
    """Parse a Pandoc-style ``{key=val #id .class}`` attribute block into a dict.

    Only ``key=value`` pairs are kept (classes/ids are ignored by the LaTeX
    converter — they are HTML-oriented). Returns e.g. ``{"width": "50%"}``.
    An empty/malformed group returns an empty dict."""
    if not braces:
        return {}
    inner = braces.strip("{}").strip()
    attrs = {}
    for match in re.finditer(r"(\w[\w:-]*)\s*=\s*([^\s}]+)", inner):
        attrs[match.group(1)] = match.group(2)
    return attrs


# ---------------------------------------------------------------- footnotes

FOOTNOTE_DEF_RE = re.compile(r"^\s{0,3}\[\^(\w[\w:-]*)\]:\s+(.*?)\s*$")
CROSS_REF_RE = re.compile(r"\[@(sec|fig|tab|eq|thm):(\w[\w:-]*)\]")


def extract_footnotes(lines):
    """Split input lines into (footnote_map, remaining_lines).

    A footnote definition is a (possibly up-to-3-space-indented) line
    matching ``[^id]: text``. The definition line itself is removed from the
    body; the text is stored in the map keyed by id. A blank line immediately
    before the definition is NOT consumed (it stays in the body as a normal
    blank). Consecutive definition lines for the same id are joined with a
    space (a form of continuation)."""
    fn_map = {}
    remaining = []
    for line in lines:
        m = FOOTNOTE_DEF_RE.match(line)
        if m:
            fid, text = m.group(1), m.group(2)
            fn_map[fid] = (fn_map[fid] + " " + text) if fid in fn_map else text
        else:
            remaining.append(line)
    return fn_map, remaining


# ---------------------------------------------------------------- inline

def inline(text, feat, fig_ext=None, image_path=None, footnote_map=None,
           cross_ref=False, unicode_map=None):
    """Convert inline Markdown to LaTeX. `feat` collects feature flags.
    `footnote_map`, when provided, resolves [^id] to \\footnote{...} using
    definitions collected earlier by extract_footnotes().
    `cross_ref` enables [@sec:/-@fig:/-@tab:/-@eq: -> \\ref{...}.
    `unicode_map` selects the active Unicode supplement (base + domains)."""
    slots = []

    def stash(latex):
        slots.append(latex)
        return f"{len(slots) - 1}"

    # 1. raw URLs autolink <http://...>
    text = re.sub(r"<(https?://[^>]+)>", lambda m: stash(r"\url{%s}" % m.group(1)), text)
    # 2. inline code / raw latex
    def code_sub(m):
        body = m.group(1)
        if body.startswith("\\"):  # `\cite{x}` -> raw passthrough
            return stash(body)
        return stash(r"\texttt{%s}" % esc_code(body))
    text = re.sub(r"`([^`]+)`", code_sub, text)
    # 3. inline math $...$ (not $$, not escaped \$)
    text = re.sub(r"(?<![\\$])\$([^$\n]+?)\$", lambda m: stash("$%s$" % m.group(1)), text)
    # 4. images inline (block-level handled elsewhere; inline -> includegraphics)
    def img_sub(m):
        alt, target = m.group(1), m.group(2)
        path, _, title = target.partition(" ")
        feat.add("graphics")
        rendered_path = image_path(path) if image_path else fig_path(path, fig_ext)
        return stash(r"\includegraphics[height=1em]{%s}" % rendered_path)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img_sub, text)
    # 5. links
    def link_sub(m):
        feat.add("hyperref")
        url = m.group(2).replace("%", r"\%").replace("#", r"\#")
        return stash(r"\href{%s}{%s}" % (url, esc_text(m.group(1))))
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, text)
    # 6. cross-references [@sec:label] -> \ref{sec:label} (before citations so
    # the [@kind:key] shape is claimed first). Only active under --cross-ref.
    if cross_ref:
        def cross_sub(m):
            kind, key = m.group(1), m.group(2)
            return stash(r"\ref{%s:%s}" % (kind, key))
        text = CROSS_REF_RE.sub(cross_sub, text)

    # 7. pandoc-style citations [@key; @key2]
    def cite_sub(m):
        keys = re.findall(r"@([\w:.\-/]+)", m.group(1))
        return stash(r"\cite{%s}" % ",".join(keys))
    text = re.sub(r"\[((?:@[\w:.\-/]+[; ]*)+)\]", cite_sub, text)
    # 7b. strikethrough ~~...~~ (must stash before escaping eats the tildes)
    if "~~" in text:
        feat.add("ulem")
        text = re.sub(r"~~(.+?)~~", lambda m: stash(r"\sout{%s}" % esc_text(m.group(1))), text)

    # 6c. underscore emphasis __bold__ / _italic_ (must stash before esc eats the underscores)
    text = re.sub(r"__(.+?)__", lambda m: stash(r"\textbf{%s}" % esc_text(m.group(1))), text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)",
                  lambda m: stash(r"\textit{%s}" % esc_text(m.group(1))), text)

    # 8. footnotes [^id] -> \footnote{resolved text} (stash before escaping)
    if footnote_map is not None:
        def fn_sub(m):
            fid = m.group(1)
            if fid in footnote_map:
                return stash(r"\footnote{%s}" % esc_text(footnote_map[fid]))
            return m.group(0)
        text = re.sub(r"\[\^(\w[\w:-]*)\]", fn_sub, text)

    # 7. escape what remains, then apply asterisk emphasis markers
    text = esc_text(text, unicode_map)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"\\textit{\1}", text)

    # 8. restore stashed fragments
    def restore(m):
        return slots[int(m.group(1))]
    return re.sub(r"(\d+)", restore, text)


# ---------------------------------------------------------------- blocks

class Converter:
    def __init__(self, args):
        self.args = args
        self.feat = set()
        self.fig_no = 0
        self.warnings = []
        self.footnote_map = {}
        # Build the effective Unicode map: base + any opted-in domain supplements.
        self.unicode_map = dict(UNICODE_MAP)
        for domain in args.unicode_domain or []:
            self.unicode_map.update(UNICODE_DOMAINS.get(domain, {}))

    def _parallel_dir_candidate(self, path, ext, source_dir):
        """Check for a same-stem file in a *parallel* directory.

        Projects that keep source SVG/PDF in separate folders commonly use the
        convention ``figures/svg/fig1.svg`` alongside ``figures/pdf/fig1.pdf``.
        The same-stem lookup in :meth:`image_path` only checks the SVG's own
        directory, which misses this layout.  When the SVG lives under an
        ``svg/`` (or ``svgs/``) folder we also try the sibling ``pdf/`` (or
        ``png/``) folder with the same stem."""
        head, tail = os.path.split(os.path.splitext(path)[0])
        parent, folder = os.path.split(head)
        if folder.lower() not in ("svg", "svgs"):
            return None
        candidate = os.path.join(parent, ext.lstrip("."), tail + ext)
        if os.path.isfile(os.path.normpath(os.path.join(source_dir, candidate))):
            return candidate.replace("\\", "/")
        return None

    def image_path(self, path):
        """Return a LaTeX-supported image path, preserving Markdown relativity."""
        path = path.strip().replace("\\", "/")
        # realpath normalises Windows 8.3 short names (MINGTI~1 -> MingTianbo)
        # so the isfile checks below agree with how the OS resolves the path.
        source_dir = os.path.dirname(os.path.realpath(self.args.md))

        if self.args.figure_ext:
            ext = self.args.figure_ext
            rewritten = fig_path(path, ext)
            # Same directory first (fast path).
            if os.path.isfile(os.path.normpath(os.path.join(source_dir, rewritten))):
                return rewritten
            # Parallel directory convention: figures/svg/ -> figures/pdf/.
            if os.path.splitext(path)[1].lower() == ".svg":
                parallel = self._parallel_dir_candidate(path, "." + ext.lstrip("."), source_dir)
                if parallel:
                    message = "rewrote SVG figure '%s' to existing '%s'" % (path, parallel)
                    if message not in self.warnings:
                        self.warnings.append(message)
                    return parallel
            return rewritten

        if os.path.splitext(path)[1].lower() != ".svg":
            return path

        # pdfLaTeX cannot include SVG. Prefer a vector PDF when it is next to
        # the SVG; otherwise use a same-named PNG if the project supplies one.
        stem = os.path.splitext(path)[0]
        for ext in (".pdf", ".png"):
            candidate = stem + ext
            if os.path.isfile(os.path.normpath(os.path.join(source_dir, candidate))):
                message = "rewrote SVG figure '%s' to existing '%s'" % (path, candidate)
                if message not in self.warnings:
                    self.warnings.append(message)
                return candidate

        # Fall back to the parallel-directory convention (svg/ -> pdf/|png/).
        for ext in (".pdf", ".png"):
            parallel = self._parallel_dir_candidate(path, ext, source_dir)
            if parallel:
                message = "rewrote SVG figure '%s' to existing '%s'" % (path, parallel)
                if message not in self.warnings:
                    self.warnings.append(message)
                return parallel

        message = ("SVG figure '%s' has no same-named PDF or PNG fallback; "
                   "pdfLaTeX will reject it" % path)
        if message not in self.warnings:
            self.warnings.append(message)
        return path

    def use(self, name):
        self.feat.add(name)

    # ---- individual block emitters
    def heading(self, level, text):
        cmds = ["section", "subsection", "subsubsection", "paragraph",
                "subparagraph", "subparagraph"]
        cmd = cmds[min(level, 6) - 1]
        label = slugify(text, "sec") if self.args.cross_ref else None
        line = r"\%s{%s}" % (cmd, inline(text, self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map))
        if label:
            line += r"\label{%s}" % label
        return [line, ""]

    def figure(self, alt, target, attributes=None):
        self.fig_no += 1
        path, _, title = target.partition(" ")
        title = title.strip().strip('"')
        caption = title or alt
        label = slugify(alt or caption or f"fig{self.fig_no}", "fig")
        pos = self.args.figure_pos
        self.use("graphics")
        options = self._include_graphics_options(attributes)
        lines = [r"\begin{figure}[%s]" % pos, r"  \centering",
                 r"  \includegraphics[%s]{%s}" % (options, self.image_path(path))]
        if caption:
            lines.append(r"  \caption{%s}" % inline(caption, self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map))
        lines += [r"  \label{%s}" % label, r"\end{figure}", ""]
        return lines

    @staticmethod
    def _include_graphics_options(attributes):
        r"""Build a graphicx key=value option string from a parsed attributes dict.

        Unknown keys are passed through; values are not validated (the user is
        responsible for graphicx-compatible content). With no attributes the
        default ``width=0.8\linewidth`` is preserved."""
        default = "width=0.8" + "\\linewidth"
        if not attributes:
            return default
        parts = []
        for key, value in attributes.items():
            if value in (None, ""):
                parts.append(key)
            else:
                parts.append("%s=%s" % (key, value))
        return ", ".join(parts) if parts else default

    def table(self, rows):
        # rows: list of list-of-cell strings; rows[1] is the alignment separator
        header, sep, body = rows[0], rows[1], rows[2:]
        aligns = []
        for cell in sep:
            c = cell.strip()
            left, right = c.startswith(":"), c.endswith(":")
            aligns.append("c" if left and right else ("l" if left else ("r" if right else "l")))
        n = len(header)
        aligns = (aligns + ["l"] * n)[:n]
        self.use("booktabs")
        if self.args.long_table:
            return self._longtable(aligns, header, body, n)
        return self._float_table(aligns, header, body, n)

    def _float_table(self, aligns, header, body, n):
        self.use("tabularx")
        tpl = BUILTIN_TEMPLATES[self.args.template]
        max_row_chars = max(sum(len(cell) for cell in row[:n]) for row in [header] + body)
        wide = bool(tpl.get("two_col") and (n >= 4 or max_row_chars > 55))
        table_env = "table*" if wide else "table"
        table_width = r"\textwidth" if wide else r"\linewidth"
        pos = self.args.table_pos
        if wide and pos == "H":
            pos = "t"
        col_types = {
            "l": r">{\raggedright\arraybackslash}X",
            "c": r">{\centering\arraybackslash}X",
            "r": r">{\raggedleft\arraybackslash}X",
        }
        column_spec = "".join(col_types[a] for a in aligns)
        out = [r"\begin{%s}[%s]" % (table_env, pos), r"  \centering",
               r"  \begin{tabularx}{%s}{%s}" % (table_width, column_spec), r"    \toprule"]
        out.append("    " + " & ".join(self._table_cell(c) for c in header) + r" \\")
        out.append(r"    \midrule")
        for r in body:
            cells = (r + [""] * n)[:n]
            out.append("    " + " & ".join(self._table_cell(c) for c in cells) + r" \\")
        out += [r"    \bottomrule", r"  \end{tabularx}", r"\end{%s}" % table_env, ""]
        return out

    def _longtable(self, aligns, header, body, n):
        """Page-breaking longtable (no float). Pulls in the longtable package."""
        self.use("longtable")
        column_spec = "".join(aligns)
        out = [r"\begin{longtable}[c]{%s}" % column_spec, r"  \toprule"]
        out.append("  " + " & ".join(self._table_cell(c) for c in header) + r" \\")
        out.append(r"  \midrule\endfirsthead")
        out.append(r"  \toprule")
        out.append("  " + " & ".join(self._table_cell(c) for c in header) + r" \\")
        out.append(r"  \midrule\endhead")
        out.append(r"  \bottomrule\endfoot")
        for r in body:
            cells = (r + [""] * n)[:n]
            out.append("  " + " & ".join(self._table_cell(c) for c in cells) + r" \\")
        out += [r"  \bottomrule", r"\end{longtable}", ""]
        return out

    def _table_cell(self, raw):
        """Render a single table cell. Supports explicit LaTeX merge commands
        (``\\multicolumn`` / ``\\multirow``) written in the cell, which are
        passed through unescaped so authors can build complex layouts."""
        cell = raw.strip()
        if cell.startswith("\\multicolumn") or cell.startswith("\\multirow"):
            self.use("multirow")
            return cell
        return inline(cell, self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map)

    def fenced_env(self, env, body_lines, label=None):
        """Recursively convert the body of a fenced div into a LaTeX environment.

        Theorem-like environments pull in amsthm; the body is converted by a
        nested Converter so block constructs inside the div work correctly."""
        if env in THEOREM_LIKE:
            self.use("amsthm")
        elif env == "algorithm":
            self.use("algorithm")
            self.use("algpseudocode")
        inner = Converter(self.args)
        inner.footnote_map = {}
        inner_lines = inner.convert(body_lines)
        self.feat |= inner.feat
        self.warnings.extend(w for w in inner.warnings if w not in self.warnings)
        head = r"\begin{%s}" % env
        if label is not None:
            head += r"\label{%s}" % label
        return [head] + inner_lines + [r"\end{%s}" % env, ""]

    def code_block(self, lang, code_lines):
        self.use("listings")
        opt = f"[language={lang}]" if lang else ""
        return [r"\begin{lstlisting}%s" % opt] + code_lines + [r"\end{lstlisting}", ""]

    def math_block(self, math_lines):
        env, _ = MATH_ENVS[self.args.math_env]
        return [r"\begin{%s}" % env] + math_lines + [r"\end{%s}" % env, ""]

    def convert(self, lines):
        self.footnote_map, lines = extract_footnotes(lines)
        out, i = [], 0
        para = []

        def flush_para():
            if para:
                out.append(inline(" ".join(para), self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map))
                out.append("")
                para.clear()

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # fenced code / latex
            m = re.match(r"^```(\w*)\s*$", stripped)
            if m:
                flush_para()
                lang = m.group(1)
                body = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    body.append(lines[i])
                    i += 1
                i += 1  # closing fence
                if lang == "latex":
                    out += body + [""]
                else:
                    out += self.code_block(lang, body)
                continue

            # display math $$ ... $$
            if stripped == "$$" or (stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4):
                flush_para()
                if stripped != "$$":
                    out += self.math_block([stripped.strip("$")])
                    i += 1
                    continue
                body = []
                i += 1
                while i < len(lines) and lines[i].strip() != "$$":
                    body.append(lines[i])
                    i += 1
                i += 1
                out += self.math_block(body)
                continue

            # heading
            m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if m:
                flush_para()
                out += self.heading(len(m.group(1)), m.group(2))
                i += 1
                continue

            # horizontal rule
            if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
                flush_para()
                out += [r"\bigskip\hrule\bigskip", ""]
                i += 1
                continue

            # table block
            if stripped.startswith("|") and i + 1 < len(lines) \
                    and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
                flush_para()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                    i += 1
                if len(rows) >= 2:
                    out += self.table(rows)
                continue

            # standalone image -> figure float. Supports Pandoc-style attributes
            # in a trailing brace group: ![alt](url){width=50% height=3cm}
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?\s*$", stripped)
            if m:
                flush_para()
                attributes = _parse_attrs(m.group(3)) if m.group(3) else None
                out += self.figure(m.group(1), m.group(2), attributes)
                i += 1
                continue

            # <img src="..."> html
            m = re.match(r'^<img\s+[^>]*src="([^"]+)"[^>]*>', stripped, re.I)
            if m:
                flush_para()
                alt_m = re.search(r'alt="([^"]*)"', stripped)
                out += self.figure(alt_m.group(1) if alt_m else "", m.group(1))
                i += 1
                continue

            # blockquote
            if stripped.startswith(">"):
                flush_para()
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(lines[i].strip().lstrip(">").strip())
                    i += 1
                out += [r"\begin{quote}", inline(" ".join(quote), self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map),
                        r"\end{quote}", ""]
                continue

            # lists (with indentation nesting)
            m = LIST_RE.match(line)
            if m:
                flush_para()
                stack = []  # list of (indent, env)
                while i < len(lines):
                    lm = LIST_RE.match(lines[i])
                    if not lm:
                        if lines[i].strip() == "":
                            i += 1
                            break
                        break
                    indent = len(lm.group(1).replace("\t", "    "))
                    marker, content = lm.group(2), lm.group(3)
                    env = "enumerate" if marker[0].isdigit() else "itemize"
                    while stack and indent < stack[-1][0]:
                        out.append(r"\end{%s}" % stack.pop()[1])
                    if not stack or indent > stack[-1][0]:
                        stack.append((indent, env))
                        out.append(r"\begin{%s}" % env)
                    elif env != stack[-1][1]:
                        out.append(r"\end{%s}" % stack.pop()[1])
                        stack.append((indent, env))
                        out.append(r"\begin{%s}" % env)
                    tm = TASK_RE.match(content)
                    if tm:
                        self.use("amssymb")
                        box = r"$\boxtimes$" if tm.group(1).lower() == "x" else r"$\square$"
                        out.append(r"  \item %s %s" % (box, inline(tm.group(2), self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map)))
                    else:
                        out.append(r"  \item %s" % inline(content, self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map))
                    i += 1
                while stack:
                    out.append(r"\end{%s}" % stack.pop()[1])
                out.append("")
                continue

            # fenced div -> LaTeX environment (theorem/proof/algorithm/custom)
            m = FENCED_DIV_OPEN_RE.match(stripped)
            if m and stripped != ":::":
                flush_para()
                rest = (m.group(1) or "").strip()
                env, tail = None, rest
                bracket = FENCED_DIV_ENV_RE.search(rest)
                if bracket:
                    env = bracket.group(1)
                    tail = (bracket.group(2) or "").strip()
                else:
                    bare = FENCED_DIV_BARE_RE.match(rest)
                    if bare:
                        env = bare.group(1)
                        tail = (bare.group(2) or "").strip()
                if not env:
                    env = "div"
                label_match = DIV_LABEL_RE.search(tail)
                label = label_match.group(1) if label_match else None
                body = []
                i += 1
                while i < len(lines) and lines[i].strip() != ":::":
                    body.append(lines[i])
                    i += 1
                i += 1  # closing :::  (tolerates missing closer by ending at EOF)
                out += self.fenced_env(env, body, label)
                continue

            # definition list: "term\n: definition" (PHP Markdown Extra style)
            m = DEF_RE.match(line)
            if m and para:
                term = " ".join(para)
                para.clear()
                flush_para()  # keeps spacing consistent; term already captured
                defn = [m.group(2)]
                i += 1
                while i < len(lines):
                    dm = DEF_RE.match(lines[i])
                    if dm:
                        defn.append(dm.group(2))
                        i += 1
                        continue
                    # a blank line ends the definition (but peek: a new term
                    # followed by ": " continues the list)
                    if lines[i].strip() == "":
                        if i + 1 < len(lines) and DEF_RE.match(lines[i + 1]):
                            i += 1
                            continue
                        break
                    break
                self.use("description")
                out += [r"\begin{description}",
                        r"  \item[%s] %s" % (
                            inline(term, self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map),
                            inline(" ".join(defn), self.feat, self.args.figure_ext, self.image_path, self.footnote_map, self.args.cross_ref, self.unicode_map)),
                        r"\end{description}", ""]
                continue

            # raw LaTeX line (e.g. \newpage, \bibliography{...})
            if stripped.startswith("\\"):
                flush_para()
                out.append(stripped)
                i += 1
                continue

            # blank / paragraph text
            if stripped == "":
                flush_para()
            else:
                para.append(stripped)
            i += 1

        flush_para()
        return out


# ---------------------------------------------------------------- document

def build_preamble(args, feat, cjk):
    tpl = BUILTIN_TEMPLATES[args.template]
    # fixed packages, plus feature-gated ones (graphicx/booktabs/listings/hyperref)
    packages = ["amsmath", "amssymb", "float", "xcolor"]
    for pkg in ["graphicx", "booktabs", "tabularx", "listings", "hyperref"]:
        if (pkg if pkg != "graphicx" else "graphics") in feat:
            packages.append(pkg)
    if "amsthm" in feat:
        packages.append("amsthm")
    if "algorithm" in feat:
        packages += ["algorithm", "algpseudocode"]
    if "longtable" in feat:
        packages.append("longtable")
    if "multirow" in feat:
        packages.append("multirow")
    if "ulem" in feat:
        packages.append("ulem")
    packages += [p for p in tpl["extra_packages"] if p not in packages]
    if cjk and not tpl.get("cjk"):
        packages.append("xeCJK")
    lines = [r"\documentclass[%s]{%s}" % (tpl["options"], tpl["class"]), ""]
    lines += [r"\usepackage{%s}" % p for p in packages if p != "ulem"]
    if "ulem" in packages:
        lines.append(r"\usepackage[normalem]{ulem}  % keep \emph italic under \sout")
    lines.append("")
    if "listings" in feat:
        lines += [LISTINGS_CFG, ""]
    lines += [r"\begin{document}", ""]
    return lines


def apply_template_file(path, body):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    begin = re.search(r"%\s*-+\s*begin md\s*-+", text)
    end = re.search(r"%\s*-+\s*end md\s*-+", text)
    if not begin or not end:
        sys.exit("template file must contain '% ----- begin md -----' and "
                 "'% ----- end md -----' markers")
    return text[:begin.end()] + "\n\n" + body + "\n\n" + text[end.start():]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.add_argument("md", help="input Markdown file")
    p.add_argument("-o", "--out", help="output .tex (default: <md>.tex)")
    p.add_argument("--force", action="store_true", help="replace an existing output .tex file")
    p.add_argument("--template", choices=list(BUILTIN_TEMPLATES), default="article",
                   help="built-in document template (default: article)")
    p.add_argument("--template-file", help="custom .tex template with begin/end md markers")
    p.add_argument("--fragment", action="store_true",
                   help="emit body only, no preamble (for \\input into another document)")
    p.add_argument("--bibliography", help="explicit .bib file to reference with \\bibliography; unavailable with --fragment or --template-file")
    p.add_argument("--bib-style", default="plain", help="BibTeX style name used with --bibliography (default: plain)")
    p.add_argument("--math-env", choices=list(MATH_ENVS), default="equation",
                   help="environment for $$ display math")
    p.add_argument("--figure-pos", default="H", help="figure float specifier (default: H)")
    p.add_argument("--figure-ext", metavar="EXT",
                   help="rewrite image file extensions (e.g. 'pdf': LaTeX cannot embed .svg; "
                        "point them at a same-named .pdf/.png you exported separately)")
    p.add_argument("--table-pos", default="H", help="table float specifier (default: H)")
    p.add_argument("--long-table", action="store_true",
                   help="use longtable (page-breaking) instead of table/tabularx for every table")
    p.add_argument("--cross-ref", action="store_true",
                   help="emit \\label on headings/figures/tables and resolve [@sec:/-@fig:/-@tab:/-@eq: to \\ref")
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--compile", action="store_true", help="explicitly compile the generated TeX once for validation; default is conversion only")
    p.add_argument("--unicode-domain", action="append", choices=list(UNICODE_DOMAINS),
                   help="opt-in Unicode supplement: 'math' (Greek/logic/set), 'chem' (reaction arrows), 'text' (smart quotes/currency). Repeatable.")
    p.add_argument("--strict", action="store_true", help="refuse to write TeX when conversion emits warnings requiring manual review")
    args = p.parse_args()
    if args.bibliography and (args.fragment or args.template_file):
        p.error("--bibliography is only supported with a built-in full-document template")
    if args.bibliography and not os.path.isfile(args.bibliography):
        p.error("--bibliography must name an existing .bib file")

    with open(args.md, encoding=args.encoding) as f:
        src = f.read()
    # strip YAML frontmatter
    src = re.sub(r"\A---\n.*?\n---\n", "", src, flags=re.S)

    conv = Converter(args)
    body_lines = conv.convert(src.splitlines())
    conv.warnings.extend(w for w in unicode_warnings(src) if w not in conv.warnings)
    body = "\n".join(body_lines).strip() + "\n"

    cjk = bool(CJK_RE.search(src))
    if args.template_file:
        result = apply_template_file(args.template_file, body)
    elif args.fragment:
        result = body
    else:
        pre = build_preamble(args, conv.feat, cjk)
        bibliography = ""
        if args.bibliography:
            bib_name = os.path.splitext(os.path.basename(args.bibliography))[0]
            bibliography = f"\n\\bibliographystyle{{{args.bib_style}}}\n\\bibliography{{{bib_name}}}\n"
        result = "\n".join(pre) + body + bibliography + "\n\\end{document}\n"

    out_path = args.out or os.path.splitext(args.md)[0] + ".tex"
    if args.strict and conv.warnings:
        sys.exit("strict conversion refused due to warnings: " + "; ".join(conv.warnings))
    protected = {os.path.abspath(args.md)}
    if args.template_file:
        protected.add(os.path.abspath(args.template_file))
    if os.path.abspath(out_path) in protected:
        sys.exit("output .tex must not replace the Markdown or template input")
    if os.path.exists(out_path) and not args.force:
        sys.exit(f"output exists: {out_path}; use --force to replace it")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)

    report = {"input": args.md, "output": out_path,
              "template": None if args.template_file else args.template,
              "template_file": args.template_file,
              "fragment": args.fragment, "bibliography": args.bibliography,
              "bib_style": args.bib_style if args.bibliography else None, "cjk_detected": cjk,
              "features": sorted(conv.feat), "warnings": conv.warnings}
    if args.compile:
        compiler = "xelatex" if cjk or args.template == "ctexart" else "pdflatex"
        executable = shutil.which(compiler)
        if not executable:
            report["compile"] = {"requested": True, "compiler": compiler, "status": "unavailable"}
        else:
            run = subprocess.run([executable, "-interaction=nonstopmode", "-no-shell-escape", os.path.basename(out_path)], cwd=os.path.dirname(os.path.abspath(out_path)) or ".", capture_output=True, text=True, encoding="utf-8", errors="replace")
            report["compile"] = {"requested": True, "compiler": compiler, "status": "passed" if run.returncode == 0 else "failed", "returncode": run.returncode, "log_tail": run.stdout[-2000:]}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if cjk and not BUILTIN_TEMPLATES[args.template].get("cjk") and not args.fragment:
        if args.template_file:
            print("note: CJK characters detected — confirm the template includes CJK support and compile with XeLaTeX",
                  file=sys.stderr)
        else:
            print("note: CJK characters detected — compile with XeLaTeX (xeCJK added), "
                  "or use --template ctexart", file=sys.stderr)


if __name__ == "__main__":
    main()
