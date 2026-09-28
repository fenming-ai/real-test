# Fieldnote 落地页 Brief

做一个名为 Fieldnote 的桌面应用落地页。它是一款 local-first research notebook，面向经常在网络不稳定环境中工作的独立研究者和记者。页面目标是让读者下载 macOS beta。

视觉气质：安静、务实、略带编辑感，像一本耐用的野外笔记本和一组整理过的 contact sheets。不要未来主义，不要蓝紫霓虹，不要假装已有大量用户。

只生成一个可直接打开的 `index.html`，CSS 和必要 JavaScript 全部内嵌。不要使用框架、构建步骤、外部字体、CDN 或远程资源。必须使用当前目录的 `hero.jpg` 作为真实图片素材并提供准确 alt。适配桌面和窄屏，但本轮只验收桌面。

保持以下内容和信息，不得编造客户 Logo、评价、融资、使用人数或效果数字：

- 导航：Fieldnote；Why local；Workflow；Download beta。
- Hero 标签：Local-first research notebook
- Hero 标题：Keep the source close.
- Hero 正文：Capture interviews, PDFs and field notes without waiting for the cloud. Search everything on your Mac, then export a clean research bundle.
- 主按钮：Download macOS beta
- 次按钮：See the workflow
- 原则句：Your notes stay on your Mac. Sync is optional, not the price of entry.
- Workflow 三步：Collect offline；Connect the evidence；Export the bundle。每步补一句具体说明，但不得增加未经提供的能力。
- 第二个核心区块标题：Built for the train, the archive and the bad connection.
- 第二个核心区块正文：Fieldnote keeps the working set local, links every claim back to its source, and exports plain files your team can keep.
- 底部 CTA 标题：Take one project offline.
- 底部 CTA 正文：Start with a small research folder. Import five sources, connect one claim, and export the bundle.
- 页脚：Fieldnote beta；Local files first；macOS。

页面必须有清楚的信息层级、可见焦点状态、合理语义标签和 `prefers-reduced-motion` 回退。不要用假产品截图、假数据和纯装饰性状态点。
