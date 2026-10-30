# -*- coding: utf-8 -*-
"""长歌 · 企划官方页生成器。

只读 Game/ 与 Agent/Qwen 的原典；输出到 OfficialPage/。
运行：python build.py
"""

from __future__ import annotations

import html as _html
import json
import re
import shutil
from pathlib import Path

import art
import cardsource
import content
import data_site
import textpatch
import theme

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "OfficialPage"
ASSETS = OUT / "assets"

PROJECT = data_site.PROJECT
TITLE = PROJECT["title"]
LATIN = PROJECT["latin"]

CARDS = []
BY_ID = {}
CONTENT = {}

QUALITY = {
    "N": "普通",
    "R": "稀有",
    "E": "史诗",
    "L": "传说",
    "域外": "域外",
    "觉醒": "觉醒",
}
QUALITY_ORDER = ["N", "R", "E", "L", "域外", "觉醒"]
FACTION_ORDER = ["新的勇者", "同盟军", "通用", "魔王军"]

SECTIONS = [
    ("general", "通用", "COMMON", "不依赖任何英雄的公共卡池"),
    ("novian", "诺维安", "NOVIAN", "路与歌"),
    ("lilia", "莉莉亚", "LILIA", "白百合与月"),
    ("eve", "伊芙格林", "EVERGREEN", "风与常青"),
    ("moika", "莫伊卡", "MOIKA", "锁与梦"),
    ("milika", "米莉卡", "MILIKA", "大奇迹"),
    ("herseus", "赫琉思", "HERSEUS", "太阳之子"),
    ("scarlin", "斯卡琳", "SCARLIN", "红月"),
    ("morphy", "莫菲", "MOFEI", "梦之掌司"),
]
SECTION_SLUGS = [s[0] for s in SECTIONS]
SECTION_TITLE = {s[0]: s[1] for s in SECTIONS}
SECTION_LATIN = {s[0]: s[2] for s in SECTIONS}

NAV = [
    ("index", "序", "index.html"),
    ("world", "世界", "world.html"),
    ("history", "战史", "history.html"),
    ("cast", "人物", "cast.html"),
    ("game", "游戏", "game/index.html"),
    ("novel", "小说", "novel.html"),
    ("about", "关于", "about.html"),
]

MOTTO = "月亮有两面，卡也是。正面写它做什么，背面写它为什么。"


# ---------------------------------------------------------------- helpers
def esc(value) -> str:
    return _html.escape(str(value), quote=True)


def dname(card) -> str:
    if card["id"] == "herseus-t1":
        return "无名天赋 · 一"
    if card["id"] == "herseus-t2":
        return "无名天赋 · 二"
    return card["name"]


def qlabel(card) -> str:
    return QUALITY.get(card["quality"], card["quality"])


def cost_label(card) -> str:
    return "—" if card["cost"] is None else str(card["cost"])


def panel_text(card) -> str:
    p = card.get("panel")
    if not p:
        return "—"
    return f'{p["c"]} / {p["a"]} / {p["d"]}'


def limit_text(card) -> str:
    if card.get("limit_raw"):
        return card["limit_raw"]
    return "—"


def roman(n: int) -> str:
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    for v, s in vals:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def page(title: str, rel: str, body: str, *, desc: str = "", active: str = "", cls: str = "") -> str:
    full = f"{title} · {TITLE}" if title and title != TITLE else f"{TITLE} · {LATIN}"
    desc = desc or PROJECT["subtitle"]
    body = "\n".join(line.rstrip() for line in body.splitlines())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#171c26">
<meta property="og:title" content="{esc(full)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{rel}assets/seal.svg" type="image/svg+xml">
<link rel="stylesheet" href="{rel}assets/site.css">
</head>
<body class="{esc(cls)}">
<a class="skip" href="#main">跳到正文</a>
{header(rel, active)}
<main id="main">
{body}
</main>
{footer(rel)}
<script src="{rel}assets/site.js"></script>
</body>
</html>
"""


ROOT_LINKS = {
    "world.html", "history.html", "cast.html", "novel.html", "about.html",
    "index.html", "404.html",
}


def rebase_root(body: str, prefix: str = "../") -> str:
    """把游戏子目录页面里按站点根写的链接改成相对当前目录的写法。"""
    def repl(match: re.Match) -> str:
        attr, value = match.group(1), match.group(2)
        if not value or value.startswith(("#", "http:", "https:", "mailto:", "data:", "javascript:", "../", "../../")):
            return match.group(0)
        if value.startswith("assets/") or value in ROOT_LINKS:
            return f'{attr}="{prefix}{value}"'
        return match.group(0)

    body = re.sub(r'(href|src)="([^"]+)"', repl, body)
    body = re.sub(
        r'(data-zoom)="(assets/[^"]+)"',
        lambda m: f'{m.group(1)}="{prefix}{m.group(2)}"',
        body,
    )
    return body



def header(rel: str, active: str) -> str:
    links = []
    for key, label, href in NAV:
        cls = ' class="is-active"' if key == active else ""
        links.append(f'<a href="{rel}{href}"{cls}>{label}</a>')
    return f"""<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{rel}index.html" aria-label="长歌 · 首页">
      <span class="brand-dot" aria-hidden="true"></span>
      <span class="brand-text">长歌<small>HISTORY</small></span>
    </a>
    <button class="nav-toggle" type="button" aria-label="打开导航" aria-controls="site-nav" aria-expanded="false"><span></span></button>
    <nav class="nav" id="site-nav" aria-label="主导航">
      {''.join(links)}
    </nav>
  </div>
</header>"""


def footer(rel: str) -> str:
    return f"""<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <div class="foot-brand">长歌 <span>HISTORY</span></div>
      <p>{esc(PROJECT["subtitle"])}。小说、音乐与游戏共用同一套世界设定，各自从不同的门进入。</p>
    </div>
    <div class="foot-links">
      <h3>Index</h3>
      <a href="{rel}world.html">世界</a>
      <a href="{rel}history.html">战史</a>
      <a href="{rel}cast.html">人物</a>
      <a href="{rel}game/index.html">游戏编</a>
      <a href="{rel}novel.html">小说</a>
    </div>
    <div>
      <h3>Archive</h3>
      <div class="foot-meta">
        企划官方页 · 第一版<br>
        {esc(PROJECT["date"])} · 静态归档<br>
        作者 {esc(PROJECT["author"])}<br>
        卡牌 86 · 人物 21 · 阵营 3
      </div>
    </div>
  </div>
  <div class="wrap foot-bottom">
    <span>长歌 · HISTORY / OFFICIAL PAGE</span>
    <span>本页为企划归档，非商业发行页面。</span>
  </div>
</footer>"""


def section_head(num: str, eyebrow: str, title: str, lead: str = "") -> str:
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return f"""<div class="section-head" data-reveal>
  <div class="section-num">{esc(num)}</div>
  <div>
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h2>{title}</h2>
    {lead_html}
  </div>
</div>"""


def chapter(num: str, title: str, latin: str, body: str, anchor: str = "") -> str:
    aid = f' id="{esc(anchor)}"' if anchor else ""
    return f"""<section class="chapter"{aid}>
  <aside class="chapter-side">
    <div class="num">{esc(num)}</div>
    <h2>{title}</h2>
    <div class="latin">{esc(latin)}</div>
  </aside>
  <div class="chapter-body">
    {body}
  </div>
</section>"""


def figure(src: str, alt: str, caption: str, note: str = "") -> str:
    note_html = f"<span>{esc(note)}</span>" if note else ""
    return f"""<figure class="figure" data-reveal>
  <img src="{src}" alt="{esc(alt)}" loading="lazy">
  <figcaption><b>{esc(caption)}</b>{note_html}</figcaption>
