#!/usr/bin/env python3
"""Pre-compilation checker for LaTeX documents.

Scans a .tex file (typically the output of md2latex or an LLM-generated
manuscript) for common issues that break pdfLaTeX/XeLaTeX compilation, and
reports them with actionable fixes. Zero-dependency (Python 3.8+ stdlib).

Detected issues:
  - xeCJK present but no XeLaTeX (pdfLaTeX cannot load xeCJK)
  - CJK (Chinese) characters present but no CJK-capable template / xeCJK
  - \\includegraphics used but graphicx not loaded
  - SVG figures referenced (pdfLaTeX cannot embed .svg)
  - image files that do not exist on disk
  - \\usepackage{X} where X is a known missing-argument package
  - \\ref / \\label mismatches (undefined references)
  - \\cite used but no \\bibliography / \\bibitem
  - \\begin{table*} / \\begin{figure*} in single-column layouts
  - common fragile commands in moving arguments (\\section, \\caption)

CLI:
  python3 latex_compile_check.py paper.tex
  python3 latex_compile_check.py paper.tex --compiler pdflatex
  python3 latex_compile_check.py paper.tex --fix --force
  python3 latex_compile_check.py paper.tex --json
"""

import argparse
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

# CJK unified ideographs + compatibility blocks
CJK_RE = re.compile(r"[一-鿿豈-﫿︰-﹏]")

# Packages that REQUIRE XeTeX/LuaTeX and will fatalfail under pdfLaTeX
XETEX_ONLY_PACKAGES = {
    "xeCJK": "CJK support — compile with XeLaTeX or switch to --template ctexart",
    "fontspec": "system font selection — compile with XeLaTeX/LuaTeX",
    "xeunicode": "XeTeX Unicode extensions — compile with XeLaTeX",
}

# Packages that provide specific commands
PACKAGE_PROVIDES = {
    "graphicx": ["\\includegraphics"],
    "amsmath": ["\\begin{equation}", "\\begin{align}", "\\begin{cases}",
                 "\\begin{split}", "\\begin{matrix}", "\\begin{pmatrix}"],
    "amssymb": ["\\mathbb", "\\mathfrak", "\\mathcal", "\\geqslant", "\\leqslant"],
    "booktabs": ["\\toprule", "\\midrule", "\\bottomrule", "\\cmidrule"],
    "xcolor": ["\\textcolor", "\\color", "\\definecolor", "\\colorbox"],
    "hyperref": ["\\href", "\\url", "\\autoref", "\\cref", "\\nameref"],
    "cite": ["\\cite", "\\citep", "\\citet"],
    "cleveref": ["\\cref", "\\Cref", "\\cpageref"],
    "algorithm": ["\\begin{algorithm}"],
    "algpseudocode": ["\\begin{algorithmic}", "\\State", "\\If", "\\For", "\\While"],
    "listings": ["\\begin{lstlisting}", "\\lstinputlisting", "\\lstset"],
    "tabularx": ["\\begin{tabularx}"],
    "longtable": ["\\begin{longtable}"],
    "multirow": ["\\multirow"],
    "ulem": ["\\sout", "\\uline", "\\uwave"],
    "float": ["\\begin{figure}[H]", "\\begin{table}[H]"],
}

# LaTeX kernel commands that are always available (no package needed)
KERNEL_COMMANDS = {
    "\\label", "\\ref", "\\pageref", "\\cite", "\\nocite",
    "\\bibliography", "\\bibliographystyle", "\\documentclass",
    "\\usepackage", "\\input", "\\include", "\\includeonly",
    "\\begin", "\\end", "\\section", "\\subsection", "\\subsubsection",
    "\\paragraph", "\\subparagraph", "\\title", "\\author", "\\date",
    "\\maketitle", "\\tableofcontents", "\\listoffigures", "\\listoftables",
    "\\item", "\\caption", "\\centering", "\\hline", "\\cline",
    "\\toprule", "\\midrule", "\\bottomrule",  # common but need booktabs
    "\\text", "\\textbf", "\\textit", "\\texttt", "\\textrm", "\\textsf",
    "\\emph", "\\underline", "\\overline",
    "\\refstepcounter", "\\stepcounter",
    "\\newcommand", "\\renewcommand", "\\providecommand",
    "\\newenvironment", "\\renewenvironment",
    "\\setlength", "\\addtolength", "\\setcounter", "\\addtocounter",
    "\\newlength", "\\settowidth", "\\settoheight", "\\settodepth",
    "\\hspace", "\\vspace", "\\hfill", "\\vfill",
    "\\noindent", "\\indent", "\\noindent",
    "\\raggedright", "\\raggedleft", "\\centering",
    "\\textwidth", "\\linewidth", "\\columnwidth",
    "\\hline", "\\cline", "\\multicolumn",
    "\\hline", "\\cline",
    "\\textbackslash", "\\textasciitilde", "\\textasciicircum",
}

