# -*- coding: utf-8 -*-
"""patch_fix5.py —— 第四轮：清除「五段」「军团长」「洗回牌库」残留。"""
import io, re

B = r"D:\Projects\HisStory\dsh\src\build.py"
M = r"D:\Projects\HisStory\dsh\src\meta.py"
D = r"D:\Projects\HisStory\dsh\src\data_cards.py"

# ── build.py ──────────────────────────────
s = io.open(B, encoding="utf-8").read()
s = s.replace('"一条被切成五段的线，两端各立着一座信仰。所有的伤害，最终都要穿过这条线。"',
              '"若干条被切成数段战区的线串在一起，两端各立着一座信仰。所有的伤害，最终都要穿过这些线。"')
s = s.replace('aria-label="五段战场示意图"', 'aria-label="战场示意图"')
s = s.replace("示意图 · 五段战场，两端各一座信仰", "示意图 · 若干战区，两端各一座信仰")
s = s.replace("示意图固定为五段。原典设定：战区排布由随机地图决定，末端战区必然存在，且不能被对方占领。",
              '" + esc(R.BOARD_NOTE) + "')
io.open(B, "w", encoding="utf-8").write(s)

# ── meta.py ──────────────────────────────
t = io.open(M, encoding="utf-8").read()
t = t.replace('tag="军团长"', 'tag="领袖"')
t = t.replace("新的勇者、七位大贤者、魔王军七军团长", "新的勇者、七位大贤者、魔王军七位领袖")
io.open(M, "w", encoding="utf-8").write(t)

# ── data_cards.py ─────────────────────────
d = io.open(D, encoding="utf-8").read()
d = d.replace("两枚「水晶」构成检索闭环，都把自己洗回牌库", "两枚「水晶」构成检索闭环，都把自己加入卡组")
io.open(D, "w", encoding="utf-8").write(d)
print("fixed")