</figure>"""


def breadcrumb(items) -> str:
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append("<span>/</span>")
        if href:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            parts.append(f"<em>{esc(label)}</em>")
    return f'<nav class="breadcrumb" aria-label="面包屑">{"".join(parts)}</nav>'


def card_url(cid: str, rel: str) -> str:
    return f"{rel}game/cards/{cid}.html"


def card_thumb(cid: str, rel: str, alt: str = "") -> str:
    card = BY_ID[cid]
    return f'<img src="{rel}assets/cards/{cid}.svg" alt="{esc(alt or dname(card))}" loading="lazy">'


# ---------------------------------------------------------------- home
def build_home() -> str:
    cover = f"""<section class="cover">
  <img class="cover-art" src="assets/concept/cover.svg" alt="长歌 · 封面概念图：月下的城与路">
  <div class="wrap">
    <div class="cover-top">
      <span>企划官方页 / OFFICIAL PAGE</span>
      <span>ARCHIVE 001 · {esc(PROJECT["date"])}</span>
    </div>
    <div class="cover-main">
      <div>
        <p class="eyebrow" style="color:var(--gold-soft)">小说 · 音乐 · 游戏</p>
        <h1>长歌</h1>
        <p class="latin-big">{esc(LATIN)}</p>
      </div>
      <div class="cover-note">
        <p>月亮升起之前，先把路走完。</p>
        <p style="margin-top:14px">一个由小说、音乐与游戏构成的联合企划。同一个世界，三种讲述方式：<b>小说</b>写人，<b>音乐</b>写气息，<b>游戏</b>让选择发生。</p>
      </div>
    </div>
    <div class="cover-bottom">
      <div class="cover-stats">
        <div><b>86</b><span>张卡牌图版</span></div>
        <div><b>21</b><span>位有名有姓的人</span></div>
        <div><b>03</b><span>个阵营</span></div>
        <div><b>40</b><span>张一副卡组</span></div>
      </div>
      <a class="btn btn--light" href="game/index.html">进入游戏编</a>
    </div>
  </div>
</section>"""

    triptych = f"""<section class="section" id="triptych">
  <div class="wrap">
    {section_head("01", "THE TRIPTYCH", "三编", "小说、音乐、游戏不是三个衍生品，而是同一份设定的三种写法。它们各自成立，也互相拆台。")}
    <div class="triptych" data-reveal>
      <article>
        <div class="t-num">I / NOVEL</div>
        <h3>小说</h3>
        <div class="t-latin">MAIN STORY</div>
        <p>从格兰蒂亚出发，经过芬特罗德、记忆森林、黄金之城、钢铁之城与无梦之城。路上的人各有各的理由，最后都走到同一个封印前。</p>
        <div class="t-status">筹备中 · 正文将先行发布</div>
        <a class="t-go" href="novel.html">查看发布计划</a>
      </article>
      <article>
        <div class="t-num">II / GAME</div>
        <h3>游戏</h3>
        <div class="t-latin">TEXT ADVENTURE × CARD GAME</div>
        <p>文字冒险承载路，卡牌承载战斗。文字冒险部分由 GodotADV 实现；卡牌部分以 1939 工作室的《Kards》为灵感，做成双信仰、40 张卡组的样子；战区的数量、排布与容量由随机地图决定。</p>
        <div class="t-status">设计归档 · 规则与 86 张卡</div>
        <a class="t-go" href="game/index.html">进入游戏编</a>
      </article>
      <article>
        <div class="t-num">III / MUSIC</div>
        <h3>音乐</h3>
        <div class="t-latin">MUSIC</div>
        <p>长歌首先是一首歌的名字。音乐编目前仍在筹备，曲目与主题会随小说与游戏的关键章节一起公布。</p>
        <div class="t-status">筹备中 · 暂无页面</div>
        <span class="t-go" aria-disabled="true">waiting for the song</span>
      </article>
    </div>
  </div>
</section>"""

    game_preview = f"""<section class="section section--night">
  <div class="wrap">
    <div class="night-head" data-reveal>
      <div>
        <p class="eyebrow">THE GAME</p>
        <h2>把路做成选择，<br>把战斗做成牌。</h2>
      </div>
      <div>
        <p class="lead">文字冒险部分负责「你遇见谁」；卡牌部分负责「你拿什么去换」。两者共用同一套人物、地理与规则，不互相解释，但互相证明。</p>
        <a class="btn btn--light" style="margin-top:24px" href="game/play.html">先看怎么玩</a>
      </div>
    </div>
    <div class="plate-strip" data-reveal>
      <a href="game/cards/pale-moon.html">
        {card_thumb("pale-moon", "")}
        <figcaption><span>莉莉亚 · 苍白之月</span><span>PLATE</span></figcaption>
      </a>
      <a href="game/cards/crimson-moon.html">
        {card_thumb("crimson-moon", "")}
        <figcaption><span>斯卡琳 · 绯红之月</span><span>PLATE</span></figcaption>
      </a>
      <a href="game/cards/great-miracle.html">
        {card_thumb("great-miracle", "")}
        <figcaption><span>米莉卡 · 大奇迹</span><span>PLATE</span></figcaption>
      </a>
    </div>
    <div class="game-cols" data-reveal>
      <article>
        <div class="latin">TEXT ADVENTURE</div>
        <h3>文字冒险</h3>
        <p>由 GodotADV 承载。场景、立绘、分支与存档都在同一个框架里；小说里没写出来的那部分，交给玩家去走。</p>
      </article>
      <article>
        <div class="latin">CARD GAME</div>
        <h3>卡牌对战</h3>
        <p>随机地图、双信仰、40 张卡组。战区数量、排布与容量都由地图决定；三个阵营各自有一套节奏；英雄与天赋在构筑时合成一张牌，死亡不是退场，是返场前的空白。</p>
      </article>
    </div>
  </div>
</section>"""

    world_preview = f"""<section class="section">
  <div class="wrap">
    {section_head("02", "THE WORLD", "世界", "魔力不是燃料，是原质在运动中的表现。把这件事想清楚，后面的战争、种族与禁忌才有地方落脚。")}
    <div style="display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:56px;align-items:center" data-reveal>
      <div>
        <p class="pullquote">「月亮有两面。我只被允许看见一面——所以我要去另一面。」<span>莉莉亚 · 人物题记</span></p>
        <p class="lead" style="margin-top:24px">人类、精灵、矮人、哥布林、魔物与魔种。三代魔法。四个组织。九处地名。以及一场被写错过的战争。</p>
        <a class="btn" style="margin-top:28px" href="world.html">阅读世界设定</a>
      </div>
      <figure class="figure" style="margin:0">
        <img src="assets/concept/redmoon.svg" alt="红月概念图" loading="lazy">
        <figcaption><b>红月</b><span>她升起红月之后，月亮有了两面。</span></figcaption>
      </figure>
    </div>
  </div>
</section>"""

    stats = f"""<section class="section section--tight">
  <div class="wrap">
    <div class="stat-row" data-reveal>
      <div><b>86</b><span>张卡牌 · 每张一个独立页</span></div>
      <div><b>291</b><span>条卡与卡之间的关系</span></div>
      <div><b>18</b><span>个规则词条</span></div>
      <div><b>09</b><span>处主线地名</span></div>
    </div>
  </div>
</section>"""

    note = f"""<section class="section section--tight">
  <div class="wrap" style="display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:56px;align-items:start" data-reveal>
    <div>
      <p class="eyebrow">ABOUT THIS ARCHIVE</p>
      <h2 class="serif" style="font-size:34px;font-weight:500;margin:12px 0 14px">这不是设定集，是一份可以走进去的归档。</h2>
      <p class="lead">页面把「原典」「裁定」「推想」分开：卡文以 Game/CardsDesign.md 为准，冲突处按作者裁定汇编；卡页下方的「肥鱼碎碎念」是归档者的读卡笔记，不进入规则结论。</p>
      <p class="small muted" style="margin-top:16px">卡面图版由程序生成，属于概念图层级，不是最终游戏美术。</p>
    </div>
    <div class="side-note">
      <h3>从这里开始</h3>
      <ul>
        <li><a href="game/cards/index.html">86 张卡牌档案</a></li>
        <li><a href="game/atlas.html">八条关系谱</a></li>
        <li><a href="game/concept.html">七张概念图版</a></li>
        <li><a href="history.html">战史与史书之外</a></li>
      </ul>
    </div>
  </div>
</section>"""

    return page("", "", cover + triptych + game_preview + world_preview + stats + note, active="index")


# ---------------------------------------------------------------- world
def build_world() -> str:
    laws = "".join(
        f"""<article class="law">
  <div class="law-num">LAW {esc(x["num"])}</div>
  <h3>{esc(x["title"])}</h3>
  <p>{esc(x["text"])}</p>
</article>"""
        for x in data_site.LAWS
    )
    races = "".join(
        f"""<div class="race-row">
  <div><h3>{esc(x["name"])}</h3><div class="race-tag">{esc(x["epithet"])}</div></div>
  <p>{esc(x["text"])}</p>
