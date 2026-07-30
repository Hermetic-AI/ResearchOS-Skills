# Gap Analysis Methodology

Used by the `literature-reader` skill:
- Function 2 does not read this file — comparison dimensions live in
  `references/comparison-matrix.md`.
- Function 3 reads this file **in full**.

Purpose: turn a compared paper set into candidate research gaps with a type
label and an honest feasibility verdict — not a generic "future work" list.

---

## Comparison dimensions

The dimension library, discipline-specific columns, note-to-matrix alignment
rules, and conflict-handling rules live in **`references/comparison-matrix.md`**.
Function 2 reads that file, not this one. Gap identification below assumes a
matrix built by those rules; the signals it scans for (empty regions, `?`
rows, conflict clusters, monoculture) are defined there.

---

## Gap identification workflow (Function 3)

### Step 1 — Dimension scan
Walk the matrix column by column and look for:
- **Empty regions**: a method class never applied to a dataset/setting that
  dominates the matrix.
- **Rows of `?`**: dimensions the whole literature ignores (e.g. nobody reports
  compute cost, nobody evaluates on real users).
- **Conflict clusters**: unresolved contradictions (see above).
- **Monoculture**: one dataset/metric/baseline used by ≥ 70% of papers → results
  may be artifacts of that choice.
- **Recency edge**: the newest 1–2 papers open a direction older ones can't cover.

### Step 2 — Enumerate gap candidates
For each signal from Step 1, write one candidate in the form:
"在 X 条件下，用 Y 方法解决 Z 问题，目前无人做 / 只有 W 做过但有缺陷 Q".
A candidate without an "依据" pointer to ≥ 2 matrix rows is speculation — keep it
but label it `[弱依据]`.

### Step 3 — Gap-type classification

| Type | Definition | Example | Typical risk |
|---|---|---|---|
| **方法空白** Method | known problem, but an applicable method family never tried | diffusion models never used for this PDE | may have been tried and failed silently |
| **数据空白** Data | method exists, but no dataset/benchmark for the real setting | models trained on clean data, no noisy-domain benchmark | data collection cost dominates |
| **人群空白** Population | evidence comes from one narrow population; others never studied | findings from WEIRD undergrad samples; models trained on adult data, deployed on children | "new population" alone may be judged incremental |
| **情境迁移空白** Setting-transfer | validated in one context, untested where conditions differ | works on English, untested on low-resource languages; lab results, no field trial | "just transfer" may be trivial and unpublishable — must predict *why* transfer should break or hold |
| **理论空白** Theory | empirical success/failure without explanation | method works, no convergence or mechanism analysis | hard to scope for a master's thesis |
| **评估空白** Evaluation | shared metric/protocol is flawed or gamed | SOTA driven by test-set leakage; accuracy on imbalanced data | community may reject the critique |
| **负结果空白** Negative-result | a plausible approach was likely tried and failed, but nothing is published — the failure is invisible | everyone uses method family A for X; nobody reports whether the obvious family B fails | you may be re-walking into the same wall; find indirect evidence first |

Population and setting-transfer gaps look similar but fail differently: a
population gap asks "does the effect exist in group Y at all", a transfer gap
asks "does a validated mechanism survive changed conditions". Keep them
separate — the study designs differ (new sampling vs new environment).

### Step 3b — Evidence requirements per gap type

A gap claim is only as strong as the evidence that the space is truly empty.
Before writing up a candidate, collect the type-specific evidence:

