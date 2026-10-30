# -*- coding: utf-8 -*-
"""正文文字补丁层。

官方页的可见正文由 build.py 生成。这里保存一份「原件文字 -> 新文字」的补丁，
在 build.py 写出每页之前应用，这样本地文本编辑器的修改不会被下一次重建覆盖。

补丁只作用于 <main> 里的文本节点，不碰属性、链接与脚本。
"""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATCH_FILE = ROOT / "Agent" / "dsh" / "editor" / "patches.json"

_MAIN_RE = re.compile(r"(<main\b[^>]*>)(.*?)(</main>)", re.S | re.I)
_RULE_NOTE_RE = re.compile(r'[ \t]*<p class="rule-note">(.*?)</p>[ \t]*(?:\r?\n)?', re.S)
_TOKEN_RE = re.compile(r"<[^>]*>|[^<]+", re.S)
_TAG_RE = re.compile(r"<\s*(/?)\s*([a-zA-Z0-9:-]+)")
_SKIP_TAGS = {"script", "style", "code", "pre", "svg", "button", "textarea", "select", "option"}


def load() -> dict:
    """读取补丁文件；缺失或损坏时当作空补丁。"""
    try:
        data = json.loads(PATCH_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save(data: dict) -> None:
    PATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = PATCH_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, PATCH_FILE)


def _replace_visible_token(main: str, old: str, new: str, index: int | None) -> tuple[str, bool]:
    """在 <main> 内部替换一个可见文本节点。

    index 是编辑器看到的非空文本节点序号；如果序号对不上（页面结构变了），
    再退回按文字查找。只替换第一个匹配，避免误伤重复文字。
    """
    tokens = _TOKEN_RE.findall(main)
    if not tokens:
        return main, False

    target = None
    text_index = -1
    skip = 0
    for i, token in enumerate(tokens):
        if token.startswith("<"):
            match = _TAG_RE.match(token)
            if match and match.group(2).lower() in _SKIP_TAGS:
                if match.group(1):
                    skip = max(0, skip - 1)
                elif not token.rstrip().endswith("/>"):
                    skip += 1
            continue
        if skip or not token.strip():
            continue
        text_index += 1
        if text_index == index:
            target = i
            break

    def replace_at(i: int) -> bool:
        text = html.unescape(tokens[i])
        pos = text.find(old)
        if pos < 0:
            return False
        tokens[i] = html.escape(text[:pos] + new + text[pos + len(old):], quote=False)
        return True

    changed = target is not None and replace_at(target)
    if not changed:
        # 序号失效时退回文字查找；跳过 script/style。
        skip = 0
        for i, token in enumerate(tokens):
            if token.startswith("<"):
                match = _TAG_RE.match(token)
                if match and match.group(2).lower() in _SKIP_TAGS:
                    if match.group(1):
                        skip = max(0, skip - 1)
                    elif not token.rstrip().endswith("/>"):
                        skip += 1
                continue
            if skip or not token.strip():
                continue
            if old in html.unescape(token):
                changed = replace_at(i)
                break

    if not changed:
        return main, False
    return "".join(tokens), True


def _drop_empty_rule_notes(main: str) -> str:
    """删掉被编辑到完全空白的 rule-note，避免留下空框。"""

    def repl(match: re.Match[str]) -> str:
        text = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        return "" if not text else match.group(0)

    return _RULE_NOTE_RE.sub(repl, main)


def apply_page(page_html: str, page: str) -> tuple[str, int, int]:
    """把某页的补丁应用到生成的 HTML，返回 (html, 成功数, 失效数)。"""
    patches = load().get(page)
    if not isinstance(patches, list) or not patches:
        return page_html, 0, 0

    match = _MAIN_RE.search(page_html)
    if not match:
        return page_html, 0, len(patches)

    main = match.group(2)
    applied = 0
    stale = 0
    for item in patches:
        if not isinstance(item, dict):
            stale += 1
            continue
        old = item.get("old")
        new = item.get("new")
        if not isinstance(old, str) or not isinstance(new, str) or not old or old == new:
            continue
        index = item.get("index")
        try:
            index = int(index) if index is not None else None
        except (TypeError, ValueError):
            index = None
        updated, ok = _replace_visible_token(main, old, new, index)
        if ok:
            main = updated
            applied += 1
        else:
            stale += 1

    if not applied:
        return page_html, 0, stale
    main = _drop_empty_rule_notes(main)
    return page_html[: match.start(2)] + main + page_html[match.end(2):], applied, stale