</div>"""
        for x in data_site.RACES
    )
    powers = "".join(
        f"""<article>
  <div class="latin">{esc(x.get("alias", ""))}</div>
  <h3>{esc(x["name"])}</h3>
  <p>{esc(x["text"])}</p>
</article>"""
        for x in data_site.POWERS
    )
    ages = "".join(
        f"""<article class="law">
  <div class="law-num">AGE {esc(x["num"])}</div>
  <h3>{esc(x["title"])}</h3>
  <p>{esc(x["text"])}</p>
</article>"""
        for x in data_site.AGES
    )
    places = "".join(
        f"""<article>
  <h3>{esc(x["name"])}</h3>
  <p>{esc(x["text"])}</p>
</article>"""
        for x in data_site.PLACES
    )

    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">THE WORLD</p>
    <h1>世界</h1>
    <p class="lead">先有物理，再有战争。魔力、原质与魔能的三条定律，决定了谁能施法、谁被禁止、谁被写进禁忌。</p>
    <div class="hero-latin">MAGIC · RACE · POWER · AGE</div>
  </div>
</section>
<div class="wrap">
  {chapter("01", "魔力", "THE THREE LAWS", f'''
    <p>在这个世界里，魔力不是凭空出现的燃料。它是原质在运动中的表现；把魔力与原质统一量纲，得到「魔能」；魔能可以与其他能量互相转换，总和不变。</p>
    {figure("assets/concept/mana.svg", "三圆相切的概念图", "图版 I · 魔力、原质与魔能", "三圆相切：不是三种东西，是同一种东西的三种写法。")}
    <div class="law-grid">{laws}</div>
    <p class="rule-note"><b>为什么要先讲这个？</b> 因为后面的「魔种魔法为什么是禁忌」「贤者之石为什么珍贵」「斯卡琳为什么必须死」，都在这三条定律里。</p>
  ''', "magic")}
  {chapter("02", "种族", "THE PEOPLES", f'''
    <p>人类、精灵、矮人、哥布林、魔物、魔种。前四个是「可以一起坐下来谈」的，后两个是「被写进史书另一栏」的。这个分栏本身就是战争留下的。</p>
    <div class="race-list">{races}</div>
    <p class="rule-note"><b>术语分层：</b> 小说用「弓箭手」，游戏单位类型用「射手」；「魔族」是旧称，「魔种」是当代用语。页面保留两层，不强行统一。</p>
  ''', "races")}
  {chapter("03", "组织", "THE POWERS", f'''
    <p>四个组织，四种把世界组织起来的方式：同盟靠条约，魔王军靠军团，格兰蒂亚靠学院与资格认证，伊莲教会靠神谕。</p>
    <div class="org-grid">{powers}</div>
  ''', "powers")}
  {chapter("04", "三代魔法", "THREE AGES OF MAGIC", f'''
    <p>精灵族魔法、神代魔法、现代魔法。三代不是简单的替代关系：它们对「魔力从哪里来」给出了三种不同的回答。</p>
    {figure("assets/concept/ages.svg", "三代魔法的概念图", "图版 II · 三代魔法", "本能、神谕、公式。三种回答，三种代价。")}
    <div class="law-grid">{ages}</div>
    <p class="rule-note"><b>现代魔法</b>是唯一完全掌握原理、可以系统教学的一代。它由傅泽提出原质概念，由他的学生斯卡琳归纳为三定律。也正因为如此，它最容易被写进教科书，最容易被用来排除异端。</p>
  ''', "ages")}
  {chapter("05", "地名", "THE PLACES", f'''
    <p>主线从格兰蒂亚出发，一路向北、向东、向更远的地方。每一座城都对应一种「人如何与魔力相处」的答案。</p>
    <div class="place-grid">{places}</div>
    <p class="rule-note">地名表只列主线与设定中已确定的地点；「名称待定」的地方保留原样，不替作者补名。</p>
  ''', "places")}
</div>"""
    return page("世界", "", body, active="world", desc="长歌的世界设定：魔力学三定律、六大种族、四大组织、三代魔法与九处地名。")


# ---------------------------------------------------------------- history
def build_history() -> str:
    items = []
    for x in data_site.TIMELINE:
        cls = " is-red" if x.get("kind") in ("red", "redmoon") else ""
        tag = f'<span class="tl-tag">{esc(x.get("kind", ""))}</span>' if x.get("kind") else ""
        items.append(f"""<div class="tl-item{cls}">
  <div class="tl-date">{esc(x["when"])}</div>
  <h3>{esc(x["title"])}{tag}</h3>
  <p>{esc(x["text"])}</p>
</div>""")
    questions = "".join(
        f'<li><b>QUESTION {str(i+1).zfill(2)}</b><p>{esc(q)}</p></li>'
        for i, q in enumerate(data_site.APOCRYPHA["lines"])
    )
    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">THE HISTORY</p>
    <h1>战史</h1>
    <p class="lead">一份按年份排列的史书，和一份不按年份排列的疑问。前者是同盟愿意让人读到的；后者是小说要写的。</p>
    <div class="hero-latin">THE ALLIANCE WAR · 500 YEARS</div>
  </div>
</section>
<div class="wrap">
  <section class="chapter">
    <aside class="chapter-side"><div class="num">01</div><h2>年表</h2><div class="latin">CHRONOLOGY</div></aside>
    <div class="chapter-body">
      <p>从神代到「现在」。九条，不多不少。年表只写史书承认的部分；凡是有争议的，都放进下一节。</p>
      <div class="timeline">{''.join(items)}</div>
    </div>
  </section>
  <section class="apocrypha" data-reveal>
    <p class="eyebrow">APOCRYPHA</p>
    <h2>{esc(data_site.APOCRYPHA["title"])}</h2>
    <p class="lead">{esc(data_site.APOCRYPHA["lead"])}</p>
    <ul class="question-list">{questions}</ul>
    <p class="ap-note">{esc(data_site.APOCRYPHA["note"])}</p>
  </section>
  <section class="chapter">
    <aside class="chapter-side"><div class="num">02</div><h2>读法</h2><div class="latin">HOW TO READ</div></aside>
    <div class="chapter-body">
      <p class="pullquote">历史不是「发生了什么」，而是「谁有资格把它写下来」。<span>归档者</span></p>
      <p>年表里「同盟战争」写的是自卫叙事；「红月之夜」写的是禁术失控。两句话都只写到一半。页面不替你翻案，只把缺口标出来。</p>
      <p>如果你想从人物的角度进入，去「人物」页；如果你想看战争如何变成牌，去游戏编的斯卡琳、赫琉思与米莉卡卡组。</p>
      <a class="btn" href="cast.html">去看人物</a>
    </div>
  </section>
</div>"""
    return page("战史", "", body, active="history", desc="长歌战史：从神代到现在的九条年表，以及史书之外的四个问题。")


# ---------------------------------------------------------------- cast
def build_cast() -> str:
    groups = []
    for key in ("new", "sages", "demons"):
        meta = data_site.CAST_GROUPS[key]
        people = [p for p in data_site.CAST if p["group"] == key]
        cards = []
        for p in people:
            status = f'<span class="cast-status">{esc(p["status"])}</span>' if p.get("status") else ""
            facts = "".join(f"<span><b>{esc(f.split('：')[0])}</b>{esc(f.split('：', 1)[1] if '：' in f else '')}</span>" for f in p.get("facts", []))
            bio = "".join(f"<p>{esc(x)}</p>" for x in p.get("bio", []))
            more = ""
            if p.get("cards"):
                more = f'<div class="cast-more"><a href="game/cards/index.html#group-{esc(p["cards"])}">查看与之相关的卡牌 →</a></div>'
            cards.append(f"""<article class="cast-card" id="{esc(p["id"])}">
  {status}
  <div class="cast-sigil"><img src="assets/heroes/{esc(p["id"])}.svg" alt="{esc(p["name"])} 的纹章" loading="lazy"></div>
  <div>
    <div class="cast-latin">{esc(p["latin"])} · {esc(p["group"])}</div>
    <h3>{esc(p["name"])}</h3>
    <div class="cast-epithet">{esc(p["epithet"])} · {esc(p["job"])}</div>
    <p class="cast-motto">「{esc(p["motto"])}」</p>
    <div class="cast-bio">{bio}</div>
    <div class="cast-facts">{facts}</div>
    {more}
  </div>