| Type | Required evidence that the gap is real |
|---|---|
| 方法空白 | The method family appears **nowhere** in the matrix rows, AND a search of the last 2 years' preprints finds no attempt (silently-failed risk). State the method's applicability premise in one line — why it *should* work here. |
| 数据空白 | ≥ 2 matrix rows work around the missing data (proxies, synthetic substitutes, clean-data-only training) — the workaround is the evidence. A gap nobody works around is usually a gap nobody needs. |
| 人群空白 | Matrix's population column is ≥ 80% monoculture, AND the excluded population is named explicitly with a reason to expect difference (physiology, culture, age), not just "hasn't been done". |
| 情境迁移空白 | The boundary condition is identified (what exactly changes between contexts: distribution shift, resource constraints, regulation), AND ≥ 1 row documents a failed or degraded transfer in an analogous case. |
| 理论空白 | The empirical effect is replicated across ≥ 2 independent rows (an unreplicated effect needs replication, not theory), AND existing theory rows fail to cover it. |
| 评估空白 | The flaw is demonstrable: you can point to the leakage path, the gaming behavior, or a concrete case where the metric ranks methods wrongly. Suspicion without a mechanism is a complaint, not a gap. |
| 负结果空白 | Indirect evidence only: the approach is conspicuously absent despite being obvious; related papers cite "preliminary experiments did not improve" without details; practitioners' forums/report mention failures. Label `[间接证据]` and plan a cheap probe experiment as the first step. |

### Step 3c — Gap statement sentence templates

A usable gap statement names: condition + missing thing + why it matters +
evidence. Templates (fill the slots, cut what does not apply):

- **方法空白**: "针对 <问题Z>，现有工作均基于 <方法族A>（矩阵行 <…>），尚无研究尝试 <方法族B>；考虑到 <B的适配前提>，这一空白值得探索。"
- **数据空白**: "现有 <方法/模型> 均在 <理想条件数据> 上验证（行 <…>），缺乏 <真实场景> 的公开基准，导致 <具体后果：无法评估/结果被高估>。"
- **人群空白**: "已有证据几乎全部来自 <人群P>（矩阵人群列 <…>）；由于 <预期差异的理由>，结论能否推广到 <人群Q> 尚属未知。"
- **情境迁移空白**: "<方法/效应> 已在 <情境A> 中确立（行 <…>），但 <情境B> 改变了 <边界条件>；类比案例 <行X> 显示迁移后性能下降，因此直接迁移的可靠性存疑。"
- **理论空白**: "<现象> 已被多项独立工作复现（行 <…>），但其 <机制/收敛性/边界> 缺乏理论解释，限制了 <外推/改进>。"
- **评估空白**: "该领域普遍采用 <协议/指标>（行 <…>），但存在 <具体缺陷机制>，使得 <被误导的结论>；需要 <修正的协议> 重新评估。"
- **负结果空白**: "尽管 <方法族B> 是 <问题Z> 的自然候选，文献中无任何尝试报告（含失败报告）；间接证据 <…> 提示其可能失败，但失败原因未知。"

Every statement ends with the evidence pointer; a gap statement without a
matrix-row reference is an opinion.

### Step 4 — Feasibility verdict

Score each candidate on four axes, then give one verdict:

1. **数据可得性**: does the needed data/benchmark exist or can it be built within
   the user's timeline? Non-negotiable.
2. **方法成熟度**: are the required building blocks published + implemented
   (usable code), or would the user be building infrastructure from scratch?
3. **工作量 vs 学位要求**: a master's thesis ≈ 1 well-scoped contribution;
   a PhD chapter ≈ 2–3. Reject candidates needing a new field.
4. **撞车风险**: is an active group obviously working on this (recent preprints,
   workshop tracks)? Crowded ≠ impossible, but the differentiation must be named.

Verdicts:
- **可做** — all four axes pass; name the first concrete step.
- **谨慎** — one axis weak; state the mitigation (narrow scope, find collaborator,
  reproduce first).
- **不建议** — two+ axes fail; say why plainly. A candid 不建议 is a valuable
  deliverable, not a failure of the analysis.

### Output format (Chinese report)

```
## 研究空白分析报告（基于 N 篇文献对比矩阵）

### 候选空白 1：<一句话描述>
- 依据：矩阵行 <A, B, C> — <哪一列的信号>
- 类型：方法空白 / 数据空白 / 人群空白 / 情境迁移空白 / 理论空白 / 评估空白 / 负结果空白
- 可行性：可做（or 谨慎 / 不建议）
  - 数据可得性：…
  - 方法成熟度：…
  - 工作量匹配：…
  - 撞车风险：…
- 与现有文献的区分点：<一句话>
- 建议第一步：<一个可在两周内完成的具体动作>

（按 可行性 × 价值 排序；弱依据候选单列在最后）
```
