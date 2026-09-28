# Taste：同一份需求，两版页面差在哪？

[在线对比入口](https://fenming-ai.github.io/real-test/taste/) · [不用 Taste](https://fenming-ai.github.io/real-test/taste/2026-09-25-fieldnote/baseline/) · [使用 Taste](https://fenming-ai.github.io/real-test/taste/2026-09-25-fieldnote/with-taste/)

这里是 2026-09-25 的真实单次对照产物，不是官方演示，也不是事后重画的效果稿。Fieldnote 是测试用合成产品，没有真实安装包；页面下载按钮只打开说明窗口。

## 我怎么看

图文作者更喜欢使用 Taste 的版本：**“我觉得就是好看，舒服，这感觉骗不了人。”**

Taste 版的字体、森林绿配色与留白更统一、克制；不用 Taste 的版本使用衬线标题、橘色按钮和倾斜照片，编辑感更强。你可以直接打开两个完整页面，再作自己的判断。

原实验的 AI 匿名评审更偏好不用 Taste 版的 Fieldnote 气质；这与图文作者的个人偏好不同，两者都不是读者投票或稳定胜率。本公开对照沿用图文编号 **A＝不用 Taste，B＝使用 Taste**；原盲评曾采用相反编号，因此目录只使用 baseline / with-taste，避免混淆。

## 怎么测的

- 相同的 [brief.md](brief.md)、本地照片、模型与设置，两个隔离工作目录，各生成一次。
- Codex CLI 0.153.4；模型 `gpt-6-astra`；reasoning effort `none`；macOS 26.5.1 / arm64。
- 基线组明确不读取设计 Skill；Taste 组先完整读取固定 Skill，再生成页面并进行适用检查。两份 [基线输入](baseline/prompt.txt) / [Taste 输入](with-taste/prompt.txt) 原样归档。
- Taste 固定版本：[c184364c58658b2f131b4ae8bd3d206cabb3deee](https://github.com/Leonxlnx/taste-skill/tree/c184364c58658b2f131b4ae8bd3d206cabb3deee)，当时为 v2 experimental。复现时将该版本的 `skills/taste-skill/SKILL.md` 放到 Taste 工作目录的 `skill/SKILL.md`，两组分别放入相同 brief 和 hero.jpg。
- 隔离参数：`--ephemeral --ignore-user-config --ignore-rules --skip-git-repo-check --sandbox workspace-write`。这是显式规则注入实验，不是安装或自动触发测试。
- 页面 HTML 与 hero.jpg 均按原始字节复制；顶部、中段、底部截图是当时的浏览器截图，不重新生成冒充原始结果。文件指纹见 [SHA256SUMS](SHA256SUMS)。

## 当时的结果

| 指标 | 不用 Taste | 使用 Taste |
|---|---:|---:|
| 运行次数 | 1 | 1 |
| 耗时（秒） | 172.01 | 194.36 |
| CLI 报告 tokens | 21,427 | 55,080 |
| HTML 字节数 | 12,920 | 9,892 |

Tokens 是历史 CLI 报告总量，不是账单费用。此案例不是省 Token 实验，不能从 HTML 更小推导 Token 更省。

当时在 Chrome 152、1512×717 桌面视口验收：两组本地图片加载、完整文案、首屏 CTA、dialog、单个 h1、四个主区块、焦点与减少动态效果规则、无横向溢出均通过。归档时的独立桌面回归见 [verification.json](verification.json)；这不是重跑模型。

只测了一道从零生成的静态落地页任务，没有重复采样、真实转化数据、手机端验收或小程序/App 实测，也没有测试旧页改造。本例支持展示这一次的差异，不代表每次都会更好。

## 原始页面与截图

- 不用 Taste：[HTML 源码](baseline/index.html)、[顶部](baseline/screenshots/top.png)、[中段](baseline/screenshots/middle.png)、[底部](baseline/screenshots/bottom.png)。
- 使用 Taste：[HTML 源码](with-taste/index.html)、[顶部](with-taste/screenshots/top.png)、[中段](with-taste/screenshots/middle.png)、[底部](with-taste/screenshots/bottom.png)。

本地查看：在仓库根运行 `python3 -m http.server 8000`，打开 `http://localhost:8000/taste/`。两份原始页面也可直接打开。

## 照片来源与公开范围

森林照片：Jordan Sanchez，[Unsplash 原图](https://unsplash.com/photos/sLraJyotfeY)，通过 [Lorem Picsum #786](https://picsum.photos/id/786/info) 获取。原始 JPEG 的 EXIF 标注 `Picsum ID: 786`，与元数据接口匹配。照片按 [Unsplash License](https://unsplash.com/license) 使用；不将其宣称为原创或另行授予许可证。

仅公开合成任务、原始页面、所需照片、截图及任务输入。不公开宿主指令、完整模型会话、个人配置、临时目录和凭证。固定 Skill 通过官方版本链接引用，不将第三方仓库材料误作自有内容。
