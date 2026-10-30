# -*- coding: utf-8 -*-
"""长歌官方页 · 官方维护编辑器。

只在 127.0.0.1 上运行，不进入 GitPage。
用法：
    python Tools/OfficialPageEditor/server.py
    python Tools/OfficialPageEditor/server.py --port 8765 --no-open
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(__file__).resolve().parent


def _find_root(start: Path) -> Path:
    """从工具目录向上找仓库根，避免写死层级。"""
    for candidate in (start, *start.parents):
        if (candidate / "OfficialPage").is_dir() and (candidate / "Agent" / "dsh" / "official" / "build.py").is_file():
            return candidate
    raise RuntimeError("找不到仓库根目录（需要 OfficialPage/ 与 Agent/dsh/official/build.py）")


ROOT = _find_root(HERE)
SITE = ROOT / "OfficialPage"
OFFICIAL = ROOT / "Agent" / "dsh" / "official"

sys.path.insert(0, str(OFFICIAL))
import textpatch  # noqa: E402

BUILD_LOCK = threading.Lock()

PAGE_LABELS = {
    "index.html": "序 · 首页",
    "world.html": "世界",
    "history.html": "战史",
    "cast.html": "人物",
    "novel.html": "小说",
    "about.html": "关于",
    "404.html": "404",
    "game/index.html": "游戏编",
    "game/play.html": "玩法",
    "game/concept.html": "概念图",
    "game/atlas.html": "关系谱",
    "game/cards/index.html": "卡牌档案",
}

FIXED_ORDER = [
    "index.html",
    "world.html",
    "history.html",
    "cast.html",
    "novel.html",
    "about.html",
    "game/index.html",
    "game/play.html",
    "game/concept.html",
    "game/atlas.html",
    "game/cards/index.html",
]

H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)


def _plain(value: str) -> str:
    value = TAG_RE.sub("", value)
    return re.sub(r"\s+", " ", value).strip()


def _title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return path.stem
    match = H1_RE.search(text)
    if match:
        value = _plain(match.group(1))
        if value:
            return value
    match = TITLE_RE.search(text)
    if match:
        return _plain(match.group(1)).replace(" · 长歌", "")
    return path.stem


def _group(rel: str) -> str:
    if rel == "game/cards/index.html" or rel.startswith("game/cards/"):
        return "卡牌档案"
    if rel.startswith("game/"):
        return "游戏编"
    return "总览"


def _rank(rel: str) -> int:
    if rel in FIXED_ORDER:
        return FIXED_ORDER.index(rel)
    if rel.startswith("game/cards/"):
        return 1000
    return 500


def list_pages() -> list[dict]:
    patches = textpatch.load()
    pages: list[dict] = []
    if not SITE.exists():
        return pages
    for path in SITE.rglob("*.html"):
        if "assets" in path.parts:
            continue
        rel = path.relative_to(SITE).as_posix()
        pages.append(
            {
                "path": rel,
                "title": PAGE_LABELS.get(rel) or _title(path),
                "group": _group(rel),
                "patched": len(patches.get(rel, [])),
            }
        )
    group_order = {"总览": 0, "游戏编": 1, "卡牌档案": 2}
    pages.sort(key=lambda item: (group_order.get(item["group"], 9), _rank(item["path"]), item["title"]))
    return pages


def _resolve_site(rel: str, *, html_only: bool = False) -> tuple[Path, str]:
    if not isinstance(rel, str):
        raise ValueError("路径无效")
    rel = unquote(rel).replace("\\", "/").strip()
    if not rel or rel.startswith("/"):
        raise ValueError("路径无效")
    parts = [part for part in rel.split("/") if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise ValueError("路径无效")
    target = SITE.joinpath(*parts).resolve()
    site = SITE.resolve()
    if target != site and site not in target.parents:
        raise ValueError("路径越界")
    if target.is_dir():
        target = target / "index.html"
        parts.append("index.html")
    if html_only and target.suffix.lower() != ".html":
        raise ValueError("不是页面")
    if not target.is_file():
        raise FileNotFoundError("文件不存在")
    return target, "/".join(parts)


def _clean_changes(raw) -> list[dict]:
    if not isinstance(raw, list):
        raise ValueError("changes 必须是数组")
    changes: list[dict] = []
    for item in raw[:300]:
        if not isinstance(item, dict):
            continue
        old = item.get("old")
        new = item.get("new")
        if not isinstance(old, str) or not isinstance(new, str):
            continue
        old = old.strip()
        new = new.strip()
        if not old or old == new or len(old) > 4000 or len(new) > 4000:
            continue
        index = item.get("index")
        try:
            index = int(index) if index is not None else None
        except (TypeError, ValueError):
            index = None
        changes.append({"old": old, "new": new, "index": index})
    if not changes:
        raise ValueError("没有可保存的修改")
    return changes


def _build() -> str:
    with BUILD_LOCK:
        proc = subprocess.run(
            [sys.executable, str(OFFICIAL / "build.py")],
            cwd=str(OFFICIAL),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            tail = output[-4000:] if output else f"build.py 退出码 {proc.returncode}"
            raise RuntimeError(tail)
        return output.strip()


class Handler(BaseHTTPRequestHandler):
    server_version = "OfficialPageEditor/1.0"

    def log_message(self, fmt, *args):  # noqa: A003
        sys.stderr.write("[editor] " + (fmt % args) + "\n")

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def _json(self, code: int, data) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def _file(self, path: Path) -> None:
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix.lower() in {".html", ".css", ".js", ".svg", ".txt", ".json"}:
            ctype += "; charset=utf-8"
        self._send(200, path.read_bytes(), ctype)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path in ("/", "/index.html"):
                self._file(HERE / "index.html")
            elif path == "/ui.css":
                self._file(HERE / "ui.css")
            elif path == "/ui.js":
                self._file(HERE / "ui.js")
            elif path == "/api/pages":
                self._json(200, {"pages": list_pages()})
            elif path == "/api/patches":
                rel = parse_qs(parsed.query).get("path", [""])[0]
                _, clean = _resolve_site(rel, html_only=True)
                self._json(200, {"path": clean, "patches": textpatch.load().get(clean, [])})
            elif path == "/favicon.ico":
                self._send(204, b"", "image/x-icon")
            elif path.startswith("/site/"):
                rel = path[len("/site/"):]
                target, _ = _resolve_site(rel)
                self._file(target)
            else:
                self._json(404, {"ok": False, "error": "not found"})
        except FileNotFoundError:
            self._json(404, {"ok": False, "error": "文件不存在"})
        except ValueError as exc:
            self._json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2_000_000:
                raise ValueError("请求体无效")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("请求体无效")
            if parsed.path == "/api/save":
                self._save(data)
            elif parsed.path == "/api/reset":
                self._reset(data)
            elif parsed.path == "/api/rebuild":
                self._rebuild()
            else:
                self._json(404, {"ok": False, "error": "not found"})
        except ValueError as exc:
            self._json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})

    def _save(self, data: dict) -> None:
        _, rel = _resolve_site(data.get("path", ""), html_only=True)
        changes = _clean_changes(data.get("changes"))
        before = textpatch.load()
        after = json.loads(json.dumps(before, ensure_ascii=False))
        after.setdefault(rel, []).extend(changes)
        textpatch.save(after)
        try:
            output = _build()
        except Exception:
            textpatch.save(before)
            raise
        self._json(200, {"ok": True, "count": len(changes), "path": rel, "output": output[-1200:]})

    def _reset(self, data: dict) -> None:
        _, rel = _resolve_site(data.get("path", ""), html_only=True)
        before = textpatch.load()
        after = json.loads(json.dumps(before, ensure_ascii=False))
        after.pop(rel, None)
        textpatch.save(after)
        try:
            output = _build()
        except Exception:
            textpatch.save(before)
            raise
        self._json(200, {"ok": True, "path": rel, "output": output[-1200:]})

    def _rebuild(self) -> None:
        self._json(200, {"ok": True, "output": _build()[-1200:]})


def main() -> None:
    parser = argparse.ArgumentParser(description="长歌官方页 · 官方维护编辑器")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    if not SITE.exists():
        raise SystemExit(f"找不到 OfficialPage：{SITE}")

    httpd = None
    for port in range(args.port, args.port + 20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            httpd.daemon_threads = True
            break
        except OSError:
            continue
    if httpd is None:
        raise SystemExit("找不到可用端口")

    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    print(f"长歌官方页编辑器：{url}")
    print("Ctrl+C 停止。修改保存在 Tools/OfficialPageEditor/patches.json，重建后仍会应用。")
    if not args.no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
