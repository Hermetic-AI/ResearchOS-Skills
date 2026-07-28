#!/usr/bin/env python3
"""Syntax-level sanity checker + renderer advisor for code-as-diagram sources.

Purpose: this environment has no diagram renderer, so this script only checks
mermaid / graphviz DOT / plantuml sources for common syntax problems (header
declaration, bracket balance, unquoted special characters, unclosed subgraphs,
missing @enduml), optionally writes the checked source to a file, and prints
the exact local render command. It never claims a diagram renders correctly —
only that no known-bad pattern was found.

Dependencies: none (Python 3.8+ stdlib only).

CLI:
  python3 diagram_check.py --lang mermaid --in flow.mmd [--out checked.mmd]
  python3 diagram_check.py --lang dot --in arch.dot
  python3 diagram_check.py --lang plantuml --in seq.puml
  echo "flowchart TD\nA-->B" | python3 diagram_check.py --lang mermaid --in -

Output: human-readable report (errors / warnings / ok) on stdout, the checked
source file when --out is given, and a render-command suggestion. Exit code 1
when errors are found, 0 otherwise.
"""

import argparse
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MERMAID_HEADERS = (
    "flowchart", "graph", "sequenceDiagram", "erDiagram", "gantt",
    "classDiagram", "stateDiagram", "stateDiagram-v2", "pie", "journey",
    "gitGraph", "mindmap", "timeline", "C4Context",
)
RENDER_HINTS = {
    "mermaid": "npx -y @mermaid-js/mermaid-cli -i {src} -o {src}.svg  (needs Node; first run downloads puppeteer)",
    "dot": "dot -Tsvg {src} -o {src}.svg  (needs graphviz installed; try neato/fdp for other layouts)",
    "plantuml": "java -jar plantuml.jar {src}  OR paste into https://www.plantuml.com/plantuml  (no renderer here — user renders locally)",
}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lang", choices=["mermaid", "dot", "plantuml"], required=True)
    p.add_argument("--in", dest="src", required=True, help="source file, or - for stdin")
    p.add_argument("--out", help="write the (checked) source to this file")
    return p.parse_args()


def balance(text, pairs):
    """Count unbalanced openers outside of quoted strings."""
    errors = []
    for op, cl in pairs:
        depth = 0
        in_quote = False
        for ch in text:
            if ch == '"':
                in_quote = not in_quote
            if in_quote:
                continue
            if ch == op:
                depth += 1
            elif ch == cl:
                depth -= 1
            if depth < 0:
                errors.append(f"unbalanced '{cl}' before any '{op}'")
                break
        if depth > 0:
            errors.append(f"{depth} unclosed '{op}' (expected matching '{cl}')")
    return errors


def check_mermaid(src):
    errors, warnings = [], []
    lines = [l.strip() for l in src.splitlines() if l.strip() and not l.strip().startswith("%%")]
    if not lines:
        return ["empty source"], warnings
    first = lines[0].split()[0]
    if first not in MERMAID_HEADERS:
        errors.append(f"first line must declare a diagram type ({', '.join(MERMAID_HEADERS[:8])}...), got {first!r}")
    if first == "graph":
        warnings.append("'graph' is legacy syntax; prefer 'flowchart'")
    for i, line in enumerate(lines[1:], 2):
        # unquoted label containing parentheses/braces: A[f(x)] or A{...} bodies
        m = re.search(r"\[[^\]\"]*[(){}][^\]\"]*\]", line)
        if m:
            errors.append(f"line {i}: label with special characters must be quoted: {m.group(0)} "
                          f"→ use A[\"{m.group(0)[1:-1]}\"]")
        if "-- |" in line or re.search(r"--\s*\|[^|]*\|\s*->", line):
            warnings.append(f"line {i}: edge label should use '-->|label|' arrow syntax")
        if re.search(r"\|[^|]*\|[^|]*\|", line):
            errors.append(f"line {i}: edge label contains a '|' character — remove it or reword the label")
    n_sub = sum(1 for l in lines if l.startswith("subgraph"))
    n_end = sum(1 for l in lines if l == "end")
    if n_sub > n_end:
        errors.append(f"{n_sub - n_end} unclosed 'subgraph' (missing 'end')")
    errors += balance(src, [("[", "]"), ("{", "}")])
    return errors, warnings


def check_dot(src):
    errors, warnings = [], []
    m = re.match(r"\s*(strict\s+)?(di)?graph\b", src)
    if not m:
        errors.append("source must start with 'digraph G {' or 'graph G {'")
    if not m or not m.group(2):
        for mm in re.finditer(r"->", src):
            errors.append("'->' used in an undirected graph; use '--' or switch to digraph")
            break
    errors += balance(src, [("{", "}")])
    for i, line in enumerate(src.splitlines(), 1):
        for m in re.finditer(r"\[label=([^\"\]\s][^\],]*)", line):
            warnings.append(f"line {i}: label with spaces/punctuation should be quoted: label=\"{m.group(1).strip()}\"")
    return errors, warnings


def check_plantuml(src):
    errors, warnings = [], []
    if "@startuml" not in src and "@start" not in src:
        errors.append("missing '@startuml' opening directive")
    if "@enduml" not in src and "@end" not in src:
        errors.append("missing '@enduml' closing directive")
    return errors, warnings


def main():
    args = parse_args()
    src = sys.stdin.read() if args.src == "-" else open(args.src, encoding="utf-8").read()
    errors, warnings = {"mermaid": check_mermaid, "dot": check_dot,
                        "plantuml": check_plantuml}[args.lang](src)
    for w in warnings:
        print(f"warning: {w}")
    if errors:
        for e in errors:
            print(f"error: {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — fix before rendering.")
        sys.exit(1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(src if src.endswith("\n") else src + "\n")
        print(f"wrote {args.out}")
    print(f"ok: no known syntax problems in {args.lang} source ({len(warnings)} warning(s))")
    hint_src = args.out or (args.src if args.src != "-" else f"diagram.{'mmd' if args.lang == 'mermaid' else args.lang}")
    print("note: syntax check only — this environment has no renderer, so correctness of the")
    print("      visual output is NOT verified. Render locally with:")
    print(f"  {RENDER_HINTS[args.lang].format(src=hint_src)}")


if __name__ == "__main__":
    main()
