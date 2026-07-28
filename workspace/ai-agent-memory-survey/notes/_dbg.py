text = open(r'C:\WorkSpace\Coding\ResearchOS-Skills\workspace\ai-agent-memory-survey\notes\03_shinn_2023_reflexion.md', encoding='utf-8').read()
needle = 'Shares "no weight updates" stance with'
print('Has needle:', needle in text)
print('---')
for line in text.split('\n'):
    if 'no weight updates' in line:
        print('LINE:', repr(line))