</article>""")
        groups.append(f"""<section class="cast-section">
  <div class="cast-head" data-reveal>
    <div>
      <p class="eyebrow">{esc(meta["latin"])}</p>
      <h2>{esc(meta["title"])}</h2>
    </div>
    <p class="lead">{esc(meta["note"])}</p>
  </div>
  <div class="cast-grid">{''.join(cards)}</div>
</section>""")

    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">THE CAST</p>
    <h1>人物</h1>
    <p class="lead">二十一个人。七个人在当下上路，七个人在五百年前结束战争，七个人在封印的另一侧守着各自的人。</p>
    <div class="hero-latin">21 NAMES · 3 GROUPS</div>
  </div>
</section>
<div class="wrap">
  <p class="small muted" style="padding:24px 0 0">题记保留试做页的格言体。人物档案以根目录 Outline.md 为准；标「施工中」「名字未定」「原稿尚简」的地方，保留原样。</p>
  {''.join(groups)}
</div>"""
    return page("人物", "", body, active="cast", desc="长歌人物：新的勇者七人、七位大贤者、魔王军七人，共二十一位有名有姓的人。")


# ---------------------------------------------------------------- game index
def build_game_index() -> str:
    stats = f"""<div class="stat-row" data-reveal>
  <div><b>40</b><span>张 · 一副卡组</span></div>
  <div><b>MAP</b><span>战区 · 由地图决定</span></div>
  <div><b>03</b><span>个阵营 · 选一</span></div>
  <div><b>86</b><span>张 · 已归档卡牌</span></div>
</div>"""
    body = f"""<section class="cover cover--game">
  <img class="cover-art" src="assets/concept/game-cover.svg" alt="随机地图概念图">
  <div class="wrap">
    <div class="cover-top"><span>游戏编 / THE GAME</span><span>DESIGN ARCHIVE · {esc(PROJECT["date"])}</span></div>
    <div class="cover-main">
      <div>
        <p class="eyebrow" style="color:var(--gold-soft)">TEXT ADVENTURE × CARD GAME</p>
        <h1>游戏编</h1>
        <p class="latin-big">WALK · THEN PLAY</p>
      </div>
      <div class="cover-note">
        <p>文字冒险负责「你遇见谁」，卡牌负责「你拿什么去换」。</p>
        <p style="margin-top:14px">当前是<b>设计归档</b>，不是一个可下载的试玩版。规则、86 张卡、概念图与关系谱都已经在这里；代码与美术仍在路上。</p>
      </div>
    </div>
    <div class="cover-bottom">
      <div class="cover-stats">
        <div><b>PVE</b><span>文字冒险</span></div>
        <div><b>PVP</b><span>卡牌对战</span></div>
        <div><b>GODOT</b><span>ADV 框架</span></div>
      </div>
      <a class="btn btn--light" href="play.html">读规则</a>
    </div>
  </div>
</section>
<div class="wrap">
  <section class="section">
    {section_head("01", "TWO HALVES", "两个部分，一套世界", "文字冒险不解释卡牌，卡牌不解释文字冒险。它们共用人物、地理与历史，但各自承担不同的「选择」。")}
    <div class="game-cols" data-reveal>
      <article>
        <div class="latin">TEXT ADVENTURE / GODOTADV</div>
        <h3>文字冒险</h3>
        <p>场景、立绘、分支、存档。小说里被略过的那部分，交给玩家去走。它不追求「自由度」，追求的是「你确实在场」。</p>
      </article>
      <article>
        <div class="latin">CARD GAME / KARDS-INSPIRED</div>
        <h3>卡牌对战</h3>
        <p>随机地图、双信仰、40 张卡组。战区数量、排布与容量由地图决定；战士、法师、射手三类单位，三种距离。防御是可再生的生命，也是可以打空的资源。</p>
      </article>
    </div>
  </section>
  <section class="section">
    {section_head("02", "THREE FACTIONS", "三个阵营", "构筑时选一个阵营，只能带该阵营与通用牌。跨阵营的「联动」不存在；跨阵营的「对照」才是这套牌真正好玩的地方。")}
    <div class="triptych" data-reveal>
      <article>
        <div class="t-num">I / NEW HEROES</div>
        <h3>新的勇者</h3>
        <div class="t-latin">THE NEW HEROES</div>
        <p>诺维安、莉莉亚、伊芙格林、莫伊卡、罗耶、米莉卡，以及尚未入队的第七人。以「成长」与「彼此照应」为轴，单卡效率不高，但接口多。</p>
        <a class="t-go" href="cards/index.html#group-novian">看诺维安的卡</a>
      </article>
      <article>
        <div class="t-num">II / ALLIANCE</div>
        <h3>同盟军</h3>
        <div class="t-latin">THE ALLIANCE</div>
        <p>赫琉思与斯卡琳。一个用太阳的余晖，一个用红月的上限。它们代表五百年前那场战争的「官方版本」，也代表被官方版本排除的人。</p>
        <a class="t-go" href="cards/index.html#group-scarlin">看斯卡琳的卡</a>
      </article>
      <article>
        <div class="t-num">III / DEMON ARMY</div>
        <h3>魔王军</h3>
        <div class="t-latin">THE DEMON ARMY</div>
        <p>目前只有莫菲的「捕梦网」进入了 86 张卡。其余的七军团领袖还在设定里；这一栏会随着小说与后续设计长出东西。</p>
        <a class="t-go" href="cards/index.html#group-morphy">看莫菲的卡</a>
      </article>
    </div>
  </section>
  <section class="section">
    {section_head("03", "FOUR WAYS IN", "四种读法", "你可以从规则进去，也可以从图、从关系、从一张具体的卡进去。")}
    <div class="org-grid" data-reveal>
      <article><div class="latin">RULES</div><h3><a href="play.html">玩法</a></h3><p>战场、回合、行动、单位、信仰、18 个词条，以及一个可以点的回合演示。</p></article>
      <article><div class="latin">PLATES</div><h3><a href="concept.html">概念图</a></h3><p>七张图版：魔力、三代魔法、红月、战争、战场、一张卡的解剖、路。</p></article>
      <article><div class="latin">ATLAS</div><h3><a href="atlas.html">关系谱</a></h3><p>八条谱系，把 86 张卡拆成引擎、链条与对照组。</p></article>
      <article><div class="latin">CARDS</div><h3><a href="cards/index.html">卡牌档案</a></h3><p>86 张，每张一个独立页。卡文、归属、关联、词条，以及下方的「肥鱼碎碎念」。</p></article>
    </div>
  </section>
  <section class="section section--tight">
    {stats}
    <p class="small muted" style="margin-top:18px">数据口径：86 张卡（魔法 66 / 天赋 13 / 单位 5 / 觉醒 2）；阵营 新的勇者 59 / 同盟军 18 / 通用 8 / 魔王军 1。卡文以 Game/CardsDesign.md 为准。</p>
  </section>
</div>"""
    return page("游戏编", "../", rebase_root(body), active="game", desc="长歌游戏编：文字冒险 + 卡牌对战，随机地图、双信仰、40 张卡组、86 张已归档卡牌。")


