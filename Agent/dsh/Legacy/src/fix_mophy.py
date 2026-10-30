# -*- coding: utf-8 -*-
import io, re

P_META = r"D:\Projects\HisStory\dsh\src\meta.py"
P_WORLD = r"D:\Projects\HisStory\dsh\src\meta_world.py"
P_GEN = r"D:\Projects\HisStory\dsh\src\gen_cards.py"

s = io.open(P_META, encoding="utf-8").read()

# 1. 同盟军 19 → 18 张
old = "赫琉思拆盾，斯卡琳攒月——19 张，前者攻、后者守"
assert old in s
s = s.replace(old, "赫琉思拆盾，斯卡琳攒月——18 张，前者攻、后者守")

# 2. 魔王军：已有 1 张
old = '''    dict(id="魔王军", motto="——", tag="施工中",
         sub="THE DEMON ARMY",
         desc="七位军团长的阵营。卡牌设计稿里还没有一张挂着它的名字——唯一被人物表归入其中的莫菲，她的卡仍挂在同盟军名下。归档照录这处矛盾，不替作者裁定。",'''
new = '''    dict(id="魔王军", motto="梦之掌司，先落一网。", tag="1 张",
         sub="THE DEMON ARMY",
         desc="七位军团长的阵营。目前只有第七军团长莫菲的一张牌进入归档：捕梦网，1 费，禁锢一个战区。其余六位军团长的牌还没有被写下来。",'''
assert old in s
s = s.replace(old, new)

# 3. 莫菲：英雄条目改阵营
old = '''dict(id="mophy", name="莫菲", sub="一张网，盖住一个战区", fac="同盟军", type="法师 · 神官",'''
new = '''dict(id="mophy", name="莫菲", sub="一张网，盖住一个战区", fac="魔王军", type="法师 · 神官",'''
assert old in s
s = s.replace(old, new)

old = 'design="同盟军里最便宜、也最像「关灯」的一张牌。'
new = 'design="魔王军目前唯一的一张牌，也是全场最便宜、最像「关灯」的一张。'
assert old in s
s = s.replace(old, new)

# 4. 莫菲编组改阵营
old = '''dict(id="mophy", name="莫菲", fac="同盟军", tag="未完成", hero="mophy",'''
new = '''dict(id="mophy", name="莫菲编组", fac="魔王军", tag="军团长", hero="mophy",'''
assert old in s
s = s.replace(old, new)

# 5. 原典行数
s = re.sub(r'"Outline\.md", "(\d+) 行', lambda m: '"Outline.md", "171 行', s, count=1) if '"Outline.md", "' in s else s
io.open(P_META, "w", encoding="utf-8").write(s)
print("meta patched; outline line ok:", '"171 行' in s)

# ---- meta_world: 冲突说明改成已更正 ----
w = io.open(P_WORLD, encoding="utf-8").read()
old = w[w.index("CAST_CONFLICT = dict("):]
new = '''CAST_CONFLICT = dict(
    title="莫菲：归属已更正",
    body="卡牌设计稿原先把她写在「同盟军」名下，是笔误；作者已确认莫菲属魔王军第七军团长「梦之掌司」。"
         "归档已按魔王军重排她的卡与人物条目——现在两边一致了。",
)
'''
w = w.replace(old, new)
io.open(P_WORLD, "w", encoding="utf-8").write(w)
print("world patched")

# ---- gen_cards: 新卡默认阵营 ----
g = io.open(P_GEN, encoding="utf-8").read()
old = '"helius": "同盟军", "scarlett": "同盟军", "mophy": "同盟军"}'
assert old in g
g = g.replace(old, '"helius": "同盟军", "scarlett": "同盟军", "mophy": "魔王军"}')
io.open(P_GEN, "w", encoding="utf-8").write(g)
print("gen patched")
