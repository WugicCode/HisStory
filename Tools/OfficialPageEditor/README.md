# 长歌官方页编辑器

> 官方内部工具，仅供企划维护者本地使用。  
> 不部署到 GitPage，不随 `OfficialPage/` 发布。

这个工具用来直接修改官方页的正文文字。它编辑的不是最终 HTML，而是
`patches.json` 里的「原文字 → 新文字」补丁；`build.py` 重建页面时会把补丁应用到
`<main>` 的文本节点上，所以修改不会被下一次构建覆盖。

## 启动

需要 Python 3.10+。在仓库根目录（`D:\Projects\HisStory`）运行：

```powershell
python Tools/OfficialPageEditor/server.py
```

浏览器会自动打开 `http://127.0.0.1:8765/`。如果端口被占用，会自动尝试后面的端口。
也可以指定端口、或者不自动开浏览器：

```powershell
python Tools/OfficialPageEditor/server.py --port 8765 --no-open
```

## 怎么用

- 左边选页面，右边直接点正文修改；链接在编辑模式里不会跳转。
- 改完按 `Ctrl+S`，或点右上角「保存并重建」。
- 保存会做三件事：把修改写入 `Tools/OfficialPageEditor/patches.json` → 重跑
  `Agent/dsh/official/build.py` → 重新载入页面。
- 「还原此页」会删除该页的所有文字补丁并重建。
- 「重建站点」只重跑 `build.py`，不修改补丁。
- 带圆点的页面表示已有补丁；侧栏搜索可以按标题过滤。

## 边界

- 只改可见正文，不改属性、链接、脚本、SVG、卡面图和版式。
- 只处理 `<main>` 里的文本节点；页头、页脚、导航不在编辑范围内。
- 把一条「规则注」删到完全空白时，重建会自动移除这个空块；需要恢复时点「还原此页」。
- 不要直接改 `OfficialPage/*.html`：它是生成产物，下一次 `build.py` 会覆盖。
- 修改历史可以直接看 `git diff Tools/OfficialPageEditor/patches.json`。

## 文件

- `server.py` — 本地 HTTP 服务，只用 Python 标准库
- `index.html` / `ui.css` / `ui.js` — 编辑器界面
- `patches.json` — 官方页文字补丁，属于内容资产，随仓库提交
- `../../Agent/dsh/official/textpatch.py` — 补丁层的应用逻辑，由 `build.py` 调用

## 注意

- 只监听 `127.0.0.1`，不要把它暴露到公网。
- 这个目录在 `Tools/` 下，不属于 `OfficialPage/`，GitPage 不会发布它。
- `patches.json` 与 `OfficialPage/` 必须一起提交，否则部署后的页面会缺少修改。
- 如果改了 `build.py` 的页面结构，已有补丁可能需要「还原此页」后重做。