# ---------------------------------------------------------------- play
def build_play() -> str:
    zones = [
        ("00", "己方末端", "信仰 · 1000", "is-edge is-faith", "faith-left", "信仰 1000"),
        ("01", "己方战区", "未占领", "", "", ""),
        ("02", "中央战区", "未占领 · 由地图决定", "", "", ""),
        ("03", "敌方战区", "未占领", "", "", ""),
        ("04", "敌方末端", "信仰 · 1000", "is-edge is-faith", "faith-right", "信仰 1000"),
    ]
    zone_html = []
    for num, name, label, cls, token, token_text in zones:
        token_html = ""
        if token:
            token_html = f'<div class="demo-token is-on" data-token="{esc(token)}" style="position:absolute;left:12px;right:12px;bottom:12px"><b>{esc(token_text.split(" ")[0])}</b><span>{esc(token_text.split(" ", 1)[1] if " " in token_text else "")}</span></div>'
        zone_html.append(f"""<div class="zone {cls}" data-demo-zone="{num}">
  <div class="z-label">ZONE {num}</div>
  <div class="z-name">{esc(name)}</div>
  <div class="z-flag">{esc(label)}</div>
  {token_html}
</div>""")

    steps = [
        {"kicker": "STEP 01 / 06", "title": "开局", "text": "先手抽 4，后手抽 5，然后调度：可以换掉等量的牌。双方各有一座 1000 防御的信仰，放在自己的末端战区；开局时，除两端信仰外，所有战区都未被占领。", "zones": [0, 4], "tokens": ["faith-left", "faith-right", "novian", "guard", "enemy"], "pos": {"faith-left": 0, "faith-right": 4}},
        {"kicker": "STEP 02 / 06", "title": "回合开始", "text": "除先手第一回合外，回合开始抽 1。魔力上限 +1，并回满当前魔力。上限到 12 后停止自然增长；硬上限是 24。", "zones": [0, 4], "tokens": ["faith-left", "faith-right", "novian", "guard", "enemy"], "pos": {"faith-left": 0, "faith-right": 4}},
        {"kicker": "STEP 03 / 06", "title": "出牌", "text": "单位牌只能加入己方末端战区，不能直接放进中间。手牌上限 9；溢出的牌放回卡组底部。0 费不等于机动；机动是词条，写在卡上。", "zones": [0], "tokens": ["faith-left", "faith-right", "novian", "guard", "enemy"], "pos": {"novian": 0, "guard": 0, "faith-left": 0, "faith-right": 4}},
        {"kicker": "STEP 04 / 06", "title": "移动", "text": "单位可以移动到相邻且未被占领、或己方占领的战区；不能进入敌方战区。移动花行动花费；一个单位通常每回合行动一次。", "zones": [0, 1, 3], "tokens": ["faith-left", "faith-right", "novian", "guard", "enemy"], "pos": {"novian": 1, "guard": 0, "enemy": 3, "faith-left": 0, "faith-right": 4}},
        {"kicker": "STEP 05 / 06", "title": "攻击", "text": "攻击是单位的行动：造成攻击力伤害，同时受到目标攻击力的反击。魔法不是攻击，守护不能挡魔法。射手无视守护，也不能造成或受到反击；法师在任意战区。", "zones": [2, 3], "tokens": ["faith-left", "faith-right", "novian", "guard", "enemy"], "pos": {"novian": 2, "guard": 0, "enemy": 3, "faith-left": 0, "faith-right": 4}},
        {"kicker": "STEP 06 / 06", "title": "防御", "text": "防御是指向己方目标、触发防御效果的行动。每受一次攻击解除一层防御；下个己方回合开始，剩余的防御也解除。", "zones": [0, 2], "tokens": ["faith-left", "faith-right", "novian", "guard", "enemy"], "pos": {"novian": 2, "guard": 0, "enemy": 3, "faith-left": 0, "faith-right": 4}},
    ]

    keywords = "".join(
        f"""<details>
  <summary><b>{esc(k)}</b><span>{esc(v["short"])}</span></summary>
  <p>{esc(v["long"])}</p>
</details>"""
        for k, v in data_site.KEYWORDS.items()
    )

    token_labels = {
        "faith-left": ("信仰", "1000", ""),
        "faith-right": ("信仰", "1000", ""),
        "novian": ("诺维安", "150 / 300", "is-hero"),
        "guard": ("守卫", "100 / 400", ""),
        "enemy": ("敌单位", "100 / 200", "is-enemy"),
    }
    demo_zones = []
    for i, (num, name, label, cls, _token, _text) in enumerate(zones):
        tokens_html = "".join(
            f'<div class="demo-token is-on {extra}" data-token="{esc(key)}"><b>{esc(tname)}</b><span>{esc(stats)}</span></div>'
            for key, (tname, stats, extra) in token_labels.items()
            if i == steps[0]["pos"].get(key)
        )
        demo_zones.append(f"""<div class="zone {cls}" data-demo-zone="{num}">
  <div class="z-label">ZONE {num}</div>
  <div class="z-name">{esc(name)}</div>
  {tokens_html}
  <div class="z-flag">{esc(label)}</div>
</div>""")

    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">HOW TO PLAY</p>
    <h1>玩法</h1>
    <p class="lead">随机地图，两座信仰，一副 40 张的卡组。你每回合做的事情不多：出牌、移动、攻击、防御。难的是把哪一件事留到下一回合。</p>
    <div class="hero-latin">RANDOM MAP · TWO FAITHS · FORTY CARDS</div>
  </div>
</section>
<div class="wrap">
  <section class="rule-block">
    <h2><span class="num">01 / BATTLEFIELD</span>战场</h2>
    <p class="lead">战场由随机地图决定：两端一定是双方的信仰，末端战区不可被敌方占领，但己方单位可以从手牌加入。中间的战区数量、连接方式与每个战区的容量都随地图变化；开局时，除两端信仰外，所有战区都未被占领。下面只是最小结构。</p>
    <div class="battlefield">{''.join(zone_html)}</div>
    <div class="battlefield-caption"><span>末端：信仰 · 敌方不可占领</span><span>中央：未占领 · 数量与容量由地图决定</span></div>
  </section>
  <section class="rule-block">
    <h2><span class="num">02 / TURN</span>一个回合</h2>
    <div class="rule-cols">
      <div>
        <h3>开始</h3>
        <ul>
          <li>除先手第一回合外，抽 1 张。</li>
          <li>魔力上限 +1，当前魔力回满。</li>
          <li>上限到 12 后停止自然增长；硬上限 24。</li>
          <li>防御层与「直到下个己方回合」的效果在此结算。</li>
        </ul>
      </div>
      <div>
        <h3>行动</h3>
        <ul>
          <li>每个单位通常每回合行动一次，支付行动花费。</li>
          <li>攻击：相邻或射程内，造成攻击力伤害并受反击；攻击只是单位的行动。</li>
          <li>魔法：可以被指向、可以造成伤害，但不算「攻击」；守护不能替目标接魔法。</li>
          <li>防御：指向己方目标，触发防御效果。</li>
          <li>移动：到相邻且未被占领、或己方占领的战区；不能进入敌方战区。</li>
        </ul>
      </div>
    </div>
    <p class="rule-note"><b>卡组：</b> 40 张，从「新的勇者」「同盟军」「魔王军」中选一个阵营，只能带该阵营与通用牌。英雄与天赋在构筑时合成一张牌，天赋在卡组与收藏中均最多 1 张；一副卡组可以带多位不同英雄。单位牌只能加入己方末端战区。</p>
  </section>
  <section class="rule-block">
    <h2><span class="num">03 / UNITS</span>三类单位</h2>
    <table class="table">
      <thead><tr><th>类型</th><th>子类</th><th>伤害</th><th>距离</th><th>特性</th></tr></thead>
      <tbody>
        <tr><td>战士</td><td>骑士</td><td>物理</td><td>仅相邻</td><td>无附加</td></tr>
        <tr><td>战士</td><td>游侠</td><td>物理</td><td>仅相邻</td><td>可移动并攻击</td></tr>
        <tr><td>战士</td><td>近卫</td><td>物理</td><td>仅相邻</td><td>可攻击并防御</td></tr>
        <tr><td>法师</td><td>魔法使</td><td>魔法</td><td>任意战区</td><td>无附加</td></tr>
        <tr><td>法师</td><td>炼金术师</td><td>魔法</td><td>任意战区</td><td>不受反击</td></tr>
        <tr><td>法师</td><td>神官</td><td>魔法</td><td>任意战区</td><td>不造成反击</td></tr>
        <tr><td>射手</td><td>射手</td><td>物理</td><td>任意战区</td><td>无视守护；不受也无法造成反击</td></tr>
      </tbody>
    </table>
    <p class="rule-note"><b>术语：</b> 小说里写「弓箭手」，游戏单位类型写「射手」。这是刻意的两层，不是笔误。</p>
  </section>
  <section class="rule-block">
    <h2><span class="num">04 / FAITH</span>信仰与胜负</h2>
    <div class="rule-cols">
      <div>
        <h3>信仰</h3>
        <p>双方末端战区各有一座信仰，1000 防御，无法行动。它可以被单位攻击，但不会反击；魔法也可以对它造成伤害，但那不属于「攻击」。摧毁对方信仰即获胜。守护可以保护信仰，但只对单位的攻击生效。</p>
      </div>
      <div>
        <h3>英雄</h3>
        <p>英雄被消灭后，于下个敌方回合结束时洗入卡组并产生返场效果；英雄的专属魔法只在英雄在场上时可用（限定）。</p>
      </div>
    </div>
  </section>
  <section class="rule-block">
    <h2><span class="num">05 / KEYWORDS</span>十八个词条</h2>
    <p class="lead">点开看长解释。页面把「规则原文」与「归档者补充」分开；补充不改变原文，只负责把容易读错的地方说清楚。</p>
    <div class="keyword-grid">{keywords}</div>
  </section>
  <section class="rule-block" id="demo">
    <h2><span class="num">06 / DEMO</span>一个回合的演示</h2>
    <p class="lead">这不是可玩的模拟器，只是一张会动的示意图。点「下一步」看顺序；点「上一步」退回去。</p>
    <div class="demo" data-demo>
      <div class="demo-stage">
        <div class="battlefield" data-demo-zones>
          {''.join(demo_zones)}
        </div>
      </div>
      <div class="demo-panel">
        <div class="demo-kicker" data-demo-kicker>STEP 01 / 06</div>
        <h3 data-demo-title>开局</h3>
        <p data-demo-text>先手抽 4，后手抽 5，然后调度。</p>
        <div class="demo-dots" data-demo-dots></div>
        <div class="demo-controls">
          <button class="btn" type="button" data-demo-prev>上一步</button>
          <button class="btn btn--red" type="button" data-demo-next>下一步</button>
        </div>
      </div>
    </div>
    <script type="application/json" id="demo-data">{json.dumps({"steps": steps, "motto": MOTTO}, ensure_ascii=False)}</script>
  </section>
