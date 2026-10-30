# -*- coding: utf-8 -*-
"""长歌·归档页 —— 静态站点构建器
所有输出都写在 dsh/ 目录内；只读取 dsh/src/ 中的数据与图象模块。
"""
import json
import math
import re
import os
from pathlib import Path

import art
import meta as M
import meta_rules as R
import meta_world as MW
from data_cards import CARD_LIST

ROOT = Path(__file__).resolve().parent.parent          # dsh/
IMG = ROOT / "assets" / "img"
CARDS_DIR = ROOT / "cards"
HEROES_DIR = ROOT / "heroes"

QKEY = {"N": "N", "R": "R", "E": "E", "L": "L", "域外": "O", "—": "T"}
FAC_SLUG = {"新的勇者": "new-heroes", "同盟军": "alliance", "魔王军": "demon-army", "通用": "common"}

BY = {c["id"]: c for c in CARD_LIST}
HERO_BY = {h["id"]: h for h in M.HEROES}
CL_BY = {c["id"]: c for c in M.CLUSTERS}


# ══════════════════════════════ 基础工具 ══════════════════════════════

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def rich(s):
    """转义后把【词条】变成粗体。"""
    s = esc(s)
    out, i = [], 0
    while True:
        a = s.find("【", i)
        if a < 0:
            out.append(s[i:])
            break
        b = s.find("】", a)
        if b < 0:
            out.append(s[i:])
            break
        out.append(s[i:a])
        out.append("<b>" + s[a + 1:b] + "</b>")
        i = b + 1
    return "".join(out)


def short_text(c, n=78):
    t = c["text"]
    cut = t.find("。")
    if 0 < cut < n:
        return t[:cut + 1]
    if len(t) > n:
        return t[:n - 1] + "…"
    return t


WORDS = {80: "EIGHTY", 81: "EIGHTY-ONE", 82: "EIGHTY-TWO", 83: "EIGHTY-THREE", 84: "EIGHTY-FOUR",
         85: "EIGHTY-FIVE", 86: "EIGHTY-SIX", 87: "EIGHTY-SEVEN", 88: "EIGHTY-EIGHT", 89: "EIGHTY-NINE"}
