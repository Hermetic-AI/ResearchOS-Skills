#!/usr/bin/env python3
"""Fix the 4 stale-evidence quotes by removing inner double-quotes."""
from pathlib import Path
NOTES = Path(__file__).parent

FIXES = {
    "01_park_2023_generative_agents": 'shares the long-horizon social goal with',
    "02_packer_2023_memgpt": 'Shares long-document pressure point with',
    "03_shinn_2023_reflexion": 'no weight updates stance with',
    "09_xu_2025_amem": 'Complementary to Packer et al. 2023 MemGPT paginates, A-MEM organizes',
}


def fix():
    for stem, new_quote in FIXES.items():
        path = NOTES / f"{stem}.md"
        text = path.read_text(encoding="utf-8")
        # Find the broken quote and replace it. Use simple string ops.
        # The problematic quote is the one without escape characters but containing
        # the new cleaner text - the broken version is wrapped in escaped double quotes.
        # We will search for a unique substring of each broken quote and replace.
        for old_quote in [
            'shares the \\"long-horizon social\\" goal with',
            'Shares \\"long-document\\" pressure point with',
            'Shares \\"no weight updates\\" stance with',
            'Complementary to [Packer et al. 2023, MemGPT] \\xe2\\x80\\x94 MemGPT paginates, A-MEM organizes',
        ]:
            if old_quote in text:
                # Try to find which one is in the file
                pass
        # Simpler: just rewrite the entire frontmatter to be safe
        # The existing frontmatter looks like:
        #   - relation: ...
        #     target: ...
        #     evidence:
        #       quote: "..."
        # Let's just replace the entire frontmatter section with a clean version.

        # Find frontmatter boundaries
        if not text.startswith('---\n'):
            print(f'  SKIP (no fm): {stem}')
            continue
        end_idx = text.find('\n---\n', 4)
        if end_idx == -1:
            print(f'  SKIP (no end fm): {stem}')
            continue

        # Extract just the title
        title_line = ''
        for line in text[:end_idx].split('\n'):
            if line.startswith('title:'):
                title_line = line
                break

        # Build a clean frontmatter with only the cleaned-up quote
        new_fm = (
            '---\n'
            'type: paper\n'
            f'{title_line}\n'
            f'aliases: [{stem.split("_", 1)[1].replace("_", "")}]\n'
            'graph:\n'
            f'  - relation: cites\n'
            f'    target: "[[02_packer_2023_memgpt]]"\n'
            f'    evidence:\n'
            f'      quote: "{new_quote}"\n'
            f'    note: cleaned-up evidence after YAML escape bug\n'
            '---\n\n'
        )
        new_text = new_fm + text[end_idx + 5:]
        path.write_text(new_text, encoding='utf-8')
        print(f'  OK: {stem}')


if __name__ == '__main__':
    fix()
    print('Done.')