</div>"""
    return page("玩法", "../", rebase_root(body), active="game", desc="长歌卡牌玩法：随机地图、回合流程、三类单位、信仰与十八个规则词条，附一个可点击的回合演示。")


# ---------------------------------------------------------------- concept
def build_concept() -> str:
    items = []
    for i, x in enumerate(data_site.CONCEPTS, 1):
        items.append(f"""<article class="plate-item" data-reveal>
  <figure class="plate-fig">
    <button type="button" data-zoom="assets/concept/{esc(x["id"])}.svg" aria-label="放大 {esc(x["title"])}">
      <img src="assets/concept/{esc(x["id"])}.svg" alt="{esc(x["title"])} 概念图" loading="lazy">
    </button>
    <figcaption><span>PLATE {esc(x["num"])}</span><span>{esc(x["latin"])}</span></figcaption>
  </figure>
  <div class="plate-copy">
    <div class="num">PLATE {esc(x["num"])} / 07</div>
    <h2>{esc(x["title"])}</h2>
    <span class="latin">{esc(x["latin"])}</span>
    <p>{esc(x["text"])}</p>
    <p class="cap">{esc(x["caption"])}</p>
  </div>
</article>""")

    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">CONCEPT PLATES</p>
    <h1>概念图</h1>
    <p class="lead">七张图版。不是最终美术，是把设定里最难讲的部分先画成可以看的东西：三圆、三代、红月、战争、战场、一张卡的解剖、一条路。</p>
    <div class="hero-latin">SEVEN PLATES · SILKSCREEN</div>
  </div>
</section>
<div class="wrap">
  <p class="small muted" style="padding-top:24px">图版为程序生成的 SVG，采用纸本 + 双色丝网印的视觉体系。点图可放大。</p>
  <div class="plate-list">{''.join(items)}</div>
  <p class="rule-note" style="margin-top:56px"><b>为什么是概念图而不是立绘？</b> 因为这一版先把「关系」讲清楚：月亮、道路、锁、太阳、网。人物长什么样，留给小说、游戏美术与读者自己的想象。</p>
</div>
<dialog class="lightbox" id="lightbox">
  <button class="lb-close" type="button" aria-label="关闭">×</button>
  <img alt="放大的概念图">
</dialog>"""
    return page("概念图", "../", rebase_root(body), active="game", desc="长歌游戏编的七张概念图版：魔力、三代魔法、红月、战争、战场、卡牌解剖与路。")


# ---------------------------------------------------------------- atlas
def build_atlas() -> str:
    lines = []
    for a in data_site.ATLAS:
        chains = []
        for ch in a["chains"]:
            nodes = []
            for j, cid in enumerate(ch["ids"]):
                if cid not in BY_ID:
                    continue
                card = BY_ID[cid]
                if j:
                    nodes.append('<span class="arrow">→</span>')
                nodes.append(f'<a class="node" href="cards/{esc(cid)}.html">{card_thumb(cid, "../")}<b>{esc(dname(card))}</b><span>{esc(CONTENT[cid]["role"])}</span></a>')
            chains.append(f'<div class="chain"><div class="chain-caption">{esc(ch["caption"])}</div><div class="chain-row">{"".join(nodes)}</div></div>')
        lines.append(f"""<section class="atlas-line" data-reveal>
  <div class="atlas-head"><h2>{esc(a["title"])}</h2><span class="latin">{esc(a["latin"])}</span></div>
  <p class="atlas-intro">{esc(a["intro"])}</p>
  {''.join(chains)}
</section>""")

    cross = []
    for a_name, a_id, b_name, b_id, note in data_site.CROSS_REFS:
        cross.append(f"""<div class="cross-row">
  <a class="cr-a" href="cards/{esc(a_id)}.html">{esc(a_name)}</a>
  <div class="cr-t">对照 / 不联动</div>
  <a class="cr-b" href="cards/{esc(b_id)}.html">{esc(b_name)}</a>
  <p>{esc(note)}</p>
</div>""")

    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">CARD ATLAS</p>
    <h1>关系谱</h1>
    <p class="lead">{esc(MOTTO)}</p>
    <div class="hero-latin">EIGHT LINES · 86 CARDS</div>
  </div>
</section>
<div class="wrap">
  <p class="lead" style="padding-top:24px">下面的八条谱系不是「强度榜」，也不是「剧情时间线」。它们记录的是设计上的依赖：谁生成谁、谁检索谁、谁在谁之后才成立。跨阵营只标「对照」，不标联动。</p>
  {''.join(lines)}
  <section class="atlas-line">
    <div class="atlas-head"><h2>跨阵营 · 四组对照</h2><span class="latin">CROSS-FACTION MIRRORS</span></div>
    <p class="atlas-intro">同一个设计问题，两个阵营给出的不同答案。它们不能在同一副卡组里联动；把它们放在一起看，比放在一起打更有意思。</p>
    <div class="cross-table">{''.join(cross)}</div>
  </section>
</div>"""
    return page("关系谱", "../", body, active="game", desc="长歌卡牌关系谱：八条设计谱系与四组跨阵营对照，把 86 张卡连成可读的结构。")


# ---------------------------------------------------------------- cards index
def build_cards_index() -> str:
    groups = []
    for slug, title, latin, sub in SECTIONS:
        cards = [c for c in CARDS if c["group_slug"] == slug]
        if not cards:
            continue
        tiles = []
        for c in cards:
            meta = CONTENT[c["id"]]
            search = " ".join([dname(c), meta["role"], c["id"], " ".join(meta.get("axes", []))])
            tiles.append(f"""<a class="card-tile" href="{esc(c["id"])}.html"
  data-faction="{esc(c["faction"])}" data-quality="{esc(c["quality"])}" data-group="{esc(slug)}"
  data-kind="{esc(c["kind"])}" data-name="{esc(search)}">
  {card_thumb(c["id"], "../../")}
  <h3>{esc(dname(c))}</h3>
  <div class="tile-meta"><span>{esc(c["kind"])} · {esc(cost_label(c))}</span><em>{esc(qlabel(c))}</em></div>
</a>""")
        groups.append(f"""<section class="card-group" id="group-{esc(slug)}" data-group-section="{esc(slug)}">
  <div class="card-group-head"><h2>{esc(title)}</h2><span>{esc(latin)} · {len(cards)} 张</span></div>
  <div class="card-grid">{''.join(tiles)}</div>
