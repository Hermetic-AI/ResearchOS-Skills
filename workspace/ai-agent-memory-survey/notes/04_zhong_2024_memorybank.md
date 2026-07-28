---
type: paper
title: "MemoryBank of LLM"
aliases: [zhong2024memorybank]
graph:
  - relation: extends
    target: "[[01_park_2023_generative_agents]]"
    evidence:
      quote: "Builds on the memory stream of [Park et al. 2023"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[08_maharana_2024_forgetting]]"
    evidence:
      quote: "Compared with [Maharana et al. 2024, Forgetting Curve Theory]"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[09_xu_2025_amem]]"
    evidence:
      quote: "Addressed by [Xu et al. 2025, A-MEM]"
    note: from §7 Connections of the source paper note
---


# MemoryBank: Long-Term Memory for LLM with Ebbinghaus Forgetting Curve

- **Citation**: Zhong et al. (2024). arXiv:2401.09419. — `Zhong et al. 2024`
- **DOI / arXiv**: arXiv:2401.09419
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: Adds a **cognitive-inspired long-term memory** to an LLM chat system by scoring each memory's retention with the Ebbinghaus forgetting curve, periodically re-triggering forgotten items, and selectively merging redundant entries.

## 1. Research question
LLM-based chatbots forget across sessions — a user returns the next day and the bot has no memory of yesterday's conversation. Existing solutions either (a) stuff all history into the prompt (wasteful, doesn't scale), (b) naive retrieval by embedding similarity (ignores *time-based forgetting*). Can a **psychology-grounded retention model** (Ebbinghaus curve + spaced repetition) make long-term memory both more compact and more human-aligned?

## 2. Method (方法)
- **Memory storage**: each interaction is stored as a memory unit with metadata: timestamp, semantic embedding, importance.
- **Ebbinghaus retention score**: a memory's current "strength" decays over time following R = e^(-t/S), where S is a stability parameter (higher S = slower forgetting). Crucially, **access increases S** (the curve flattens after retrieval), implementing spaced repetition.
- **Selective merging**: periodically a "memory manager" LLM call identifies and merges near-duplicate memories to prevent unbounded growth.
- **Two-stage recall**: at query time, (1) fast cosine-similarity retrieval produces a candidate set; (2) the Ebbinghaus-weighted score re-ranks; (3) top-k is returned.

**关键设计**：the **time-decay curve with access-driven stabilization** — this is what differentiates MemoryBank from a vanilla vector-store retrieval.

## 3. Contributions (创新点)
- **Claimed**: (1) introduction of forgetting curve into LLM memory, (2) selective memory merging, (3) long-term dialogue benchmark.
- **Actual (my judgment)**: The contribution is mostly the **integration of cognitive-science memory theory into a deployable system**. The selective merging is an engineering contribution that matters for the system but is not theoretically deep. The benchmark is new and a useful community resource.

## 4. Experimental setup (实验设置)
- **Data**: a long-term dialogue dataset of 200 user-bot conversations over weeks; MSC (Multi-Session Chat) evaluation; LoCoMo `[not verified — confirm dataset names]`.
- **Baselines**: full-context LLM, RAG (vanilla), "no forgetting" MemoryBank variant.
- **Metrics**: BLEU / ROUGE / LLM-judged relevance, plus a "long-term memory probe" (does the bot remember facts from session 1 in session 5).
- **Key results** (please verify):
  - Outperforms full-context baseline on long-term probe. `[请人工核对]`
  - Selective merging reduces memory store size by ~40% with < 2% quality drop. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: forgetting-curve parameters are hand-set; assumes single-user; merging can drop important details.
- **My assessment**:
  - The Ebbinghaus curve parameters (S initial, S increment) are essentially free hyperparameters; the paper does not ablate these — does the result depend on the choice?
  - The long-term probe is operationalized as "does the bot answer a question about session 1" — a narrow construct. What about nuanced contextual recall?
  - Single-user assumption is acknowledged; multi-user agent (where two users have different memories of the same bot) is a real gap.

## 6. Reusable resources
- **Code**: <https://github.com/BAI-LAB/MemoryBank> `[not verified from PDF]`
- **Reusable ideas**: the **decay-with-access-stabilization** scheme is the most useful artifact. It is a 30-line add-on to any retrieval system.

## 7. Connections
- Builds on the memory stream of [Park et al. 2023, Generative Agents] and adds the missing forgetting dimension.
- Compared with [Maharana et al. 2024, Forgetting Curve Theory] in that paper's related work — both are Ebbinghaus-based, but Maharana's framing is theoretical.
- Addressed by [Xu et al. 2025, A-MEM] which generalizes the idea to note-organization with LLMs.

## 8. Open questions / TODO
- Verify dataset names and the 40% memory-reduction number.
- Test the forgetting-curve hyperparameters: does the system hold up if we replace e^(-t/S) with linear decay?
- Extend to multi-user agents where each user has a separate memory store.
