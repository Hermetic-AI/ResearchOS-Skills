---
type: paper
title: "Voyager: An Open-Ended Embodied Agent with LLMs"
aliases: [wang2024voyager]
graph:
  - relation: cites
    target: "[[03_shinn_2023_reflexion]]"
    evidence:
      quote: "Pairs with [Shinn et al. 2023, Reflexion]"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[06_sumers_2024_coala]]"
    evidence:
      quote: "Categorized in [Sumers et al. 2024, CoALA] as a procedural-memory agent"
    note: from §7 Connections of the source paper note
---


# Voyager: An Open-Ended Embodied Agent with Large Language Models

- **Citation**: Wang et al. (2024). TMLR. — `Wang et al. 2024`
- **DOI / arXiv**: arXiv:2305.16291 `[not verified from PDF]`
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: A Minecraft agent that uses GPT-4 to propose increasingly difficult tasks, write code, and **curate a growing skill library** as its memory; over thousands of in-game items the agent compounds skills without weight updates.

## 1. Research question
Embodied agents in open environments (Minecraft) need to acquire a continually expanding repertoire of skills. Hand-engineering curricula and skills does not scale. Can an LLM, used as a curriculum proposer and a code generator, drive a long-horizon embodied agent that **accumulates a skill memory over time**?

## 2. Method (方法)
- **Curriculum (automatic task generation)**: GPT-4 is prompted with the agent's current state and previous tasks to propose the next-most-useful task, in natural language, conditioned on an "in-context curriculum" of prior attempts.
- **Skill library**: a persistent, indexed store of (a) executable JavaScript code and (b) natural-language description per skill. Each skill is **a piece of code**, not a behavior trace.
- **Iterative improvement**: when a skill execution fails, GPT-4 is asked to refine the code; the refined version replaces the old one.
- **Retrieval**: at decision time, an embedding-based retriever surfaces relevant existing skills given the current task description.

**关键设计**：the skill is a **code snippet**, not a free-form text note. This makes the memory **executable**, which is rare in the agent-memory literature.

## 3. Contributions (创新点)
- **Claimed**: (1) LLM-driven automatic curriculum, (2) code-as-skill memory, (3) state-of-the-art in Minecraft tech-tree acquisition.
- **Actual (my judgment)**: All three are genuine. The code-as-skill design is the most portable contribution; the curriculum is a more domain-specific innovation. The Minecraft results are a strong demonstration but Minecraft-specific.

## 4. Experimental setup (实验设置)
- **Environment**: Minecraft (via Mineflayer JavaScript API).
- **Tasks**: 314 in-game items, tech-tree acquisition (wood → tools → diamond → netherite).
- **Metrics**: number of unique items collected, tech-tree milestone progress, diversity of skills in the library.
- **Baselines**: ReAct-style LLM agent, Auto-GPT variants, prior SOTA MineAgent `[verify]`.
- **Key results** (please verify):
  - Voyager collects 3.3× more unique items than the strongest baseline. `[请人工核对]`
  - Skill library size grows to 200+ complex skills. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: depends on code-generation quality; bounded by Minecraft API capabilities; skill library grows without consolidation.
- **My assessment**:
  - **No long-term forgetting or consolidation**: skills are only added, never pruned or generalized. A real-world agent with this memory would run out of storage.
  - Minecraft success does not imply general embodied-agent success. The "open-ended" framing may overgeneralize from a single environment.
  - **No negative results reported**: when does the curriculum proposer get stuck or loop?

## 6. Reusable resources
- **Code**: <https://github.com/MineDojo/Voyager> `[not verified from PDF]`
- **Reusable ideas**: the **executable skill as memory unit** is the most copy-worthy idea. It is the right level of abstraction for any agent that must *do* things, not just talk.

## 7. Connections
- Direct successor of LLM-as-curriculum in prior work (e.g., SPRING); reframes memory as **code** rather than text.
- Pairs with [Shinn et al. 2023, Reflexion]: Reflexion's reflections could be Voyager's next-skill generation signals.
- Categorized in [Sumers et al. 2024, CoALA] as a procedural-memory agent.

## 8. Open questions / TODO
- Verify 3.3× item-collection claim.
- A version with skill **consolidation / generalization** (e.g., abstract common code into a library function) — does it help or hurt?
- What if the code executor fails silently? A fault-tolerance layer on top of the skill library.
