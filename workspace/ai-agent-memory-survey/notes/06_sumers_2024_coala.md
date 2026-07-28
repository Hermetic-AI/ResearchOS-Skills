---
type: paper
title: "Cognitive Architectures for Language Agents (CoALA)"
aliases: [sumers2024coala]
graph:
  - relation: cites
    target: "[[01_park_2023_generative_agents]]"
    evidence:
      quote: "[Park et al. 2023] is declarative-memory-heavy"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[05_wang_2024_voyager]]"
    evidence:
      quote: "[Wang et al. 2024, Voyager] is procedural-memory-heavy"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[04_zhong_2024_memorybank]]"
    evidence:
      quote: "[Zhong et al. 2024, MemoryBank] is declarative+conditional"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[11_wu_2024_survey]]"
    evidence:
      quote: "Frequently cited alongside [Wu et al. 2024, survey]"
    note: from §7 Connections of the source paper note
---


# Cognitive Architectures for Language Agents (CoALA)

- **Citation**: Sumers et al. (2024). TMLR. — `Sumers et al. 2024`
- **DOI / arXiv**: arXiv:2309.02427 `[not verified from PDF]`
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: A **conceptual framework** that maps the classical cognitive-architecture concepts (working memory, long-term memory, procedural memory, action space, decision-making) onto LLM agents — proposing a vocabulary rather than a method.

## 1. Research question
The LLM-agent literature is fragmenting into ad-hoc mechanisms (memory streams, tool calls, scratchpads, reflexion buffers, skill libraries) without a shared vocabulary. Is there a **principled design space** that subsumes them — and does that design space reveal gaps?

## 2. Method (方法)
- A **conceptual proposal**, not an empirical method. The paper:
  1. Reviews the cognitive-architecture tradition (SOAR, ACT-R, CLARION) and identifies concepts that map cleanly to LLM agents.
  2. Defines a **language-agent cognitive architecture** with components: perception, working memory, long-term memory (declarative, procedural, conditional), action space, decision procedure.
  3. Classifies existing agent papers against the framework to show coverage and gaps.
  4. Argues that the framework suggests concrete research directions (e.g., conditional memory, explicit metacognition).

**关键设计**：the **proposal itself is the contribution**. The framework's value is in its reusability, not in any specific empirical result.

## 3. Contributions (创新点)
- **Claimed**: a unified conceptual framework for LLM agents, with implications for evaluation and research direction.
- **Actual (my judgment)**: This is the most **cited-and-quoted** framework paper in the field for a reason: the vocabulary has stuck. The actual *technical* contribution is minimal (no method, no metric, no benchmark). The contribution is **organizational**.

## 4. Experimental setup (实验设置)
- None. This is a position / framework paper.
- **Ablations / analyses**: the paper does offer a structured comparison of existing agents against the CoALA framework — useful as a "landscape map" but not a controlled experiment.

## 5. Limitations (局限性)
- **Stated by authors**: many design choices are underspecified; framework is not yet operationalized into a benchmark.
- **My assessment**:
  - The framework's most useful cell — *conditional memory* (memory that is only retrieved when a condition holds) — is underpopulated. Real implementations of conditional memory in LLM agents are scarce.
  - The framework is silent on **evaluation**. How do you know one CoALA instantiation is better than another? The paper does not solve this, and the field has not either.
  - The "decision procedure" category collapses several distinct mechanisms (chain-of-thought, planning, tool selection) into one — useful as taxonomy, but obscures the engineering differences.

## 6. Reusable resources
- **Code**: framework is a paper, not code.
- **Reusable ideas**: the **declarative / procedural / conditional / working** memory taxonomy is the most directly copyable artifact. It is the vocabulary this survey will adopt.

## 7. Connections
- The framework **subsumes** all the empirical papers in this library: [Park et al. 2023] is declarative-memory-heavy; [Wang et al. 2024, Voyager] is procedural-memory-heavy; [Zhong et al. 2024, MemoryBank] is declarative+conditional.
- Frequently cited alongside [Wu et al. 2024, survey] and [Zhang et al. 2024, survey] as the conceptual backbone.

## 8. Open questions / TODO
- Build an empirical benchmark that operationalizes one axis of CoALA (e.g., conditional memory) — does the framework make testable predictions?
- Compare CoALA's memory taxonomy to that in [Packer et al. 2023, MemGPT]; there is overlap but no direct alignment.
