# 大规模文献集分批、恢复与增量更新

## 目录

- [目录隔离](#目录隔离)
- [首次运行与分批](#首次运行与分批)
- [恢复与增量更新](#恢复与增量更新)
- [状态和失败处理](#状态和失败处理)
- [交付检查](#交付检查)

## 目录隔离

原始语料目录只读，派生产物目录必须位于语料树之外。先创建两个明确目录，例如 `corpus/` 与 `derived/`；工具拒绝把输出放回 `corpus/`，不删除源文件，也不自动删除已经失去来源的旧产物。

默认发现 `.pdf`、`.txt`、`.bib`、`.ris`、`.xml` 和 `.json`。Markdown 只有在显式 `--include '*.md'` 时处理，因为普通研究笔记不一定是参考文献列表。隐藏文件、越出根目录的链接和排除规则命中的文件会跳过。

## 首次运行与分批

```bash
python3 scripts/batch_literature.py corpus \
  --out-dir derived \
  --limit 100
```

`--limit` 只处理指定数量的 pending/changed 文件，每个文件完成后原子更新 `derived/batch-state.json`。默认处理器：

- PDF → `pdf-extraction`；OCR 默认 `never`，只有显式 `--pdf-ocr auto|always` 才启用。
- `.txt` → 参考文献元数据提取 JSON。
- BibTeX/RIS/EndNote XML/JSON → 规范化 `bibliography-library` 和转换 manifest。

用可重复 `--include`/`--exclude` 缩小范围，例如 `--include 'topic-a/*.pdf' --exclude '**/archive/*'`。默认单文件上限 50 MiB；`--max-file-mib` 可调整。超限文件记录为 `skipped-large`，不读取全文哈希、不处理。

## 恢复与增量更新

已有 checkpoint 时必须显式 `--force`，表示允许更新状态和已经发生内容变化的派生产物：

```bash
python3 scripts/batch_literature.py corpus --out-dir derived --limit 100 --force
```

每个相对路径保存 SHA-256、大小、处理类型、稳定输出名和状态。相同哈希且产物仍在的项目变为 `unchanged`；新增或内容变化的项目重新处理；已删除源项目变为 `removed`，但旧产物保留，等待人工归档。不要把时间戳当增量依据。

路径稳定名由规范化 stem 和相对路径哈希组成，因此同名文件不会碰撞。内容改变仍写回同一派生路径，便于下游引用；只有带 `--force` 的恢复运行才能覆盖它。

## 状态和失败处理

- `success`：本次成功处理。
- `unchanged`：哈希相同且产物存在，未重跑。
- `pending`：受 `--limit` 限制，留待下一批。
- `failed`：子处理器非零退出；checkpoint 保留截断后的 stdout/stderr。
- `skipped-large`：超过文件上限。
- `removed`：源文件消失，派生产物未删除。

相同哈希的失败项默认不反复执行；确认依赖或配置已修复后添加 `--retry-failed --force`。源内容改变会自动再次处理。任何 `failed` 使批处理返回非零；仅有 pending、removed 或 skipped-large 不冒充全部完成，应检查 summary。

新建 checkpoint 时若稳定目标文件已经存在，工具默认失败而不覆盖。检查来源后，以 `--force` 重新运行才允许替换。checkpoint 的 source/output root 与新命令不一致时拒绝恢复，防止串库。

## 交付检查

```bash
python tools/validate_artifact.py derived/batch-state.json --type literature-batch
```

交付前要求：`pending == 0`、`failed == 0`；逐项说明 `skipped-large` 和 `removed`；抽查每种处理器至少一个输出；对 PDF 保留 OCR warnings；对文献库再运行 bibliography audit。checkpoint 是运行账本，不是最终综述，也不证明每篇文献已经精读。