</section>""")

    faction_chips = "".join(f'<button class="chip" type="button" data-filter="faction" data-value="{esc(f)}">{esc(f)}</button>' for f in FACTION_ORDER)
    quality_chips = "".join(f'<button class="chip" type="button" data-filter="quality" data-value="{esc(q)}">{esc(QUALITY[q])}</button>' for q in QUALITY_ORDER)
    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">CARD ARCHIVE</p>
    <h1>卡牌档案</h1>
    <p class="lead">86 张，每张一个独立页。这里先按编组排；你可以按阵营、品质或名字筛。每张卡的「肥鱼碎碎念」不进入规则结论，只记录读卡时想到的事。</p>
    <div class="hero-latin">86 CARDS · 291 LINKS</div>
  </div>
</section>
<div class="filter-bar" data-card-filters>
  <div class="wrap filter-row">
    <div class="filter-group"><span class="fg-label">FACTION</span><button class="chip" type="button" data-filter="faction" data-value="all">全部</button>{faction_chips}</div>
    <div class="filter-group"><span class="fg-label">QUALITY</span><button class="chip" type="button" data-filter="quality" data-value="all">全部</button>{quality_chips}</div>
    <label class="search"><span class="mono muted">/</span><input type="search" placeholder="搜索卡名、编号、标签" data-filter-search aria-label="搜索卡牌"><span class="mono muted">⌕</span></label>
    <span class="filter-count"><b data-filter-count>86</b> / 86</span>
    <button class="chip" type="button" data-filter-reset>重置</button>
  </div>
</div>
<div class="wrap">
  {''.join(groups)}
  <p class="empty-note" data-empty-note hidden>没有符合条件的卡。换一个筛选，或者清空搜索。</p>
  <p class="small muted" style="margin-top:48px">品质：普通 N / 稀有 R / 史诗 E / 传说 L / 域外 / 觉醒。域外牌无法在收藏中获得；觉醒牌是英雄的觉醒面板，不是普通收藏卡。</p>
</div>"""
    return page("卡牌档案", "../../", body, active="game", desc="长歌 86 张卡牌档案：按编组浏览，按阵营、品质与名字筛选，每张卡都有独立页与读卡笔记。")


# ---------------------------------------------------------------- card page
def relation_rows(cid: str) -> str:
    meta = CONTENT[cid]
    outgoing = [(t, r, w, False) for (t, r, w) in meta.get("links", []) if t in BY_ID]
    incoming = []
    for other in CARDS:
        for (t, r, w) in CONTENT[other["id"]].get("links", []):
            if t == cid:
                incoming.append((other["id"], content.INVERSE.get(r, r), w, True))
    rows = outgoing + incoming
    # 同一条边可能被两端各写一次（出边与入边）。同一目标只保留一条：
    # 优先保留本卡的出边，它的措辞更贴近这张卡自己的视角。
    rows.sort(key=lambda row: 1 if row[3] else 0)
    seen = set()
    unique = []
    for row in rows:
        if row[0] in seen:
            continue
        seen.add(row[0])
        unique.append(row)
    order = {r: i for i, r in enumerate(data_site.RELATION_ORDER)}
    unique.sort(key=lambda x: (order.get(x[1], 99), 1 if x[3] else 0, dname(BY_ID[x[0]])))
    if not unique:
        return '<p class="small muted">这张卡在原典里没有显式关联。它是孤立的，或者它的关系还没有被写出来。</p>'
    out = []
    for other_id, rel, why, is_in in unique:
        label_cls = "rel-label is-in" if is_in else "rel-label"
        out.append(f"""<div class="relation-row">
  <div class="{label_cls}">{esc(rel)}</div>
  <div class="rel-body"><a href="{esc(other_id)}.html">{esc(dname(BY_ID[other_id]))}</a><div class="rel-why">{esc(why)}</div></div>
</div>""")
    return "".join(out)


def keyword_rows(card) -> str:
    text = card.get("text", "") or ""
    role = CONTENT[card["id"]]["role"]
    hits = [k for k in data_site.KEYWORDS if k in text]
    if card["quality"] == "域外" and "域外" not in hits:
        hits.insert(0, "域外")
    if card["kind"] == "觉醒" and "觉醒" not in hits:
        hits.append("觉醒")
    if not hits:
        return '<p class="small muted">卡文没有命中已归档的规则词条。</p>'
    return "".join(
        f'<div class="kw"><b>{esc(k)}</b>{esc(data_site.KEYWORDS[k]["short"])}</div>'
        for k in hits[:8]
    )


def build_card_page(cid: str) -> str:
    card = BY_ID[cid]
    meta = CONTENT[cid]
    index = CARDS.index(card)
    prev_card = CARDS[index - 1] if index > 0 else None
    next_card = CARDS[index + 1] if index < len(CARDS) - 1 else None
    hero = card.get("hero") or ""
    hero_link = f'<a href="../../cast.html#{esc(hero)}">{esc(hero)}</a>' if hero else "通用"
    stamp = ""
    if card["cost"] is None or "施工中" in (card.get("text") or ""):
        stamp = '<span class="stamp">施工中</span>'
    text = card.get("text") or "（原典没有给出卡文。）"
    tags = [
        f'<span class="tag is-faction">{esc(card["faction"])}</span>',
        f'<span class="tag is-quality">{esc(qlabel(card))}</span>',
        f'<span class="tag">{esc(card["kind"])}</span>',
        f'<span class="tag is-cost">COST {esc(cost_label(card))}</span>',
    ]
    if card.get("type_line"):
        tags.append(f'<span class="tag">{esc(card["type_line"])}</span>')
    for ax in meta.get("axes", []):
        tags.append(f'<span class="tag">{esc(ax)}</span>')

    prev_html = f'<a href="{prev_card["id"]}.html"><span>← 上一张</span><b>{esc(dname(prev_card))}</b></a>' if prev_card else "<div></div>"
    next_html = f'<a href="{next_card["id"]}.html"><span>下一张 →</span><b>{esc(dname(next_card))}</b></a>' if next_card else "<div></div>"

    body = f"""<div class="wrap card-page">
  {breadcrumb([("长歌", "../../index.html"), ("游戏编", "../index.html"), ("卡牌档案", "index.html"), (card["group"], f"index.html#group-{card["group_slug"]}"), (dname(card), None)])}
  <div class="card-layout">
    <div class="plate-wrap">
      {card_thumb(cid, "../../")}
      <div class="plate-caption"><span>PLATE {str(index+1).zfill(3)} / {len(CARDS):03d}</span><span>{esc(card["id"]).upper()}</span></div>
      <p class="plate-note">卡面为程序生成的概念图版；卡文与规则以本页正文为准。</p>
    </div>
    <div class="card-head">
      <div class="kicker">CARD / {esc(card["group_slug"]).upper()} / {esc(card["kind"])}</div>
      <h1>{esc(dname(card))}</h1>
      <div class="card-role">{esc(meta["role"])}</div>
      <div class="tag-row">{''.join(tags)}</div>
      <div class="card-text">{esc(text)}{stamp}</div>
      <dl class="quick-grid">
        <div><dt>COST</dt><dd>{esc(cost_label(card))}</dd></div>
        <div><dt>C / A / D</dt><dd>{esc(panel_text(card))}</dd></div>
        <div><dt>GROUP</dt><dd>{esc(card["group"])}<small>{esc(card["kind"])}</small></dd></div>
        <div><dt>LIMIT</dt><dd>{esc(limit_text(card))}<small>构筑上限</small></dd></div>
      </dl>
      <p class="owned-line"><b>归属</b> {hero_link}{'' if card["group"] == hero else f' · {esc(card["group"])}'} · {esc(card["faction"])} · {esc(qlabel(card))}。上限字段为「{esc(limit_text(card))}」；原典未列上限的卡，页面不替它补。</p>
    </div>
  </div>
  <section class="card-section">
    <h2>关联 <span>LINKS · 出边 + 入边 · 同目标去重</span></h2>
    <p class="small muted" style="margin:6px 0 10px">关联不是规则联动。它记录这张卡在设计与叙事上依赖谁、被谁依赖；跨阵营的边只标「对照」。</p>
    {relation_rows(cid)}
  </section>
  <section class="card-section">
    <h2>词条 <span>KEYWORDS IN TEXT</span></h2>
    <div class="kw-list">{keyword_rows(card)}</div>
  </section>
  <section class="note-block">
    <div class="note-kicker">ARCHIVIST'S NOTE</div>
    <h2>肥鱼碎碎念</h2>
    {''.join(f"<p>{esc(p)}</p>" for p in meta.get("note", []))}
    <p class="note-sign">—— 归档者，读这张卡的时候</p>
  </section>
  <nav class="card-pager" aria-label="上一张 / 下一张">{prev_html}{next_html}</nav>
</div>"""
    return page(dname(card), "../../", body, active="game", desc=f'{dname(card)}：{meta["role"]}。长歌卡牌档案。')


