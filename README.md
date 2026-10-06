# Nivat 论文：凸截面与全部二次位置的互补下界

公开冻结包 v1.0；稿件 v1.1。已由一个全新的 gpt-6.1-sol 上下文完成对抗复核，未发现数学阻塞项。记录：[对抗复核-v1.0.md](对抗复核-v1.0.md)；绑定 v1.0 稿件 SHA-256：`3bd81a166c53f8a073ad893eeaef24fe05b83468023151b3b550db385d9fd52c`。v1.1 仅修订表述；297 个数学片段和第 1–4 节证明逐字节保持一致，详见[修订记录](表述修订记录-v1.1.md)。

- [英文正文](优化合稿-English-v1.1.md)：标题在首行；[粘贴正文](proof/submission.md)不超过 20,000 个 UTF-16 单元。
- [证据协议](证据协议-v1.0.md)：配置、几何、全局覆盖、锚点避碰、指纹与篡改负控。
- [复跑说明](复跑说明.md)：只需 Python 3.9+ 标准库，离线运行；不需 Git 或工作区中的其他文件。
- [引用与披露](引用与披露.md)：原文版本、归因、既有轻量检索及 AI 分工。
- [独立重建结果](运行记录/独立重建检查结果-v1.0.json)与[障碍检查结果](运行记录/障碍与无限族检查结果-v1.0.json)。

三角形窗口得到：定理 T 下界 497，全位置下界及解析扩展秩 679，截面下界 882，全局实际模式数 7037。矩形得到 55／86／60／347。删点例的一般下界为 83，实际扩展秩为 84。

新检查器与生成器分别实现、没有相互导入；同一 Codex 上下文完成，不称为独立模型审阅。旧矩形和删点证书原样复用，旧检查器只移植可移植的数学检查函数与负控，去掉工作区专用主程序。历史路径与哈希属于出处元数据，不是复跑依赖。

仓库：[https://github.com/iamwangxi/apex-p03-nivat-complementary-bounds](https://github.com/iamwangxi/apex-p03-nivat-complementary-bounds)；固定标签 `v1.0`。`MANIFEST.sha256` 列出全部发布文件（自身除外）；`.git/` 不属证据。随附审阅输入是未改动的历史 v1.0，其 pending 仅表示当时状态。当前稿件与粘贴正文见上方链接；实际平台投稿尚未执行。

## 版本说明 / Revision note

本版本与 `e534fd9954c3a55478a3a6f008a66e23a69fbae3`（标签 `v1.0`）相比，只改了 `优化合稿-English-v1.1.md` 与 `proof/submission.md` 两个文件中公式的写法。GitHub 的 Markdown 处理会去掉 `$...$` 里的 `\{`、`\,` 等反斜杠转义，还有部分公式没被识别，并且禁用 `\operatorname` 与 `\tag`；所以这两个文件的全部公式改用 GitHub 的原样数学语法，这两个宏换成等价写法。数学文字没有任何改动。`运行记录/KaTeX核验-v1.0.json` 与 `表述修订记录-v1.1.md` 中记录的哈希对应标签 `v1.0` 的文件；审阅输入与 `引用/` 下的记录保持原样。

This revision differs from `e534fd9954c3a55478a3a6f008a66e23a69fbae3` (tag `v1.0`) only in how formulas are written in `优化合稿-English-v1.1.md` and `proof/submission.md`. GitHub's Markdown processing removed backslash escapes such as `\{` and `\,` inside `$...$`, did not recognise some formulas, and blocks `\operatorname` and `\tag`; so every formula in these two files now uses GitHub's literal math syntax, and the two macros were replaced by equivalent ones. No mathematical text was changed. The hashes recorded in `运行记录/KaTeX核验-v1.0.json` and `表述修订记录-v1.1.md` refer to the files at tag `v1.0`; the review input and the records under `引用/` are unchanged.
