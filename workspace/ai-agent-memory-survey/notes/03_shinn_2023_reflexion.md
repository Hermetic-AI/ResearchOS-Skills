---
type: paper
title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
aliases: [shinn2023reflexion]
graph:
  - relation: cites
    target: "[[06_sumers_2024_coala]]"
    evidence:
      quote: "the Reflection pattern reappears in"
    note: from §7 Connections
  - relation: cites
    target: "[[02_packer_2023_memgpt]]"
    evidence:
      quote: "no weight updates"
    note: from §7 Connections
  - relation: cites
    target: "[[10_hu_2024_longagent]]"
    evidence:
      quote: "Compared against [Hu et al. 2024, LongAgent] in follow-ups"
    note: from §7 Connections
---




# Reflexion: Language Agents with Verbal Reinforcement Learning

- **Citation**: Shinn et al. (2023). NeurIPS 2023. — `Shinn et al. 2023`
- **DOI / arXiv**: arXiv:2303.11366 `[not verified from PDF]`
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: Agents reflect in natural language on their failed trajectories and store those reflections in an **episodic memory buffer** that conditions the next attempt — a verbal-reinforcement-learning loop with no weight updates.

## 1. Research question
LLM agents often fail on multi-step reasoning, code, and decision tasks not because they lack the capability, but because they cannot **learn from their own mistakes within a single session** — every new attempt starts from scratch. Can a verbal self-reflection mechanism, stored and retrieved as memory, function as a form of in-context reinforcement learning?

## 2. Method (方法)
- **Actor**: the LLM produces actions / tool calls conditioned on the trajectory so far.
- **Evaluator**: a separate LLM call scores whether the trajectory succeeded (binary or graded).
- **Self-reflection**: on failure, the LLM is prompted to generate a free-text reflection — what went wrong, what to do differently.
- **Memory buffer**: reflections are stored in an **episodic memory** (sliding window of the last k reflections).
- **Next attempt**: the actor receives (a) the original task and (b) the most recent reflections as additional context.

**关键设计**：the **reflection is written back into the LLM's context for the next attempt** — making verbal feedback a parameter-free learning signal.

## 3. Contributions (创新点)
- **Claimed**: (1) verbal reinforcement learning, (2) state-of-the-art on HumanEval, MBPP, AlfWorld, (3) ~11% absolute gain on HotPotQA-style multi-hop QA.
- **Actual (my judgment)**: The mechanism is **simple and reproducible**, which is a real contribution. But the gain attribution is confounded: many of the reported gains are in fact close to the gain from a single retry with chain-of-thought. The *ablation* against "retry without memory" is the load-bearing experiment — and the paper does run it.

## 4. Experimental setup (实验设置)
- **Data / tasks**: HumanEval (code), MBPP, HotPotQA, AlfWorld (household decision making), decision-making text games.
- **Baselines**: ReAct, Chain-of-Thought prompting, single-shot GPT-4, "retry without memory" (key ablation).
- **Metrics**: pass@1, success rate, exact match.
- **Key results** (paper text; please verify):
  - HumanEval: 91.0% pass@1 vs 80.0% GPT-4 baseline (example from paper text; please verify). `[请人工核对]`
  - AlfWorld: substantial gain over ReAct. `[请人工核对]`
- **Ablations / analyses**: most important ablation = "retry without memory" vs. full Reflexion — separates the effect of *iteration* from the effect of *reflection as memory*.

## 5. Limitations (局限性)
- **Stated by authors**: reflection quality depends on base LLM; memory grows linearly with attempts; no long-term across-session consolidation.
- **My assessment**:
  - "Verbal reinforcement learning" is a strong claim for what is essentially in-context demonstration. The paper does not measure whether reflections *generalize* beyond the immediate retry.
  - The 11% on multi-hop QA, if real, is impressive; the experimental protocol uses single-seed numbers — **no variance reported**. A 1–2 pp difference is noise until multi-seeded.
  - No negative result: when does reflection **hurt**?

## 6. Reusable resources
- **Code**: <https://github.com/noahshinn/reflexion> `[not verified from PDF]`
- **Reusable ideas**: the **episodic-memory-of-reflections** pattern generalizes to any LLM agent with a retry loop. The actor/evaluator/self-reflection triplet is a clean template.

## 7. Connections
- Direct ancestor of many "self-improve" agents; the Reflection pattern reappears in [Sumers et al. 2024, CoALA] under a different name.
- Shares "no weight updates" stance with [Packer et al. 2023, MemGPT] but solves a different problem (within-task learning vs. cross-context capacity).
- Compared against [Hu et al. 2024, LongAgent] in follow-ups; LongAgent applies RL to the same general problem.

## 8. Open questions / TODO
- Verify exact pass@1 numbers in the main table.
- Re-run the "retry vs. Reflexion" ablation with at least 3 seeds to assess variance.
- Try Reflexion on a setting where reflection can mislead (e.g., adversarial tasks) to map failure modes.