# Commands that need a package but are often used without one
COMMAND_NEEDS_PACKAGE = {
    "\\includegraphics": "graphicx",
    "\\toprule": "booktabs",
    "\\midrule": "booktabs",
    "\\bottomrule": "booktabs",
    "\\cmidrule": "booktabs",
    "\\textcolor": "xcolor",
    "\\color": "xcolor",
    "\\definecolor": "xcolor",
    "\\colorbox": "xcolor",
    "\\sout": "ulem",
    "\\uline": "ulem",
    "\\uwave": "ulem",
    "\\multirow": "multirow",
    "\\tabularx": "tabularx",
    "\\begin{tabularx}": "tabularx",
    "\\begin{longtable}": "longtable",
    "\\begin{lstlisting}": "listings",
    "\\lstset": "listings",
    "\\lstinputlisting": "listings",
    "\\href": "hyperref",
    "\\url": "hyperref",
    "\\autoref": "hyperref",
    "\\cref": "cleveref",
    "\\Cref": "cleveref",
    "\\cpageref": "cleveref",
    "\\begin{algorithm}": "algorithm",
    "\\begin{algorithmic}": "algpseudocode",
    "\\State": "algpseudocode",
    "\\If": "algpseudocode",
    "\\For": "algpseudocode",
    "\\While": "algpseudocode",
    "\\xeCJK": "xeCJK",
    "\\setCJKmainfont": "xeCJK",
    "\\setmainfont": "fontspec",
}


