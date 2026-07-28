# Citation Style Check Report (paper-writing-assistant Function 2)

**Paper:** AI Agent Memory: A Survey of Mechanisms, Trade-offs, and Open Problems
**File:** `paper/paper.md`
**Style chosen:** **IEEE** (per user requirement: "English, arXiv/conference/SCI style")
**Date:** 2026-07-28

---

## 维度 ① 正文引用 ↔ 文献表一一对应

| Check | Result |
|---|---|
| Reference list has 14 entries [1]–[14] | ✅ |
| Body cites 14 unique numbers | ✅ |
| Orphan references (in list, not cited) | **0** ✅ |
| Orphan citations (cited, not in list) | **0** ✅ |
| Citation numbering consecutive | ✅ |
| Citation numbering follows first-appearance order | ✅ (verified by reading) |

**Verdict:** ✅ Pass.

---

## 维度 ② 格式合规（IEEE）

按 `paper-writing-assistant/references/citation-styles.md §2` 的 IEEE 规则卡逐条检查。

| Item | Rule | Result |
|---|---|---|
| Author name format | `F. Last` (initial before surname) | ✅ all 14 entries |
| Title | in double quotes `"…"` | ✅ all 14 entries |
| Venue | italic in IEEE rendering; we mark with abbreviated journal name + `vol./no./pp.` | ✅ all 14 entries |
| Year | last field, 4-digit | ✅ all 14 entries |
| DOI/URL | included where available | ⚠️ only [1] has full DOI; arXiv preprints have arXiv IDs |
| `et al.` for >6 authors | needed | ⚠️ [7] uses `et al.` after first author; [5], [9], [10] list all authors (≤6) — fine |
| Month abbreviation | for journal entries | ⚠️ [1] `UIST` is a conference; [12] `TACL` doesn't need month; [5], [6], [8], [11], [14] omit month (TMLR/arXiv don't require) |

**Verdict:** ✅ Pass for venue/year/author format. ⚠️ Minor: some arXiv preprints have no volume/issue/page, which is correct per IEEE for preprints.

**Items to flag for production (if submitting to a journal that requires full bib metadata):**
- [2], [3], [4], [8], [9], [10], [11], [14]: arXiv preprints — should be cross-checked against published venues (some may have appeared at ICLR/NeurIPS/ACL by submission time).
- [1]: confirm full page range `pp. 1-22` from ACM DL.
- [12]: confirm page range `pp. 157-173` from TACL.

---

## 维度 ③ 字段完整

| Field | Required for IEEE | Present? |
|---|---|---|
| Authors | Yes | ✅ all 14 |
| Title | Yes | ✅ all 14 |
| Venue (journal/conf name) | Yes | ✅ all 14 |
| Year | Yes | ✅ all 14 |
| Volume / Issue / Pages (for journals) | Yes for journal/conference | ✅ where applicable |
| DOI | Recommended | ⚠️ 1/14 |
| arXiv ID (for preprints) | Recommended | ✅ 7/14 |

**Verdict:** ✅ Pass for required fields; ⚠️ DOIs for preprints not present (would need to look up at submission time).

---

## 维度 ④ 风格一致

| Consistency check | Result |
|---|---|
| All entries use IEEE author format | ✅ |
| All titles in double quotes | ✅ |
| All venues abbreviated (IEEE style) | ✅ |
| Punctuation: comma between fields, period at end | ✅ |
| No mixing of citation styles (no `(Author, Year)` mixed with `[N]`) | ✅ — all `[N]` |
| Reference list sorted by appearance order, not alphabetically | ✅ (per IEEE) |

**Verdict:** ✅ Pass.

---

## Final verdict

| Dimension | Verdict |
|---|---|
| ① Citation ↔ reference list correspondence | ✅ Pass |
| ② Format compliance (IEEE) | ✅ Pass (with minor arXiv/venue caveats) |
| ③ Field completeness | ✅ Pass |
| ④ Style consistency | ✅ Pass |

**Overall:** The paper's reference handling is **submission-ready for arXiv**. For journal submission (e.g., TMLR, ACM CSUR, IEEE TAI), cross-check that all arXiv preprints have been updated to their published-venue citations, and add DOIs where available.

---

## Notes on this check

- This check was done by direct pattern-matching against the markdown, since the source file is `.md` not `.docx`. The paper-writing-assistant's `docx_text.py` is for Word documents and was not used here.
- The check script (`_check_citations.py`) is included in `paper/` for reproducibility.
- For an arXiv submission, the references should be exported to a `.bib` file. This is a mechanical conversion that was not done in this survey but is recommended as a one-line follow-up.
