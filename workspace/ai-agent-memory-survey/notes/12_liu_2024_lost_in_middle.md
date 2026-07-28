---
type: paper
title: "Lost in the Middle: How Language Models Use Long Contexts"
aliases: [liu2024lostinmiddle]
graph:
  - relation: cites
    target: "[[10_hu_2024_longagent]]"
    evidence:
      quote: "[Hu et al. 2024, LongAgent] is the most direct training-side response"
    note: from §7 Connections of the source paper note
  - relation: cites
    target: "[[02_packer_2023_memgpt]]"
    evidence:
      quote: "[Packer et al. 2023, MemGPT] is the most direct memory-engineering response"
    note: from §7 Connections of the source paper note
---


# Lost in the Middle: How Language Models Use Long Contexts

- **Citation**: Liu et al. (2024). TACL 11: 157–173. — `Liu et al. 2024`
- **DOI / arXiv**: [not verified from PDF, known TACL paper]
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: A controlled study showing that LLMs (open and closed) perform **best on information at the start or end of their context window, and worst in the middle** — establishing the central empirical problem that memory-augmentation is designed to solve.

## 1. Research question
LLMs now claim 100K+ token context windows, but do they actually *use* the entire context uniformly? An earlier intuition suggested they might; an emerging empirical pattern suggested they do not. How robust is the "lost in the middle" effect, across model families, task types, and input lengths?

## 2. Method (方法)
- **Multi-document QA task**: a question is paired with N input documents, one of which contains the answer. The answer's position in the context is varied (beginning / middle / end).
- **Models tested**: open (LLaMA-family), closed (GPT-3.5, Claude), and a range of context-window sizes.
- **Conditions varied**: input length, number of distractor documents, closed-book vs. open-book setting, with and without chain-of-thought.

**关键设计**：the **answer-position manipulation** is the cleanest experimental control in the long-context literature.

## 3. Contributions (创新点)
- **Claimed**: a robust U-shaped position-accuracy curve across model families and tasks; chain-of-thought does not fix it.
- **Actual (my judgment)**: This is one of the most-cited *empirical* findings in the long-context literature. The contribution is the controlled experiment; the *explanation* (U-shaped curve) is descriptive, not mechanistic.

## 4. Experimental setup (实验设置)
- **Data**: NaturalQuestions-based multi-doc QA, manually constructed distractors.
- **Baselines**: random-guess, oracle (model told which document has the answer).
- **Metrics**: accuracy as a function of answer position.
- **Key results** (well-cited; please verify):
  - Performance is highest at positions 0–10% and 90–100% of the context, lowest at 40–60%. `[请人工核对]`
  - Effect persists in GPT-3.5, Claude, and LLaMA-2. `[请人工核对]`
  - Chain-of-thought prompting *does not* close the gap. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: multi-doc QA is one of several long-context tasks; effect magnitude may differ on generation tasks.
- **My assessment**:
  - **Closed-source models** (GPT-4, Claude-3+) are not fully tested in the original paper; subsequent work has shown the effect may be smaller in newer models.
  - The paper does not test **agentic** settings (where the model actively chooses what to read next) — this is the most relevant follow-up.

## 6. Reusable resources
- **Code**: dataset and evaluation scripts released on GitHub `[not verified from PDF]`.
- **Reusable ideas**: the **position-vary multi-doc QA protocol** is now the standard long-context evaluation; any new memory system should be tested against it.

## 7. Connections
- **Empirical foundation** for memory-augmentation work: every memory system in this library is implicitly a workaround for the lost-in-the-middle problem.
- [Hu et al. 2024, LongAgent] is the most direct training-side response.
- [Packer et al. 2023, MemGPT] is the most direct memory-engineering response.

## 8. Open questions / TODO
- Verify the exact U-curve numbers in the original paper.
- Test the effect on **agentic** tasks where the model decides what to read — the assumption that the model passively attends to context may break.
- Re-test on 2024-vintage models (Claude-3.5, GPT-4o, etc.) — has the effect diminished?
