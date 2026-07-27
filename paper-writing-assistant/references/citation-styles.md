# 引用风格规则卡（GB/T 7714 · IEEE · APA · ACM）

检查「每条文献格式合规」「风格一致性」时，先让用户从这四套里选定目标风格，再逐条比对。
下面每套给出：**正文引用标记** + **参考文献表条目格式**（按文献类型），以及最常见的踩坑点。

标注含义：`[必填字段]`、`〈标点/样式要求〉`。

---

## 1. GB/T 7714-2015（中文硕博论文国标）

**正文引用**：顺序编码制，右上标数字 `[1]`；或著者-出版年制 `(张三, 2020)`。同一处引多篇 `[1-3,5]`。
每条文献末尾带**文献类型标识码**：专著[M] 期刊[J] 学位论文[D] 论文集[C] 报告[R] 标准[S] 专利[P] 电子文献[EB/OL]。

**期刊论文**：
```
[1] 主要责任者. 题名[J]. 刊名, 年, 卷(期): 起止页码.
[1] 张三, 李四. 深度学习综述[J]. 计算机学报, 2020, 43(6): 1120-1135.
```
**专著**：
```
[2] 主要责任者. 书名[M]. 版本(第1版可省). 出版地: 出版者, 出版年: 页码.
```
**学位论文**：
```
[3] 作者. 题名[D]. 保存地: 保存单位, 年.
```
**电子文献**：
```
[4] 作者. 题名[EB/OL]. (发布日期)[引用日期]. URL.
```
常见踩坑：① 缺类型标识码 `[J]/[M]`；② 作者超 3 人应写「前3人, 等.」（英文 et al.）；③ 卷期页用半角，`卷(期): 页`；④ 中文用中文标点会出错，参考文献表统一半角标点；⑤ 西文作者「姓在前，名缩写在后」如 `Smith J`。

---

## 2. IEEE（工科会议/期刊，含多数 CS）

**正文引用**：方括号数字，行内正常大小 `[1]`，按出现顺序编号；多篇 `[1], [3], [5]` 或 `[1]-[3]`。当作句子成分：`as shown in [4]`。

**期刊论文**：
```
[1] A. B. Author, "Title of paper," Journal Name Abbrev., vol. x, no. x, pp. xxx-xxx, Month year.
[1] J. Zhang and L. Wang, "A survey on deep learning," IEEE Trans. Neural Netw., vol. 30, no. 6, pp. 1120-1135, Jun. 2020.
```
**会议论文**：
```
[2] A. Author, "Title," in Proc. Conf. Name Abbrev., City, Country, year, pp. xxx-xxx.
```
**书籍**：
```
[3] A. Author, Book Title, xth ed. City, Country: Publisher, year, pp. xx-xx.
```
常见踩坑：① 标题用**双引号**、期刊/书名用**斜体**；② 作者名「首字母缩写在前，姓在后」`A. B. Author`；③ 6 位以上作者可用 `A. Author et al.`；④ 月份缩写 `Jan./Feb./.../Dec.`；⑤ 会议前必须有 `in Proc.`。

---

## 3. APA 7th（社科/人文/教育/心理）

**正文引用**：著者-年 `(Smith, 2020)` 或 `Smith (2020)`；带页码引用 `(Smith, 2020, p. 15)`；三名及以上作者首次即用 `(Smith et al., 2020)`。

**期刊论文**（参考文献表按作者姓字母排序，悬挂缩进）：
```
Author, A. A., & Author, B. B. (Year). Title of article. Journal Name, Volume(Issue), pages. https://doi.org/xxx
Zhang, J., & Wang, L. (2020). A survey on deep learning. Journal of Computer Science, 43(6), 1120-1135. https://doi.org/10.xxxx
```
**书籍**：
```
Author, A. A. (Year). Title of work (Xth ed.). Publisher.
```
常见踩坑：① 期刊名和卷号**斜体**，期号不斜体；② 文章标题「句首字母大写」（sentence case），期刊名「每个实词首字母大写」（title case）；③ 用 `&` 不用 `and`（正文括号内）；④ 优先给 DOI，为 URL 时不加句号结尾；⑤ 参考文献表按姓氏字母序、悬挂缩进。

---

## 4. ACM（计算机，ACM Reference Format）

**正文引用**：数字上标或方括号 `[1]`（numbered，多数 ACM 模板），按引用顺序或作者字母序编号；也有 author-year 变体 `[Smith 2020]`。

**期刊论文**（编号 + DOI 必带）：
```
[1] First Last and First Last. Year. Title of the article. Journal Name Vol, Issue (Month Year), page-range. https://doi.org/xxx
[1] Jie Zhang and Lei Wang. 2020. A survey on deep learning. ACM Comput. Surv. 53, 6 (Nov. 2020), 1-35. https://doi.org/10.1145/xxx
```
**会议论文**：
```
[2] First Last. Year. Title. In Proceedings of Conference Name (Abbrev '20). ACM, City, Country, page-range. https://doi.org/xxx
```
常见踩坑：① 作者写**全名**（不缩写）`Jie Zhang`，与 IEEE 相反；② 年份紧跟作者后 `Author. 2020. Title.`；③ 会议名后带 `(Abbrev 'YY)` 简称；④ 标题正常大小写、期刊/会议名斜体；⑤ ACM 强制要 DOI/URL。

---

## 跨风格一致性自查（不论选哪套）
- 全文只用一套风格，不混用（作者名缩写规则、标点、斜体范围要统一）。
- 正文引用编号/著者形式全文统一（不要一处 `[1]` 一处 `(Smith, 2020)`）。
- 参考文献表排序规则统一（顺序编码制=按出现顺序；著者-年制=按姓氏字母序）。
- 作者超限时的省略写法统一（都用 `et al.` 或都用「等」，阈值一致）。
- 期刊名缩写要么全缩写要么全不缩写，不要一半一半。
