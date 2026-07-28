"""Verify all 14 references are cited in the body of the paper (and no orphan citations)."""
import re
from pathlib import Path

PAPER = Path(r'C:\WorkSpace\Coding\ResearchOS-Skills\workspace\ai-agent-memory-survey\paper\paper.md')
REFS = Path(r'C:\WorkSpace\Coding\ResearchOS-Skills\workspace\ai-agent-memory-survey\paper\references_ieee.md')

text = PAPER.read_text(encoding='utf-8')

# Find reference entries (lines starting with [N])
ref_nums = set()
for line in text.splitlines():
    m = re.match(r'^\s*\[(\d+)\]', line)
    if m:
        ref_nums.add(int(m.group(1)))

# Find all citations in body — exclude reference list
# Split into "body" and "refs" by finding the "## References" line
ref_section_start = None
for i, line in enumerate(text.splitlines()):
    if line.strip() == '## References':
        ref_section_start = i
        break

body_lines = text.splitlines()[:ref_section_start] if ref_section_start else text.splitlines()
body_text = '\n'.join(body_lines)

cite_nums = set()
for m in re.finditer(r'\[(\d+)\]', body_text):
    cite_nums.add(int(m.group(1)))

print(f"References in ref list: {sorted(ref_nums)}")
print(f"Citations in body:       {sorted(cite_nums)}")
print(f"Orphan refs (in list, not cited): {sorted(ref_nums - cite_nums)}")
print(f"Orphan cites (cited, not in list): {sorted(cite_nums - ref_nums)}")

# Check style consistency for each reference entry
print("\n--- Per-entry style check ---")
ref_section = '\n'.join(text.splitlines()[ref_section_start:]) if ref_section_start else ''
issues = []
for entry in ref_section.split('\n\n'):
    entry = entry.strip()
    if not entry:
        continue
    m = re.match(r'^\[(\d+)\]\s+(.*?),\s+"([^"]+),"\s+(.*?),\s+(\d{4})\.\s*$', entry, re.DOTALL)
    if not m:
        # Try to find the entry anyway
        m2 = re.match(r'^\[(\d+)\]\s+(.+)$', entry, re.DOTALL)
        if m2:
            issues.append(f"[{m2.group(1)}] format anomaly: {entry[:100]}")
        continue
    num, authors, title, venue, year = m.groups()
    if ' et al' not in authors and authors.count(',') > 5:
        # IEEE allows 6+ authors → "A. Author et al."
        issues.append(f"[{num}] >6 authors but no et al.: {authors[:60]}")
    if 'arXiv' not in venue and not re.search(r'(Proc\.|Trans\.|IEEE|ACM|UIST|NeurIPS|TMLR|TACL|vol\.|no\.)', venue):
        issues.append(f"[{num}] venue may be incomplete: {venue[:60]}")
    if not re.match(r'^[A-Z]\.', authors.strip()):
        issues.append(f"[{num}] author initial format: {authors[:60]}")

if issues:
    for issue in issues:
        print(issue)
else:
    print("All entries pass basic format check.")
