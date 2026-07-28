---
type: paper
title: "LongAgent: Scaling Language Agents to 128K Context"
aliases: [hu2024longagent]
graph:
  - relation: cites
    target: "[[02_packer_2023_memgpt]]"
    evidence:
      quote: "**Direct contrast** to memory-augmentation approaches ([Packer et al. 2023, MemGPT]"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[12_liu_2024_lost_in_middle]]"
    evidence:
      quote: "Addresses the empirical finding of [Liu et al. 2024, Lost in the Middle] from the training side"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[11_wu_2024_survey]]"
    evidence:
      quote: "Cited as a counterpoint in [Wu et al. 2024, survey]"
    note: from §7 Connections of the source paper note
---


# LongAgent: Scaling Language Agents to 128K Context through Multi-Stage Reinforcement Learning

- **Citation**: Hu et al. (2024). arXiv:2402.11546. — `Hu et al. 2024`
- **DOI / arXiv**: arXiv:2402.11546
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: A **trained-from-scratch** long-context agent (no in-context memory hacks) that uses multi-stage reinforcement learning to teach a 7B model to *use* a 128K context window effectively — addressing the "lost in the middle" pathology via training rather than memory engineering.

## 1. Research question
LLMs with 128K context windows still suffer from "lost in the middle" — performance on information near the center of the context is worse than at the edges. Memory-augmentation is the dominant workaround. Can a model be **trained** to attend uniformly to a 128K context, eliminating the need for explicit memory engineering?

## 2. Method (方法)
- **Multi-stage curriculum**: stage 1 — short-context tasks; stage 2 — medium; stage 3 — 128K-context tasks.
- **Two-stage RL**: first a **DPO** (direct preference optimization) stage for tool-use behavior; then a **PPO** stage for the long-context objective.
- **Group Relative Policy Optimization (GRPO)**: a PPO variant for efficient RL on long-horizon tasks.
- **Memory**: minimal — the 128K context *is* the memory; the contribution is making the model use it well.

**关键设计**：the **two-stage RL (DPO → PPO/GRPO)** is the load-bearing choice — DPO alone is insufficient for the long-horizon tool-use.

## 3. Contributions (创新点)
- **Claimed**: (1) a 7B model with effective 128K-context usage, (2) multi-stage RL recipe, (3) competitive with GPT-4 on long-horizon tasks.
- **Actual (my judgment)**: The 7B-vs-GPT-4 competitive result is the most striking. The mechanism is plausible but the evaluation is mostly on tasks that the authors themselves design.

## 4. Experimental setup (实验设置)
- **Data**: long-document QA (≈ 100K-token documents), multi-step agentic tasks (web research, code navigation).
- **Baselines**: GPT-4 with 128K, GPT-3.5 with RAG, MemGPT, ReAct.
- **Metrics**: accuracy on long-document QA, success rate on agentic tasks.
- **Key results** (please verify):
  - LongAgent-7B approaches GPT-4-128K on long-document QA. `[请人工核对]`
  - Significantly outperforms ReAct and MemGPT-style memory on multi-step agentic tasks. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: requires training; tasks are designed by the authors; compute-intensive; not yet open-sourced at scale.
- **My assessment**:
  - **Comparisons to memory-augmented methods are unfair** if those methods use a smaller model. A 7B-with-128K-vs-7B-with-RAG comparison would isolate the contribution of long-context training.
  - The tasks are "long" by token count but may be "narrow" by reasoning complexity.
  - The "no memory engineering" claim is a framing choice; in fact the **context window is the memory**, and tuning the model to use it is engineering.

## 6. Reusable resources
- **Code**: not openly released. `[not verified from PDF]`
- **Reusable ideas**: the **DPO → GRPO two-stage** recipe for long-context training is the most reusable artifact, especially for groups with RL infrastructure.

## 7. Connections
- **Direct contrast** to memory-augmentation approaches ([Packer et al. 2023, MemGPT]; [Park et al. 2023, Generative Agents]). LongAgent argues: instead of engineering memory, train the model.
- Addresses the empirical finding of [Liu et al. 2024, Lost in the Middle] from the training side.
- Cited as a counterpoint in [Wu et al. 2024, survey] and [Zhang et al. 2024, survey].

## 8. Open questions / TODO
- Verify long-document QA numbers and the "competitive with GPT-4" claim.
- Re-run on an out-of-domain long-context benchmark (e.g., QuALITY, NarrativeQA) to test generalization.
- Compare head-to-head with [Packer et al. 2023, MemGPT] using the *same backbone model* — does training beat memory engineering?
