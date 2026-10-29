# -*- coding: utf-8 -*-
"""第三轮补丁：【觉醒】独立成类别、域外不可构筑、相关文案同步。"""
import io, re, subprocess, sys

SRC = r"D:\Projects\HisStory\dsh\src"
PY = sys.executable


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def sub(s, old, new, tag=""):
    if old not in s:
        print("  MISS:", tag or old[:40])
        return s
    print("  ok:", tag or old[:24])
    return s.replace(old, new, 1)


# ---------- 1. gen_cards：觉醒类别 ----------
p = SRC + r"\gen_cards.py"
s = rd(p)
if 'e["name"] == "【觉醒】"' not in s:
    s = sub(s, "    cat = cat_of(e)",
            '''    cat = cat_of(e)
    if e["name"] == "【觉醒】":
        cat = "觉醒"''', "gen: cat")
    wr(p, s)

print(subprocess.run([PY, SRC + r"\gen_cards.py"], capture_output=True, text=True).stdout.strip())

# ---------- 2. data：两条 note 澄清「觉醒不是天赋」 ----------
p = SRC + r"\data_cards.py"
s = rd(p)
s = sub(s, "觉醒不是一张「更强的天赋」，而是把三张天赋的能力叠成了一台引擎：",
        "觉醒不是天赋，也不是「一张更强的天赋」——它是三张天赋的能力叠成的一台引擎；"
        "只是在构筑时你带不进去，得先在场上把蓄能走完：", "note: lilia")
s = sub(s, 'note="攻击后 +25 攻击力、专属魔法不再扣防御',
        'note="（觉醒面板，不能作为天赋带进卡组。）攻击后 +25 攻击力、专属魔法不再扣防御', "note: eve")
wr(p, s)

# ---------- 3. meta ----------
p = SRC + r"\meta.py"
s = rd(p)
s = sub(s, 'CAT_LABEL = {"魔法": "魔法", "单位": "单位", "天赋": "天赋"}',
        'CAT_LABEL = {"魔法": "魔法", "单位": "单位", "天赋": "天赋", "觉醒": "觉醒"}', "meta: CAT_LABEL")
s = sub(s, 'dict(name="【觉醒】", why="一张天赋牌，同时是苍白之月、经络与苍白缄默三张牌的入口。", tag="莉莉亚 · 天赋")',
        'dict(name="【觉醒】", why="不是天赋，不能带进卡组：走完两次蓄能、拿到苍白之月之后，才换上的那套面板。", tag="莉莉亚 · 觉醒")', "meta: FEATURED")
s = sub(s, 'panel="2C / 200A / 250D（觉醒）", talents=4,', 'panel="2C / 200A / 250D（觉醒）", talents=3,', "meta: lilia talents")
s = sub(s, 'panel="1C / 150A / 200D（觉醒）", talents=4,', 'panel="1C / 150A / 200D（觉醒）", talents=3,', "meta: eve talents")
s = sub(s, "第四张天赋就是觉醒本身——入场先把「通向月面的经络」塞进手里。",
        "觉醒不是第四张天赋：它是走完两次蓄能之后换来的一套面板，带不进卡组。", "meta: lilia profile")
s = sub(s, 'kw=["御风", "觉醒", "林地"]', 'kw=["御风", "觉醒", "林地"]', "meta: eve kw")
wr(p, s)

# ---------- 4. build：类别 chips / 首页文案 / 归属行 ----------
p = SRC + r"\build.py"
s = rd(p)
s = sub(s, 'for k in ("魔法", "单位", "天赋"):', 'for k in ("魔法", "单位", "天赋", "觉醒"):', "build: cat chips")
s = sub(s, "挑六张：一张检索、一张天赋、一张终局、一张御风、一张唯一、一张标题。",
        "挑六张：一张检索、一张觉醒、一张终局、一张御风、一张唯一、一张标题。", "build: feat lead")
s = sub(s, """    belong.append('<p class="tiny dim" style="margin:0">类别：' + esc(c["cat"]) +
                  ('　·　收藏上限 ' + esc(c["lim"]) if c.get("lim") else "") + '</p>')""",
        """    buildable = c["cat"] not in ("觉醒",) and c["q"] != "域外"
    lim_txt = ('收藏上限 ' + esc(c["lim"])) if (buildable and c.get("lim")) else "不可构筑"
    belong.append('<p class="tiny dim" style="margin:0">类别：' + esc(c["cat"]) +
                  '　·　' + lim_txt + '</p>')""", "build: belong")
wr(p, s)

# ---------- 5. sandbox.js：域外与觉醒不进池 ----------
p = r"D:\Projects\HisStory\dsh\assets\js\sandbox.js"
s = rd(p)
s = sub(s, "  var CARDS = window.CARDS;",
        """  // 【域外】与【觉醒】不可构筑：不出现在池子里，也不接受加入
  var CARDS = window.CARDS.filter(function (c) { return c.q !== "域外" && c.cat !== "觉醒"; });""",
        "sandbox: filter")
s = sub(s, """    var c = byId[id];
    if (!c) return;""",
        """    var c = byId[id];
    if (!c) return;
    if (c.q === "域外" || c.cat === "觉醒") return;""", "sandbox: guard")
wr(p, s)

print("done")
