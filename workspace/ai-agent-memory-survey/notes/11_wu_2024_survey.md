---
type: paper
title: "Long-term Memory in LLM-Powered Autonomous Agents: A Survey"
aliases: [wu2024survey]
graph:
  - relation: cites
    target: "[[14_zhang_2024_survey]]"
    evidence:
      quote: "Companion to [Zhang et al. 2024, another survey]"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[06_sumers_2024_coala]]"
    evidence:
      quote: "and [Sumers et al. 2024, CoALA framework]"
    note: from §7 Connections of the source paper note
---


# Long-term Memory in LLM-Powered Autonomous Agents: A Survey

- **Citation**: Wu et al. (2024). arXiv:2502.00400. — `Wu et al. 2024`
- **DOI / arXiv**: arXiv:2502.00400
- **Read date**: 2026-07-28 | **Depth**: 速读 (triage — this is a survey, treated as a meta-source for this literature review)
- **One-liner**: A recent survey that organizes the agent-memory landscape into a taxonomy of memory types, mechanisms, and evaluation protocols.

## 1. Research question
A field-mapping survey — what is the current organization of long-term memory in LLM agents, and what categories of mechanisms are in use?

## 2. Method (方法)
- A structured literature review: collect papers, classify along pre-defined axes (memory type, write mechanism, read mechanism, evaluation).
- Comparison table of representative systems.
- Discussion of open problems.

**关键设计**：the **taxonomy** is the contribution; the analytical depth is the standard "survey" depth.

## 3. Contributions (创新点)
- **Claimed**: a comprehensive taxonomy and coverage of the field up to early 2024.
- **Actual (my judgment)**: Useful as a meta-source. Some of its taxonomy overlaps with [Sumers et al. 2024, CoALA], but Wu et al. are more *empirical-system-centric* while CoALA is more *cognitive-architecture-centric*.

## 4. Experimental setup (实验设置)
- None. Survey paper.

## 5. Limitations (局限性)
- **Stated by authors**: limited to early-2024 papers; doesn't cover very recent (2025) systems like [Xu et al. 2025, A-MEM].
- **My assessment**:
  - Survey-of-surveys; the analytical claims are conservative. For this literature review, the main value is **reference-list mining** — many of the 12 primary papers were identified from its bibliography.

## 6. Reusable resources
- **Reusable ideas**: its **taxonomy axes** (memory type, write mechanism, read mechanism, evaluation) are directly useful for building the comparison matrix in this review.

## 7. Connections
- Companion to [Zhang et al. 2024, another survey] and [Sumers et al. 2024, CoALA framework]. The three together cover the field.
- Cites most of the 12 primary papers in this library.

## 8. Open questions / TODO
- Pull the Wu-et-al. taxonomy as a starting point; verify whether CoALA's cognitive-architecture framing covers the same ground.
