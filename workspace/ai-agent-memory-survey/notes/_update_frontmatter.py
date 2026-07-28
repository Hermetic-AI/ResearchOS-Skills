#!/usr/bin/env python3
"""Replace existing frontmatter with quotes that ARE in the body (from §7 Connections)."""
import re
from pathlib import Path

NOTES = Path(__file__).parent

# (filename_stem, [list of (relation, target, evidence_quote) tuples])
# All quotes must be exact substrings of the body.
CONNECTIONS = {
    "01_park_2023_generative_agents": [
        ("cites", "[[05_wang_2024_voyager]]",
         'shares the "long-horizon social" goal with'),
        ("cites", "[[04_zhong_2024_memorybank]]",
         "[Zhong et al. 2024, MemoryBank] is explicit about building on this"),
        ("cites", "[[06_sumers_2024_coala]]",
         "Connects to cognitive-architecture theory"),
    ],
    "02_packer_2023_memgpt": [
        ("cites", "[[06_sumers_2024_coala]]",
         "Predates and motivates CoALA"),
        ("cites", "[[11_wu_2024_survey]]",
         "surveyed in [Wu et al. 2024]"),
        ("cites", "[[12_liu_2024_lost_in_middle]]",
         'Shares "long-document" pressure point with'),
    ],
    "03_shinn_2023_reflexion": [
        ("cites", "[[06_sumers_2024_coala]]",
         "the Reflection pattern reappears in"),
        ("cites", "[[02_packer_2023_memgpt]]",
         'Shares "no weight updates" stance with'),
        ("cites", "[[10_hu_2024_longagent]]",
         "Compared against [Hu et al. 2024, LongAgent] in follow-ups"),
    ],
    "04_zhong_2024_memorybank": [
        ("extends", "[[01_park_2023_generative_agents]]",
         "Builds on the memory stream of [Park et al. 2023"),
        ("cites", "[[08_maharana_2024_forgetting]]",
         "Compared with [Maharana et al. 2024, Forgetting Curve Theory]"),
        ("cites", "[[09_xu_2025_amem]]",
         "Addressed by [Xu et al. 2025, A-MEM]"),
    ],
    "05_wang_2024_voyager": [
        ("cites", "[[03_shinn_2023_reflexion]]",
         "Pairs with [Shinn et al. 2023, Reflexion]"),
        ("cites", "[[06_sumers_2024_coala]]",
         "Categorized in [Sumers et al. 2024, CoALA] as a procedural-memory agent"),
    ],
    "06_sumers_2024_coala": [
        ("cites", "[[01_park_2023_generative_agents]]",
         "[Park et al. 2023] is declarative-memory-heavy"),
        ("cites", "[[05_wang_2024_voyager]]",
         "[Wang et al. 2024, Voyager] is procedural-memory-heavy"),
        ("cites", "[[04_zhong_2024_memorybank]]",
         "[Zhong et al. 2024, MemoryBank] is declarative+conditional"),
        ("cites", "[[11_wu_2024_survey]]",
         "Frequently cited alongside [Wu et al. 2024, survey]"),
    ],
    "07_qian_2024_chatdev": [
        ("cites", "[[11_wu_2024_survey]]",
         "precedes [Wu et al. 2024, survey]'s categorization"),
    ],
    "08_maharana_2024_forgetting": [
        ("cites", "[[04_zhong_2024_memorybank]]",
         "**Theoretical counterpart** to [Zhong et al. 2024, MemoryBank]"),
    ],
    "09_xu_2025_amem": [
        ("extends", "[[01_park_2023_generative_agents]]",
         "Builds on the **declarative-memory** tradition ([Park et al. 2023"),
        ("extends", "[[13_modarressi_2024_retllm]]",
         "Complementary to [Packer et al. 2023, MemGPT] �� MemGPT paginates, A-MEM organizes"),
        ("cites", "[[06_sumers_2024_coala]]",
         "A practical implementation of the **declarative + conditional** memory cell in [Sumers et al. 2024, CoALA]"),
    ],
    "10_hu_2024_longagent": [
        ("cites", "[[02_packer_2023_memgpt]]",
         "**Direct contrast** to memory-augmentation approaches ([Packer et al. 2023, MemGPT]"),
        ("cites", "[[12_liu_2024_lost_in_middle]]",
         "Addresses the empirical finding of [Liu et al. 2024, Lost in the Middle] from the training side"),
        ("cites", "[[11_wu_2024_survey]]",
         "Cited as a counterpoint in [Wu et al. 2024, survey]"),
    ],
    "11_wu_2024_survey": [
        ("cites", "[[14_zhang_2024_survey]]",
         "Companion to [Zhang et al. 2024, another survey]"),
        ("cites", "[[06_sumers_2024_coala]]",
         "and [Sumers et al. 2024, CoALA framework]"),
    ],
    "12_liu_2024_lost_in_middle": [
        ("cites", "[[10_hu_2024_longagent]]",
         "[Hu et al. 2024, LongAgent] is the most direct training-side response"),
        ("cites", "[[02_packer_2023_memgpt]]",
         "[Packer et al. 2023, MemGPT] is the most direct memory-engineering response"),
    ],
    "13_modarressi_2024_retllm": [
        ("cites", "[[09_xu_2025_amem]]",
         "Architectural ancestor of [Xu et al. 2025, A-MEM]"),
        ("cites", "[[02_packer_2023_memgpt]]",
         "and [Packer et al. 2023, MemGPT] (with different retrieval styles)"),
    ],
    "14_zhang_2024_survey": [
        ("cites", "[[11_wu_2024_survey]]",
         "Direct companion to [Wu et al. 2024]"),
        ("cites", "[[06_sumers_2024_coala]]",
         "and [Sumers et al. 2024, CoALA]"),
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


def update():
    for stem, graph in CONNECTIONS.items():
        path = NOTES / f"{stem}.md"
        text = path.read_text(encoding="utf-8")
        # remove existing frontmatter
        if text.startswith("---\n"):
            end = text.find("\n---\n")
            if end != -1:
                text = text[end + 5:]

        title = TITLES[stem]
        aliases = [stem.split("_", 1)[1].replace("_", "")]
        graph_yaml = []
        for relation, target, quote in graph:
            safe_quote = quote.replace('"', '\\"')
            graph_yaml.append(f"  - relation: {relation}")
            graph_yaml.append(f'    target: "{target}"')
            graph_yaml.append("    evidence:")
            graph_yaml.append(f'      quote: "{safe_quote}"')
            graph_yaml.append("    note: from §7 Connections of the source paper note")

        fm = (
            "---\n"
            "type: paper\n"
            f'title: "{title}"\n'
            f"aliases: [{', '.join(aliases)}]\n"
            "graph:\n"
            + "\n".join(graph_yaml)
            + "\n---\n\n"
        )
        path.write_text(fm + text, encoding="utf-8")
        print(f"  OK: {path.name}")


if __name__ == "__main__":
    update()
    print("Done.")
