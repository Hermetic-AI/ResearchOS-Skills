---
type: paper
title: "RET-LLM: Towards a General Read-Write Memory for LLMs"
aliases: [modarressi2024retllm]
graph:
  - relation: cites
    target: "[[09_xu_2025_amem]]"
    evidence:
      quote: "Architectural ancestor of [Xu et al. 2025, A-MEM]"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[02_packer_2023_memgpt]]"
    evidence:
      quote: "and [Packer et al. 2023, MemGPT] (with different retrieval styles)"
    note: from §7 Connections of the source paper note
---


# RET-LLM: Towards a General Read-Write Memory for Large Language Models

- **Citation**: Modarressi et al. (2024). arXiv:2305.14322. — `Modarressi et al. 2024`
- **DOI / arXiv**: arXiv:2305.14322
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: Equips an LLM with a **read-write memory** through a controller that ingests conversational context into a structured memory store and retrieves from it via natural-language query — an early architectural blueprint for ChatGPT-style long-term memory.

## 1. Research question
Conversational LLMs forget across sessions. Naive retrieval augmentation (store every turn, retrieve on each query) is wasteful. Can a **controller-based read-write memory** — where an LLM writes structured memory entries and another LLM retrieves them with natural-language queries — provide more compact, more useful long-term conversational memory?

## 2. Method (方法)
- **Memory controller**: an LLM is given the conversational turn and asked to produce a **structured memory entry** with fields (e.g., "user fact", "preference", "experience summary") and a **natural-language query** for retrieval.
- **Memory store**: a collection of (memory entry, NL query) pairs indexed by the NL query's embedding.
- **Retriever controller**: an LLM is given the user's current turn and produces a NL query to fetch the top-k memory entries.
- **Two-controller pattern**: separate LLMs (or roles) for writing and reading.

**关键设计**：the **structured memory entry** — a fixed but extensible schema — keeps memory items comparable and queryable.

## 3. Contributions (创新点)
- **Claimed**: (1) a general read-write memory architecture, (2) a memory controller LLM, (3) outperforms vanilla RAG on long-term dialogue tasks.
- **Actual (my judgment)**: The architecture is sound and has been independently re-discovered in many later systems (ChatGPT's "Memory" feature, MemGPT, etc.). The contribution is mostly *architectural*; the experiments are limited.

## 4. Experimental setup (实验设置)
- **Data**: LoCoMo `[verify]` or a similar long-conversation dataset.
- **Baselines**: full-prompt, vanilla RAG, "no memory".
- **Metrics**: response quality (LLM-judged), F1 on long-term probe questions.
- **Key results** (please verify):
  - Outperforms vanilla RAG by a meaningful margin on long-term dialogue benchmarks. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: limited schema; controller-LLM adds latency and cost; not tested on long-horizon multi-session scenarios.
- **My assessment**:
  - The "structured memory entry" idea is the right one, but the schema is too rigid — [Xu et al. 2025, A-MEM]'s dynamic schema is a generalization.
  - The paper predates many of the better long-conversation benchmarks; results may not generalize to current datasets.

## 6. Reusable resources
- **Code**: not openly released. `[not verified from PDF]`
- **Reusable ideas**: the **read / write memory controller** template is the most importable. Many later systems are variations on this idea.

## 7. Connections
- Architectural ancestor of [Xu et al. 2025, A-MEM] and [Packer et al. 2023, MemGPT] (with different retrieval styles).
- One of the first to articulate the "read-write" framing for LLM memory.
- Discussed in [Wu et al. 2024, survey] as a foundational work.

## 8. Open questions / TODO
- Verify the LoCoMo result and the baseline gap.
- Re-implement with current models; how much of the gap remains?
- Test the read-write loop on agentic (not just conversational) settings.
