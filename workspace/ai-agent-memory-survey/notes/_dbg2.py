import sys
sys.path.insert(0, r'C:\WorkSpace\Coding\ResearchOS-Skills\knowledge-graph-builder\scripts')
from build_graph import split_frontmatter
text = open(r'C:\WorkSpace\Coding\ResearchOS-Skills\workspace\ai-agent-memory-survey\notes\03_shinn_2023_reflexion.md', encoding='utf-8').read()
fm, body = split_frontmatter(text)
joined = '\n'.join(body)
needle = 'Shares "no weight updates" stance with'
print('Body lines count:', len(body))
print('Has needle in joined body:', needle in joined)
print('Has needle in raw body list element 67:', needle in body[67] if len(body) > 67 else 'N/A')
# Print body line 67
for i, l in enumerate(body):
    if 'no weight updates' in l and 'stance' in l:
        print(f'Found at body line {i}:', repr(l[:80]))
        print('Needle in this line:', needle in l)
