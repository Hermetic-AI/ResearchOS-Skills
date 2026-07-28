---
type: paper
title: "Forgetting Curve Theory for Memory-Augmented LLMs"
aliases: [maharana2024forgetting]
graph:
  - relation: cites
    target: "[[04_zhong_2024_memorybank]]"
    evidence:
      quote: "**Theoretical counterpart** to [Zhong et al. 2024, MemoryBank]"
    note: from §7 Connections of the source paper note
---


# Forgetting Curve Theory for Memory-Augmented LLMs

- **Citation**: Maharana et al. (2024). arXiv:2402.02720. — `Maharana et al. 2024`
- **DOI / arXiv**: arXiv:2402.02720
- **Read date**: 2026-07-28 | **Depth**: 精读
- **One-liner**: A theoretical analysis that adapts the **Ebbinghaus forgetting curve** into a Bayesian memory-augmented LLM framework, providing a principled update rule for memory strength and connecting to continual-learning stability-plasticity tradeoffs.

## 1. Research question
Memory-augmented LLMs (RALMs, retrieval-augmented LMs, agent memory systems) all face the same **stability-plasticity** tension: how do you incorporate new information without overwriting old, important knowledge? Existing systems use heuristics (e.g., exponential decay). Can a **Bayesian, theoretically grounded** update rule be derived from a principled model of memory?

## 2. Method (方法)
- **Model**: each memory item has a strength S(t) that decays in the absence of access, following dS/dt = -f(S).
- **Bayesian update**: on a retrieval event, S is updated via a likelihood term that depends on the relevance signal.
- **Connection to Ebbinghaus**: shows that the classical Ebbinghaus curve R = e^(-t/S) is a special case of their model.
- **Continual learning analysis**: relates the strength dynamics to stability-plasticity in continual learning, showing that a properly tuned decay can mitigate catastrophic forgetting.
- **Algorithm**: practical instantiation — at each memory write, compute new S; at each retrieval, expose S to the LLM as part of the prompt.

**关键设计**：treating **memory strength as a continuous-time stochastic process** — the right level of abstraction for the stability-plasticity problem.

## 3. Contributions (创新点)
- **Claimed**: (1) a Bayesian theory of LLM memory, (2) derivation of Ebbinghaus-style update, (3) demonstration that it mitigates forgetting in continual-learning settings.
- **Actual (my judgment)**: The theory is the contribution; the experimental evidence is supportive but small. The paper's strongest claim — that the right memory-strength dynamics *prevent* catastrophic forgetting — deserves more benchmarks.

## 4. Experimental setup (实验设置)
- **Data**: (a) synthetic sequential learning tasks, (b) knowledge-update tasks where the model must overwrite or maintain facts.
- **Baselines**: vanilla RALM, fixed-strength memory, no-forgetting memory.
- **Metrics**: forgetting rate on old knowledge; accuracy on new knowledge.
- **Key results** (please verify):
  - The Bayesian-strength memory reduces forgetting by 30–50% over no-forgetting baseline. `[请人工核对]`
  - Ebbinghaus update matches or exceeds other decay schedules. `[请人工核对]`

## 5. Limitations (局限性)
- **Stated by authors**: theory assumes i.i.d. memory accesses; continuous-time model may be overkill for discrete event data; parameters still need tuning.
- **My assessment**:
  - The continual-learning experiments are small. A larger benchmark (e.g., StreamingQA, FACTOID `[verify]`) would strengthen the claim.
  - The paper does not test against [Zhong et al. 2024, MemoryBank], which is the most direct empirical counterpart.
  - The theory-vs-algorithm gap: what does the practitioner actually code? A reference implementation would help.

## 6. Reusable resources
- **Code**: not released (theory paper). `[not verified from PDF]`
- **Reusable ideas**: the **continuous-time Bayesian strength model** is a useful conceptual scaffold. The key takeaway for any agent-memory system is: *decay should be a continuous, parameter-controlled process, not a heuristic.*

## 7. Connections
- **Theoretical counterpart** to [Zhong et al. 2024, MemoryBank] (which is empirical). The two should be cited together when discussing forgetting in agent memory.
- Provides theoretical grounding for the decay parameters in many other systems.

## 8. Open questions / TODO
- Verify the 30–50% forgetting-reduction number and the benchmark setting.
- Cross-cite with [Zhong et al. 2024]: does MemoryBank's specific decay function match the Bayesian-optimal?
- Extend the theory to multi-modal memory (text + image + action).
