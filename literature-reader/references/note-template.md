# Structured Reading Note Template

Used by **Function 1** of the `literature-reader` skill. Fill one note per paper.
Language: follow the user's library language (English notes for English libraries,
Chinese notes for Chinese thesis libraries). Fields that cannot be determined from
the text must be `[未提及]` / `[not stated]` — never guessed.

Length discipline: the whole note should fit on ~1.5 pages. If a section wants to
grow past its cap, the excess belongs in the user's own manuscript notes, not here.

---

## Template

```markdown
# <Paper Title>

- **Citation**: <Authors (Year). Venue.> — e.g. `Vaswani et al. (2017). NeurIPS.`
- **DOI / arXiv**: <doi or arXiv id, or [未提及]>
- **Read date**: <YYYY-MM-DD> | **Depth**: 速读 / 精读
- **One-liner (一句话)**: <one sentence: who solves what problem with what method>

## 1. Research question (研究问题)
<What problem, why it matters, what was blocking prior work. 2–4 sentences.
Quote the paper's own problem statement if crisp; otherwise restate in your words.>

## 2. Method (方法)
<Core technical approach: model/algorithm/procedure class + the ONE design choice
that makes it work. Include key equations or architecture only if the user would
need them to reimplement. 3–6 sentences or a short bullet list.>

## 3. Contributions (创新点)
<Distinguish claimed vs actual. Format:
- **Claimed**: what the authors list.
- **Actual (my judgment)**: which claimed contributions are genuinely new vs
  repackaged/engineering, and any unclaimed contribution you noticed.>

## 4. Experimental setup (实验设置)
- **Data**: <datasets, size, domain, splits>
- **Baselines**: <compared against what>
- **Metrics**: <evaluation metrics>
- **Key results**: <headline numbers — flag "请人工核对" if read from figures>
- **Ablations / analyses**: <which ablation matters most, in one line>

## 5. Limitations (局限性)
- **Stated by authors**: <their own limitation paragraph, compressed>
- **My assessment**: <what they did NOT say: threats to validity, weak baselines,
  dataset leakage risk, missing ablations, generality concerns>

## 6. Reusable resources (可复用资源)
- **Code**: <repo URL / official / third-party / none — [未提及] if not found>
- **Data / models released**: <what artifacts, licenses if stated>
- **Reusable ideas for my work**: <what YOU can borrow: a module, an evaluation
  protocol, a dataset, a framing. This is the most personal section — write it
  for the user's project, not generically.>

## 7. Connections (关联)
<2–3 bullets: how this paper relates to other notes in the library — extends X,
contradicts Y, shares dataset with Z. Leave empty if the library is still small.>

## 8. Open questions / TODO
<Follow-ups: papers to chase from its references, experiments to verify,
things to check when the code is released.>
```

---

## Filling rules per field

### Header / One-liner
- Citation string comes from `scripts/extract_metadata.py` output when the input
  was a pasted reference; verify venue/year against the PDF front page.
- **Depth** is honesty bookkeeping: a 速读 note (abstract + figures + conclusion)
  must not contain claims only verifiable by full reading.
- The one-liner must name *problem + method*, not just topic. Bad: "一篇关于图神经网络的论文". Good: "用稀疏注意力把 GNN 扩展到十亿边图".

### §1 Research question
- Separate the *motivating problem* (real-world) from the *technical gap* (why prior
  methods fail). Most papers state the first well and hide the second — dig for it
  in the last paragraph of the intro.

### §2 Method
- Cap at 6 sentences / 8 bullets. The test: could the user, a month later, explain
  the method to their advisor from this section alone?
- Name the single load-bearing design choice explicitly ("关键设计：…").

### §3 Contributions
- The **Actual** line is the point of the note. Common patterns to call out:
  - "novel framework" that is a known method + new dataset → 工程组合, not a method contribution
  - contribution claimed against weak/absent baselines → discount it
  - unclaimed but real: a useful negative result, a clean ablation, a released artifact

### §4 Experimental setup
- Key results: quote at most 3 numbers, always with the baseline number next to
  them ("72.1 vs 70.3 baseline"). A result without its comparator is useless.
- Numbers read from figures (not tables) get the `请人工核对` flag.

### §5 Limitations
- **My assessment** should contain at least one item not in the authors' own list.
  If you genuinely find none, write why the evaluation looks solid — that is also
  information.

### §6 Reusable resources
- Only claim a code/data resource exists if the text gives a URL or explicit
  statement ("code will be released at…"). "Available upon request" ≠ released.
- "Reusable ideas" is written for the user's project context — ask the user one
  line about their project if you don't know it.

### §7–8
- §7 links make the library compound over time; add them whenever ≥2 notes exist.
- §8 TODOs should be actionable ("verify Table 2 baseline against original paper"),
  not vague ("read more about X").