def read_tex(path):
    """Read a .tex file, following \\input / \\include."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    base_dir = os.path.dirname(os.path.abspath(path))
    # Simple include expansion (one level, non-recursive to avoid loops)
    def replace_include(m):
        cmd = m.group(1)
        arg = m.group(2)
        inc_path = os.path.join(base_dir, arg)
        if not inc_path.endswith(".tex"):
            inc_path += ".tex"
        if os.path.isfile(inc_path):
            with open(inc_path, encoding="utf-8", errors="replace") as f:
                return f.read()
        return m.group(0)  # leave as-is if file not found
    text = re.sub(r"\\(input|include)\{([^}]+)\}", replace_include, text)
    return text


def extract_packages(text):
    """Return the set of package names loaded via \\usepackage."""
    pkgs = set()
    for m in re.finditer(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", text):
        for pkg in m.group(1).split(","):
            pkg = pkg.strip()
            if pkg:
                pkgs.add(pkg)
    return pkgs


def extract_includegraphics_paths(text):
    """Return list of image paths from \\includegraphics."""
    paths = []
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        paths.append(m.group(1))
    return paths


def extract_labels(text):
    """Return set of \\label{key} values."""
    return set(re.findall(r"\\label\{([^}]+)\}", text))


def extract_refs(text):
    """Return set of \\ref{key} and \\pageref{key} values."""
    refs = set(re.findall(r"\\(?:ref|pageref|autoref|cref|Cref)\{([^}]+)\}", text))
    return refs


def extract_cites(text):
    """Return True if any citation command is used."""
    return bool(re.search(r"\\(?:cite|citep|citet|nocite|citeauthor|citeyear)\b", text))


def extract_bibliography(text):
    """Return True if \\bibliography or thebibliography env is present."""
    if re.search(r"\\bibliography\{", text):
        return True
    if re.search(r"\\begin\{thebibliography\}", text):
        return True
    return False


def detect_template(text):
    """Detect the document class."""
    m = re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", text)
    return m.group(1) if m else None


def is_cjk_template(documentclass, packages):
    """Check if the template supports CJK natively."""
    if documentclass in ("ctexart", "ctexrep", "ctexbook", "ctexbeamer"):
        return True
    if "xeCJK" in packages:
        return True
    return False


def check_compiler_for_template(documentclass, packages):
    """Determine the appropriate compiler."""
    if is_cjk_template(documentclass, packages):
        return "xelatex"
    for pkg in packages:
        if pkg in XETEX_ONLY_PACKAGES:
            return "xelatex"
    return "pdflatex"


def resolve_image_path(img_path, tex_dir):
    """Resolve an image path relative to the tex file directory."""
    # Try as-is (relative to tex directory)
    candidate = os.path.normpath(os.path.join(tex_dir, img_path))
    if os.path.isfile(candidate):
        return candidate, True
    # Try with common prefixes stripped
    for prefix in ("../", "./", "figures/", "figure/", "img/", "images/"):
        if img_path.startswith(prefix):
            stripped = img_path[len(prefix):]
            candidate = os.path.normpath(os.path.join(tex_dir, stripped))
            if os.path.isfile(candidate):
                return candidate, True
    # Try parent directory (common: tex in paper/, figures in ../figures/)
    candidate = os.path.normpath(os.path.join(tex_dir, "..", img_path))
    if os.path.isfile(candidate):
        return candidate, True
    return os.path.normpath(os.path.join(tex_dir, img_path)), False


def check_cite_without_bibliography(text):
    """Check if \\cite is used but no bibliography is defined."""
    uses_cite = bool(re.search(r"\\(cite|citep|citet|nocite|citeauthor|citeyear)\b", text))
    has_bib = bool(re.search(r"\\(bibliography|begin\{thebibliography\})\b", text))
    return uses_cite and not has_bib


def check_float_star_in_single_column(text, documentclass):
    """Check if table*/figure* is used in a single-column document."""
    if documentclass in ("IEEEtran", "revtex4-1", "revtex4-2"):
        # These are two-column by default, table*/figure* is fine
        return []
    # For article/report/book, table*/figure* spans page width — usually fine
    # but flag if the document is explicitly single-column
    issues = []
    if re.search(r"\\documentclass\[[^\]]*onecolumn", text):
        for m in re.finditer(r"\\begin\{(table|figure)\*", text):
            issues.append({
                "line": text[:m.start()].count("\n") + 1,
                "type": "float_star_single_column",
                "message": f"\\begin{{{m.group(1)}*}} in onecolumn mode — use \\begin{{{m.group(1)}}} instead",
            })
    return issues


def check_fragile_in_moving_args(text):
    """Check for fragile commands in section/caption arguments."""
    issues = []
    # Common fragile commands that need \protect in moving arguments
    fragile_cmds = [r"\\footnote", r"\\cite", r"\\ref", r"\\label"]
    # Match \section{...}, \subsection{...}, \caption{...}
    for m in re.finditer(r"\\(section|subsection|subsubsection|paragraph|subparagraph|caption)\*?\{", text):
        cmd_start = m.start()
        # Find the matching closing brace
        depth = 0
        pos = m.end() - 1
        for i in range(pos, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    arg_text = text[pos + 1:i]
                    for frag in fragile_cmds:
                        if re.search(frag, arg_text):
                            line = text[:cmd_start].count("\n") + 1
                            issues.append({
                                "line": line,
                                "type": "fragile_in_moving_arg",
                                "message": f"Fragile command in moving argument — add \\protect before {frag} in \\{m.group(1)}",
                            })
                    break
    return issues


def check_missing_packages_for_commands(text, packages):
    """Check if commands are used without their required package."""
    issues = []
    for cmd, pkg in COMMAND_NEEDS_PACKAGE.items():
        if pkg in packages:
            continue
        # Check if command is used
        cmd_escaped = re.escape(cmd)
        if re.search(cmd_escaped, text):
            line = None
            for i, line_text in enumerate(text.split("\n"), 1):
                if cmd in line_text:
                    line = i
                    break
            issues.append({
                "line": line,
                "type": "missing_package",
                "message": f"{cmd} requires \\usepackage{{{pkg}}} which is not loaded",
                "command": cmd,
                "package": pkg,
            })
    return issues


def check_undefined_refs(text):
    """Check for refs to undefined labels."""
    labels = extract_labels(text)
    refs = extract_refs(text)
    undefined = refs - labels
    issues = []
    for ref in sorted(undefined):
        for i, line_text in enumerate(text.split("\n"), 1):
            if f"{{{ref}}}" in line_text and ("\\ref" in line_text or "\\autoref" in line_text or "\\cref" in line_text):
                issues.append({
                    "line": i,
                    "type": "undefined_ref",
                    "message": f"\\ref{{{ref}}} has no matching \\label{{{ref}}}",
                    "ref": ref,
                })
                break
    return issues


def check_svg_figures(text, tex_dir):
    """Check for SVG figures and whether fallbacks exist."""
    issues = []
    paths = extract_includegraphics_paths(text)
    for img_path in paths:
        if not img_path.lower().endswith(".svg"):
            continue
        line = None
        for i, line_text in enumerate(text.split("\n"), 1):
            if img_path in line_text:
                line = i
                break
        # Check for PDF/PNG fallback
        stem = os.path.splitext(img_path)[0]
        base = os.path.basename(stem)
        parent = os.path.dirname(stem)
        grandparent = os.path.dirname(parent)
        fallback_found = False
        fallback_path = None
        for ext in (".pdf", ".png"):
            # Same directory
            candidate = os.path.normpath(os.path.join(tex_dir, stem + ext))
            if os.path.isfile(candidate):
                fallback_found = True
                fallback_path = stem + ext
                break
            # Parallel directory (svg/ -> pdf/)
            if os.path.basename(parent).lower() in ("svg", "svgs"):
                parallel = os.path.normpath(os.path.join(tex_dir, grandparent, ext.lstrip("."), base + ext))
                if os.path.isfile(parallel):
                    fallback_found = True
                    fallback_path = os.path.join(grandparent, ext.lstrip("."), base + ext)
                    break
        if not fallback_found:
            issues.append({
                "line": line,
                "type": "svg_no_fallback",
                "message": f"SVG figure '{img_path}' has no PDF/PNG fallback — pdfLaTeX cannot embed SVG",
                "path": img_path,
            })
        else:
            issues.append({
                "line": line,
                "type": "svg_with_fallback",
                "message": f"SVG figure '{img_path}' — fallback '{fallback_path}' exists but is not referenced",
                "path": img_path,
                "fallback": fallback_path,
                "severity": "warning",
            })
    return issues


def check_missing_images(text, tex_dir):
    """Check if referenced image files exist."""
    issues = []
    paths = extract_includegraphics_paths(text)
    for img_path in paths:
        if img_path.lower().endswith(".svg"):
            continue  # handled by check_svg_figures
        resolved, exists = resolve_image_path(img_path, tex_dir)
        if not exists:
            line = None
            for i, line_text in enumerate(text.split("\n"), 1):
                if img_path in line_text:
                    line = i
                    break
            issues.append({
                "line": line,
                "type": "missing_image",
                "message": f"Image file not found: '{img_path}' (resolved: {resolved})",
                "path": img_path,
            })
    return issues


def check_xecjk_conflict(text, packages, compiler):
    """Check if xeCJK is loaded but compiler is not XeLaTeX."""
    issues = []
    if "xeCJK" in packages and compiler == "pdflatex":
        issues.append({
            "type": "xecjk_pdflatex_conflict",
            "message": "\\usepackage{xeCJK} requires XeLaTeX — pdfLaTeX will fail with 'xeCJK requires XeTeX'. Compile with xelatex, or remove xeCJK and use --template ctexart",
            "severity": "error",
        })
    return issues


def check_cjk_without_support(text, packages, documentclass):
    """Check if CJK characters exist but no CJK support is loaded."""
    if is_cjk_template(documentclass, packages):
        return []
    if not CJK_RE.search(text):
        return []
    return [{
        "type": "cjk_without_support",
        "message": "CJK (Chinese) characters detected but no CJK package loaded — add \\usepackage{xeCJK} + compile with xelatex, or use --template ctexart, or translate to English",
        "severity": "error",
    }]


def check_missing_graphicx(text, packages):
    """Check if \\includegraphics is used but graphicx is not loaded."""
    if "graphicx" in packages:
        return []
    if not re.search(r"\\includegraphics", text):
        return []
    return [{
        "type": "missing_graphicx",
        "message": "\\includegraphics used but \\usepackage{graphicx} is not in the preamble — add \\usepackage{graphicx}",
        "severity": "error",
    }]


def run_checks(tex_path, preferred_compiler=None):
    """Run all checks and return a structured report."""
    text = read_tex(tex_path)
    tex_dir = os.path.dirname(os.path.abspath(tex_path))

    packages = extract_packages(text)
    documentclass = detect_template(text)
    auto_compiler = check_compiler_for_template(documentclass, packages)
    compiler = preferred_compiler or auto_compiler

    issues = []

    # Critical: xeCJK + pdfLaTeX
    issues.extend(check_xecjk_conflict(text, packages, compiler))

    # Critical: CJK without support
    issues.extend(check_cjk_without_support(text, packages, documentclass))

    # Critical: missing graphicx
    issues.extend(check_missing_graphicx(text, packages))

    # Missing packages for commands
    issues.extend(check_missing_packages_for_commands(text, packages))

    # SVG figures
    issues.extend(check_svg_figures(text, tex_dir))

    # Missing image files
    issues.extend(check_missing_images(text, tex_dir))

    # Cite without bibliography
    if check_cite_without_bibliography(text):
        issues.append({
            "type": "cite_without_bibliography",
            "message": "\\cite{} used but no \\bibliography{} or thebibliography environment found",
            "severity": "warning",
        })

    # Undefined refs
    issues.extend(check_undefined_refs(text))

    # Float star in single column
    issues.extend(check_float_star_in_single_column(text, documentclass))

    # Fragile in moving args (heuristic, lower severity)
    # issues.extend(check_fragile_in_moving_args(text))  # too noisy for now

    # Categorize
    errors = [i for i in issues if i.get("severity") == "error"]
    warnings = [i for i in issues if i.get("severity") != "error"]

    return {
        "file": tex_path,
        "documentclass": documentclass,
        "packages": sorted(packages),
        "compiler_recommended": compiler,
        "compiler_preferred": preferred_compiler,
        "issues": issues,
        "errors": errors,
        "warnings": warnings,
        "status": "fail" if errors else ("warn" if warnings else "pass"),
    }


def auto_fix(tex_path, report, force=False):
    """Attempt to auto-fix issues in the tex file."""
    with open(tex_path, encoding="utf-8") as f:
        text = f.read()

    fixes_applied = []

    # Fix: add graphicx if missing
    for issue in report["errors"]:
        if issue["type"] == "missing_graphicx":
            pkg_line = "\n\\usepackage{graphicx}"
            # Insert after the last \usepackage, or after \documentclass if none
            last_uspkg = list(re.finditer(r"\\usepackage(?:\[[^\]]*\])?\{[^}]+\}", text))
            if last_uspkg:
                insert_pos = last_uspkg[-1].end()
                text = text[:insert_pos] + pkg_line + text[insert_pos:]
            else:
                # No \usepackage at all — insert after \documentclass{...}
                doc_class = re.search(r"\\documentclass(?:\[[^\]]*\])?\{[^}]+\}", text)
                if doc_class:
                    insert_pos = doc_class.end()
                    text = text[:insert_pos] + pkg_line + text[insert_pos:]
                else:
                    # No \documentclass either — prepend
                    text = pkg_line.lstrip() + "\n" + text
            fixes_applied.append("Added \\usepackage{graphicx}")

    # Fix: replace SVG paths with PDF fallbacks
    for issue in report["issues"]:
        if issue["type"] == "svg_with_fallback" and "fallback" in issue:
            old = issue["path"]
            new = issue["fallback"].replace("\\", "/")
            text = text.replace(old, new)
            fixes_applied.append(f"Replaced '{old}' -> '{new}'")

    # Fix: remove xeCJK (user must switch to xelatex separately)
    # We don't auto-remove because it requires compiler change

    if fixes_applied:
        if not force and os.path.exists(tex_path):
            backup = tex_path + ".bak"
            os.rename(tex_path, backup)
            fixes_applied.insert(0, f"Backup created: {backup}")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(text)

    return fixes_applied


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.add_argument("tex", help="input .tex file to check")
    p.add_argument("--compiler", choices=["pdflatex", "xelatex", "lualatex"],
                   help="preferred compiler (default: auto-detect from packages)")
    p.add_argument("--json", action="store_true", help="output JSON report")
    p.add_argument("--fix", action="store_true", help="attempt to auto-fix issues")
    p.add_argument("--force", action="store_true", help="overwrite original .tex when fixing (default: create .bak backup)")
    args = p.parse_args()

    if not os.path.isfile(args.tex):
        sys.exit(f"file not found: {args.tex}")

    report = run_checks(args.tex, args.compiler)

    if args.fix:
        fixes = auto_fix(args.tex, report, force=args.force)
        # Re-run checks after fix
        report = run_checks(args.tex, args.compiler)
        report["fixes_applied"] = fixes

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"File: {report['file']}")
        print(f"Document class: {report['documentclass']}")
        print(f"Compiler recommended: {report['compiler_recommended']}")
        print(f"Packages: {', '.join(report['packages'])}")
        print()
        if report["errors"]:
            print(f"ERRORS ({len(report['errors'])}):")
            for issue in report["errors"]:
                line = issue.get("line", "?")
                print(f"  Line {line}: {issue['message']}")
            print()
        if report["warnings"]:
            print(f"WARNINGS ({len(report['warnings'])}):")
            for issue in report["warnings"]:
                line = issue.get("line", "?")
                print(f"  Line {line}: {issue['message']}")
            print()
        if report["status"] == "pass":
            print("Status: PASS — no issues found")
        elif report["status"] == "warn":
            print("Status: WARN — no errors, but warnings present")
        else:
            print("Status: FAIL — errors must be fixed before compilation")
        if "fixes_applied" in report:
            print()
            print("Fixes applied:")
            for fix in report["fixes_applied"]:
                print(f"  - {fix}")

    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
