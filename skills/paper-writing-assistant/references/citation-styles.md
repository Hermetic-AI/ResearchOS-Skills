# Citation Style Rules Card (GB/T 7714 · IEEE · APA · ACM)

When checking "format compliance of each reference" and "style consistency", first have the user select a target style from these four, then compare item by item.
For each style below, we give: **in-text citation marker** + **reference list entry format** (by document type), along with the most common pitfalls.

Notation: `[required field]`, `〈punctuation/style requirement〉`.

---

## 1. GB/T 7714-2015 (Chinese national standard for theses)

**In-text citation**: sequential numbering system, superscript number in the upper right `[1]`; or author-year system `(Zhang San, 2020)`. Multiple citations at one place `[1-3,5]`.
Each reference entry ends with a **document type code**: monograph[M] journal[J] dissertation[D] proceedings[C] report[R] standard[S] patent[P] electronic resource[EB/OL].

**Journal article**:
```
[1] Primary responsible person. Title[J]. Journal Name, Year, Volume(Start-End pages).
[1] Zhang San, Li Si. A survey on deep learning[J]. Chinese Journal of Computers, 2020, 43(6): 1120-1135.
```
**Monograph**:
```
[2] Primary responsible person. Book Title[M]. Edition (1st ed. may be omitted). Place of publication: Publisher, Year: pages.
```
**Dissertation**:
```
[3] Author. Title[D]. Location: Institution, Year.
```
**Electronic resource**:
```
[4] Author. Title[EB/OL]. (Publication date)[Access date]. URL.
```
Common pitfalls: ① Missing type code `[J]/[M]`; ② When authors exceed 3, write "first 3 authors, et al."; ③ Volume/issue/pages use half-width characters, `volume(issue): pages`; ④ Using Chinese punctuation causes errors — the reference list should use half-width punctuation uniformly; ⑤ Western authors "surname first, given name abbreviated" e.g. `Smith J`.

---

## 2. IEEE (engineering conferences/journals, including most CS)

**In-text citation**: bracketed numbers, inline at normal size `[1]`, numbered in order of appearance; multiple `[1], [3], [5]` or `[1]-[3]`. When used as a sentence element: `as shown in [4]`.

**Journal article**:
```
[1] A. B. Author, "Title of paper," Journal Name Abbrev., vol. x, no. x, pp. xxx-xxx, Month year.
[1] J. Zhang and L. Wang, "A survey on deep learning," IEEE Trans. Neural Netw., vol. 30, no. 6, pp. 1120-1135, Jun. 2020.
```
**Conference paper**:
```
[2] A. Author, "Title," in Proc. Conf. Name Abbrev., City, Country, year, pp. xxx-xxx.
```
**Book**:
```
[3] A. Author, Book Title, xth ed. City, Country: Publisher, year, pp. xx-xx.
```
Common pitfalls: ① Titles use **double quotes**, journal/book names use *italics*; ② Author names "initials first, surname last" `A. B. Author`; ③ For 6 or more authors, `A. Author et al.` may be used; ④ Abbreviated months `Jan./Feb./.../Dec.`; ⑤ `in Proc.` is required before conference names.

---

## 3. APA 7th (social sciences/humanities/education/psychology)

**In-text citation**: author-year `(Smith, 2020)` or `Smith (2020)`; with page `(Smith, 2020, p. 15)`; three or more authors use `(Smith et al., 2020)` from the first citation.

**Journal article** (reference list sorted alphabetically by author surname, hanging indent):
```
Author, A. A., & Author, B. B. (Year). Title of article. Journal Name, Volume(Issue), pages. https://doi.org/xxx
Zhang, J., & Wang, L. (2020). A survey on deep learning. Journal of Computer Science, 43(6), 1120-1135. https://doi.org/10.xxxx
```
**Book**:
```
Author, A. A. (Year). Title of work (Xth ed.). Publisher.
```
Common pitfalls: ① Journal name and volume number are *italic*, issue number is not italic; ② Article titles use sentence case, journal names use title case; ③ Use `&` not `and` (inside parentheses in text); ④ Prefer DOI; when a URL is used, do not end with a period; ⑤ Reference list sorted alphabetically by surname, with hanging indent.

---

## 4. ACM (computer science, ACM Reference Format)

**In-text citation**: superscript or bracketed numbers `[1]` (numbered, most ACM templates), numbered in order of citation or alphabetically by author; there is also an author-year variant `[Smith 2020]`.

**Journal article** (numbered + DOI required):
```
[1] First Last and First Last. Year. Title of the article. Journal Name Vol, Issue (Month Year), page-range. https://doi.org/xxx
[1] Jie Zhang and Lei Wang. 2020. A survey on deep learning. ACM Comput. Surv. 53, 6 (Nov. 2020), 1-35. https://doi.org/10.1145/xxx
```
**Conference paper**:
```
[2] First Last. Year. Title. In Proceedings of Conference Name (Abbrev '20). ACM, City, Country, page-range. https://doi.org/xxx
```
Common pitfalls: ① Authors written in **full name** (not abbreviated) `Jie Zhang`, opposite to IEEE; ② Year follows immediately after author `Author. 2020. Title.`; ③ Conference name followed by `(Abbrev 'YY)` short form; ④ Title in normal case, journal/conference name in italics; ⑤ ACM mandates DOI/URL.

---

## Cross-style consistency self-check (regardless of which style is chosen)
- Use only one style throughout the paper; do not mix (author abbreviation rules, punctuation, italic scope must be uniform).
- In-text citation numbering/author form must be consistent throughout (do not use `[1]` in one place and `(Smith, 2020)` in another).
- Reference list sorting rules must be uniform (sequential numbering = in order of appearance; author-year = alphabetical by surname).
- Omission format when author count exceeds the limit must be uniform (all use `et al.`, with consistent threshold).
- Journal name abbreviations must be either all abbreviated or all unabbreviated; do not mix.
