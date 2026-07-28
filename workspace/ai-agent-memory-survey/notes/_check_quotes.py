import sys
sys.path.insert(0, r'C:\WorkSpace\Coding\ResearchOS-Skills\knowledge-graph-builder\scripts')
from build_graph import split_frontmatter
text = open(r'C:\WorkSpace\Coding\ResearchOS-Skills\workspace\ai-agent-memory-survey\notes\01_park_2023_generative_agents.md', encoding='utf-8').read()
fm, body = split_frontmatter(text)
joined = '\n'.join(body)
print('Body lines:', len(body))
print('---')
print('Searching for: Smallville sandbox, 25 agents, 2 days')
print('Found:', 'Smallville sandbox, 25 agents, 2 days' in joined)
print('---')
print('Searching for: MemoryBank is explicit about building on this')
print('Found:', 'MemoryBank is explicit about building on this' in joined)
print('---')
print('First 30 lines of body:')
for i, l in enumerate(body[:30], 1):
    print(f'{i:3d}: {l[:80]}')
