# -*- coding: utf-8 -*-
"""第二轮：build.py —— 导航、卡页词条栏、战场注记、三个新页面。"""
import io, re

P = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(P, encoding="utf-8").read()


def sub(old, new, cnt=1):
    global s
    if old not in s:
        raise SystemExit("MISS: " + old[:60].replace("\n", "\\n"))
    s = s.replace(old, new, cnt)


# ---------- 1. 导航 ----------
sub('''NAV_MAIN = [("序", "#preface"), ("世界观", "#world"), ("战场", "#board"),
            ("玩法", "#play"), ("阵营", "#factions"), ("特色卡牌", "#featured"),
            ("关系", "#constellation"), ("图鉴", "archive.html"),
            ("沙盘", "sandbox.html"), ("规则", "rulebook.html")]

NAV_SUB = [("图鉴", "archive.html"), ("沙盘", "sandbox.html"),
           ("规则", "rulebook.html"), ("英雄", "index.html#heroes"),
           ("主页", "index.html")]''',
'''NAV_MAIN = [("世界观", "#world"), ("战争史", "story.html"), ("人物", "cast.html"),
            ("战场", "#board"), ("玩法", "#play"), ("阵营", "#factions"),
            ("图鉴", "archive.html"), ("沙盘", "sandbox.html"),
            ("规则", "rulebook.html")]

NAV_SUB = [("世界观", "world.html"), ("战争史", "story.html"), ("人物", "cast.html"),
           ("图鉴", "archive.html"), ("沙盘", "sandbox.html"),
           ("规则", "rulebook.html"), ("主页", "index.html")]''')

# ---------- 2. 战场注记 ----------
sub("""<i class="lg-none"></i>无法触及</span></div></div>'""",
    """'<span><i class="lg-none"></i>无法触及</span></div>'
        '<p class="tiny dim" style="margin:12px 0 0">示意图固定为五段。原典设定：战区排布由随机地图决定，'
        '末端战区必然存在，且不能被对方占领。</p></div>'""")

# ---------- 3. 卡页词条栏 ----------
sub("""    fish_paras = c["note"].split("\\n") if isinstance(c["note"], str) else [c["note"]]""",
    '''    # 词条栏：从卡面文本里抓【…】，逐条给出原典定义
    term_map = {t["n"].replace(" ", ""): t for t in M.TERMS}
    seen_kw, kw_rows = set(), []
    for raw in re.findall(r"【([^】]+)】", c["text"]):
        key = raw.replace(" ", "")
        t = term_map.get(key) or term_map.get(re.sub(r"[0-9]+$", "X", key))
        if not t or t["n"] in seen_kw:
            continue
        seen_kw.add(t["n"])
        kw_rows.append('<div class="kwdef"><dt>' + esc(t["n"]) + '</dt><dd>' + esc(t["t"]) +
                       ('<span class="kn">' + esc(t["note"]) + '</span>' if t.get("note") else "") + '</dd></div>')
    kw_panel = ('<div class="side-card"><h4>词条</h4>' +
                ("".join(kw_rows) if kw_rows else
                 '<p class="tiny dim" style="margin:0">这张卡面上没有出现规则词条。</p>') +
                '<p class="tiny dim" style="margin:12px 0 0">释义照录规则原文；标注「归档注」的是归档者补的说明。</p></div>')

    fish_paras = c["note"].split("\\n") if isinstance(c["note"], str) else [c["note"]]''')

sub('''        + rel_html + '</div><div>' + "".join(belong) +
        '</div></div></div></div>\'''',
    '''        + rel_html + '</div><div>' + "".join(belong) + kw_panel +
        '</div></div></div></div>\'''')

# ---------- 4. 新页面 ----------
NEW = r'''

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
                                    ("cast.html", "人物", "新的勇者、七位大贤者、魔王军七军团长。"))) +
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
        for i, t in enumerate(W.TIMELINE)) + '</ul>')

    aside = ('<div class="aside-box"><h4>' + esc(W.STORY_ASIDE["title"]) + '</h4><p>' +
             esc(W.STORY_ASIDE["body"]) + '</p></div>')

    hero = ('<div class="page-head"><div class="page-kicker">STORY / THE ALLIANCE WAR</div>'
            '<h1 class="page-title">战争史</h1>'
            '<p class="page-lead">五百年前，七个人结束了五十年的战争。史书到这里就写完了。'
            '这一页照录史书，也照录它没有写的那一句。</p></div>')

    body = (head("战争史", "同盟战争的编年与史书的空白", "") + nav("", False, "story.html") + hero +
            sec("preface", "01", "背景", "BEFORE THE MOON RISES", "", '<div class="preface-body">' + paras + '</div>') +
            sec("timeline", "02", "编年", "A TIMELINE", "七格，从诸族并立到预言之世。", tl) +
            sec("after", "03", "战后", "AFTER THE WAR", "", '<div class="preface-body">' + after + '</div>' + aside) +
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

    body = (head("人物", "新的勇者、七位大贤者、魔王军七军团长", "") + nav("", False, "cast.html") + hero +
            "".join(blocks) + '<section class="sec"><div class="wrap">' + conflict + '</div></section>' + foot(""))
    write(ROOT / "cast.html", body)

'''

anchor = "# ══════════════════════════════ 资源 ══════════════════════════════"
s = s.replace(anchor, NEW.lstrip("\n") + "\n" + anchor, 1)

# 模块级引用与 main 调用
sub("import meta as M", "import meta as M\nimport meta_world as MW")
sub("import math\n", "import math\nimport re\n") if "import re\n" not in s else None
print("re imported:", "import re" in s)

io.open(P, "w", encoding="utf-8").write(s)
print("build.py patched")
