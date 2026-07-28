---
type: paper
title: "A Survey on the Memory Mechanism of LLM-based Agents"
aliases: [zhang2024survey]
graph:
  - relation: cites
    target: "[[11_wu_2024_survey]]"
    evidence:
      quote: "Direct companion to [Wu et al. 2024]"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[06_sumers_2024_coala]]"
    evidence:
      quote: "and [Sumers et al. 2024, CoALA]"
    note: from §7 Connections of the source paper note
---


# A Survey on the Memory Mechanism of LLM-based Agents

- **Citation**: Zhang et al. (2024). arXiv:2501.00357. — `Zhang et al. 2024`
- **DOI / arXiv**: arXiv:2501.00357
- **Read date**: 2026-07-28 | **Depth**: 速读 (triage — survey, meta-source)
- **One-liner**: Another recent survey on agent memory; more detailed taxonomy of **memory operations** (write, read, manage) than Wu et al.

## 1. Research question
Same as Wu et al. (2024) — a structured map of LLM-agent memory mechanisms. Different angle: focuses on the **operational decomposition** (write/read/manage) rather than the type taxonomy.

## 2. Method (方法)
- Decomposes memory into three operational phases: **memory writing** (what to store), **memory reading** (how to retrieve), **memory management** (consolidation, forgetting, indexing).
- Reviews representative systems under each phase.
- Discusses evaluation and benchmarks.

**关键设计**：the **operational decomposition** is a useful complement to Wu-et-al.'s type taxonomy.

## 3. Contributions (创新点)
- **Claimed**: a structured review with operation-level decomposition.
- **Actual (my judgment)**: Together with [Wu et al. 2024] and [Sumers et al. 2024, CoALA], forms the *three survey-level references* any agent-memory review should anchor on.

## 4. Experimental setup (实验设置)
- None. Survey paper.

## 5. Limitations (局限性)
- **Stated by authors**: rapid field evolution; taxonomy may need updates.
- **My assessment**:
  - Overlaps heavily with Wu et al. and CoALA. The added value is the operational decomposition, which is **directly useful** for the taxonomy section of this review.

## 6. Reusable resources
- **Reusable ideas**: the **write / read / manage** axis is the most directly useful framing for organizing the comparison matrix.

## 7. Connections
- Direct companion to [Wu et al. 2024] and [Sumers et al. 2024, CoALA].
- Cites most of the 12 primary papers in this library.

## 8. Open questions / TODO
- Mine the bibliography for any primary papers this review has missed.
