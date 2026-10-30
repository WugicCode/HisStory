# 长歌官方页 · 本地文本编辑器

这是一个只在本地运行的编辑工具，用来直接修改 `OfficialPage/` 里的正文文字。
它**不会**进入 GitPage；`OfficialPage/` 仍然是可以单独部署的静态站点。

## 启动

在仓库根目录（`D:\Projects\HisStory`）运行：

```powershell
python Agent/dsh/editor/server.py
```

浏览器会自动打开 `http://127.0.0.1:8765/`。如果端口被占用，会自动尝试后面的端口。
也可以指定端口、或者不自动开浏览器：

```powershell
python Agent/dsh/editor/server.py --port 8765 --no-open
```

## 怎么用

- 左边选页面，右边直接点正文修改；链接在编辑模式里不会跳转。
- 改完按 `Ctrl+S`，或点右上角「保存并重建」。
- 保存会做三件事：把修改写入 `Agent/dsh/editor/patches.json` → 重跑 `Agent/dsh/official/build.py` → 重新载入页面。
- 「还原此页」会删除该页的所有文字补丁并重建。
- 「重建」只重跑 `build.py`，不修改补丁。
- 带圆点的页面表示已有补丁；侧栏搜索可以按标题过滤。

## 原理

`build.py` 每次生成页面后，会把 `patches.json` 里对应页面的「原文字 → 新文字」补丁应用到 `<main>` 的文本节点上，然后再写出 HTML。因此：

- 修改不会被下一次重建覆盖；
- 不需要把 `build.py` 里的文案重构成数据库；
- 补丁只作用于正文文本，不碰属性、链接、脚本和 SVG；
- `OfficialPage/` 在没有补丁文件时也能独立构建、独立部署。

补丁按保存顺序链式应用。如果页面结构后来变了，找不到原文字的补丁会被跳过，服务端会打印 `stale` 数量。

## 文件

- `server.py` — 本地 HTTP 服务（Python 标准库，无第三方依赖）
- `index.html` / `ui.css` / `ui.js` — 编辑器界面
- `patches.json` — 文字补丁（提交到仓库，重建时使用）

## 注意

- 只监听 `127.0.0.1`，不要把它暴露到公网。
- 这个目录在 `Agent/dsh/` 下，不属于 `OfficialPage/`，GitPage 不会发布它。
- 如果把一条「规则注」删到完全空白，重建时会自动移除这个空块；需要恢复时点「还原此页」。
- 如果改了 `build.py` 的页面结构，已有补丁可能需要「还原此页」后重做。
