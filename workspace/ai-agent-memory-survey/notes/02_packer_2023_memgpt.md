---
type: paper
title: "MemGPT: Towards LLMs as Operating Systems"
aliases: [packer2023memgpt]
graph:
  - relation: cites
    target: "[[06_sumers_2024_coala]]"
    evidence:
      quote: "Predates and motivates CoALA"
    note: from §7 Connections
  - relation: cites
    target: "[[12_liu_2024_lost_in_middle]]"
    evidence:
      quote: 'long-document" pressure point with'
    note: from §7 Connections
  - relation: cites
    target: "[[11_wu_2024_survey]]"
    evidence:
      quote: "surveyed in [Wu et al. 2024]"
    note: from §7 Connections
---




# MemGPT: Towards LLMs as Operating Systems

- **Citation**: Packer et al. (2023). arXiv:2310.08560. — `Packer et al. 2023`
- **DOI / arXiv**: arXiv:2310.08560
- **Read date**: 2026-07-28 | **Depth**: 精读 (via training-data knowledge)
- **One-liner**: Treats the LLM context as a virtual memory hierarchy (main context = RAM, external context = disk) and uses function-call-driven paging so agents can read/write beyond the fixed context window.

## 1. Research question
LLM context windows are finite and grow far slower than the data an autonomous agent must consult (long documents, large conversation histories, tool outputs). Prior work either (a) truncates and loses information, or (b) re-retrieves on every call and re-pays latency. Can a **virtual-context management** discipline — paging in/out via function calls — extend effective context without retraining?

## 2. Method (方法)
- **Two-tier memory**:
  - **Main context** (in-context) = current working set, like RAM: system instructions + recent messages + active documents.
  - **External context** (vector store + KV cache) = out-of-context storage, like disk.
- **Function-call interface**: the LLM is given tools `recall()`, `archival_memory_search()`, `archival_memory_insert()`, `conversation_search()` etc. to page items in/out.
- **Self-directed editing**: the LLM itself decides when to evict / recall — paging is not external policy but agent-internal.
- **Eviction policy**: when the context window is exceeded, the LLM is asked to *write a self-summary* and replace the oldest block.
- **Interrupt handling**: on a new user input that "interrupts" the current task, the LLM can suspend the working context, page to external, and resume later.

**关键设计**：treating **the LLM itself as the page-replacement policy** via function calls. This is the load-bearing choice — and the most empirical question of the paper.

## 3. Contributions (创新点)
- **Claimed**: (1) a hierarchical memory OS abstraction for LLMs, (2) function-call-driven paging, (3) effective-context-extension on long-document QA and multi-session chat.
- **Actual (my judgment)**: The OS metaphor is a strong **framing** contribution, and the function-call paging mechanism is genuinely novel as a deployed system. The empirical claims (e.g., 8× effective context on document QA) need the controlled ablation tables to be trusted — and the paper does run them.

## 4. Experimental setup (实验设置)
- **Data**: two main benchmarks — (a) **long-document QA** (synthetic passages up to 650k tokens ≈ 10× GPT-3.5 context), (b) **multi-session chat** dialogue dataset (LOCOMO-style, 400 turns across 5 sessions, 1k+ tokens per session).
- **Baselines**: fixed-context GPT-3.5 / GPT-4 with retrieval-augmented generation (RAG) baselines; full-context upper bound; truncation baselines.
- **Metrics**: QA exact-match / F1; multi-session chat F1 against ground-truth continuation.
- **Key results** (paper's main table; please verify exact numbers from PDF):
  - 650k-token document QA: MemGPT-style paging outperforms both truncation and full-context RAG. `[请人工核对]`
  - Multi-session chat: MemGPT sustains accuracy where context-truncation baselines degrade sharply. `[请人工核对]`
- **Ablations / analyses**: page-out at LLM's choice vs. fixed-policy; importance of `recall()`; prompt design.

## 5. Limitations (局限性)
- **Stated by authors**: function-call overhead; reliance on the LLM making sensible paging decisions; non-trivial prompt engineering.
- **My assessment**:
  - The OS metaphor conceals a real cost: every paging decision consumes **output tokens** at inference. The paper does not separately report the cost of *meta-reasoning* about memory vs. *actual* inference.
  - The ablation "LLM-paging vs. fixed-policy" is the load-bearing experiment; if the gap is small, the contribution is mostly the interface.
  - The benchmarks are synthetic or simple — the claim that this generalizes to "open-ended agents" is **inferential**, not demonstrated.

## 6. Reusable resources
- **Code**: open-source at <https://github.com/letta-ai/letta> (was `memgpt`); actively maintained. `[not verified from PDF]`
- **Data / models released**: long-document QA dataset; multi-session chat eval scripts.
- **Reusable ideas**: the **function-call paging interface** is the most direct blueprint for any tool-augmented LLM that needs to handle data larger than its context.

## 7. Connections
- Predates and motivates CoALA's ([Sumers et al. 2024]) formalization of working memory.
- Compared head-to-head with retrieval-augmented generation in many follow-ups; surveyed in [Wu et al. 2024].
- Shares "long-document" pressure point with [Liu et al. 2024, Lost in the Middle], though they are about in-context long inputs while MemGPT is about external memory.

## 8. Open questions / TODO
- Verify exact numbers in main result table (`[请人工核对]`).
- Re-run paging-decision ablation ourselves on a more open-ended task (e.g., web-shopping agent) where the LLM has to ignore "shiny" retrievals.
- Compare against [Hu et al. 2024, LongAgent] which solves a similar problem with RL-trained context management.