CN = {10: "十", 11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五", 16: "十六"}


def qty(n):
    return WORDS.get(n, str(n)) + (" ENTRY" if n == 1 else "")


def cn_num(n):
    return CN.get(n, str(n))


def qname(q):
    return M.QUALITY.get(q, (q, q))[0]


def qlatin(q):
    return M.QUALITY.get(q, (q, q))[1]


def type_line(c):
    parts = [c["cat"]]
    if c.get("utype"):
        parts.append(c["utype"])
    return " · ".join(parts)


def talent_ids(hero_id):
    return [c["id"] for c in CARD_LIST if c["cat"] == "天赋" and c.get("hero") == hero_id]


def cards_of_hero(hero_id):
    return [c for c in CARD_LIST if c.get("hero") == hero_id]


def cards_of_cluster(cid):
    return [c for c in CARD_LIST if c["cluster"] == cid]


def valid_links(c):
    out = []
    for l in c.get("links") or []:
        if not l:
            continue
        tgt = l[0]
        if tgt not in BY:
            continue
        out.append(l)
    return out


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ══════════════════════════════ 页面骨架 ══════════════════════════════

NAV_MAIN = [("世界观", "#world"), ("战争史", "story.html"), ("人物", "cast.html"),
            ("战场", "#board"), ("玩法", "#play"), ("阵营", "#factions"),
            ("图鉴", "archive.html"), ("沙盘", "sandbox.html"),
            ("规则", "rulebook.html")]

NAV_SUB = [("世界观", "world.html"), ("战争史", "story.html"), ("人物", "cast.html"),
           ("图鉴", "archive.html"), ("沙盘", "sandbox.html"),
           ("规则", "rulebook.html"), ("主页", "index.html")]


def head(title, desc, root=""):
    return (
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + esc(title) + ' · 长歌 HisStory</title>'
        '<meta name="description" content="' + esc(desc) + '">'
        '<meta name="theme-color" content="#07080c">'
        '<link rel="stylesheet" href="' + root + 'assets/css/style.css">'
        '</head><body data-root="' + root + '">'
    )


def nav(root="", sub=False, current=""):
    links = NAV_SUB if sub else NAV_MAIN
    out = ['<div class="nav-prog"></div>',
           '<header class="nav">',
           '<a class="nav-brand" href="' + root + 'index.html">',
           '<svg class="nav-mark" viewBox="0 0 32 32" aria-hidden="true">'
           '<path d="M22 4a13 13 0 100 24 10 10 0 110-24z" fill="none" stroke="currentColor" stroke-width="1.4"/>'
           '<path d="M16 24V9" stroke="currentColor" stroke-width="1"/></svg>',
           '<span><span class="nav-name">长歌</span><span class="nav-latin">HISSTORY</span></span>',
           '</a><nav class="nav-links">']
    for label, href in links:
        cls = ' class="is-active"' if href.split("#")[0] == current and current else ""
        out.append('<a href="' + (href if href.startswith("#") else root + href) + '"' + cls + '>' + label + '</a>')
    out.append("</nav></header>")
    return "".join(out)


def foot(root="", extra=""):
    return ('<footer class="foot"><div class="wrap"><div class="foot-grid"><div>'
            '<h4>长歌</h4><p>' + esc(M.FOOTER["credit"]) + '</p>'
            '<p>' + esc(M.FOOTER["note"]) + '</p>'
            '<p>' + esc(M.FOOTER["files"]) + '</p>'
            '</div><div class="foot-mark">月亮升起之前，先把路走完</div></div></div></footer>'
            '<script src="' + root + 'assets/js/site.js"></script>' + extra + '</body></html>')


def sec(sid, no, cn, en, lead, body):
    return ('<section class="sec" id="' + sid + '"><div class="wrap">'
            '<div class="sec-head reveal"><div class="sec-no">' + no + '</div><div>'
            '<h2 class="sec-title">' + cn + '<small>' + en + '</small></h2>'
            + ('<p class="sec-lead">' + lead + '</p>' if lead else "") +
            '</div></div>' + body + '</div></section>')


# ══════════════════════════════ 卡面 ══════════════════════════════

def face(c, root="", href=True, cls="", text=None, lazy=True):
    q = c["q"]
    art_src = root + "assets/img/cards/" + c["id"] + ".svg"
    stats = c.get("stats") or ""
    if stats in ("-", "—"):
        stats = ""
    inner = (
        '<div class="cface-cost">' + esc(c.get("cost") or "—") + '</div>'
        '<div class="cface-q">' + esc(qname(q)) + '</div>'
        '<div class="cface-art"><img src="' + art_src + '" alt="' + esc(c["name"]) + '"' +
        (' loading="lazy"' if lazy else "") + '></div>'
        '<div class="cface-body">'
        '<div class="cface-name">' + esc(c["name"]) + '</div>'
        '<div class="cface-type">' + esc(type_line(c)) + '</div>'
        + ('<div class="cface-stats">' + esc(stats) + '</div>' if stats else "") +
        '<div class="cface-text">' + rich(c["text"] if text is None else text) + '</div>'
        '<div class="cface-foot"><span>' + esc(c["fac"]) + '</span><span>' +
        esc(c["cat"]) + '</span></div>'
        '</div>')
    attrs = ' data-q="' + QKEY.get(q, "N") + '" class="cface ' + cls + '"'
    if href:
        return '<a' + attrs + ' href="' + root + 'cards/' + c["id"] + '.html">' + inner + '</a>'
    return '<div' + attrs + '>' + inner + '</div>'


def grid(cards, root="", cls="", items_cls=""):
    if not cards:
        return ""
    out = ['<div class="grid-cards ' + cls + '">']
    for c in cards:
        out.append('<div class="' + items_cls + '">' + face(c, root) + '</div>')
    out.append("</div>")
    return "".join(out)


# ══════════════════════════════ 星图 ══════════════════════════════

def star_map(nodes, edges, w=880, h=560, center=None):
    """nodes: dict(id,label,color,size[,href]) ; edges: (a,b)"""
    pos = {}
    if center:
        pos[center] = (w / 2.0, h / 2.0)
        ring = [n for n in nodes if n["id"] != center]
        R = min(w, h) / 2.0 - 86
        for i, n in enumerate(ring):
            a = -math.pi / 2 + 2 * math.pi * i / max(1, len(ring))
            pos[n["id"]] = (w / 2 + R * 1.28 * math.cos(a), h / 2 + R * math.sin(a))
    else:
        R = min(w, h) / 2.0 - 72
        for i, n in enumerate(nodes):
            a = -math.pi / 2 + 2 * math.pi * i / max(1, len(nodes))
            pos[n["id"]] = (w / 2 + R * 1.34 * math.cos(a), h / 2 + R * math.sin(a))

    svg = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="卡牌关系星图">' % (w, h, w, h)]
    seen = set()
    for a, b in edges:
        if a == b or a not in pos or b not in pos:
            continue
        key = (a, b) if a < b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        svg.append('<line class="cedge" data-a="%s" data-b="%s" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                   % (esc(a), esc(b), x1, y1, x2, y2))
    for n in nodes:
        if n["id"] not in pos:
            continue
        x, y = pos[n["id"]]
        r = n.get("size", 5)
        tag = "a" if n.get("href") else "g"
        href_attr = ' href="%s"' % n["href"] if n.get("href") else ""
        svg.append('<%s class="cnode" data-id="%s" tabindex="0"%s>' % (tag, esc(n["id"]), href_attr))
        svg.append('<circle class="halo" cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                   % (x, y, r * 4.6, n.get("color", "#c8a86a")))
        svg.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="0.85"/>'
                   % (x, y, r, n.get("color", "#c8a86a")))
        svg.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="0.8" opacity="0.5"/>'
                   % (x, y, r + 4, n.get("color", "#c8a86a")))
        svg.append('<text x="%.1f" y="%.1f" text-anchor="middle" paint-order="stroke" stroke="#08090d" stroke-width="4" stroke-linejoin="round">%s</text>'
                   % (x, y - r - 10, esc(n.get("label", n["id"]))))
        svg.append('</%s>' % tag)
    svg.append("</svg>")
    return "".join(svg)


# ══════════════════════════════ 战场图 ══════════════════════════════

def board_svg():
    W, H = 1000, 360
    x0, step, bw, by, bh = 76, 176, 160, 118, 158
    s = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="战场示意图">' % (W, H, W, H)]
    s.append('<defs><linearGradient id="bl" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#c8a86a" stop-opacity=".22"/>'
             '<stop offset=".5" stop-color="#9aa8b8" stop-opacity=".10"/>'
             '<stop offset="1" stop-color="#c8a86a" stop-opacity=".22"/></linearGradient></defs>')
    s.append('<line x1="40" y1="%d" x2="%d" y2="%d" stroke="url(#bl)" stroke-width="1"/>'
             % (by + bh + 30, W - 40, by + bh + 30))
    # 信仰
    for cx, label in ((52, "我方信仰"), (W - 52, "敌方信仰")):
        cy = by + bh / 2.0
        s.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="rgba(200,168,106,.08)" stroke="rgba(200,168,106,.6)" stroke-width="1.2"/>'
                 % (cx, cy - 44, cx + 34, cy, cx, cy + 44, cx - 34, cy))
        s.append('<text class="faith-num" x="%.1f" y="%.1f" text-anchor="middle">1000</text>' % (cx, cy - 52))
        s.append('<text class="zone-name" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                 % (cx, cy + 62, label))
    romans = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ"]
    for i in range(1, 6):
        x = x0 + (i - 1) * step
        s.append('<g class="zone" data-z="%d">' % i)
        s.append('<rect x="%d" y="%d" width="%d" height="%d"/>' % (x, by, bw, bh))
        s.append('<text class="zone-idx" x="%.1f" y="%d" text-anchor="middle">%s</text>'
                 % (x + bw / 2.0, by - 16, romans[i - 1]))
        s.append('<text class="zone-name" x="%.1f" y="%d" text-anchor="middle">战区</text>'
                 % (x + bw / 2.0, by - 2))
        s.append('</g>')
    s.append('<g id="demo-token" transform="translate(0,0)">'
             '<circle r="12" fill="rgba(223,230,240,.14)" stroke="rgba(223,230,240,.85)" stroke-width="1"/>'
             '<circle r="4.5" fill="#dfe6f0"/>'
             '<path d="M-7,28 L0,21 L7,28" fill="none" stroke="rgba(223,230,240,.55)" stroke-width="1"/></g>')
    s.append('<text class="zone-name" x="%d" y="%d" text-anchor="middle">示意图 · 若干战区，两端各一座信仰</text>' % (W / 2, H - 14))
    s.append("</svg>")
    return "".join(s)


def build_index():
    S = M.SITE
    title_spans = "".join('<span style="animation-delay:%.2fs">%s</span>' % (0.1 * i, ch)
                          for i, ch in enumerate(S["title"]))
    hero = (
        '<div class="hero"><div class="hero-bg"><img src="assets/img/banner.svg" alt="长歌主视觉"></div>'
        '<div class="hero-veil"></div><div class="hero-inner"><div>'
        '<div class="hero-kicker"><span class="lat">' + esc(S["kicker"]) + '</span></div>'
        '<h1 class="hero-title">' + title_spans + '</h1>'
        '<p class="hero-latin">' + esc(S["latin"]) + '</p>'
        '<p class="hero-tag">' + esc(S["tagline"]) + '</p>'
        '<div class="hero-meta">' +
        "".join('<div><b>' + esc(n) + '</b><span>' + esc(l) + '</span></div>' for n, l in M.STATS) +
        '</div></div><div class="hero-side"><div class="hero-seal">' + esc(S["epigraph"]) + '</div>'
        '<span class="lat">' + esc(S["edition"]) + ' / ' + esc(S["date"]) + '</span>'
        '</div></div><div class="scroll-hint">SCROLL</div></div>'
    )

    # 序
    preface = (
        '<div class="preface"><div class="preface-body">' +
        "".join("<p>" + esc(p) + "</p>" for p in M.PREFACE) + '</div>'
        '<div><div class="pull">' + esc(S["epigraph"]) + '<br><span class="tiny dim">' + esc(S["epigraph_src"]) + '</span></div>'
        '<ul class="legend" style="margin-top:28px">' +
        "".join('<li><span class="tag ' + ('draft' if k == '草案' else 'guess' if k == '推想' else '') + '">' + k + '</span><span>' + esc(v) + '</span></li>'
                for k, v in M.LEGEND) +
        '</ul><div class="srcs">' +
        "".join('<div><b>' + esc(a) + '</b><span>' + esc(b) + ' · ' + esc(c) + '</span></div>' for a, b, c in M.SOURCES) +
        '</div></div></div>'
    )

    # 世界观
    world = ('<div class="flow">' + "".join(
        ('<div class="flow-item reveal' + (' blank' if w["k"] == '留白' else '') + '" data-d="%d">'
         '<div class="flow-k">' + esc(w["k"]) + '</div>'
         '<div class="flow-sub">' + esc(w["sub"]) + '</div>'
         '<p>' + esc(w["text"]) + '</p>'
         '<div class="flow-note">' + esc(w["note"]) + '</div></div>') % (i % 5 + 1)
        for i, w in enumerate(M.WORLD)) + '</div>')

    # 战场
    board = (
        '<div class="board-wrap"><div><div class="board" id="board">' + board_svg() + '</div>'
        '<div class="board-legend"><span><i class="lg-atk"></i>可攻击</span>'
        '<span><i class="lg-self"></i>单位所在</span><span><i class="lg-none"></i>无法触及</span></div>'
        '<p class="tiny dim" style="margin:12px 0 0">' + esc(R.BOARD_NOTE) + '</p></div>'
        '<div class="board-side"><div class="range-btns">' +
        "".join('<button class="rb" data-unit="%s" aria-pressed="%s">%s</button>' % (u, "true" if u == "knight" else "false", n)
                for u, n in (("knight", "战士·骑士"), ("ranger", "战士·游侠"), ("guard", "战士·近卫"),
                             ("mage", "法师"), ("archer", "弓箭手"))) +
        '</div><div class="range-out"><h4 id="rangeName">战士 · 骑士 · 位于 Ⅲ 区</h4>'
        '<div class="kv"><span>可攻击</span><b id="rangeAtk">Ⅱ、Ⅳ</b></div>'
        '<div class="kv"><span>可防御</span><b id="rangeDef">自身与相邻战区</b></div>'
        '<p id="rangeExtra" class="tiny" style="margin-top:12px"></p></div>'
        '<p class="tiny dim">点选单位类型，再点任一战区委身其中——高亮会告诉你它够得到哪里。'
        '这是归档者按原典规则做的射程演示，不是游戏实现。</p></div></div>'
    )

    # 玩法
    play = ('<div class="plays">' + "".join(
        '<div class="play reveal" data-d="%d"><div class="play-n">%s</div><h3>%s</h3><p>%s</p><ul>%s</ul></div>'
        % (i % 5 + 1, esc(p["n"]), esc(p["k"]), esc(p["p"]),
           "".join("<li>" + esc(b) + "</li>" for b in p["bullets"]))
        for i, p in enumerate(M.PLAY)) + '</div>')

    # 魔力
    mana = ('<div class="mana reveal"><div><div class="mana-bars">' +
            "".join('<div class="mbar" data-t="%d"><span>%d</span></div>' % (i, i) for i in range(1, 14)) +
            '</div></div><div class="mana-ctl"><div class="mana-read"><b id="manaCap">1</b><span>上限</span></div>'
            '<input id="manaInput" type="range" min="1" max="24" value="1" step="1" aria-label="魔力上限">'
            '<p class="small" id="manaTurn">第 1 回合 · 自然增长中</p>'
            '<p class="tiny dim" id="manaNote"></p>'
            '<p class="tiny dim">拖动滑块，看一副牌最多能跑多少回合：12 是自然增长的天花板，24 是硬上限。</p>'
            '</div></div>')

    terms = ('<div class="terms">' + "".join(
        '<button class="term" data-tip="' + esc(t["t"]) + '">' + esc(t["n"]) + '</button>'
        for t in M.TERMS) + '</div>')

    # 阵营
    facs = ('<div class="facs">' + "".join(
        '<div class="fac reveal" data-d="%d" style="--fc:%s"><div class="fac-sigil"><img src="assets/img/sigil-%s.svg" alt="%s徽记"></div>'
        '<h3>%s</h3><p class="fac-motto">%s</p><div style="text-align:center;position:relative;margin-bottom:14px">'
        '<span class="tag %s">%s</span></div><p>%s</p>'
        '<div class="fac-roster">%s</div></div>'
        % (i % 5 + 1,
           "rgba(169,200,239,.20)" if f["id"] == "新的勇者" else "rgba(240,196,138,.20)" if f["id"] == "同盟军" else "rgba(227,166,198,.18)",
           FAC_SLUG[f["id"]], esc(f["id"]), esc(f["id"]), esc(f["motto"]),
           "draft" if f["tag"] == "草案" else "wip", esc(f["tag"]), esc(f["desc"]),
           "".join('<span class="dim small">' + esc(r) + '</span>' for r in f["roster"])
           if f["roster"] else '<span class="fac-empty">尚未公开</span>')
        for i, f in enumerate(M.FACTIONS)) + '</div>')

    # 特色卡
    feat_cards = []
    for f in M.FEATURED:
        c = next((x for x in CARD_LIST if x["name"] == f["name"]), None)
        if c:
            feat_cards.append((c, f))
    feat = ('<div class="feat">' + "".join(face(c, "", cls="reveal", text=short_text(c, 52)) for c, _ in feat_cards) + '</div>'
            '<div class="feat-note">' + "".join(
                '<div><b>' + esc(f["name"]) + '</b><span class="dim">' + esc(f["tag"]) + '</span><br>' + esc(f["why"]) + '</div>'
                for _, f in feat_cards) + '</div>')

    # 星图（簇）
    nodes = []
    for cl in M.CLUSTERS:
        n = len(cards_of_cluster(cl["id"]))
        nodes.append(dict(id=cl["id"], label=cl["name"], size=4 + math.sqrt(max(n, 1)) * 1.6,
                          color=M.FACTION_COLOR.get(cl["fac"], "#c8a86a"),
                          href="cards/" + cards_of_cluster(cl["id"])[0]["id"] + ".html" if n else ""))
    edges, seen = [], set()
    for c in CARD_LIST:
        for l in valid_links(c):
            a, b = c["cluster"], BY[l[0]]["cluster"]
            if a == b:
                continue
            k = tuple(sorted([a, b]))
            if k in seen:
                continue
            seen.add(k)
            edges.append(k)
    const = ('<div class="const-wrap"><div class="const reveal">' + star_map(nodes, edges, 880, 560) + '</div>'
             '<div><h3 style="font-size:1.2rem;letter-spacing:.18em;color:#efe9dc;margin-bottom:14px">十二个编组，八种接线</h3>'
             '<p class="small muted">每个点是一个卡簇（编组），线是它们之间的语义关系：谁生成谁、谁检索谁、谁因谁而变强。'
             '把鼠标停在点上，只留下与它相关的线。</p>'
             '<ul class="rels" style="margin-top:18px">' +
             "".join('<li><span class="rel-k k-%s">%s</span><div><p style="margin:0">%s</p></div></li>'
                     % (k, k, esc(v)) for k, v in M.REL_KINDS) +
             '</ul><p class="tiny dim" style="margin-top:16px">关系表由归档者从卡牌文本中整理；'
             '原典并未逐条声明这些连线，它们是「读出来的结构」。</p></div></div>')

    # 英雄索引
    heroes = ('<div class="grid-cards wide">' + "".join(
        '<a class="side-card reveal" href="heroes/' + h["id"] + '.html" style="display:grid;gap:6px">'
        '<div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px">'
        '<b style="font-size:1.1rem;font-weight:500;color:#efe9dc;letter-spacing:.1em">' + esc(h["name"]) + '</b>'
        '<span class="tiny dim">' + esc(h["fac"]) + '</span></div>'
        '<div class="tiny" style="color:var(--gold-2);letter-spacing:.1em">' + esc(h["sub"]) + '</div>'
        '<div class="tiny dim">' + esc(h["panel"]) + ' · ' + esc(h["type"]) + '</div>'
        '<div class="tiny" style="color:var(--text-2)">' + esc(h["line"]) + '</div></a>'
        for h in M.HEROES) + '</div>')

    # 归档索引
    idx = ('<div class="idx">' + "".join(
        '<a href="' + esc(href) + '"><span class="n">' + esc(tag) + '</span><h3>' + esc(t) + '</h3>'
        '<p>' + esc(d) + '</p><span class="arrow">→</span></a>'
        for href, t, d, tag in M.ARCHIVE_INDEX) + '</div>')

    body = (
        head(S["title"] + " · 企划归档", S["tagline"]) + nav("", False, "index.html") + hero +
        sec("preface", "00 / PREFACE", "序", "BEFORE THE MOON RISES",
            "为什么会有这一页，以及它凭什么可信。", preface) +
        sec("world", "01 / WORLD", "世界观", "SUBSTANCE · MANA · MAGIC",
            "原典写了四条概念、三条定律。魔力学先立住，世界才谈得上运转。", world) +
        sec("board", "02 / BATTLEFIELD", "战场", "THE BATTLEFIELD",
            "若干条被切成数段战区的线串在一起，两端各立着一座信仰。所有的伤害，最终都要穿过这些线。", board) +
        sec("play", "03 / HOW TO PLAY", "玩法", "THE RULES AS WRITTEN",
            "下面六段是规则原文的重排，每一段都能在原典里找到出处。", play +
            '<div class="hair"></div>' + mana +
            '<div class="hair"></div><div class="sec-head" style="margin-bottom:22px"><div class="sec-no">TERMS</div>'
            '<div><h3 style="font-size:1.2rem;letter-spacing:.16em;color:#efe9dc">词条与操作</h3>'
            '<p class="tiny dim" style="margin:6px 0 0">点一下看释义。悬停也行。</p></div></div>' + terms) +
        sec("factions", "04 / FACTIONS", "阵营", "THREE BANNERS, ONE ROAD",
            "三大阵营选其一。三面旗都立起来了，只是一面还只有一张牌。", facs +
            '<div class="hair"></div><div class="sec-head" id="heroes" style="margin-bottom:22px;scroll-margin-top:90px">'
            '<div class="sec-no">HEROES</div><div><h3 style="font-size:1.2rem;letter-spacing:.16em;color:#efe9dc">八位英雄</h3>'
            '<p class="tiny dim" style="margin:6px 0 0">英雄不是卡。他们的「天赋」才是——一套卡组只带一张天赋。</p></div></div>' + heroes) +
        sec("featured", "05 / SELECTED", "特色卡牌", "SIX CARDS WORTH READING",
            "挑六张：一张检索、一张觉醒、一张终局、一张御风、一张唯一、一张标题。", feat) +
        sec("constellation", "06 / CONSTELLATION", "关系星图", "TWELVE CLUSTERS",
            "卡不是孤岛。它们彼此生成、转化、检索、依赖。", const) +
        sec("index", "07 / ARCHIVE", "归档目录", "WHERE TO GO NEXT",
            "", idx) +
        foot()
    )
    write(ROOT / "index.html", body)


# ══════════════════════════════ 图鉴 ══════════════════════════════

def build_archive():
    fac_chips = ['<button class="fchip" data-val="" aria-pressed="true">全部</button>']
    for f in ("新的勇者", "同盟军", "魔王军", "通用"):
        fac_chips.append('<button class="fchip" data-val="' + f + '" aria-pressed="false">' + f + '</button>')
    q_chips = ['<button class="fchip" data-val="" aria-pressed="true">全部</button>']
    for q in ("N", "R", "E", "L", "域外"):
        q_chips.append('<button class="fchip" data-val="' + q + '" aria-pressed="false">' + qname(q) + '</button>')
    cat_chips = ['<button class="fchip" data-val="" aria-pressed="true">全部</button>']
    for k in ("魔法", "单位", "天赋", "觉醒"):
        cat_chips.append('<button class="fchip" data-val="' + k + '" aria-pressed="false">' + k + '</button>')

    filters = (
        '<div class="filters"><div class="frow"><b>阵营</b><div class="fchips" data-group="fac">' + "".join(fac_chips) + '</div></div>'
        '<div class="frow"><b>品质</b><div class="fchips" data-group="q">' + "".join(q_chips) + '</div></div>'
        '<div class="frow"><b>类别</b><div class="fchips" data-group="cat">' + "".join(cat_chips) + '</div></div>'
        '<div class="frow"><b>搜索</b><input class="search" id="q" type="search" placeholder="名字、文本、词条……" autocomplete="off"></div>'
        '<div class="fstat"><span id="fcount">' + str(len(CARD_LIST)) + ' 张</span><span>选阵营时同时显示「通用」</span></div></div>'
    )

    blocks = []
    for cl in M.CLUSTERS:
        cs = cards_of_cluster(cl["id"])
        if not cs:
            continue
        items = []
        for c in cs:
            search = (c["name"] + " " + c["text"] + " " + " ".join(c.get("tags") or [])).lower()
            items.append('<div class="card-item" data-fac="' + esc(c["fac"]) + '" data-q="' + c["q"] +
                         '" data-cat="' + esc(c["cat"]) + '" data-search="' + esc(search) + '">' +
                         face(c) + '</div>')
        blocks.append(
            '<section class="cluster-block"><div class="cluster-head"><h3>' + esc(cl["name"]) + '</h3>'
            '<span class="lat">' + esc(cl["tag"]) + '</span><span class="cnt">' + str(len(cs)) + ' / ' + str(len(cs)) + '</span></div>'
            '<p class="tiny dim" style="margin:-8px 0 20px;max-width:70ch">' + esc(cl["summary"]) + '</p>'
            '<div class="grid-cards">' + "".join(items) + '</div></section>')

    body = (
        head("卡牌图鉴", str(len(CARD_LIST)) + " 张卡牌，按编组排列，可即时筛选。", "") +
        nav("", True, "archive.html") +
        '<section class="sec" style="padding-top:clamp(90px,14vh,150px)"><div class="wrap">'
        '<div class="sec-head reveal" style="margin-bottom:26px"><div class="sec-no">ARCHIVE / CARDS</div><div>'
        '<h1 class="sec-title" style="font-size:clamp(2rem,4vw,3rem)">卡牌图鉴<small>' + qty(len(CARD_LIST)) + ' ENTRIES</small></h1>'
        '<p class="sec-lead">全部 ' + str(len(CARD_LIST)) + ' 张，按' + cn_num(len(M.CLUSTERS)) + '个编组排列。筛选是即时的：阵营、品质、类别可以叠加，'
        '搜索框认名字、认文本、也认词条。</p></div></div>' + filters +
        '<div id="archive" style="margin-top:42px">' + "".join(blocks) +
        '<div class="empty hidden" id="fempty">没有符合条件的卡牌。<br><span class="tiny">试着放宽一个条件。</span></div>'
        '</div></div></section>' + foot("", '<script src="assets/js/archive.js"></script>')
    )
    write(ROOT / "archive.html", body)


# ══════════════════════════════ 沙盘 ══════════════════════════════

def build_sandbox():
    fac_chips = ['<button class="fchip" data-val="" aria-pressed="true">全部</button>']
    for f in ("新的勇者", "同盟军", "魔王军", "通用"):
        fac_chips.append('<button class="fchip" data-val="' + f + '" aria-pressed="false">' + f + '</button>')
    q_chips = ['<button class="fchip" data-val="" aria-pressed="true">全部</button>']
    for q in ("N", "R", "E", "L", "域外"):
        q_chips.append('<button class="fchip" data-val="' + q + '" aria-pressed="false">' + qname(q) + '</button>')

    side = (
        '<aside class="sb-side">'
        '<div class="sb-panel"><h4>卡组</h4><div class="sb-count"><b id="deckCount">0</b><span>/ 40 张</span></div>'
        '<div class="sb-track" id="deckTrack"><i></i></div>'
        '<div class="curve" id="curve"></div>'
        '<ul class="sb-issues" id="issues"></ul>'
        '<div class="sb-actions"><button class="btn" id="clearDeck" type="button">清空</button>'
        '<button class="btn solid" id="copyDeck" type="button">复制牌表</button></div></div>'
        '<div class="sb-panel"><h4>已选</h4><div class="sb-list" id="deckList">'
        '<p class="tiny dim">尚未选择任何卡牌。</p></div></div>'
        '<div class="sb-panel"><h4>校验</h4><p class="tiny dim" id="facState">阵营：未选定</p>'
        '<p class="tiny dim" style="margin-top:8px">40 张一组 · 只可含所选阵营与通用 · 同一英雄的天赋只能带一张 · '
        '单卡不超过其收藏上限 · 【域外】与【觉醒】不可加入。</p>'
        '<p class="tiny dim" style="margin-top:6px">「上限」只约束构筑与战斗外的获得；对局中被生成出来的牌不受它约束。</p></div>'
        '</aside>')

    body = (
        head("构筑沙盘", "按原典规则试组一副 40 张的卡组，实时校验阵营、天赋与费用曲线。", "") +
        nav("", True, "sandbox.html") +
        '<section class="sec" style="padding-top:clamp(90px,14vh,150px)"><div class="wrap">'
        '<div class="sec-head reveal" style="margin-bottom:26px"><div class="sec-no">SANDBOX / DECK</div><div>'
        '<h1 class="sec-title" style="font-size:clamp(2rem,4vw,3rem)">构筑沙盘<small>FORTY CARDS, ONE DECK</small></h1>'
        '<p class="sec-lead">点卡面加入，点已选移除。右侧实时算数量、费用曲线与规则冲突：'
        '跨阵营、天赋重复、超上限都会被拦下。牌表存进浏览器本地，关掉再开还在。</p></div></div>'
        '<div class="sb" id="sandbox"><div><div class="filters" style="position:static">'
        '<div class="frow"><b>阵营</b><div class="fchips" data-group="fac">' + "".join(fac_chips) + '</div></div>'
        '<div class="frow"><b>品质</b><div class="fchips" data-group="q">' + "".join(q_chips) + '</div></div>'
        '<div class="frow"><b>搜索</b><input class="search" id="sbq" type="search" placeholder="名字、文本、词条……" autocomplete="off"></div>'
        '</div><div class="grid-cards" id="pool" style="margin-top:22px"></div></div>' + side + '</div>'
        '</div></section>' + foot("",
            '<script src="assets/data/cards.js"></script><script src="assets/js/sandbox.js"></script>')
    )
    write(ROOT / "sandbox.html", body)


# ══════════════════════════════ 规则手册 ══════════════════════════════

def build_rulebook():
    def rows(items):
        return '<ul class="rb-list">' + "".join(
            '<li><b>' + esc(k) + '</b><div><p>' + rich(v) + '</p></div></li>' for k, v in items) + '</ul>'

    unit_rows = [(u, t + "　" + sub) for (u, t, sub) in R.UNIT_TYPES]
    words = [t for t in M.TERMS if t["g"] == "词条"]
    acts = [t for t in M.TERMS if t["g"] == "操作"]

    secs = [
        ("overview", "00", "总览", "OVERVIEW",
         "《长歌》的游戏部分由两半构成：文字冒险与卡牌对战。文字冒险交给另一个项目 GodotADV；"
         "这里是卡牌对战的部分——一套以西幻战场为骨、以魔力为血的两人对局。原典的构想是对战（PVP）与剧情（PVE）并行。",
         rows([("定位", "与小说《长歌》平行且一致的独立游戏。"),
               ("结构", "文字冒险（GodotADV）+ 卡牌对战。"),
               ("规模", "双方各一副 40 张的卡组；战场由若干战区构成，排布取决于随机到的地图。"),
               ("胜负", "摧毁敌方信仰。没有第二种胜利条件。")])),
        ("cards", "01", "卡牌与卡组", "CARDS & DECK",
         "一张卡有阵营、类别、品质与费用；一副卡组有且只有一个阵营。",
         rows([("卡组", "40 张，从「同盟军」「魔王军」「新的勇者」中选一个阵营；"
                       "卡组只能包含所选阵营的卡与「通用」卡。"),
               ("类别", "魔法 / 单位 / 天赋 / 觉醒。天赋与觉醒牌本身也是卡，详见「英雄」一节。"),
               ("品质", "普通（N）、稀有（R）、史诗（E）、传说（L），以及不可收藏的【域外】。"),
               ("域外", "无法在收藏中获得，只能由其他卡牌生成——它们是牌与牌之间的接线。"),
               ("上限", "卡面写的「上限」只约束构筑携带数与战斗外的获得；战斗中（包括生成）不受它约束。"),
               ("费用", "卡面左上为魔力花费；单位面板写作「行动花费/攻击/防御」，如 1C/150A/300D。")])),
        ("hand", "02", "手牌与调度", "HAND & MULLIGAN",
         "先手少一张，后手多一张；开局可以换牌，手牌有上限。",
         rows([("起手", "先手抽 4 张，后手抽 5 张。"),
               ("调度", "开局进入调度阶段，可将手牌放回卡组并换取等量的新牌。"),
               ("抽牌", "除先手的第一回合外，己方回合开始时抽 1 张。"),
               ("上限", "手牌上限 9 张；超出时新抽的牌放回卡组底部。")])),
        ("mana", "03", "魔力", "MANA",
         "每回合涨一点，涨到 12 就停——除非有卡替你继续推。",
         rows([("增长", "每个己方回合开始时，魔力上限 +1，并回复至上限。"),
               ("自然上限", "上限不小于 12 时不再自然增长。"),
               ("硬上限", "上限最高 24；12 以上的每一格，都只能靠卡牌效果加上去。"),
               ("获得", "以任何方式获得的魔力都可以超过当前上限；0 费的牌可以免费打出。"),
               ("花费", "出牌、单位的入场与行动，都从此池中支付。")])),
        ("actions", "04", "行动", "ACTIONS",
         "一个单位一回合通常只能行动一次：打、挡、走，三选一。",
         rows([("攻击", "对目标造成等同于攻击力的伤害，同时受到目标攻击力的反击伤害。反击算「一次伤害」。"),
               ("防御", "指向己方目标，触发其防御效果；该防御在下个己方回合开始时解除。"
                       "被防御的目标每受到一次攻击，解除一层防御。"),
               ("移动", "移动到相邻的、未被占领或己方占领的战区。"),
               ("次数", "每个单位一般每回合行动一次，并支付其行动花费；"
                       "【奋战 X】【疾行 X】【护卫 X】分别增加攻击、移动、防御的次数。"),
               ("敌我", "未写敌我的「一个单位／一个目标」既可以指敌方，也可以指己方。")])),
        ("units", "05", "单位类型", "UNIT TYPES",
         "三类单位，六个子类。每一条子类规则都在改写上面那三条行动。",
         rows(unit_rows)),
        ("faith", "06", "信仰", "FAITH",
         "末端战区里的那个东西。它不还手，但它的 1000 点防御决定了一切。",
         rows([("位置", "双方各自的末端战区。末端战区必定存在，且不能被对方占领。"),
               ("面板", "防御 1000，无法行动，也没有反击面板。"),
               ("意义", "摧毁敌方信仰即获胜——所以所有战术最终都指向那 1000 点。")])),
        ("magic", "07", "魔法与专属魔法", "MAGIC",
         "魔法牌是消耗品；专属魔法是英雄的延长线。",
         rows([("使用", "支付费用，结算牌面效果。"),
               ("专属魔法", "构筑时携带了对应英雄（的合成牌）即可携带，与英雄是否在场无关；"
                         "【限定】只限制「使用」，不限制「持有」。"),
               ("触发", "可在手牌中激活，在下个敌方回合满足条件时自动发动——唯一一种「提前埋下」的牌。"),
               ("多英雄", "一副卡组可以携带多位不同的英雄。")])),
        ("hero", "08", "英雄与天赋", "HEROES & TALENTS",
         "英雄与对应的天赋，在构筑界面里合成为一张牌。",
         rows([("合成", "「英雄 + 对应天赋」在构筑界面里合成一张牌。英雄本身无需获取；天赋在获取过程中每张算一张牌，"
                       "没有「上限」字段，花费与面板都由所选天赋决定。"),
               ("抽取", "「抽取英雄」抽的就是这张合成牌——它可以存在于卡组与手牌里。"),
               ("返场", "英雄被消灭时，在下个敌方回合结束时洗入卡组；觉醒的英雄返场后仍是觉醒状态。"),
               ("专属魔法", "卡组携带该英雄后才可携带，通常带【限定】。")])),
        ("terms", "09", "词条", "KEYWORDS",
         "十二条词条。它们不是修辞，是规则。",
         rows([(t["n"], t["t"]) for t in words])),
        ("ops", "10", "卡牌操作", "CARD OPERATIONS",
         "六种被反复使用的动作，原典把它们单列成一节。",
         rows([(t["n"], t["t"]) for t in acts])),
        ("verbs", "11", "动词表", "VERBS",
         "牌面上出现「加入／洗入／抽取／转化／返回／开发」时，它们各自指一件不同的事。这一节是后加的，"
         "依据是作者对动词体系的裁定。",
         rows([(n, m + "　" + d) for (n, m, d) in R.VERBS]) +
         "".join('<p class="rb-note"><b>' + esc(k) + '</b>　' + esc(v) + '</p>' for k, v in R.VERB_NOTES)),
        ("rulings", "12", "作者裁定", "RULINGS",
         "原典没有写死、由作者裁定补齐的部分。它们从这里开始就是规则，不再是推想。",
         "".join('<h4 class="rb-sub">' + esc(g) + '</h4>' + rows(items) for g, items in R.RULINGS)),
        ("opens", "13", "待确认与留白", "OPEN QUESTIONS",
         "还没定下来的地方。归档照录，不代为补完。",
         rows([(k, v) for k, v in R.OPENS])),
    ]

    toc = "".join('<a href="#rb-%s">%s %s</a>' % (k, n, c) for k, n, c, e, lead, body in secs) + '<a href="#rb-notes">14 归档注</a>'
    blocks = []
    for k, n, c, e, lead, body in secs:
        blocks.append('<section class="rb-sec" id="rb-%s"><h3>%s %s<em>%s</em></h3>'
                      '<p class="lead">%s</p>%s</section>' % (k, n, esc(c), e, esc(lead), body))

    notes = (
        '<div class="rb-sec" id="rb-notes"><h3>14 归档注<em>EDITOR\'S NOTES</em></h3>'
        '<p class="lead">原典经过两轮修订。改动分两类：一类是错字，一类是卡面文字（规则）变更，后者不是错字。</p>'
        '<div class="orig"><em>错字 · 行动 · 攻击</em>「…同时收到目标攻击力的反击伤害。」</div>'
        '<p class="rb-note">「收到」改为「受到」。原典文件已同步改正。</p>'
        '<div class="orig"><em>错字 · 卡牌操作 · 转换</em>「…则会接触施加于其上的所有防御，中止自身的蓄能。」</div>'
        '<p class="rb-note">「接触」改为「解除」。原典文件已同步改正。</p>' +
        "".join('<div class="hair"></div><h4 class="rb-sub">' + esc(k) + '</h4><p class="rb-note">' + esc(v) + '</p>'
                for k, v in R.CARD_TEXT_CHANGES) +
        '<div class="hair"></div><p class="tiny dim">世界观一章的四条概念、三条定律与三代魔法史见「世界观」页；'
        '本页的「结构重排」均为归档者的排版，语义以原典为准。</p></div>'
    )

    body = (
        head("规则手册", "《长歌》卡牌对战规则的结构化重排，含归档注。", "") +
        nav("", True, "rulebook.html") +
        '<section class="sec" style="padding-top:clamp(90px,14vh,150px)"><div class="wrap">'
        '<div class="sec-head reveal" style="margin-bottom:34px"><div class="sec-no">RULEBOOK / AS WRITTEN</div><div>'
        '<h1 class="sec-title" style="font-size:clamp(2rem,4vw,3rem)">规则手册<small>THE RULES, REARRANGED</small></h1>'
        '<p class="sec-lead">原典是一份 101 行的企划说明。这里把它拆成十四节：前十节逐条重排，不改语义；'
        '后四节是动词表、作者裁定、待确认项与归档注。</p></div></div>'
        '<div class="split"><div>' + "".join(blocks) + notes + '</div>'
        '<nav class="rb-toc">' + toc + '</nav></div></div></section>' + foot("")
    )
    write(ROOT / "rulebook.html", body)


# ══════════════════════════════ 英雄页 ══════════════════════════════

def build_hero(h):
    hid = h["id"]
    cl = next((c for c in M.CLUSTERS if c["id"] == hid), None)
    talents = [BY[i] for i in talent_ids(hid)]
    allc = cards_of_hero(hid) or (cards_of_cluster(hid) if cl else [])
    main = [c for c in allc if c["cat"] != "天赋"]

    hd = ('<div class="hero-head"><div class="bg"><img src="../assets/img/heroes/' + hid + '.svg" alt=""></div>'
          '<div class="wrap inner"><div><div class="hero-idx">HERO / ' + hid.upper() + ' · ' + esc(h["fac"]) + '</div>'
          '<h1 class="hero-name">' + esc(h["name"]) + '</h1>'
          '<div class="hero-sub">' + esc(h["sub"]) + '</div></div>'
          '<div class="hero-panel">'
          '<div><b>阵营</b><span>' + esc(h["fac"]) + '</span></div>'
          '<div><b>类型</b><span>' + esc(h["type"]) + '</span></div>'
          '<div><b>面板</b><span>' + esc(h["panel"]) + '</span></div>'
          '<div><b>天赋</b><span>' + (str(len(talents)) + " 张") + '</span></div>'
          '<div><b>关键词</b><span>' + esc(" / ".join(h["kw"])) + '</span></div>'
          '</div></div></div>')

    tal_html = (grid(talents, "../") if talents else
                '<p class="small dim">原典中这位英雄还没有天赋卡。面板与防御行为因此未定——'
                '<span class="tag wip">施工中</span></p>')

    design = ('<div class="split"><div class="prose"><p>' + esc(h["profile"]) + '</p>'
              '<p>' + esc(h["design"]) + '</p>'
              '<p class="pull" style="margin-top:26px">' + esc(h["line"]) + '</p></div>'
              '<div class="side-card"><h4>速览</h4><p class="tiny dim" style="margin:-6px 0 10px">关键词为归档者归纳，不全是原典词条。</p><div class="kwlist">' +
              "".join('<span class="kw">' + esc(k) + '</span>' for k in h["kw"]) + '</div>'
              '<div class="hair"></div><p class="tiny dim">' + esc(h["fac"]) + ' · ' + esc(h["type"]) + '</p>'
              '<p class="tiny dim">' + esc(h["panel"]) + '</p>'
              '<a class="btn" style="display:inline-block;margin-top:6px" href="../archive.html">在卡牌图鉴中查看</a>'
              '</div></div>')

    nodes = []
    cmap = M.FACTION_COLOR.get(h["fac"], "#c8a86a")
    for c in allc:
        nodes.append(dict(id=c["id"], label=c["name"], size=5.4, color=cmap,
                          href="../cards/" + c["id"] + ".html"))
    idset = {c["id"] for c in allc}
    edges = []
    for c in allc:
        for l in valid_links(c):
            if l[0] in idset:
                edges.append((c["id"], l[0]))
    star = ('<div class="const-wrap"><div class="const reveal">' + star_map(nodes, edges, 900, 600) + '</div>'
            '<div><h3 style="font-size:1.2rem;letter-spacing:.18em;color:#efe9dc;margin-bottom:12px">编组内部的关系</h3>'
            '<p class="small muted">这张星图只画与' + esc(h["name"]) + '相关的 ' + str(len(allc)) + ' 张卡。'
            '悬停任一节点，与它相连的线会亮起；点进去就是单卡页。</p>'
            '<p class="tiny dim" style="margin-top:14px">连线取自卡牌文本中的明确指涉（生成、转化、检索、条件、同源、联动）。'
            '没有连线的卡不代表无关，只代表它们的关系还没被写进文本里。</p>'
            '<a class="btn" style="display:inline-block;margin-top:10px" href="../archive.html">打开完整图鉴</a></div></div>')

    body = (
        head(h["name"] + " · 英雄档案", h["line"], "../") + nav("../", True, "heroes/" + hid + ".html") + hd +
        sec("profile", "01 / PORTRAIT", "侧写", "THE ONE WHO CARRIES IT", "", design) +
        sec("talents", "02 / TALENTS", "天赋", "EACH TALENT IS A CARD",
            "一个英雄有多张天赋，一套卡组只带一张——所以下面的玩法，其实是「选哪一张」。", tal_html) +
        sec("cards", "03 / CARDS", "编组卡牌", "THE DECK AROUND THE HERO",
            ("共 " + str(len(allc)) + " 张，其中天赋 " + str(len(talents)) + " 张。") if allc else "",
            grid([c for c in allc if c["cat"] != "天赋"], "../") if main else '<p class="small dim">尚无其他卡牌。</p>') +
        sec("constellation", "04 / CONSTELLATION", "关系星图", "INSIDE THE CLUSTER", "", star) +
        foot("../")
    )
    write(HEROES_DIR / (hid + ".html"), body)


# ══════════════════════════════ 单卡页 ══════════════════════════════

def build_card(c):
    cid = c["id"]
    cl = CL_BY.get(c["cluster"], {})
    hero = HERO_BY.get(c.get("hero") or "")

    crumb = ('<div class="breadcrumb"><a href="../index.html">长歌</a><span>/</span>'
             '<a href="../archive.html">卡牌图鉴</a><span>/</span>'
             '<a href="../archive.html">' + esc(c["fac"]) + '</a><span>/</span>' + esc(c["name"]) + '</div>')

    meta_pills = ['<span class="pill">' + esc(c["fac"]) + '</span>']
    if c["cat"] != "觉醒":
        meta_pills.append('<span class="pill q" style="color:' + M.QUALITY_COLOR.get(c["q"], "#c8a86a") + '">' +
                          esc(qname(c["q"])) + " · " + esc(qlatin(c["q"])) + '</span>')
    meta_pills.append('<span class="pill">' + esc(c["cat"]) + '</span>')
    if c.get("utype"):
        meta_pills.append('<span class="pill">' + esc(c["utype"]) + '</span>')
    if c.get("stats") and c["stats"] not in ("-", "—"):
        meta_pills.append('<span class="pill mono">' + esc(c["stats"]) + '</span>')
    meta_pills.append('<span class="pill">费用 ' + esc(c.get("cost") or "—") + '</span>')

    belong = ['<div class="side-card"><h4>归属</h4><p class="small" style="margin:0 0 10px">' +
              esc(c["fac"]) + ' › ' + esc(cl.get("name", c["cluster"])) + '</p><p class="tiny dim" style="margin:0 0 12px">' +
              esc(cl.get("summary", "")) + '</p>']
    if hero:
        belong.append('<p class="small" style="margin:0 0 12px">英雄：<a href="../heroes/' + hero["id"] +
                      '.html" style="color:var(--gold-2);border-bottom:1px solid var(--line-2)">' +
                      esc(hero["name"]) + '</a>　<span class="tiny dim">' + esc(hero["sub"]) + '</span></p>')
    buildable = c["cat"] not in ("觉醒",) and c["q"] != "域外"
    lim_txt = ('收藏上限 ' + esc(c["lim"])) if (buildable and c.get("lim")) else "不可构筑"
    belong.append('<p class="tiny dim" style="margin:0">类别：' + esc(c["cat"]) +
                  '　·　' + lim_txt + '</p>')
    tags = c.get("tags") or []
    if tags:
        belong.append('<p class="tiny dim" style="margin:14px 0 6px">标签（归档者归纳，含规则词条）</p>'
                      '<div class="kwlist">' +
                      "".join('<span class="kw">' + esc(t) + '</span>' for t in tags) + '</div>')
    belong.append('</div>')

    # 关系
    out_links = valid_links(c)
    incoming = []
    for o in CARD_LIST:
        if o["id"] == cid:
            continue
        for l in valid_links(o):
            if l[0] == cid:
                incoming.append((o, l[1], l[2]))
    rel_rows = []
    for tgt, kind, note in out_links:
        t = BY[tgt]
        rel_rows.append('<li><span class="rel-k k-' + kind + '">' + kind + '</span><div>'
                        '<a href="../cards/' + tgt + '.html">' + esc(t["name"]) + '</a>'
                        '<p>' + esc(note) + '</p></div></li>')
    for src, kind, note in incoming:
        rel_rows.append('<li><span class="rel-k k-' + kind + '">被' + kind + '</span><div>'
                        '<a href="../cards/' + src["id"] + '.html">' + esc(src["name"]) + '</a>'
                        '<p>' + esc(note) + '</p></div></li>')
    rel_html = ('<ul class="rels">' + "".join(rel_rows) + '</ul>' if rel_rows else
                '<p class="small dim">原典没有为这张卡写明与其他卡的关系。它可能是一张孤牌，'
                '也可能只是关系还没被写下来。</p>')

    same = [x for x in cards_of_cluster(c["cluster"]) if x["id"] != cid][:6]

    # 词条栏：从卡面文本里抓【…】，逐条给出原典定义
    term_map = {t["n"].replace(" ", ""): t for t in M.TERMS}
    seen_kw, kw_rows = set(), []
    marks = re.findall(r"【([^】]+)】", c["text"]) + list(c.get("tags") or [])
    for raw in marks:
        key = raw.replace(" ", "")
        t = term_map.get(key) or term_map.get(re.sub(r"[0-9]+$", "X", key))
        if not t or t["n"] in seen_kw:
            continue
        seen_kw.add(t["n"])
        kw_rows.append('<div class="kwdef"><dt>' + esc(t["n"]) + '</dt><dd>' + esc(t["t"]) +
                       ('<span class="kn">' + esc(t["note"]) + '</span>' if t.get("note") else "") + '</dd></div>')
    kw_panel = ('<div class="side-card"><h4>词条</h4>' +
                ("".join(kw_rows) if kw_rows else
                 '<p class="tiny dim" style="margin:0">这张卡面上没有出现规则词条：它的文本只用到通用规则，没有额外词条。</p>') +
                '<p class="tiny dim" style="margin:12px 0 0">释义照录规则原文；标注「归档注」的是归档者补的说明。</p></div>')

    fish_paras = c["note"].split("\n") if isinstance(c["note"], str) else [c["note"]]

    _origins = [o for o in R.ORIGINS if cid in o.get("cards", [])]
    origin_html = ""
    if _origins:
        origin_html = ('<div class="origin"><h4>机制的来历 <span class="tag guess">推想</span></h4>' +
                       "".join('<p><b>' + esc(o["k"]) + '</b>　' + esc(o["t"]) + '</p>' for o in _origins) +
                       '<p class="tiny dim">这是归档者读牌时的对应关系，不是原典设定。</p></div>')


    body = (
        head(c["name"], short_text(c, 120), "../") + nav("../", True, "cards/" + cid + ".html") +
        '<section class="sec" style="padding-top:clamp(96px,13vh,150px)"><div class="wrap">' + crumb +
        '<div class="cardpage"><div class="cardstage">' + face(c, "../", href=False, lazy=False, text="") + '</div>'
        '<div><h1 class="card-title">' + esc(c["name"]) + '</h1>'
        '<div class="card-meta">' + "".join(meta_pills) + '</div>'
        '<div class="card-text">' + rich(c["text"]) + '</div>'
        '<div class="split" style="gap:clamp(24px,4vw,44px)"><div>'
        '<h3 style="font-size:1.05rem;letter-spacing:.18em;color:var(--gold-2);margin-bottom:14px">关联</h3>'
        + rel_html + '</div><div>' + "".join(belong) + kw_panel +
        '</div></div></div></div>'
        '<div class="fish"><div class="fish-h"><b>肥鱼碎碎念</b></div>' +
        "".join("<p>" + esc(p) + "</p>" for p in fish_paras) +
        '<p class="sig">——归档者，读这张卡的时候</p></div>' + origin_html +
        (('<div class="hair"></div><h3 style="font-size:1.05rem;letter-spacing:.18em;color:var(--gold-2);margin:0 0 18px">'
          '同编组的其他卡</h3>' + grid(same, "../")) if same else "") +
        '<div style="margin-top:40px"><a class="btn" href="../archive.html">← 回到卡牌图鉴</a></div>'
        '</div></section>' + foot("../")
    )
    write(CARDS_DIR / (cid + ".html"), body)


# ══════════════════════════════ 世界观 ══════════════════════════════

def _play(items, key_k="k", nkey=None, sub="sub", tag="tag", body_key="text", note_key="note"):
    out = ['<div class="plays">']
    for i, w in enumerate(items):
        n = w.get(nkey) if nkey else None
        out.append('<div class="play reveal" data-d="%d">' % (i % 5 + 1) +
                   ('<div class="play-n">' + esc(n) + '</div>' if n else "") +
                   '<h3>' + esc(w[key_k]) + '</h3>' +
                   ('<div class="flow-sub">' + esc(w[sub]) + '</div>' if w.get(sub) else "") +
                   '<p>' + esc(w[body_key]) + '</p>' +
                   ('<div class="flow-note">' + esc(w[note_key]) + '</div>' if w.get(note_key) else "") +
                   '</div>')
    out.append("</div>")
    return "".join(out)


def build_world():
    W = MW
    concepts = ('<div class="flow">' + "".join(
        '<div class="flow-item reveal" data-d="%d"><div class="flow-k">%s</div>'
        '<div class="flow-sub">%s</div><p>%s</p><div class="flow-note">%s</div></div>'
        % (i % 5 + 1, esc(c["k"]), esc(c["sub"]), esc(c["text"]), esc(c["note"]))
        for i, c in enumerate(W.CONCEPTS)) + '</div>')

    laws = ('<div class="plays">' + "".join(
        '<div class="play reveal" data-d="%d"><div class="play-n">%s</div><h3>%s</h3>'
        '<p>%s</p><div class="flow-note">%s</div></div>'
        % (i % 5 + 1, esc(l["n"]), esc(l["k"]), esc(l["text"]), esc(l["note"]))
        for i, l in enumerate(W.LAWS)) + '</div>'
        '<div class="pull" style="margin-top:34px">' + esc(W.MANA_NOTE["body"]) + '</div>')

    races = _play(W.RACES, body_key="desc", note_key="extra")
    orgs = _play(W.ORGS, body_key="desc", note_key="extra")
    mage = _play(W.MAGIC_HISTORY, body_key="desc", note_key="extra")

    hero = ('<div class="page-head"><div class="page-kicker">WORLD / MANA · RACES · FACTIONS</div>'
            '<h1 class="page-title">世界观</h1>'
            '<p class="page-lead">原典把世界拆成三层：魔力怎么运作，谁活在这块大陆上，以及谁替谁写历史。'
            '这一页只转录前两层——历史在下一页。</p></div>')

    body = (head("世界观", "魔力学、种族、组织与魔法史", "") + nav("", False, "world.html") + hero +
            sec("mana", "01", "魔力学", "MANA · FOUR CONCEPTS",
                "魔力、魔法、原质、魔器：四条概念各自独立，合起来才是一个可运算的世界。", concepts) +
            sec("laws", "02", "三大定律", "THREE LAWS",
                "傅泽提出「原质」，他的学生斯卡琳把它写成了三条定律。", laws) +
            sec("races", "03", "六个种族", "SIX PEOPLES",
                "长生种、短生种、魔物与魔种。种族的差别，多半写在寿命和魔法的用法上。", races) +
            sec("orgs", "04", "四大组织", "FOUR POWERS",
                "同盟、魔王军、学会、教会。前两个在打仗，后两个在解释这场仗。", orgs) +
            sec("magichist", "05", "三段魔法史", "THREE HISTORIES",
                "精灵族靠本能，神代靠信仰，现代靠理论。第三种是唯一能被教会的。", mage) +
            '<section class="sec"><div class="wrap"><div class="idx">' +
            "".join('<a class="idx-item" href="%s"><b>%s</b><span>%s</span></a>' % (u, esc(t), esc(d))
                    for u, t, d in (("story.html", "战争史", "五百年前那场仗，以及史书没写的那一半。"),
                                    ("cast.html", "人物", "新的勇者、七位大贤者、魔王军七位领袖。"))) +
            '</div></div></section>' + foot(""))
    write(ROOT / "world.html", body)


# ══════════════════════════════ 战争史 ══════════════════════════════

def build_story():
    W = MW
    paras = "".join("<p>" + esc(p) + "</p>" for p in W.STORY_PREFACE)
    after = "".join("<p>" + esc(p) + "</p>" for p in W.STORY_AFTER)

    tl = ('<ul class="tl">' + "".join(
        '<li class="reveal" data-d="%d"><div class="tl-t">%s</div><div><b>%s</b><p>%s</p></div></li>'
        % (i % 5 + 1, esc(t["t"]), esc(t["k"]), esc(t["d"]))
        for i, t in enumerate(W.TIMELINE)) + '</ul>'
        '<p class="rb-note" style="margin-top:22px">'
        '<b>〔归档者注 · 非史书〕</b>「如今」一条里的红月，不见于史书正文。'
        '它只出现在牌面与史书之外的那一节的写法里，这里按对照的读法记一句，不当作史实。</p>')

    origins = ('<div class="origins">' + "".join(
        '<div class="origin reveal" data-d="%d"><h4>%s<span class="tag guess">推想</span></h4>'
        '<p class="or-w">%s</p><p>%s</p><p class="or-c">%s</p></div>' %
        (i % 5 + 1, esc(o["k"]), esc(o["w"]), esc(o["t"]),
         "".join('<a href="cards/%s.html">%s</a>' % (cid, esc(BY[cid]["name"]))
                 for cid in o.get("cards", []) if cid in BY))
        for i, o in enumerate(R.ORIGINS)) + '</div>')

    aside = ('<div class="aside-box"><h4>' + esc(W.STORY_ASIDE["title"]) + '</h4><p>' +
             esc(W.STORY_ASIDE["body"]) + '</p></div>')

    hero = ('<div class="page-head"><div class="page-kicker">STORY / THE ALLIANCE WAR</div>'
            '<h1 class="page-title">战争史</h1>'
            '<p class="page-lead">五百年前，七个人结束了五十年的战争。史书到这里就写完了。'
            '这一页照录史书，也照录它没有写的那一句。</p></div>')

    body = (head("战争史", "同盟战争的编年与史书的空白", "") + nav("", False, "story.html") + hero +
            sec("preface", "01", "背景", "BEFORE THE MOON RISES", "", '<div class="prose">' + paras + '</div>') +
            sec("timeline", "02", "编年", "A TIMELINE", "七格，从诸族并立到预言之世。", tl) +
            sec("after", "03", "战后", "AFTER THE WAR", "", '<div class="prose">' + after + '</div>' + aside) +
            sec("origins", "04", "机制的来历", "WHERE THE MECHANICS COME FROM", R.ORIGINS_INTRO, origins) +
            '<section class="sec"><div class="wrap"><div class="idx">' +
            "".join('<a class="idx-item" href="%s"><b>%s</b><span>%s</span></a>' % (u, esc(t), esc(d))
                    for u, t, d in (("cast.html", "人物", "这七个人是谁，以及对面那七个人。"),
                                    ("world.html", "世界观", "魔力学、种族与组织。"))) +
            '</div></div></section>' + foot(""))
    write(ROOT / "story.html", body)


# ══════════════════════════════ 人物 ══════════════════════════════

def build_cast():
    W = MW
    blocks = []
    for gi, g in enumerate(W.CAST_GROUPS):
        rows = []
        for p in g["roster"]:
            who = esc(p["name"])
            if p.get("hero"):
                who = '<a href="heroes/' + p["hero"] + '.html">' + who + '</a>'
            badge = ('<span class="tag draft">有卡</span>' if p.get("card") and p.get("hero")
                     else '<span class="tag wip">无卡</span>')
            rows.append('<div class="cast-row"><div><div class="nm">' + who + '</div>'
                        '<div class="mt">' + esc(p["sex"]) + ' · ' + esc(p["race"]) + '</div></div>'
                        '<div class="jb">' + esc(p["job"]) + '</div><div class="bd">' + badge + '</div></div>')
        blocks.append(sec("g" + str(gi), "0" + str(gi + 1), g["name"], g["sub"], g["desc"],
                          '<div class="cast">' + "".join(rows) + '</div>'))

    conflict = ('<div class="aside-box"><h4>' + esc(W.CAST_CONFLICT["title"]) + '</h4><p>' +
                esc(W.CAST_CONFLICT["body"]) + '</p></div>')

    hero = ('<div class="page-head"><div class="page-kicker">CAST / TWENTY-ONE NAMES</div>'
            '<h1 class="page-title">人物</h1>'
            '<p class="page-lead">' + esc(W.CAST_NOTE) + '</p></div>')

    body = (head("人物", "新的勇者、七位大贤者、魔王军七位领袖", "") + nav("", False, "cast.html") + hero +
            "".join(blocks) + '<section class="sec"><div class="wrap">' + conflict + '</div></section>' + foot(""))
    write(ROOT / "cast.html", body)


# ══════════════════════════════ 资源 ══════════════════════════════

def build_assets():
    write(IMG / "banner.svg", art.banner())
    for fac in ("新的勇者", "同盟军", "魔王军", "通用"):
        write(IMG / ("sigil-" + FAC_SLUG[fac] + ".svg"), art.sigil(fac))

    for c in CARD_LIST:
        kind = "spell"
        ut = c.get("utype") or ""
        if c["cat"] == "单位":
            kind = "archer" if "射手" in ut else "unit"
        elif c["cat"] == "天赋":
            kind = "talent"
        write(IMG / "cards" / (c["id"] + ".svg"),
              art.card_art(c["id"], c["cluster"], kind=kind, w=600, h=380))

    for h in M.HEROES:
        cluster = h["id"] if h["id"] in art.PALETTE else "core-crystal"
        kind = "archer" if "射手" in h["type"] else "unit" if "战士" in h["type"] else "spell"
        write(IMG / "heroes" / (h["id"] + ".svg"),
              art.hero_art(h["id"], cluster, kind=kind, w=1500, h=520))

    payload = [dict(id=c["id"], name=c["name"], fac=c["fac"], q=c["q"], lim=c.get("lim") or "",
                    cost=c.get("cost") or "", cat=c["cat"], cluster=c["cluster"],
                    hero=c.get("hero"), stats=c.get("stats") or "", utype=c.get("utype") or "",
                    text=c["text"], tags=c.get("tags") or []) for c in CARD_LIST]
    write(ROOT / "assets" / "data" / "cards.js",
          "window.CARDS=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";")

    # 概念图总览页用的静态清单（供 README）
    return len(CARD_LIST)


def main():
    for d in (IMG, IMG / "cards", IMG / "heroes", CARDS_DIR, HEROES_DIR, ROOT / "assets" / "data"):
        d.mkdir(parents=True, exist_ok=True)
    n = build_assets()
    build_index()
    build_world()
    build_story()
    build_cast()
    build_archive()
    build_sandbox()
    build_rulebook()
    for h in M.HEROES:
        build_hero(h)
    for c in CARD_LIST:
        build_card(c)
    print("pages:", 7 + len(M.HEROES) + len(CARD_LIST), "cards:", n)


if __name__ == "__main__":
    main()
