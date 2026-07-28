import sys
sys.path.insert(0, r'C:\WorkSpace\Coding\ResearchOS-Skills\knowledge-graph-builder\scripts')
from build_graph import GraphBuilder, split_frontmatter
from pathlib import Path
root = Path(r'C:\WorkSpace\Coding\ResearchOS-Skills\workspace\ai-agent-memory-survey\notes')
text = (root / '03_shinn_2023_reflexion.md').read_text(encoding='utf-8')
fm_lines, body_lines = split_frontmatter(text)
full_text = "\n".join(body_lines)
needle = 'Shares "no weight updates" stance with'
print('Body line 47:', repr(body_lines[47]))
print('Needle:', repr(needle))
print('Needle in body_line 47:', needle in body_lines[47])
print('Needle in joined body:', needle in full_text)
print('---')
# Check if YAML escapes
fm_text = "\n".join(fm_lines)
print('Frontmatter text:')
print(fm_text)
