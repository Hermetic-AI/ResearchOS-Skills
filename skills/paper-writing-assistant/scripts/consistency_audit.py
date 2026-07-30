#!/usr/bin/env python3
"""Screen Markdown/LaTeX manuscripts for abbreviation, figure/table-reference, and (optionally) symbol/notation consistency."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

VERSION = "0.1.0"
ABBREV = re.compile(r"\b[A-Z][A-Z0-9]{1,9}\b")

# LaTeX builtins / kernel commands that must never be flagged as undefined user
# symbols. Conservative but covers base LaTeX, AMS math, and common document
# structure. Unknown package macros may still be flagged — the warnings field
# tells the user this is a heuristic screen, not a proof.
LATEX_BUILTINS = frozenset({
    # cross-ref & structure
    "cite", "citep", "citet", "citeauthor", "citeyear", "citeyearpar", "nocite",
    "ref", "eqref", "autoref", "cref", "Cref", "nameref", "pageref", "label",
    "tag", "bibitem",
    # environments
    "begin", "end",
    # math operators & constructors
    "frac", "dfrac", "tfrac", "cfrac", "binom", "dbinom", "tbinom", "genfrac",
    "sqrt", "root", "sideset", "substack",
    "sum", "prod", "int", "oint", "iint", "iiint", "iiiint", "idotsint",
    "bigcup", "bigcap", "bigoplus", "bigotimes", "bigodot", "biguplus",
    "bigvee", "bigwedge", "coprod",
    "lim", "liminf", "limsup", "inf", "sup", "max", "min",
    "gcd", "det", "dim", "hom", "ker", "Pr",
    "exp", "log", "ln", "lg", "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
    "arg", "deg", "mod", "bmod", "pmod",
    # greek
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi",
    "pi", "varpi", "rho", "varrho", "sigma", "varsigma", "tau", "upsilon",
    "phi", "varphi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon",
    "Phi", "Psi", "Omega",
    "digamma", "varkappa", "beth", "daleth", "gimel", "Bbbk", "Finv", "Game",
    # math accents / fonts
    "mathbf", "mathrm", "mathit", "mathtt", "mathsf", "mathcal", "mathfrak",
    "mathbb", "mathscr", "bm", "boldsymbol", "pmb", "mathnormal",
    "vec", "dot", "ddot", "dddot", "ddddot", "hat", "check", "breve",
    "acute", "grave", "tilde", "bar", "overline", "underline",
    "overbrace", "underbrace", "overleftarrow", "overrightarrow",
    "underleftarrow", "underrightarrow", "xleftarrow", "xrightarrow",
    "widehat", "widetilde", "wideoverbar",
    "not", "cancel", "bcancel", "xcancel",
    # math spacing / delimiters
    "left", "right", "middle",
    "big", "Big", "bigg", "Bigg",
    "bigl", "Bigl", "biggl", "Biggl", "bigr", "Bigr", "biggr", "Biggr",
    "bigm", "Bigm", "biggm", "Biggm",
    "langle", "rangle", "lceil", "rceil", "lfloor", "rfloor",
    "vert", "Vert", "lvert", "rvert", "lVert", "rVert",
    "lbrace", "rbrace", "lbrack", "rbrack",
    "infty", "partial", "nabla", "triangle", "square", "Box", "Diamond",
    "varnothing", "emptyset", "aleph", "hbar", "ell", "wp", "Re", "Im",
    "prime", "surd", "top", "bot", "angle",
    "forall", "exists", "nexists", "in", "notin", "ni",
    "subset", "supset", "subseteq", "supseteq", "subsetneq", "supsetneq",
    "cap", "cup", "setminus", "smallsetminus",
    "land", "lor", "lnot", "neg", "implies", "iff", "Leftrightarrow",
    "to", "rightarrow", "leftarrow", "Rightarrow", "Leftarrow",
    "mapsto", "leftrightarrow", "uparrow", "downarrow", "updownarrow",
    "sim", "simeq", "approx", "cong", "equiv", "propto", "asymp",
    "neq", "ne", "le", "ge", "leq", "geq", "ll", "gg",
    "prec", "succ", "preceq", "succeq",
    "pm", "mp", "times", "div", "ast", "star", "cdot", "cdots", "ldots",
    "vdots", "ddots", "dots", "dotsc", "dotsb", "dotsm", "dotso",
    "circ", "bullet", "oplus", "ominus", "otimes", "oslash", "odot",
    "wedge", "vee",
    "perp", "parallel", "mid", "smile", "frown",
    "models", "vdash", "dashv",
    "quad", "qquad",
    "hspace", "vspace", "hfill", "vfill", "dotfill", "hrulefill",
    "smash", "phantom", "vphantom", "hphantom",
    "mathstrut", "strut",
    "displaystyle", "textstyle", "scriptstyle", "scriptscriptstyle",
    "mathord", "mathop", "mathbin", "mathrel", "mathopen", "mathclose",
    "mathpunct", "mathinner", "mathchoice",
    "operatorname", "operatornamewithlimits", "operatorname*",
    "DeclareMathOperator",
    "text", "intertext", "mbox", "hbox", "vbox",
    "notag", "numberwithin",
    # document structure
    "documentclass", "usepackage", "RequirePackage", "LoadClass",
    "input", "include", "includeonly",
    "newcommand", "renewcommand", "providecommand",
    "def", "edef", "gdef", "xdef",
    "newenvironment", "renewenvironment",
    "newlength", "setlength", "addtolength",
    "newcounter", "setcounter", "addtocounter", "value",
    "newtheorem", "theoremstyle",
    "newfont", "DeclareMathSymbol", "DeclareMathDelimiter",
    "DeclareMathAccent", "DeclareMathRadical",
    "DeclareRobustCommand", "CheckCommand",
    "ProvidesPackage", "ProvidesClass", "ProvidesFile",
    "AtBeginDocument", "AtEndDocument",
    "makeatletter", "makeatother",
    "ignorespaces", "obeyspaces", "frenchspacing", "nonfrenchspacing",
    "normalfont", "rmfamily", "sffamily", "ttfamily",
    "upshape", "itshape", "slshape", "scshape",
    "mdseries", "bfseries",
    "fontsize", "selectfont", "usefont",
    "fontencoding", "fontfamily", "fontseries", "fontshape",
    "centering", "raggedright", "raggedleft",
    "caption", "footnote", "marginpar",
    "item", "hline", "cline", "multicolumn", "multirow",
    "rule", "raisebox", "makebox", "framebox",
    "par", "noindent", "indent",
    "newpage", "clearpage", "pagebreak", "nopagebreak",
    "linebreak", "nolinebreak",
    "bibliography", "bibliographystyle", "addbibresource",
    "printbibliography",
    "title", "author", "date", "maketitle", "thanks",
    "chapter", "section", "subsection", "subsubsection",
    "paragraph", "subparagraph",
    "appendix", "tableofcontents", "listoffigures", "listoftables",
    "abstract", "keywords",
    "emph", "textbf", "textit", "texttt", "textrm", "textsl", "textsc",
    "textsf", "textmd", "textup", "textsuperscript",
    "uppercase", "lowercase",
    "newsavebox", "sbox", "savebox", "usebox",
    "settowidth", "settoheight", "settodepth",
    "textwidth", "textheight", "linewidth", "columnwidth",
    "thispagestyle", "pagestyle",
    "geometry", "hyphenation",
    "definecolor", "color", "textcolor", "colorbox", "fcolorbox",
    "includegraphics", "scalebox", "resizebox", "rotatebox",
    "url", "href",
    "DeclareOption", "ExecuteOptions", "ProcessOptions",
    "PassOptionsToPackage", "PassOptionsToClass",
    "LoadClassWithOptions",
    "IfFileExists", "InputIfFileExists",
    "listfiles", "nofiles",
    "documentstyle",
    "typeout", "typein", "message", "wlog",
    "PackageWarning", "PackageWarningNoLine", "PackageError",
    "ClassWarning", "ClassWarningNoLine", "ClassError",
    "GenericInfo", "GenericWarning", "GenericError",
    "thebibliography",
    "define@key", "setkeys",
    "ProcessKeyvalOptions", "SetupKeyvalOptions",
    "DeclareBoolOption", "DeclareStringOption", "DeclareVoidOption",
    "DeclareDefaultOption", "DeclareOptionX", "ExecuteOptionsX", "ProcessOptionsX",
    "CurrentOption", "CurrentOptionValue",
    "bibnamedelimi", "bibnamedash", "multicitedelim", "compcitedelim",
    "multiciterelim", "compciterelim", "nameyeardelim", "nametitledelim",
    "andothersdelim", "finalandcomma",
    "newblock",
    "newbibmacro", "renewbibmacro", "providebibmacro",
    "DeclareCiteCommand", "DeclareBibliographyDriver",
    "defbibenvironment", "defbibheading", "defbibnote", "defbibfilter",
    "DeclareSourcemap", "DeclareStyleSourcemap",
    "DeclareDelimFormat", "DeclareFieldFormat", "DeclareListFormat",
    "DeclareNameFormat", "DeclareNameAlias", "DeclareFieldAlias", "DeclareListAlias",
    "DeclareDatamodelEntrytypes", "DeclareDatamodelFields",
    "DeclareDatamodelEntryfields", "DeclareDatamodelConstraints",
    "volcite", "pvolcite", "fvolcite", "notecite", "pnotecite",
    "fullcite", "footcite", "footcitetext", "smartcite",
    "textcite", "parencite", "autocite", "Autocite",
    "citealias", "citepalias", "citetalias",
    "parencites", "textcites", "autocites", "smartcites", "footcites",
    "citetitle", "citedate",
    "setcitestyle",
    "sortitem", "listitem",
    "natexlab",
    "subcaption",
    "hspace*", "vspace*",
    "smallskip", "medskip", "bigskip",
    "caption*",
    "labelitemi", "labelitemii", "labelitemiii", "labelitemiv",
    "arabic", "roman", "Roman", "alph", "Alph", "fnsymbol",
    "usecounter",
    "thesection", "thesubsection", "thesubsubsection", "theparagraph",
    "theequation", "thefigure", "thetable",
    "today",
    "unlhd", "unrhd", "lhd", "rhd", "leadsto",
    "bigcirc", "diamond",
    "between", "bowtie", "Join",
    "sqsubset", "sqsupset", "sqsubseteq", "sqsupseteq",
    "complement", "eth", "hslash", "mho",
    "backprime", "blacktriangle", "blacktriangledown",
    "triangledown", "measuredangle", "sphericalangle",
    "vartriangle", "blacklozenge", "circledS", "bigstar",
    "lozenge",
    "eqslantgtr", "eqslantless", "lesssim", "gtrsim",
    "lessgtr", "gtrless", "preccurlyeq", "succcurlyeq",
    "curlyeqprec", "curlyeqsucc", "precsim", "succsim",
    "precapprox", "succapprox", "vartriangleleft", "vartriangleright",
    "trianglelefteq", "trianglerighteq", "triangleleft", "triangleright",
    "smallfrown", "smallsmile", "shortmid", "shortparallel",
    "thicksim", "thickapprox", "approxeq", "backsim", "backsimeq",
    "subseteqq", "supseteqq", "Subset", "Supset",
    "Vvdash", "Vdash", "vDash",
    "lvertneqq", "gvertneqq", "nleq", "ngeq",
    "nless", "ngtr", "nprec", "nsucc",
    "lneq", "gneq", "npreceq", "nsucceq",
    "precneqq", "succneqq", "precnsim", "succnsim",
    "precnapprox", "succnapprox", "lnapprox", "gnapprox",
    "ncong", "nshortmid", "nshortparallel",
    "nVDash", "nVdash", "nvDash", "nvdash",
    "ntriangleleft", "ntriangleright", "ntrianglelefteq", "ntrianglerighteq",
    "ulcorner", "urcorner", "llcorner", "lrcorner",
    "diagup", "diagdown", "blacksquare",
    "nsubseteq", "nsupseteq",
    "subsetneqq", "supsetneqq",
    "nparallel", "nmid",
    "overwithdelims", "atopwithdelims", "abovewithdelims",
    "displaylines", "eqalign", "eqalignno", "leqalignno",
    "cases", "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "smallmatrix", "array",
    "vtop", "vcenter",
    "mathchar", "mathcode", "delcode",
    "radical", "mathaccent", "delimiter",
    "limits", "nolimits", "displaylimits",
    "lgroup", "rgroup",
    "choose", "brack", "bangle",
    "buildrel",
    "rel", "bin", "open", "close", "punct", "inner", "ord",
    "mathhexbox",
    "Bbb", "bold",
    "hspace*", "vspace*",
})

# Meta commands that define or reference other commands — excluded from
# "undefined" checks because they are definition machinery, not user-level usage.
META_CMDS = frozenset({
    "newcommand", "renewcommand", "providecommand", "DeclareMathOperator",
    "def", "edef", "gdef", "xdef", "newmathcommand",
    "label", "ref", "eqref", "autoref", "cref", "Cref", "pageref", "nameref",
    "begin", "end", "documentclass", "usepackage", "RequirePackage",
    "input", "include", "includeonly",
})

# Regex: any LaTeX command token  \cmdname
CMD_TOKEN = re.compile(r"\\([A-Za-z]+)")

# Regex: command definitions — \newcommand{\cmd}, \DeclareMathOperator{\cmd}, \def\cmd, \newmathcommand{\cmd}
DEFINE_PATTERNS = [
    re.compile(r"\\newcommand\*?\{(\\[A-Za-z]+)\}"),
    re.compile(r"\\renewcommand\*?\{(\\[A-Za-z]+)\}"),
    re.compile(r"\\providecommand\*?\{(\\[A-Za-z]+)\}"),
    re.compile(r"\\DeclareMathOperator\*?\{(\\[A-Za-z]+)\}"),
    re.compile(r"\\def\\([A-Za-z]+)"),
    re.compile(r"\\newmathcommand\{(\\[A-Za-z]+)\}"),
]

# Regex: equation labels and refs
EQ_LABEL = re.compile(r"\\label\{eq:([^}]+)\}")
EQ_REF = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)\{eq:([^}]+)\}")

# Notation wrappers whose argument is a single variable whose "base" we can extract.
NOTATION_WRAPPERS = (
    "mathbf", "mathrm", "mathit", "mathtt", "mathsf", "mathcal", "mathfrak",
    "mathbb", "mathscr", "bm", "boldsymbol", "pmb", "mathnormal",
    "vec", "dot", "ddot", "dddot", "ddddot", "hat", "check", "breve",
    "acute", "grave", "tilde", "bar", "overline", "underline",
    "overbrace", "underbrace",
)
# Pattern: \wrapper{<single-token>}
NOTATION_PATTERNS = [
    re.compile(r"\\(" + re.escape(w) + r")\{([^}]+)\}") for w in NOTATION_WRAPPERS
]


def _in_math(text: str, pos: int) -> bool:
    """Heuristic: is `pos` inside a math region? Counts unescaped $ and math envs before pos."""
    prefix = text[:pos]
    # Remove escaped dollars
    simplified = prefix.replace("\\$", "")
    # Remove $$ pairs
    simplified = re.sub(r"\$\$", "", simplified)
    # Count remaining $
    if simplified.count("$") % 2 == 1:
        return True
    # Check math environments
    for env in ("equation", "equation*", "align", "align*", "eqnarray", "eqnarray*",
                "gather", "gather*", "multline", "multline*", "displaymath"):
        open_pat = "\\begin{" + env + "}"
        close_pat = "\\end{" + env + "}"
        if prefix.count(open_pat) > prefix.count(close_pat):
            return True
    # \[ ... \]
    if prefix.count("\\[") > prefix.count("\\]"):
        return True
    # \( ... \)
    if prefix.count("\\(") > prefix.count("\\)"):
        return True
    return False


def symbols_report(text: str) -> dict:
    """Heuristic LaTeX symbol/notation consistency screen.

    Returns a dict with command definitions, usage, equation refs, and notation
    variants. This is a screen, not a proof — results are best-effort.
    """
    # --- command definitions ---
    defined: set[str] = set()
    # Collect the character spans of definition constructs so we can exclude the
    # definition site itself from "usage" (e.g. \newcommand{\foo} references \foo).
    def_spans: list[tuple[int, int]] = []
    for pat in DEFINE_PATTERNS:
        for m in pat.finditer(text):
            cmd = m.group(1).lstrip("\\")
            if cmd:
                defined.add(cmd)
            def_spans.append((m.start(), m.end()))
    def_spans.sort()

    def _in_def(pos: int) -> bool:
        for s, e in def_spans:
            if s <= pos < e:
                return True
            if s > pos:
                break
        return False

    # --- command usage (all \cmd tokens, excluding definition sites) ---
    used: set[str] = set()
    for m in CMD_TOKEN.finditer(text):
        if not _in_def(m.start()):
            used.add(m.group(1))

    unused = sorted(defined - used)
    # undefined = used by author but not defined here and not a builtin / meta cmd
    undefined = sorted(used - defined - LATEX_BUILTINS - META_CMDS)

    # --- equation labels & refs ---
    eq_labels = sorted(set(EQ_LABEL.findall(text)))
    eq_refs = sorted(set(EQ_REF.findall(text)))
    dangling_refs = sorted(set(eq_refs) - set(eq_labels))
    unused_labels = sorted(set(eq_labels) - set(eq_refs))

    # --- notation variants ---
    # Collect, per base variable, the set of distinct wrapper forms and locations.
    base_forms: dict[str, dict[str, list[int]]] = {}
    for pat in NOTATION_PATTERNS:
        for m in pat.finditer(text):
            wrapper = m.group(1)
            arg = m.group(2).strip()
            # Only consider single-token arguments (a single letter or short identifier)
            if not arg or len(arg) > 3 or not re.fullmatch(r"[A-Za-z0-9]+", arg):
                continue
            # Only consider occurrences inside math mode (heuristic scoping).
            if not _in_math(text, m.start()):
                continue
            loc = text.count("\n", 0, m.start()) + 1
            entry = base_forms.setdefault(arg, {})
            entry.setdefault(wrapper, []).append(loc)

    notation_variants: list[dict] = []
    for var in sorted(base_forms):
        forms = base_forms[var]
        if len(forms) < 2:
            continue
        all_locs: list[int] = []
        form_list: list[str] = []
        for w in sorted(forms):
            form_list.append("\\" + w + "{" + var + "}")
            all_locs.extend(forms[w])
        notation_variants.append({
            "variable": var,
            "forms": form_list,
            "locations": sorted(set(all_locs)),
        })

    return {
        "defined_commands": sorted(defined),
        "unused_commands": unused,
        "undefined_commands_used": undefined,
        "equation_labels": eq_labels,
        "equation_refs": eq_refs,
        "dangling_equation_refs": dangling_refs,
        "unused_equation_labels": unused_labels,
        "notation_variants": notation_variants,
    }


def markdown_report(text):
    defined = set(re.findall(r"\([^\n)]*\b([A-Z][A-Z0-9]{1,9})\b[^\n)]*\)", text))
    used = set(ABBREV.findall(text))
    references = {kind: sorted(set(re.findall(rf"\b{kind}\.?\s+(\d+)\b", text, re.I)), key=int) for kind in ("Figure", "Table")}
    return {"abbreviations_used": sorted(used), "abbreviations_with_parenthetical_definition": sorted(defined), "possibly_undefined_abbreviations": sorted(used - defined), "numbered_references": references}


def latex_report(text):
    labels = {kind: sorted(set(re.findall(rf"\\label\{{{kind}:([^}}]+)\}}", text))) for kind in ("fig", "tab")}
    refs = {kind: sorted(set(re.findall(rf"\\(?:ref|autoref|cref)\{{{kind}:([^}}]+)\}}", text))) for kind in ("fig", "tab")}
    return {"labels": labels, "references": refs, "unreferenced_labels": {k: sorted(set(labels[k])-set(refs[k])) for k in labels}, "missing_labels": {k: sorted(set(refs[k])-set(labels[k])) for k in labels}, "abbreviations": markdown_report(re.sub(r"\\[A-Za-z]+(?:\[[^]]*\])?\{[^}]*\}", "", text))}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manuscript", help=".md or .tex manuscript source")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--symbols", action="store_true", default=False,
                   help="enable LaTeX symbol/notation consistency analysis (command definitions, equation refs, notation variants)")
    a = p.parse_args(argv)
    try:
        path = Path(a.manuscript)
        if path.suffix.lower() not in {".md", ".tex"}: raise ValueError("manuscript must be .md or .tex")
        text = path.read_text(encoding="utf-8-sig")
        detail = latex_report(text) if path.suffix.lower()==".tex" else markdown_report(text)
        report = {"schema_version":"1.0.0", "artifact_type":"manuscript-consistency-screen", "tool_version":VERSION, "manuscript":str(path.resolve()), "format":path.suffix.lower(), "findings":detail, "warnings":["Heuristic screen only: capitalized tokens can be proper nouns or units, and parenthetical text is not proof of a valid abbreviation definition.", "This does not parse DOCX fields, bibliography semantics, cross-file LaTeX includes, journal style requirements, or rendered numbering."]}
        if a.symbols:
            report["symbols"] = symbols_report(text) if path.suffix.lower() == ".tex" else {}
        print(json.dumps(report, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr); return 1
if __name__ == "__main__": raise SystemExit(main())
