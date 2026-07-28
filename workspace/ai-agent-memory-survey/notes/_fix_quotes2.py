#!/usr/bin/env python3
"""Final fix: per-file evidence quote that actually appears in the body."""
from pathlib import Path
NOTES = Path(__file__).parent

# Per-file: (relation, target, evidence_quote) using the actual §7 body
FIXES = {
    "01_park_2023_generative_agents": [
        ("cites", "[[05_wang_2024_voyager]]", "long-horizon social behavior"),
        ("cites", "[[04_zhong_2024_memorybank]]", "[Zhong et al. 2024, MemoryBank] is explicit about building on this"),
        ("cites", "[[06_sumers_2024_coala]]", "CoALA later formalizes what Park et al. instantiate"),
    ],
    "02_packer_2023_memgpt": [
        ("cites", "[[06_sumers_2024_coala]]", "Predates and motivates CoALA"),
        ("cites", "[[12_liu_2024_lost_in_middle]]", "long-document pressure point with [Liu et al. 2024"),
        ("cites", "[[11_wu_2024_survey]]", "surveyed in [Wu et al. 2024]"),
    ],
    "03_shinn_2023_reflexion": [
        ("cites", "[[06_sumers_2024_coala]]", "the Reflection pattern reappears in"),
        ("cites", "[[02_packer_2023_memgpt]]", "no weight updates"),
        ("cites", "[[10_hu_2024_longagent]]", "Compared against [Hu et al. 2024, LongAgent] in follow-ups"),
    ],
    "09_xu_2025_amem": [
        ("extends", "[[01_park_2023_generative_agents]]", "Builds on the **declarative-memory** tradition"),
        ("extends", "[[13_modarressi_2024_retllm]]", "MemGPT paginates, A-MEM organizes"),
        ("cites", "[[06_sumers_2024_coala]]", "A practical implementation of the **declarative + conditional** memory cell in [Sumers et al. 2024, CoALA]"),
    ],
}

TITLES = {
    "01_park_2023_generative_agents": "Generative Agents: Interactive Simulacra of Human Behavior",
    "02_packer_2023_memgpt": "MemGPT: Towards LLMs as Operating Systems",
    "03_shinn_2023_reflexion": "Reflexion: Language Agents with Verbal Reinforcement Learning",
    "04_zhong_2024_memorybank": "MemoryBank of LLM",
    "05_wang_2024_voyager": "Voyager: An Open-Ended Embodied Agent with LLMs",
    "06_sumers_2024_coala": "Cognitive Architectures for Language Agents (CoALA)",
    "07_qian_2024_chatdev": "ChatDev: A Sociable Software Development Framework",
    "08_maharana_2024_forgetting": "Forgetting Curve Theory for Memory-Augmented LLMs",
    "09_xu_2025_amem": "A-MEM: Agentic Memory for LLM Agents",
    "10_hu_2024_longagent": "LongAgent: Scaling Language Agents to 128K Context",
    "11_wu_2024_survey": "Long-term Memory in LLM-Powered Autonomous Agents: A Survey",
    "12_liu_2024_lost_in_middle": "Lost in the Middle: How Language Models Use Long Contexts",
    "13_modarressi_2024_retllm": "RET-LLM: Towards a General Read-Write Memory for LLMs",
    "14_zhang_2024_survey": "A Survey on the Memory Mechanism of LLM-based Agents",
}


def fix():
    for stem, items in FIXES.items():
        path = NOTES / f"{stem}.md"
        text = path.read_text(encoding='utf-8')
        if not text.startswith('---\n'):
            continue
        end_idx = text.find('\n---\n', 4)
        if end_idx == -1:
            continue

        graph_yaml = []
        for relation, target, quote in items:
            graph_yaml.append(f"  - relation: {relation}")
            graph_yaml.append(f'    target: "{target}"')
            graph_yaml.append("    evidence:")
            graph_yaml.append(f'      quote: "{quote}"')
            graph_yaml.append("    note: from §7 Connections")

        new_fm = (
            '---\n'
            'type: paper\n'
            f'title: "{TITLES[stem]}"\n'
            f'aliases: [{stem.split("_", 1)[1].replace("_", "")}]\n'
            'graph:\n'
            + '\n'.join(graph_yaml)
            + '\n---\n\n'
        )
        new_text = new_fm + text[end_idx + 5:]
        path.write_text(new_text, encoding='utf-8')
        print(f'  OK: {stem}')


if __name__ == '__main__':
    fix()
    print('Done.')