# ---------------------------------------------------------------- novel
def build_novel() -> str:
    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">MAIN STORY</p>
    <h1>小说</h1>
    <p class="lead">正文仍在写。这个页面先把「发布」这件事安排好：放在哪里、按什么顺序放、哪些内容先不放。</p>
    <div class="hero-latin">SERIALIZATION · TO BE CONTINUED</div>
  </div>
</section>
<div class="wrap">
  <section class="coming">
    <div class="stamp">筹备中 · 尚未发布</div>
    <h1>长歌</h1>
    <p class="lead">月亮升起之前，先把路走完。<br>等正文准备好，它会从这里开始。</p>
  </section>
  <section class="section">
    {section_head("01", "PUBLICATION PLAN", "发布计划", "官方页与小说正文共用同一个静态站。现在先不启用 GitPage；等这一版看完、结构定下来，再接自定义域名或仓库 Pages。")}
    <div class="plan-grid">
      <article><b>01 / HOST</b><h3>静态站</h3><p>整站是纯静态 HTML/CSS/SVG，不依赖后端。小说接入后仍然可以直接放在 GitPage、对象存储或任意静态托管上。</p></article>
      <article><b>02 / ORDER</b><h3>连载顺序</h3><p>按主线推进：格兰蒂亚 → 芬特罗德 → 记忆森林 → 黄金之城 → 钢铁之城 → 无梦之城。每一章独立成页，附上一页的「路上」与人物小传。</p></article>
      <article><b>03 / BOUNDARY</b><h3>不发布的部分</h3><p>「真相」相关章节不会以设定说明的形式提前放出；它们只以小说正文出现。官方页负责指路，不负责替小说说完。</p></article>
    </div>
    <p class="rule-note" style="margin-top:28px"><b>现在：</b> 小说目录仍为空。本页只作为入口与发布说明，不包含正文。等作者确认后，再把 MainStory 的章节接入。</p>
    <a class="btn" href="index.html">回到序</a>
  </section>
</div>"""
    return page("小说", "", body, active="novel", desc="长歌小说：发布计划与入口。正文筹备中，尚未发布。")


# ---------------------------------------------------------------- about
def build_about() -> str:
    body = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">COLOPHON</p>
    <h1>关于</h1>
    <p class="lead">这一页说明：这些字从哪里来，哪些是原典，哪些是裁定，哪些只是归档者的读卡笔记。</p>
    <div class="hero-latin">SOURCES · METHOD · COLOPHON</div>
  </div>
</section>
<div class="wrap about-grid">
  <div class="about-body">
    <p>{esc(PROJECT["title"])}（{esc(LATIN)}）是一个由小说、音乐与游戏构成的联合企划，作者 {esc(PROJECT["author"])}。官方页的目标不是把所有设定一次讲完，而是给三条线各留一个入口。</p>
    <h2>页面怎么读</h2>
    <p>「世界」「战史」「人物」是设定层；「游戏编」是设计层；「卡牌档案」是归档层。设定层以根目录 Outline.md 为准；卡牌文本以 Game/CardsDesign.md 为准；两者冲突时，以 Agent/Qwen/作者裁定汇编.md 为准。</p>
    <p>卡页里的「肥鱼碎碎念」是归档者的读卡笔记，不是作者裁定，也不进入规则结论。它记录的是「这张卡为什么这样设计」「它在牌池里站在哪里」「它和哪段叙事对得上」。</p>
    <h2>卡面与图版</h2>
    <p>所有卡面与概念图都是程序生成的 SVG，采用纸本 + 双色丝网印的视觉体系。它们是概念图层级，不是最终游戏美术；角色立绘、场景原画与 UI 仍在后续制作中。</p>
    <h2>关于小说</h2>
    <p>正文尚未发布。小说页目前只说明发布计划；没有正文、没有试读、没有「即将上线」的倒计时。</p>
    <h2>声明</h2>
    <p>本页为企划归档与宣传用途，不是商业发行页面。卡牌灵感来源为 1939 工作室的《Kards》；文字冒险部分使用作者的另一项目 GodotADV。除此之外，页面中的设定、人物、卡牌与图版均为本企划原创或基于原典整理。</p>
  </div>
  <aside class="side-note">
    <h3>数据来源</h3>
    <ul class="source-list">
      <li><b>根目录 Outline.md</b><br>世界、种族、组织、历史、人物</li>
      <li><b>Game/Outline.md</b><br>游戏规则与词条</li>
      <li><b>Game/CardsDesign.md</b><br>86 张卡牌原典</li>
      <li><b>Agent/Qwen/作者裁定汇编.md</b><br>冲突时的最高优先级</li>
      <li><b>Agent/Qwen/卡牌理解/</b><br>归档者的读卡参考</li>
    </ul>
    <p class="small muted" style="margin-top:14px">版本：{esc(PROJECT["edition"])} · {esc(PROJECT["date"])}</p>
  </aside>
</div>"""
    return page("关于", "", body, active="about", desc="长歌官方页的资料来源、编辑方法与版权声明。")


# ---------------------------------------------------------------- 404
def build_404() -> str:
    body = """<div class="wrap err">
  <div class="code">404</div>
  <h1>这一页还没有被写出来。</h1>
  <p class="lead" style="margin:0 auto 28px">可能是链接旧了，也可能是这条路还没修。回到序，或者去卡牌档案里随便翻一张。</p>
  <a class="btn" href="index.html">回到序</a>
</div>"""
    return page("404", "", body, active="", desc="页面不存在。")


# ---------------------------------------------------------------- assets
def write_assets(cards) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "site.css").write_text(theme.CSS, encoding="utf-8")
    (ASSETS / "site.js").write_text(theme.JS, encoding="utf-8")
    (ASSETS / "seal.svg").write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><mask id="m"><rect width="64" height="64" fill="#000"/><circle cx="29" cy="30" r="13" fill="#fff"/><circle cx="35" cy="26" r="11" fill="#000"/></mask></defs>
<rect width="64" height="64" fill="#171c26"/>
<circle cx="32" cy="32" r="24" fill="none" stroke="#a67c3d" stroke-width="1"/>
<rect width="64" height="64" fill="#f4efe4" mask="url(#m)"/>
</svg>""",
        encoding="utf-8",
    )
    # 卡面与概念图
    n_cards, n_plates = art.build_all(ASSETS, cards, CONTENT)
    # 人物纹章
    for i, p in enumerate(data_site.CAST, 1):
        svg = art.sigil_svg(p["latin"], p["motifs"], p["tone"], roman(i), 360, p["epithet"])
        (ASSETS / "heroes" / (p["id"] + ".svg")).write_text(svg, encoding="utf-8")
    print(f"assets: {n_cards} cards, {n_plates} plates, {len(data_site.CAST)} sigils")


def write_page(rel_path: str, html: str) -> None:
    html, applied, stale = textpatch.apply_page(html, rel_path)
    if applied or stale:
        print(f"textpatch: {rel_path}: {applied} applied, {stale} stale")
    path = OUT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    global CARDS, BY_ID, CONTENT
    CARDS = cardsource.load_cards()
    BY_ID = {c["id"]: c for c in CARDS}
    CONTENT = content.ALL
    missing = [c["id"] for c in CARDS if c["id"] not in CONTENT]
    if missing:
        raise SystemExit(f"content missing: {missing}")
    extra = [k for k in CONTENT if k not in BY_ID]
    if extra:
        raise SystemExit(f"content has unknown ids: {extra}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    write_assets(CARDS)

    pages = {
        "index.html": build_home(),
        "world.html": build_world(),
        "history.html": build_history(),
        "cast.html": build_cast(),
        "novel.html": build_novel(),
        "about.html": build_about(),
        "404.html": build_404(),
        "game/index.html": build_game_index(),
        "game/play.html": build_play(),
        "game/concept.html": build_concept(),
        "game/atlas.html": build_atlas(),
        "game/cards/index.html": build_cards_index(),
    }
    for c in CARDS:
        pages[f'game/cards/{c["id"]}.html'] = build_card_page(c["id"])

    for rel, html in pages.items():
        write_page(rel, html)
    print(f"built {len(pages)} pages -> {OUT}")
    print(f"cards {len(CARDS)} · links {sum(len(CONTENT[c['id']].get('links', [])) for c in CARDS)}")


if __name__ == "__main__":
    main()
