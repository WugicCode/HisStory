# -*- coding: utf-8 -*-
"""patch_meta7.py —— 第四轮：特色卡文案、索引、人物称谓。"""
import io

P = r"D:\Projects\HisStory\dsh\src\meta.py"
s = io.open(P, encoding="utf-8").read()


def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, 1)


rep('dict(name="英雄水晶", why="把「抽不到英雄」变成「迟早抽到」——而且它把自己洗回卡组。", tag="通用 · 检索")',
    'dict(name="英雄水晶", why="把「抽不到英雄」变成「迟早抽到」——用完还加入卡组一张自身，越用越多。", tag="通用 · 检索")')
rep('dict(name="【觉醒】", why="不是天赋，不能带进卡组：走完两次蓄能、拿到苍白之月之后，才换上的那套面板。", tag="莉莉亚 · 觉醒")',
    'dict(name="【觉醒】", why="不是天赋，不能带进卡组：用掉一张苍白之月，才换上的那套面板。", tag="莉莉亚 · 觉醒")')
rep('dict(name="大奇迹·超度·英灵颂", why="死得越多，打得越轻；一个都没死，反而是一千点。", tag="米莉卡 · 唯一")',
    'dict(name="大奇迹·超度·英灵颂", why="每死一个单位就多两次 25 点；除英雄外一个都没死，反而是一千点。", tag="米莉卡 · 唯一")')
rep('dict(name="永恒的记忆", why="扣光自己的防御，对敌方全体打 300。全篇最贵的一次呼吸。", tag="伊芙格林 · 御风")',
    'dict(name="永恒的记忆", why="扣光自己的防御，对敌方全体打 300。全篇最贵的一次呼吸。", tag="伊芙格林 · 御风")')

rep('("cast.html", "人物", "新的勇者七人、七位大贤者、魔王军七军团长。", "21 NAMES")',
    '("cast.html", "人物", "新的勇者七人、七位大贤者、七位魔王军领袖。", "21 NAMES")')
rep('("rulebook.html", "规则手册", "战斗系统原文的结构化重排，含归档注与原文笔误标注。", "RULES")',
    '("rulebook.html", "规则手册", "战斗系统原文的结构化重排，附动词表、作者裁定，以及待确认项。", "RULES")')

io.open(P, "w", encoding="utf-8").write(s)

# ── meta_world：称谓、阿尔法冲突、大陆待定 ────────────────
P2 = r"D:\Projects\HisStory\dsh\src\meta_world.py"
w = io.open(P2, encoding="utf-8").read()
w = w.replace("魔王军七军团长", "七位魔王军领袖")
w = w.replace("七位军团长", "七位魔王军领袖")
w = w.replace("军团长们", "领袖们")
io.open(P2, "w", encoding="utf-8").write(w)
print("ok", w.count("领袖"))
