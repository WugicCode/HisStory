# 长歌 · 官方页构建源

这个目录是 `OfficialPage/` 的生成器与内容源。`OfficialPage/` 是可直接发布的静态站，不放构建脚本。

## 运行

```powershell
cd Agent/dsh/official
python build.py
python check.py
```

`build.py` 会清空并重建 `../../../OfficialPage/`；`check.py` 检查页面链接、资源路径、86 张卡的分区归属、关系对称与图版数量。当前口径：

- 98 个页面（12 个栏目页 + 86 张卡页）
- 86 张卡、291 条关系
- 117 个 SVG（86 卡面 + 9 图版 + 21 人物纹章 + 1 站点图标）
- 21 位人物、9 条年表、18 个词条

## 文件

| 文件 | 作用 |
| --- | --- |
| `cardsource.py` | 只读解析 `Game/CardsDesign.md`，产出 86 张卡的结构化数据与稳定 id |
| `content_general.py` | 通用 11 张的 role / 标签 / 图版 / 关联 / 肥鱼碎碎念 |
| `content_novian.py` | 诺维安 12 张 |
| `content_lilia.py` | 莉莉亚 17 张 |
| `content_eve.py` | 伊芙格林 17 张 |
| `content_moika.py` | 莫伊卡 9 张 |
| `content_rest.py` | 米莉卡、赫琉思、斯卡琳、莫菲 20 张 |
| `content.py` | 合并六组、反向关系、全量校验 |
| `data_site.py` | 人物、年表、史书之外、三定律、种族、组织、地名、词条、关系类型、概念图、八条谱系、跨阵营对照 |
| `art.py` | 程序化 SVG：卡面、人物纹章、概念图、封面、游戏编封面 |
| `theme.py` | 全站 CSS 与交互 JS |
| `build.py` | 页面模板与 98 页生成 |
| `check.py` | 静态自检 |

## 口径与边界

- 卡牌原文只从 `Game/CardsDesign.md` 读取；页面上的「原文」是原典，不改写。
- 「肥鱼碎碎念」是归档者的读卡笔记，不进入规则结论；其中标了「待确认」的地方，是原典没有写死、需要作者裁定的接口。
- 跨阵营的卡只建立「对照」关系，不写成同一套牌里的联动。
- 人物页与史书页采用「只暗示、不转录」的写法；`APOCRYPHA` 只列问题，不给答案。
- 小说区目前只有「筹备中」与发布计划，`MainStory/` 的正文尚未接入。发布载体按 GitHub Pages 设计：全站相对路径、无外部字体/库、`file://` 可直接打开。
- 构建过程不会修改 `Game/`、`MainStory/` 或根目录大纲。

## 发布

`OfficialPage/` 已经是 GitPage-ready：入口 `OfficialPage/index.html`，含 `.nojekyll`。仓库使用 GitHub Actions 发布：`.github/workflows/pages.yml` 会在 `main` 分支的 `OfficialPage/` 变化时上传该目录。GitHub 仓库的 `Settings → Pages → Source` 选 **GitHub Actions** 即可。卡页与资源全部使用相对路径；换到子路径（例如 `/HisStory/`）也不需要改代码。

## 分支

日常改动提交在 `dsh`，经 `dev` 验证后合并到 `main`；`main` 是正式发布分支，推送 `main` 才会触发 Pages 部署。
