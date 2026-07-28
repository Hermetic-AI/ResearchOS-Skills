#!/usr/bin/env python3
"""Batch-add YAML frontmatter to all reading notes.

Each note gets a paper-typed frontmatter with a graph: relations list, using
verbatim quote snippets already present in the body so build_graph.py can
verify them.
"""
import os
import re
from pathlib import Path

NOTES = Path(__file__).parent

# (filename_stem, [list of (relation, target, evidence_quote) tuples])
# quotes must be exact substrings of the body text.
FRONTMATTERS = {
    "01_park_2023_generative_agents": {
        "title": "Generative Agents: Interactive Simulacra of Human Behavior",
        "aliases": ["Park2023", "GenerativeAgents"],
        "graph": [
            ("uses-dataset", "[[Smallville]]", "Smallville sandbox, 25 agents, 2 days"),
            ("cites", "[[04_zhong_2024_memorybank]]", "MemoryBank is explicit about building on this"),
            ("cites", "[[05_wang_2024_voyager]]", "shares the \"long-horizon social\" goal with"),
            ("cites", "[[06_sumers_2024_coala]]", "CoALA later formalizes what Park et al. instantiate"),
        ],
    },
    "02_packer_2023_memgpt": {
        "title": "MemGPT: Towards LLMs as Operating Systems",
        "aliases": ["Packer2023", "MemGPT"],
        "graph": [
            ("cites", "[[06_sumers_2024_coala]]", "Predates and motivates CoALA"),
            ("cites", "[[12_liu_2024_lost_in_middle]]", "Shares \"long-document\" pressure point with"),
            ("cites", "[[10_hu_2024_longagent]]", "Compare against LongAgent which solves a similar problem"),
        ],
    },
    "03_shinn_2023_reflexion": {
        "title": "Reflexion: Language Agents with Verbal Reinforcement Learning",
        "aliases": ["Shinn2023", "Reflexion"],
        "graph": [
            ("cites", "[[06_sumers_2024_coala]]", "The Reflection pattern reappears in"),
            ("cites", "[[02_packer_2023_memgpt]]", "Shares \"no weight updates\" stance with"),
            ("cites", "[[10_hu_2024_longagent]]", "Compared against LongAgent in follow-ups"),
        ],
    },
    "04_zhong_2024_memorybank": {
        "title": "MemoryBank of LLM",
        "aliases": ["Zhong2024", "MemoryBank"],
        "graph": [
            ("extends", "[[01_park_2023_generative_agents]]", "Builds on the memory stream of Park et al."),
            ("cites", "[[08_maharana_2024_forgetting]]", "Compared with Maharana et al. in that paper's related work"),
            ("cites", "[[09_xu_2025_amem]]", "Addressed by A-MEM which generalizes the idea"),
        ],
    },
    "05_wang_2024_voyager": {
        "title": "Voyager: An Open-Ended Embodied Agent with LLMs",
        "aliases": ["Wang2024", "Voyager"],
        "graph": [
            ("cites", "[[01_park_2023_generative_agents]]", "Direct successor of LLM-as-curriculum"),
            ("cites", "[[06_sumers_2024_coala]]", "Categorized in CoALA as a procedural-memory agent"),
            ("cites", "[[03_shinn_2023_reflexion]]", "Reflexion's reflections could be Voyager's next-skill generation signals"),
        ],
    },
    "06_sumers_2024_coala": {
        "title": "Cognitive Architectures for Language Agents (CoALA)",
        "aliases": ["Sumers2024", "CoALA"],
        "graph": [
            ("cites", "[[01_park_2023_generative_agents]]", "The framework subsumes Park et al."),
            ("cites", "[[05_wang_2024_voyager]]", "The framework subsumes Voyager"),
            ("cites", "[[04_zhong_2024_memorybank]]", "The framework subsumes MemoryBank"),
            ("cites", "[[11_wu_2024_survey]]", "Frequently cited alongside Wu et al."),
        ],
    },
    "07_qian_2024_chatdev": {
        "title": "ChatDev: A Sociable Software Development Framework",
        "aliases": ["Qian2024", "ChatDev"],
        "graph": [
            ("cites", "[[11_wu_2024_survey]]", "One of the first multi-agent SE frameworks; precedes Wu et al."),
        ],
    },
    "08_maharana_2024_forgetting": {
        "title": "Forgetting Curve Theory for Memory-Augmented LLMs",
        "aliases": ["Maharana2024", "ForgettingCurve"],
        "graph": [
            ("cites", "[[04_zhong_2024_memorybank]]", "Cross-cite with MemoryBank"),
        ],
    },
    "09_xu_2025_amem": {
        "title": "A-MEM: Agentic Memory for LLM Agents",
        "aliases": ["Xu2025", "AMem"],
        "graph": [
            ("extends", "[[01_park_2023_generative_agents]]", "Builds on the declarative-memory tradition"),
            ("extends", "[[13_modarressi_2024_retllm]]", "Lifts the schema constraint of Modarressi"),
            ("cites", "[[06_sumers_2024_coala]]", "A practical implementation of CoALA"),
        ],
    },
    "10_hu_2024_longagent": {
        "title": "LongAgent: Scaling Language Agents to 128K Context through Multi-Stage RL",
        "aliases": ["Hu2024", "LongAgent"],
        "graph": [
            ("cites", "[[12_liu_2024_lost_in_middle]]", "Addresses the empirical finding of Liu et al. from the training side"),
            ("cites", "[[02_packer_2023_memgpt]]", "Direct contrast to memory-augmentation approaches"),
            ("cites", "[[11_wu_2024_survey]]", "Cited as a counterpoint in Wu et al."),
        ],
    },
    "12_liu_2024_lost_in_middle": {
        "title": "Lost in the Middle: How Language Models Use Long Contexts",
        "aliases": ["Liu2024", "LostInTheMiddle"],
        "graph": [
            ("cites", "[[10_hu_2024_longagent]]", "Hu et al. is the most direct training-side response"),
            ("cites", "[[02_packer_2023_memgpt]]", "Packer et al. is the most direct memory-engineering response"),
        ],
    },
    "13_modarressi_2024_retllm": {
        "title": "RET-LLM: Towards a General Read-Write Memory for LLMs",
        "aliases": ["Modarressi2024", "RetLLM"],
        "graph": [
            ("cites", "[[09_xu_2025_amem]]", "Architectural ancestor of A-MEM"),
            ("cites", "[[02_packer_2023_memgpt]]", "Many later systems are variations on this idea"),
        ],
    },
    "11_wu_2024_survey": {
        "title": "Long-term Memory in LLM-Powered Autonomous Agents: A Survey",
        "aliases": ["Wu2024", "WuSurvey"],
        "graph": [
            ("cites", "[[14_zhang_2024_survey]]", "Companion to Zhang et al."),
            ("cites", "[[06_sumers_2024_coala]]", "Companion to CoALA framework"),
        ],
    },
    "14_zhang_2024_survey": {
        "title": "A Survey on the Memory Mechanism of LLM-based Agents",
        "aliases": ["Zhang2024", "ZhangSurvey"],
        "graph": [
            ("cites", "[[11_wu_2024_survey]]", "Direct companion to Wu et al."),
            ("cites", "[[06_sumers_2024_coala]]", "Direct companion to CoALA"),
        ],
    },
}


def add_frontmatter():
    for stem, spec in FRONTMATTERS.items():
        path = NOTES / f"{stem}.md"
        if not path.exists():
            print(f"  SKIP (not found): {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            print(f"  SKIP (already has fm): {path.name}")
            continue

        graph_lines = []
        for relation, target, quote in spec["graph"]:
            graph_lines.append(f"  - relation: {relation}")
            graph_lines.append(f"    target: \"{target}\"")
            graph_lines.append("    evidence:")
            graph_lines.append(f"      quote: \"{quote}\"")
            graph_lines.append(f"    note: from reading-note §7 Connections")

        aliases_yaml = ", ".join(spec["aliases"])
        fm = (
            "---\n"
            "type: paper\n"
            f"title: \"{spec['title']}\"\n"
            f"aliases: [{aliases_yaml}]\n"
            "graph:\n"
            + "\n".join(graph_lines)
            + "\n---\n\n"
        )
        new_text = fm + text
        path.write_text(new_text, encoding="utf-8")
        print(f"  OK: {path.name} (+{new_text.count(chr(10))} lines)")


if __name__ == "__main__":
    add_frontmatter()
    print("Done.")
