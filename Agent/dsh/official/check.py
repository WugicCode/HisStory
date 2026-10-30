# -*- coding: utf-8 -*-
"""静态站自检：链接、资源、计数、关系对称、SVG 合法性、文本残留。"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

import cardsource
import content
import data_site

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "OfficialPage"

ERRORS = []
WARNINGS = []


def fail(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def local_target(page: Path, raw: str):
    raw = raw.strip()
    if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc:
        return None
    path = unquote(parts.path)
    if not path:
        return None
    target = (page.parent / path).resolve()
    try:
        target.relative_to(OUT.resolve())
    except ValueError:
        fail(f"{page.relative_to(OUT)}: 链接跑出站点目录 -> {raw}")
        return None
    return target


def check_links() -> None:
    html_files = sorted(OUT.rglob("*.html"))
    for page in html_files:
        text = page.read_text(encoding="utf-8")
        for attr in ("href", "src"):
            for m in re.finditer(rf'{attr}="([^"]+)"', text):
                target = local_target(page, m.group(1))
                if target is None:
                    continue
                if not target.exists():
                    fail(f"{page.relative_to(OUT)}: {attr} 目标不存在 -> {m.group(1)}")
        for m in re.finditer(r'data-zoom="([^"]+)"', text):
            target = local_target(page, m.group(1))
            if target is None or not target.exists():
                fail(f"{page.relative_to(OUT)}: data-zoom 目标不存在 -> {m.group(1)}")


def check_svg() -> None:
    svgs = sorted((OUT / "assets").rglob("*.svg"))
    for svg in svgs:
        try:
            ET.parse(svg)
        except Exception as exc:  # noqa: BLE001
            fail(f"SVG 解析失败 {svg.relative_to(OUT)}: {exc}")
    if len(svgs) < 86 + 8 + 21 + 1:
        warn(f"SVG 数量偏少：{len(svgs)}")


def check_counts() -> None:
    cards = cardsource.load_cards()
    if len(cards) != 86:
        fail(f"卡牌数量 {len(cards)} != 86")
    if len(content.ALL) != 86:
        fail(f"content.ALL {len(content.ALL)} != 86")
    card_pages = list((OUT / "game" / "cards").glob("*.html"))
    if len(card_pages) != 87:  # 86 + index
        fail(f"卡页数量 {len(card_pages)} != 87")
    for c in cards:
        page = OUT / "game" / "cards" / f'{c["id"]}.html'
        if not page.exists():
            fail(f"缺卡页 {c['id']}")
            continue
        text = page.read_text(encoding="utf-8")
        if "肥鱼碎碎念" not in text:
            fail(f"{c['id']}: 缺肥鱼碎碎念")
        if "PLATE" not in text:
            fail(f"{c['id']}: 缺图版编号")
        if "关联" not in text:
            fail(f"{c['id']}: 缺关联区")
    if len(list((OUT / "game" / "cards").glob("*.svg"))) > 0:
        fail("assets 与 cards 页面混层")

    # 关系对称（content 内部）
    ids = {c["id"] for c in cards}
    link_count = 0
    for cid, meta in content.ALL.items():
        for target, rel, why in meta.get("links", []):
            link_count += 1
            if target not in ids:
                fail(f"{cid}: 关联目标不存在 {target}")
            if not rel or not why:
                fail(f"{cid} -> {target}: 关系或说明为空")
    if link_count != 291:
        warn(f"关联条数 {link_count} != 291")

    # 编组覆盖
    for c in cards:
        if not any(c["group_slug"] == s[0] for s in [
            ("general",), ("novian",), ("lilia",), ("eve",), ("moika",),
            ("milika",), ("herseus",), ("scarlin",), ("morphy",),
        ]):
            fail(f"{c['id']}: group_slug 不在页面分区 {c['group_slug']}")


def check_atlas() -> None:
    cards = cardsource.load_cards()
    ids = {c["id"] for c in cards}
    for line in data_site.ATLAS:
        for chain in line["chains"]:
            for cid in chain["ids"]:
                if cid not in ids:
                    fail(f"ATLAS {line['title']}: 未知卡 id {cid}")
    for _, a_id, _, b_id, _ in data_site.CROSS_REFS:
        for cid in (a_id, b_id):
            if cid not in ids:
                fail(f"CROSS_REFS: 未知卡 id {cid}")
    cast_ids = {p["id"] for p in data_site.CAST}
    for p in data_site.CAST:
        if p.get("cards") and p["cards"] not in {s[0] for s in [
            ("general",), ("novian",), ("lilia",), ("eve",), ("moika",),
            ("milika",), ("herseus",), ("scarlin",), ("morphy",),
        ]}:
            fail(f"CAST {p['id']}: cards 编组不存在 {p['cards']}")
        if p["id"] not in cast_ids:
            fail(f"CAST: 重复 id {p['id']}")


def check_text() -> None:
    for page in sorted(OUT.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        if "forbid" in text:
            fail(f"{page.relative_to(OUT)}: 残留英文 forbid")
        if "**" in text:
            fail(f"{page.relative_to(OUT)}: 残留 Markdown 星号")
        if "None" in text:
            warn(f"{page.relative_to(OUT)}: 出现 None")
        if "<title>" not in text:
            fail(f"{page.relative_to(OUT)}: 缺 title")
        if "assets/site.css" not in text and "assets/site.css" not in text.replace("../", "").replace("../../", ""):
            fail(f"{page.relative_to(OUT)}: 缺 CSS")
        if "assets/site.js" not in text:
            fail(f"{page.relative_to(OUT)}: 缺 JS")


def check_pages() -> None:
    expected = [
        "index.html", "world.html", "history.html", "cast.html", "novel.html",
        "about.html", "404.html", "game/index.html", "game/play.html",
        "game/concept.html", "game/atlas.html", "game/cards/index.html",
    ]
    for rel in expected:
        if not (OUT / rel).exists():
            fail(f"缺页面 {rel}")
    for page in OUT.rglob("*.html"):
        if page.stat().st_size < 1200:
            warn(f"{page.relative_to(OUT)}: 体积偏小 {page.stat().st_size}")


def main() -> int:
    if not OUT.exists():
        print("OfficialPage 不存在，先运行 build.py")
        return 2
    check_links()
    check_svg()
    check_counts()
    check_atlas()
    check_text()
    check_pages()
    print(f"pages={len(list(OUT.rglob('*.html')))} svg={len(list((OUT/'assets').rglob('*.svg')))}")
    for w in WARNINGS:
        print("WARN", w)
    for e in ERRORS:
        print("FAIL", e)
    if ERRORS:
        print(f"\n{len(ERRORS)} error(s)")
        return 1
    print("check ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
