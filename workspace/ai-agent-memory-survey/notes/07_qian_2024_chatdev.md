---
type: paper
title: "ChatDev: A Sociable Software Development Framework"
aliases: [qian2024chatdev]
graph:
  - relation: cites
    target: "[[11_wu_2024_survey]]"
    evidence:
      quote: "precedes [Wu et al. 2024, survey]'s categorization"
    note: from §7 Connections of the source paper note
---


# ChatDev: A Sociable Software Development Framework Using LLM-Powered Multi-Agent Systems

- **Citation**: Qian et al. (2024). IEEE TSE. — `Qian et al. 2024`
- **DOI / arXiv**: arXiv:2307.07924 `[not verified from PDF]`
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: A multi-agent software-engineering framework where specialized agents (CEO, CTO, programmer, tester, reviewer) collaborate in a **chat-chain workflow** with a **communicative dehallucination** memory mechanism that records cross-agent dialogues for reuse.

## 1. Research question
Software development is a multi-role, multi-step process; can a **multi-agent LLM system** with a structured role-based communication protocol complete end-to-end software development tasks more reliably than a single LLM? And what kind of memory, shared across roles, is needed?

## 2. Method (方法)
- **Chat chain**: a directed graph of phases (Design → Coding → Testing → Review), each phase a chat between multiple role-specific LLM agents.
- **Communicative dehallucination**: when an agent produces an instruction or piece of code, peer agents in the same chat may challenge, refine, or replace it. The resulting **resolved content** is stored as memory.
- **Memory layers**: (a) per-chat short-term memory (current chat), (b) cross-chat memory (accumulated decisions, conventions used in prior tasks).
- **Roles**: CEO, CTO, programmer, reviewer, tester (configurable).

**关键设计**：the **peer-review-as-memory** pattern — a memory entry is only as good as the social check that produced it.

## 3. Contributions (创新点)
- **Claimed**: (1) end-to-end multi-agent SE workflow, (2) communicative dehallucination, (3) empirical improvement over single-LLM baselines on completeness, executability, and consistency of generated code.
- **Actual (my judgment)**: The framework is a clean *systems* contribution. The empirical gains are real but on a **synthetic benchmark**; the more interesting question is whether it generalizes. The communicative-dehallucination mechanism is a useful pattern for any multi-agent setting.

## 4. Experimental setup (实验设置)
- **Data**: SRDD (Software Requirements Description Dataset) `[verify]`, plus generated requirements; ~70 software development tasks.
- **Baselines**: single-agent GPT-4, naive multi-agent (no chat chain).
- **Metrics**: completeness, executability, consistency, code quality (human-rated), pass rate of generated code.
- **Key results** (please verify):
  - Multi-agent + chat chain outperforms single-agent GPT-4 on completeness and executability by double-digit percentages. `[请人工核对]`
  - Communicative dehallucination removes a non-trivial fraction of hallucinated APIs / function names. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: many LLM calls per task; depends on role-prompt design; tasks are toy-sized.
- **My assessment**:
  - The benchmark is hand-crafted and small; **the absence of variance reporting** is a weakness.
  - The "communicative dehallucination" effect is confounded with *more LLM calls* — a baseline that simply asks the same LLM twice and takes the better of two might close some of the gap.
  - Real-world SE is not just code generation; the paper is silent on maintenance, refactoring, and multi-file reasoning.

## 6. Reusable resources
- **Code**: <https://github.com/OpenBMB/ChatDev> `[not verified from PDF]`
- **Reusable ideas**: the **chat-chain workflow + cross-role review-as-memory** is a clean pattern. The paper is a useful template for any domain where multiple roles contribute (scientific writing, customer support, etc.).

## 7. Connections
- One of the first multi-agent SE frameworks; precedes [Wu et al. 2024, survey]'s categorization of multi-agent memory.
- Shares the cross-agent communication idea with MetaGPT `[verify]`, but ChatDev's chat chain is more domain-specific.

## 8. Open questions / TODO
- Verify dataset size and the executability gain.
- Compare communicative dehallucination against a "majority vote" baseline (same compute, no memory).
- Does the framework scale to repositories with hundreds of files?
